"""Punto de entrada de la API de SGPIS: `uvicorn app.main:app`."""

import logging

from fastapi import Depends, FastAPI
from fastapi.openapi.utils import get_openapi
from fastapi.routing import APIRoute

from app.errores import registrar_handlers
from app.permisos import autorizar, verificar_mapa
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
        "Implementación de openapi_equipo.yaml. Todas las rutas salvo /salud, /auth/login y /auth/register exigen "
        "token (401) y validan el rol y la relación con el parque contra app/permisos.py (403)."
    ),
    docs_url=f"{PREFIJO}/docs",
    openapi_url=f"{PREFIJO}/openapi.json",
    redoc_url=None,
)
registrar_handlers(app)

# Públicas o con su propia dependencia de sesión: /salud, /auth/login, /auth/register (security: [] en el
# contrato) y /auth/me, /auth/logout (SesionAutenticada).
for modulo in (autenticacion, operacion):
    app.include_router(modulo.router, prefix=PREFIJO)

# Protegidas: token válido (401) y permiso por rol y parque según app/permisos.PERMISOS (403 + bitácora).
PROTEGIDOS = (
    catalogo, generaciones, parques, historial, usuarios, asignaciones, criterios_parque,
    autoevaluacion, cumplimiento, plan_trabajo, analisis_riesgos, fases, configuracion, bitacora,
)
for modulo in PROTEGIDOS:
    app.include_router(modulo.router, prefix=PREFIJO, dependencies=[Depends(autorizar)])

verificar_mapa(r for modulo in PROTEGIDOS for r in modulo.router.routes if isinstance(r, APIRoute))


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
