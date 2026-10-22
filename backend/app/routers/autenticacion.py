"""Autenticación: registro por invitación, inicio y cierre de sesión, usuario actual (RF-03-AC-1, RF-26)."""

import hashlib
import math
from datetime import timedelta

from fastapi import APIRouter, Response
from sqlalchemy import func, select, update
from sqlalchemy.dialects.postgresql import insert as pg_insert

from app import esquemas as e
from app.comun import DB, ahora, registrar_bitacora
from app.errores import ErrorAPI
from app.modelos import EnlaceUnSoloUso, IntentoLogin, Sesion, Usuario
from app.seguridad import (
    INACTIVIDAD_MIN,
    SesionAutenticada,
    contrasena_excede_limite,
    duracion_token,
    emitir_token,
    hash_contrasena,
    verificar_configuracion,
    verificar_contrasena,
)
from app.servicios import usuario_a_esquema

router = APIRouter(prefix="/auth", tags=["Autenticación"])

MAX_INTENTOS = 5  # RF-26-AC-3
DURACION_BLOQUEO = timedelta(minutes=15)

_CREDENCIALES_INVALIDAS = ("credenciales_invalidas", "Correo o contraseña incorrectos")
_CUENTA_BLOQUEADA = ("cuenta_bloqueada", "Cuenta bloqueada temporalmente; intente de nuevo en 15 minutos")
_ENLACE_NO_VIGENTE = ("enlace_no_vigente", "El enlace de invitación ya se usó o venció")
_CONTRASENA_LARGA = ("contrasena_demasiado_larga", "La contraseña no puede exceder 72 bytes")


# ------------------------------------------------------------------ registro
@router.post("/register", response_model=e.Usuario, status_code=201)
def registrar_usuario(cuerpo: e.RegistroCreate, db: DB, response: Response):
    if contrasena_excede_limite(cuerpo.contrasena):
        raise ErrorAPI(422, *_CONTRASENA_LARGA)

    token_hash = hashlib.sha256(cuerpo.token_invitacion.encode("utf-8")).hexdigest()
    # FOR UPDATE: dos registros simultáneos con el mismo token se serializan y el segundo ve el enlace usado.
    enlace = db.scalar(
        select(EnlaceUnSoloUso)
        .where(EnlaceUnSoloUso.token_hash == token_hash, EnlaceUnSoloUso.tipo == "invitacion")
        .with_for_update()
    )
    momento = ahora()
    # Token inexistente, usado o vencido responden igual, para no revelar cuáles existen.
    if enlace is None or enlace.usado_en is not None or enlace.expira_en <= momento:
        raise ErrorAPI(410, *_ENLACE_NO_VIGENTE)
    u = db.get(Usuario, enlace.usuario_id, with_for_update=True)
    if u is None or u.estado != "pendiente_activacion":
        raise ErrorAPI(410, *_ENLACE_NO_VIGENTE)

    u.contrasena_hash = hash_contrasena(cuerpo.contrasena)
    u.estado = "activo"
    # Se consumen todas las invitaciones abiertas del usuario, no solo la usada.
    db.execute(
        update(EnlaceUnSoloUso)
        .where(
            EnlaceUnSoloUso.usuario_id == u.id,
            EnlaceUnSoloUso.tipo == "invitacion",
            EnlaceUnSoloUso.usado_en.is_(None),
        )
        .values(usado_en=momento)
    )
    registrar_bitacora(db, u, "activar_cuenta", recurso_tipo="usuario", recurso_id=u.id, parque_id=u.parque_id)
    db.commit()
    response.headers["Location"] = f"/api/usuarios/{u.id}"
    return usuario_a_esquema(db, u)


