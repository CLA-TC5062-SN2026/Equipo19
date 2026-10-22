"""Cumplimiento de obligatorios y avance general del parque (RF-08)."""

import uuid

from fastapi import APIRouter

from app import esquemas as e
from app.comun import DB, ahora
from app.errores import ErrorAPI
from app.servicios import calcular_cumplimiento, exigir_expediente, obtener_parque, tipo_vigente

router = APIRouter(tags=["Cumplimiento"])


@router.get("/parques/{parqueId}/cumplimiento", response_model=e.Cumplimiento)
def obtener_cumplimiento_parque(parqueId: uuid.UUID, db: DB):
    parque = obtener_parque(db, parqueId)
    exp = exigir_expediente(db, parque)
    tipo = tipo_vigente(db, parque.id)
    if tipo is None:
        raise ErrorAPI(404, "sin_tipo_pi", "El parque no tiene tipo de PI vigente")
    total, por_estandar = calcular_cumplimiento(db, exp, tipo)
    return e.Cumplimiento(
        parque_id=parque.id,
        tipo_pi=tipo,
        fecha_calculo=ahora(),
        total=e.CifrasCumplimiento(**total),
        por_estandar=[e.CumplimientoEstandar(**x) for x in por_estandar],
    )
