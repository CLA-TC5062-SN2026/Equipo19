"""Piezas transversales: usuario que registra, fechas en CDMX, paginación, orden y bitácora."""

import uuid
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from datetime import date, datetime, timezone
from typing import Annotated, Any
from zoneinfo import ZoneInfo

from fastapi import Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.db import get_db
from app.errores import ErrorAPI
from app.modelos import RegistroBitacora, Usuario

ZONA = ZoneInfo(get_settings().zona_horaria)


def ahora() -> datetime:
    return datetime.now(timezone.utc)


def hoy() -> date:
    """Fecha de negocio en America/Mexico_City (RNF-11)."""
    return datetime.now(ZONA).date()


def mas_un_anio(d: date) -> date:
    try:
        return d.replace(year=d.year + 1)
    except ValueError:  # 29 de febrero
        return d.replace(year=d.year + 1, day=28)


# ------------------------------------------------------------------ usuario que registra
def usuario_actual(db: Annotated[Session, Depends(get_db)]) -> Usuario:
    """Usuario al que se atribuyen las escrituras (registradoPor, cargadoPor, cerradaPor...).

    Mientras no exista autenticación es un usuario técnico fijo, configurable con
    USUARIO_SISTEMA_CORREO, que se crea la primera vez que se necesita. En S05-S06-A2 esta
    dependencia se reemplaza por la que valida el JWT y la sesión, sin tocar los routers.
    """
    s = get_settings()
    usuario = db.scalar(select(Usuario).where(func.lower(Usuario.correo) == s.usuario_sistema_correo.lower()))
    if usuario is None:
        usuario = Usuario(
            nombre=s.usuario_sistema_nombre,
            correo=s.usuario_sistema_correo.lower(),
            rol="administrador_tecnico",
            estado="pendiente_activacion",
        )
        db.add(usuario)
        db.commit()
    return usuario


Actor = Annotated[Usuario, Depends(usuario_actual)]
DB = Annotated[Session, Depends(get_db)]


# ------------------------------------------------------------------ paginación y orden
@dataclass
class ParamsPagina:
    pagina: int
    tamano_pagina: int
    orden: str | None

    @property
    def offset(self) -> int:
        return (self.pagina - 1) * self.tamano_pagina


def params_pagina(
    pagina: Annotated[int, Query(ge=1)] = 1,
    tamano_pagina: Annotated[int, Query(alias="tamanoPagina", ge=1, le=100)] = 50,
    orden: Annotated[str | None, Query(pattern=r"^-?[A-Za-z]+(,-?[A-Za-z]+)*$")] = None,
) -> ParamsPagina:
    return ParamsPagina(pagina, tamano_pagina, orden)


def params_pagina_sin_orden(
    pagina: Annotated[int, Query(ge=1)] = 1,
    tamano_pagina: Annotated[int, Query(alias="tamanoPagina", ge=1, le=100)] = 50,
) -> ParamsPagina:
    return ParamsPagina(pagina, tamano_pagina, None)


Paginacion = Annotated[ParamsPagina, Depends(params_pagina)]
PaginacionSinOrden = Annotated[ParamsPagina, Depends(params_pagina_sin_orden)]


def campos_orden(orden: str | None, permitidos: Sequence[str], defecto: str) -> list[tuple[str, bool]]:
    """Devuelve [(campo, descendente)] o 422 si se pide un campo no admitido."""
    texto = orden or defecto
    resultado = []
    for parte in texto.split(","):
        desc = parte.startswith("-")
        campo = parte.lstrip("-")
        if campo not in permitidos:
            raise ErrorAPI(
                422,
                "orden_invalido",
                f"No se puede ordenar por '{campo}'; campos admitidos: {', '.join(permitidos)}",
            )
        resultado.append((campo, desc))
    return resultado


def orden_sql(orden: str | None, columnas: dict[str, Any], defecto: str, desempate: Any) -> list:
    clausulas = []
    for campo, desc in campos_orden(orden, list(columnas), defecto):
        col = columnas[campo]
        clausulas.append(col.desc() if desc else col.asc())
    clausulas.append(desempate)
    return clausulas


def ordenar_lista(items: list, orden: str | None, claves: dict[str, Callable[[Any], Any]], defecto: str,
                  desempate: Callable[[Any], Any]) -> list:
    """Orden en memoria, estable, con varios campos y nulos al final."""
    resultado = sorted(items, key=lambda x: str(desempate(x)))
    for campo, desc in reversed(campos_orden(orden, list(claves), defecto)):
        f = claves[campo]
        con_valor = [x for x in resultado if f(x) is not None]
        nulos = [x for x in resultado if f(x) is None]
        resultado = sorted(con_valor, key=f, reverse=desc) + nulos
    return resultado


def paginar(items: list, p: ParamsPagina) -> dict:
    return {
        "pagina": p.pagina,
        "tamanoPagina": p.tamano_pagina,
        "total": len(items),
        "items": items[p.offset: p.offset + p.tamano_pagina],
    }


def clave_natural(clave: str) -> tuple:
    """'2.10.1' después de '2.9.3'."""
    return tuple((0, int(p)) if p.isdigit() else (1, p) for p in clave.split("."))


# ------------------------------------------------------------------ bitácora
def registrar_bitacora(
    db: Session,
    actor: Usuario,
    accion: str,
    *,
    recurso_tipo: str | None = None,
    recurso_id: uuid.UUID | str | None = None,
    parque_id: uuid.UUID | None = None,
    detalle: str | None = None,
    resultado: str = "exitoso",
) -> None:
    """Agrega el registro en la misma transacción de la operación (RNF-03)."""
    db.add(
        RegistroBitacora(
            usuario_id=actor.id,
            rol=actor.rol,
            parque_id=parque_id,
            accion=accion,
            recurso_tipo=recurso_tipo,
            recurso_id=str(recurso_id) if recurso_id is not None else None,
            resultado=resultado,
            detalle=detalle,
        )
    )
