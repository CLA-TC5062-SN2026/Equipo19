"""Autenticación: hash de contraseñas (bcrypt), emisión y validación del JWT y de la sesión en servidor.

El token (HS256, firmado con JWT_SECRET) lleva `sub` (usuario), `sid` (sesión), `iat` y `exp`. En cada solicitud
se valida firma y `exp`, y además que la sesión `sid` exista, pertenezca a `sub`, no esté revocada, no haya
vencido y tenga menos de 60 minutos sin actividad; si pasa, se actualiza su última actividad. El rol y el estado
del usuario se leen de la base, nunca del token (contrato, `securitySchemes.BearerAuth`).
"""

import logging
import uuid
from datetime import datetime, timedelta, timezone
from functools import lru_cache
from typing import Annotated, NamedTuple

import bcrypt
import jwt
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import update
from sqlalchemy.orm import Session

from app.config import get_settings
from app.db import get_db
from app.errores import ErrorAPI
from app.modelos import Sesion, Usuario

log = logging.getLogger("sgpis.seguridad")

ALGORITMO_JWT = "HS256"
INACTIVIDAD_MIN = 60  # RF-26-AC-6; el contrato fija 60 minutos.
MAX_BYTES_CONTRASENA = 72  # bcrypt solo procesa los primeros 72 bytes; bcrypt 5 rechaza más.
MIN_BYTES_SECRETO = 32
COSTO_BCRYPT = 12

esquema_bearer = HTTPBearer(scheme_name="BearerAuth", bearerFormat="JWT", auto_error=False)
Credenciales = Annotated[HTTPAuthorizationCredentials | None, Depends(esquema_bearer)]


class Autenticacion(NamedTuple):
    usuario: Usuario
    sesion: Sesion


def sesion_invalida() -> ErrorAPI:
    return ErrorAPI(
        401,
        "sesion_invalida",
        "La sesión no es válida o expiró; inicie sesión de nuevo",
        headers={"WWW-Authenticate": "Bearer"},
    )


def _error_configuracion(variable: str) -> ErrorAPI:
    log.error("%s no está definida o no es válida; la autenticación queda deshabilitada", variable)
    return ErrorAPI(500, "error_interno", "Error interno del servidor")


def _ahora() -> datetime:
    return datetime.now(timezone.utc)


# [S-01] Valores de ejemplo publicados en el repositorio (.env.example). Quien copie .env.example a .env sin
# cambiarlo firmaría tokens con un secreto público; el v0 lo aceptaba porque mide más de 32 bytes.
SECRETOS_DE_EJEMPLO = {"cambiar_por_un_secreto_aleatorio_de_al_menos_32_bytes"}


def _secreto() -> str:
    s = get_settings().jwt_secret
    valor = s.get_secret_value() if s is not None else ""
    if len(valor.encode("utf-8")) < MIN_BYTES_SECRETO or valor in SECRETOS_DE_EJEMPLO:
        raise _error_configuracion("JWT_SECRET")
    return valor


def duracion_token() -> timedelta:
    segundos = get_settings().jwt_expiration
    if segundos is None:
        raise _error_configuracion("JWT_EXPIRATION")
    return timedelta(seconds=segundos)


def verificar_configuracion() -> None:
    """Falla con 500 antes de tocar la base si falta JWT_SECRET o JWT_EXPIRATION."""
    _secreto()
    duracion_token()


# ------------------------------------------------------------------ contraseñas
def contrasena_excede_limite(contrasena: str) -> bool:
    return len(contrasena.encode("utf-8")) > MAX_BYTES_CONTRASENA


def hash_contrasena(contrasena: str) -> str:
    return bcrypt.hashpw(contrasena.encode("utf-8"), bcrypt.gensalt(rounds=COSTO_BCRYPT)).decode("ascii")


@lru_cache
def _hash_simulado() -> bytes:
    return bcrypt.hashpw(b"contrasena-de-relleno", bcrypt.gensalt(rounds=COSTO_BCRYPT))


def verificar_contrasena(contrasena: str, hash_guardado: str | None) -> bool:
    """Compara con bcrypt. Sin hash (correo inexistente, cuenta sin activar) o con una contraseña fuera de límite
    se hace igual una comparación del mismo costo, para que el tiempo de respuesta no revele si la cuenta existe."""
    if hash_guardado is None or contrasena_excede_limite(contrasena):
        bcrypt.checkpw(b"contrasena-de-relleno-x", _hash_simulado())
        return False
    try:
        return bcrypt.checkpw(contrasena.encode("utf-8"), hash_guardado.encode("ascii"))
    except ValueError:
        log.warning("Hash de contraseña con formato inválido en la base")
        return False


# ------------------------------------------------------------------ JWT
def emitir_token(usuario_id: uuid.UUID, sid: uuid.UUID, emitido: datetime, expira: datetime) -> str:
    claims = {
        "sub": str(usuario_id),
        "sid": str(sid),
        "iat": int(emitido.timestamp()),
        "exp": int(expira.timestamp()),
    }
    return jwt.encode(claims, _secreto(), algorithm=ALGORITMO_JWT)


def _decodificar(token: str) -> tuple[uuid.UUID, uuid.UUID]:
    secreto = _secreto()
    try:
        claims = jwt.decode(
            token,
            secreto,
            algorithms=[ALGORITMO_JWT],
            options={"require": ["sub", "sid", "iat", "exp"]},
        )
        return uuid.UUID(str(claims["sub"])), uuid.UUID(str(claims["sid"]))
    except (jwt.InvalidTokenError, ValueError, TypeError, KeyError):
        raise sesion_invalida() from None


def validar_token(db: Session, token: str) -> Autenticacion:
    """Valida JWT y sesión; si todo pasa, marca la actividad y confirma. Cualquier falla responde 401."""
    usuario_id, sid = _decodificar(token)
    momento = _ahora()
    # Validación y marca de actividad en una sola sentencia: no hay ventana entre revisar y actualizar.
    sesion = db.execute(
        update(Sesion)
        .where(
            Sesion.sid == sid,
            Sesion.usuario_id == usuario_id,
            Sesion.revocada_en.is_(None),
            Sesion.expira_en > momento,
            Sesion.ultima_actividad > momento - timedelta(minutes=INACTIVIDAD_MIN),
        )
        .values(ultima_actividad=momento)
        .returning(Sesion)
        .execution_options(synchronize_session=False)
    ).scalar_one_or_none()
    if sesion is None:
        db.rollback()
        raise sesion_invalida()
    usuario = db.get(Usuario, usuario_id)
    if usuario is None or usuario.estado != "activo":
        db.rollback()
        raise sesion_invalida()
    db.commit()
    return Autenticacion(usuario, sesion)


# ------------------------------------------------------------------ dependencias
def sesion_autenticada(cred: Credenciales, db: Annotated[Session, Depends(get_db)]) -> Autenticacion:
    """Exige `Authorization: Bearer <token>` válido; sin él, 401."""
    if cred is None:
        raise sesion_invalida()
    return validar_token(db, cred.credentials)


def usuario_autenticado(auth: Annotated[Autenticacion, Depends(sesion_autenticada)]) -> Usuario:
    return auth.usuario


SesionAutenticada = Annotated[Autenticacion, Depends(sesion_autenticada)]
UsuarioAutenticado = Annotated[Usuario, Depends(usuario_autenticado)]
