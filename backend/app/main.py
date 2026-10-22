"""Punto de entrada de la API de SGPIS: `uvicorn app.main:app`."""

import logging

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from app.errores import registrar_handlers
from app.routers import (
    analisis_riesgos,
    asignaciones,
    autenticacion,
    autoevaluacion,
    bitacora,
    catalogo,
    configuracion,
    criterios_parque,
    cumplimiento,
    fases,
    generaciones,
    historial,
    operacion,
    parques,
    plan_trabajo,
    usuarios,
)

logging.basicConfig(level=logging.INFO)

PREFIJO = "/api"

app = FastAPI(
    title="SGPIS API (contrato de equipo)",
    version="2.0.0",
    description=(
        "Implementación de openapi_equipo.yaml. S05-S06-A2: autenticación JWT en /auth; las rutas CRUD todavía "
        "no exigen token ni validan rol."
    ),
    docs_url=f"{PREFIJO}/docs",
    openapi_url=f"{PREFIJO}/openapi.json",
    redoc_url=None,
)
registrar_handlers(app)

for modulo in (
    autenticacion, operacion, catalogo, generaciones, parques, historial, usuarios, asignaciones, criterios_parque,
    autoevaluacion, cumplimiento, plan_trabajo, analisis_riesgos, fases, configuracion, bitacora,
):
    app.include_router(modulo.router, prefix=PREFIJO)


def _openapi() -> dict:
    """El esquema generado declara los 422 con el schema Error del contrato, no con HTTPValidationError."""
    if app.openapi_schema:
        return app.openapi_schema
    esquema = get_openapi(title=app.title, version=app.version, description=app.description, routes=app.routes)
    componentes = esquema.setdefault("components", {}).setdefault("schemas", {})
    componentes["DetalleError"] = {
        "type": "object",
        "required": ["campo", "problema"],
        "properties": {"campo": {"type": "string"}, "problema": {"type": "string"}},
    }
    componentes["Error"] = {
        "type": "object",
        "required": ["codigo", "mensaje"],
        "properties": {
            "codigo": {"type": "string", "pattern": "^[a-z][a-z0-9_]*$"},
            "mensaje": {"type": "string"},
            "detalles": {"type": "array", "items": {"$ref": "#/components/schemas/DetalleError"}},
        },
    }
    componentes.pop("ValidationError", None)
    componentes["HTTPValidationError"] = {"$ref": "#/components/schemas/Error"}
    app.openapi_schema = esquema
    return esquema


app.openapi = _openapi  # type: ignore[method-assign]
