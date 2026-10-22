"""Consulta de la bitácora de solo append (RF-35, RNF-03). No hay operaciones de escritura."""

import uuid
from datetime import date, datetime, time, timedelta
from typing import Annotated

from fastapi import APIRouter, Query
from sqlalchemy import func, select

from app import esquemas as e
from app.comun import DB, ZONA, PaginacionSinOrden
from app.modelos import RegistroBitacora

router = APIRouter(tags=["Bitácora"])


@router.get("/bitacora", response_model=e.Pagina[e.RegistroBitacora])
def listar_bitacora(
    db: DB,
    p: PaginacionSinOrden,
    parque_id: Annotated[uuid.UUID | None, Query(alias="parqueId")] = None,
    usuario_id: Annotated[uuid.UUID | None, Query(alias="usuarioId")] = None,
    accion: Annotated[str | None, Query(max_length=100)] = None,
    desde: Annotated[date | None, Query()] = None,
    hasta: Annotated[date | None, Query()] = None,
):
    q = select(RegistroBitacora)
    if parque_id:
        q = q.where(RegistroBitacora.parque_id == parque_id)
    if usuario_id:
        q = q.where(RegistroBitacora.usuario_id == usuario_id)
    if accion:
        q = q.where(RegistroBitacora.accion == accion)
    # Los días se cortan en hora de Ciudad de México (RNF-11).
    if desde:
        q = q.where(RegistroBitacora.fecha_hora >= datetime.combine(desde, time.min, tzinfo=ZONA))
    if hasta:
        q = q.where(RegistroBitacora.fecha_hora < datetime.combine(hasta + timedelta(days=1), time.min, tzinfo=ZONA))
    total = db.scalar(select(func.count()).select_from(q.subquery()))
    registros = db.scalars(
        q.order_by(RegistroBitacora.fecha_hora.desc(), RegistroBitacora.id.desc()).offset(p.offset).limit(p.tamano_pagina)
    ).all()
    return {
        "pagina": p.pagina,
        "tamanoPagina": p.tamano_pagina,
        "total": total,
        "items": [e.RegistroBitacora.model_validate(r) for r in registros],
    }
