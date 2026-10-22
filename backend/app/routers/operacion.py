"""Operación: estado del servicio para el monitoreo externo (RNF-08)."""

from datetime import timedelta

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy import func, select, text

from app import esquemas as e
from app.comun import ahora
from app.db import SessionLocal
from app.modelos import RegistroBitacora

router = APIRouter(tags=["Operación"])

# Acción con la que el worker (pendiente) registrará cada corrida de la revisión diaria de plazos.
ACCION_WORKER = "revision_diaria_plazos"


@router.get("/salud", response_model=e.Salud, responses={503: {"model": e.Salud}})
def obtener_salud():
    base, ultima = "ok", None
    try:
        with SessionLocal() as db:
            db.execute(text("SELECT 1"))
            ultima = db.scalar(
                select(func.max(RegistroBitacora.fecha_hora)).where(RegistroBitacora.accion == ACCION_WORKER)
            )
    except Exception:
        base = "sin_respuesta"

    worker_detenido = ultima is not None and ahora() - ultima > timedelta(hours=24)
    salud = e.Salud(
        estado="ok" if base == "ok" and not worker_detenido else "degradado",
        base_datos=base,
        ultima_corrida_worker=ultima,
    )
    codigo = 200 if salud.estado == "ok" else 503
    return JSONResponse(status_code=codigo, content=salud.model_dump(mode="json", by_alias=True))
