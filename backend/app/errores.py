"""Formato único de error ({codigo, mensaje, detalles}) y exception handlers globales.

Ninguna respuesta sale con {"detail": ...}: la validación de Pydantic, las HTTPException de
FastAPI/Starlette, las violaciones de integridad y los errores no controlados se traducen al
schema `Error` del contrato.
"""

import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
from starlette.exceptions import HTTPException as StarletteHTTPException

log = logging.getLogger("sgpis.errores")


class ErrorAPI(Exception):
    """Error de negocio con código de estado, código estable y mensaje para el usuario."""

    def __init__(self, status: int, codigo: str, mensaje: str, detalles: list[dict] | None = None):
        super().__init__(mensaje)
        self.status = status
        self.codigo = codigo
        self.mensaje = mensaje
        self.detalles = detalles


def no_encontrado(recurso: str = "recurso") -> ErrorAPI:
    return ErrorAPI(404, "no_encontrado", f"No existe el {recurso} solicitado")


def cuerpo_error(codigo: str, mensaje: str, detalles: list[dict] | None = None) -> dict:
    cuerpo: dict = {"codigo": codigo, "mensaje": mensaje}
    if detalles:
        cuerpo["detalles"] = detalles
    return cuerpo


# Traducción de errores de validación a código y texto literal del SRS, por operación.
# Llave: (método, ruta con prefijo). Valor: {campo camelCase: (codigo, mensaje) o
# {tipo_de_error_pydantic | "*": (codigo, mensaje)}}.
_TIPO_PI_ALTA = ("tipo_pi_invalido", "Debe seleccionar un tipo de PI válido")
_REGION = ("region_invalida", "Debe seleccionar una región válida")
TABLA_VALIDACION: dict[tuple[str, str], dict[str, object]] = {
    ("POST", "/api/parques"): {
        "tipoPI": _TIPO_PI_ALTA,
        "region": _REGION,
        "generacionId": {
            "missing": ("generacion_requerida", "Debe indicar la generación del parque"),
            "*": ("generacion_no_existe", "La generación indicada no existe"),
        },
    },
    ("PATCH", "/api/parques/{parqueId}"): {"region": _REGION},
    ("PUT", "/api/parques/{parqueId}/tipo-pi"): {
        "tipoPI": ("tipo_pi_invalido", "Tipo de PI inválido"),
        "motivo": ("motivo_requerido", "Indique el motivo del cambio de tipo de PI"),
    },
    ("POST", "/api/parques/{parqueId}/avances-fase"): {
        "motivo": (
            "motivo_requerido",
            "Para avanzar sin cerrar la fase actual registre el motivo de la excepción",
        ),
    },
}

_CODIGOS_HTTP = {
    400: ("cuerpo_malformado", "El cuerpo de la solicitud no se puede interpretar"),
    401: ("sesion_invalida", "La sesión no es válida o expiró; inicie sesión de nuevo"),
    403: ("sin_permiso", "No tiene permiso para realizar esta operación"),
    404: ("no_encontrado", "No existe el recurso solicitado"),
    405: ("metodo_no_permitido", "Método no permitido para este recurso"),
    409: ("conflicto", "La operación entra en conflicto con el estado actual del recurso"),
    413: ("archivo_demasiado_grande", "El archivo supera el límite configurado"),
    415: ("tipo_contenido_no_soportado", "Tipo de contenido no soportado"),
    422: ("datos_invalidos", "Los datos enviados no son válidos"),
    500: ("error_interno", "Error interno del servidor"),
}


def _campo(loc: tuple) -> str:
    partes = [str(p) for p in loc if p not in ("body", "query", "path", "header")]
    return ".".join(partes) or "cuerpo"


def _traducir(request: Request, errores: list[dict]) -> tuple[str, str] | None:
    ruta = request.scope.get("route")
    plantilla = getattr(ruta, "path_format", None)
    tabla = TABLA_VALIDACION.get((request.method, plantilla or ""))
    if not tabla:
        return None
    for err in errores:
        for parte in reversed(err.get("loc", ())):
            if isinstance(parte, str) and parte in tabla:
                regla = tabla[parte]
                if isinstance(regla, dict):
                    regla = regla.get(err.get("type"), regla.get("*"))
                if regla:
                    return regla  # type: ignore[return-value]
    return None


def registrar_handlers(app: FastAPI) -> None:
    @app.exception_handler(ErrorAPI)
    async def _error_api(_: Request, exc: ErrorAPI) -> JSONResponse:
        return JSONResponse(status_code=exc.status, content=cuerpo_error(exc.codigo, exc.mensaje, exc.detalles))

    @app.exception_handler(RequestValidationError)
    async def _validacion(request: Request, exc: RequestValidationError) -> JSONResponse:
        errores = list(exc.errors())
        detalles = [{"campo": _campo(tuple(e.get("loc", ()))), "problema": str(e.get("msg", ""))} for e in errores]

        if any(e.get("type") == "json_invalid" for e in errores):
            codigo, mensaje = _CODIGOS_HTTP[400]
            return JSONResponse(status_code=400, content=cuerpo_error(codigo, mensaje, detalles))

        # Un id de ruta mal formado (o una fase inexistente) no identifica ningún recurso: 404.
        if any(e.get("loc", ("",))[0] == "path" for e in errores):
            codigo, mensaje = _CODIGOS_HTTP[404]
            return JSONResponse(status_code=404, content=cuerpo_error(codigo, mensaje))

        traducido = _traducir(request, errores)
        if traducido:
            codigo, mensaje = traducido
        elif all(e.get("loc", ("",))[0] == "query" for e in errores):
            codigo, mensaje = "parametro_invalido", "Algún parámetro de la consulta no es válido"
        else:
            codigo, mensaje = _CODIGOS_HTTP[422]
        return JSONResponse(status_code=422, content=cuerpo_error(codigo, mensaje, detalles))

    @app.exception_handler(StarletteHTTPException)
    async def _http(_: Request, exc: StarletteHTTPException) -> JSONResponse:
        codigo, mensaje = _CODIGOS_HTTP.get(exc.status_code, ("error", str(exc.detail)))
        return JSONResponse(
            status_code=exc.status_code,
            content=cuerpo_error(codigo, mensaje),
            headers=getattr(exc, "headers", None),
        )

    @app.exception_handler(IntegrityError)
    async def _integridad(_: Request, exc: IntegrityError) -> JSONResponse:
        log.warning("Violación de integridad: %s", exc.orig)
        codigo, mensaje = _CODIGOS_HTTP[409]
        return JSONResponse(status_code=409, content=cuerpo_error(codigo, mensaje))

    @app.exception_handler(Exception)
    async def _no_controlado(_: Request, exc: Exception) -> JSONResponse:
        log.exception("Error no controlado", exc_info=exc)
        codigo, mensaje = _CODIGOS_HTTP[500]
        return JSONResponse(status_code=500, content=cuerpo_error(codigo, mensaje))
