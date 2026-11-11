"""Piezas transversales: usuario que registra (autenticado), fechas en CDMX, paginación, orden y bitácora."""

import uuid
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from datetime import date, datetime, timezone
from typing import Annotated, Any
from zoneinfo import ZoneInfo

from fastapi import Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.config import get_settings
from app.db import get_db
from app.errores import ErrorAPI
from app.modelos import RegistroBitacora, Usuario
from app.seguridad import UsuarioAutenticado

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
# Usuario al que se atribuyen las escrituras (registradoPor, cargadoPor, cerradaPor, bitácora...): siempre el
# usuario autenticado. Sin token válido la solicitud ya respondió 401 en `permisos.autorizar`.
Actor = UsuarioAutenticado
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


# ------------------------------------------------------------------ cuerpo de los PATCH
def exigir_campos(cuerpo: BaseModel, no_nulos: Sequence[str], mensajes: Mapping[str, str] | None = None) -> set[str]:
    """Reglas comunes de los PATCH (422 datos_invalidos): el cuerpo trae al menos un campo y ninguno de `no_nulos`
    viene en null. Revisa `no_nulos` en el orden dado; `mensajes` cambia el texto de un campo. Devuelve los campos
    que el cliente envió, aunque sea con null.

    [R3, S09_A1] Antes este bloque estaba copiado en parques.actualizar_parque y usuarios.actualizar_usuario."""
    campos = set(cuerpo.model_fields_set)
    if not campos:
        raise ErrorAPI(422, "datos_invalidos", "Indique al menos un campo a actualizar")
    for campo in no_nulos:
        if campo in campos and getattr(cuerpo, campo) is None:
            mensaje = (mensajes or {}).get(campo, f"El campo {campo} no admite nulo")
            raise ErrorAPI(422, "datos_invalidos", mensaje)
    return campos


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