# ------------------------------------------------------------------ inicio de sesión
def _contador(db, correo: str) -> IntentoLogin:
    """Renglón de intentos del correo, bloqueado para esta transacción (los intentos paralelos se serializan)."""
    db.execute(
        pg_insert(IntentoLogin)
        .values(correo=correo, intentos_fallidos=0)
        .on_conflict_do_nothing(index_elements=[IntentoLogin.correo])
    )
    return db.scalars(select(IntentoLogin).where(IntentoLogin.correo == correo).with_for_update()).one()


@router.post("/login", response_model=e.SesionCreada)
def iniciar_sesion(cuerpo: e.SesionCreate, db: DB, response: Response):
    verificar_configuracion()
    correo = cuerpo.correo.strip().lower()
    momento = ahora()
    intento = _contador(db, correo)

    if intento.bloqueado_hasta is not None and intento.bloqueado_hasta > momento:
        restante = max(1, math.ceil((intento.bloqueado_hasta - momento).total_seconds()))
        db.commit()
        raise ErrorAPI(429, *_CUENTA_BLOQUEADA, headers={"Retry-After": str(restante)})
    if intento.bloqueado_hasta is not None:  # el bloqueo ya venció: el contador empieza de nuevo
        intento.intentos_fallidos = 0
        intento.bloqueado_hasta = None

    u = db.scalar(select(Usuario).where(func.lower(Usuario.correo) == correo))
    valida = verificar_contrasena(cuerpo.contrasena, u.contrasena_hash if u is not None else None)

    if not valida or u is None or u.estado != "activo":
        intento.intentos_fallidos += 1
        bloqueada = intento.intentos_fallidos >= MAX_INTENTOS
        if bloqueada:
            intento.bloqueado_hasta = momento + DURACION_BLOQUEO
        if u is not None:
            registrar_bitacora(
                db, u, "iniciar_sesion", recurso_tipo="usuario", recurso_id=u.id, parque_id=u.parque_id,
                resultado="fallido", detalle="cuenta bloqueada 15 minutos" if bloqueada else None,
            )
        db.commit()
        raise ErrorAPI(401, *_CREDENCIALES_INVALIDAS)

    db.delete(intento)
    emitido = momento.replace(microsecond=0)
    expira = emitido + duracion_token()
    sesion = Sesion(usuario_id=u.id, creada=emitido, ultima_actividad=emitido, expira_en=expira)
    db.add(sesion)
    db.flush()
    token = emitir_token(u.id, sesion.sid, emitido, expira)
    registrar_bitacora(
        db, u, "iniciar_sesion", recurso_tipo="sesion", recurso_id=sesion.sid, parque_id=u.parque_id
    )
    db.commit()
    response.headers["Cache-Control"] = "no-store"
    return e.SesionCreada(
        token=token,
        tipo_token="Bearer",
        expira_en=expira,
        expira_por_inactividad_min=INACTIVIDAD_MIN,
        usuario=usuario_a_esquema(db, u),
    )


# ------------------------------------------------------------------ sesión actual y cierre
@router.get("/me", response_model=e.SesionActual)
def obtener_usuario_actual(auth: SesionAutenticada, db: DB):
    return e.SesionActual(
        sesion_id=auth.sesion.sid,
        inicio=auth.sesion.creada,
        ultima_actividad=auth.sesion.ultima_actividad,
        expira_por_inactividad_min=INACTIVIDAD_MIN,
        usuario=usuario_a_esquema(db, auth.usuario),
    )


@router.post("/logout", status_code=204, response_class=Response)
def cerrar_sesion(auth: SesionAutenticada, db: DB):
    db.execute(
        update(Sesion)
        .where(Sesion.sid == auth.sesion.sid, Sesion.revocada_en.is_(None))
        .values(revocada_en=ahora())
        .execution_options(synchronize_session=False)
    )
    registrar_bitacora(
        db, auth.usuario, "cerrar_sesion", recurso_tipo="sesion", recurso_id=auth.sesion.sid,
        parque_id=auth.usuario.parque_id,
    )
    db.commit()
    return Response(status_code=204)
