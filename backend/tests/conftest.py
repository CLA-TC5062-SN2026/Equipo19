"""Infraestructura de pruebas: base PostgreSQL real por prueba y validación de cada respuesta contra el contrato.

Cada prueba recibe una base recién clonada de una plantilla cargada con db/esquema_bd.sql, así que las pruebas no
dependen del orden. Cada respuesta del cliente se valida contra openapi_equipo.yaml (código declarado para la
operación y cuerpo conforme al schema); una respuesta fuera de contrato hace fallar la prueba.
"""

import os
import subprocess
from pathlib import Path
from urllib.parse import urlparse

import psycopg
import pytest
from werkzeug.datastructures import Headers, ImmutableMultiDict

RAIZ = Path(__file__).resolve().parents[1]
CONTRATO = Path(os.environ.get("SGPIS_CONTRATO", RAIZ.parent / "S05_S06_A1" / "openapi_equipo.yaml"))
ADMIN_URL = os.environ.get("SGPIS_TEST_ADMIN_URL", "postgresql://postgres@localhost:5432/postgres")
PLANTILLA, PRUEBA = "sgpis_plantilla", "sgpis_prueba"

_u = urlparse(ADMIN_URL)
os.environ.setdefault("JWT_SECRET", "secreto-solo-para-pruebas-" + "x" * 40)
os.environ.setdefault("JWT_EXPIRATION", "28800")
os.environ["DATABASE_URL"] = f"postgresql+psycopg://{_u.username}{':' + _u.password if _u.password else ''}@{_u.hostname}:{_u.port or 5432}/{PRUEBA}"


def _admin(sql: str) -> None:
    with psycopg.connect(ADMIN_URL, autocommit=True) as c:
        c.execute(sql)


@pytest.fixture(scope="session", autouse=True)
def _plantilla():
    _admin(f"DROP DATABASE IF EXISTS {PRUEBA}")
    _admin(f"DROP DATABASE IF EXISTS {PLANTILLA}")
    _admin(f"CREATE DATABASE {PLANTILLA}")
    url = ADMIN_URL.rsplit("/", 1)[0] + "/" + PLANTILLA
    subprocess.run(["psql", url, "-q", "-v", "ON_ERROR_STOP=1", "-f", str(RAIZ / "db" / "esquema_bd.sql")],
                   check=True, capture_output=True)
    yield


@pytest.fixture()
def bd():
    from app.db import engine

    engine.dispose()
    _admin(f"DROP DATABASE IF EXISTS {PRUEBA} WITH (FORCE)")
    _admin(f"CREATE DATABASE {PRUEBA} TEMPLATE {PLANTILLA}")
    yield
    engine.dispose()


# ------------------------------------------------------------------ validación contra el contrato
class _Peticion:
    def __init__(self, req):
        self._r = req
        self.host_url = f"{req.url.scheme}://{req.url.netloc.decode()}"
        self.path = req.url.path
        self.full_url_pattern = None
        self.method = req.method.lower()
        from openapi_core.datatypes import RequestParameters

        self.parameters = RequestParameters(
            query=ImmutableMultiDict(list(req.url.params.multi_items())),
            header=Headers(dict(req.headers)),
            cookie=ImmutableMultiDict(),
        )
        self.content_type = req.headers.get("content-type", "")
        self.body = req.content or None


class _Respuesta:
    def __init__(self, resp):
        self.status_code = resp.status_code
        self.content_type = resp.headers.get("content-type", "")
        self.headers = Headers(dict(resp.headers))
        self.data = resp.content or None


@pytest.fixture(scope="session")
def contrato():
    from openapi_core import OpenAPI

    return OpenAPI.from_file_path(str(CONTRATO))


@pytest.fixture()
def cliente(bd, contrato):
    from fastapi.testclient import TestClient

    from app.main import app

    errores: list[str] = []

    def validar(resp):
        try:
            contrato.validate_response(_Peticion(resp.request), _Respuesta(resp))
        except Exception as exc:  # noqa: BLE001 - se reporta tal cual
            causa = getattr(exc, "__cause__", None)
            errores.append(f"{resp.request.method} {resp.request.url.path} -> {resp.status_code}: {exc!r} {causa!r}"[:900])

    with TestClient(app, base_url="http://localhost:8000", raise_server_exceptions=False) as c:
        c.event_hooks = {"request": [], "response": [lambda r: (r.read(), validar(r))]}
        # Por defecto el cliente actúa como Coordinación AMPIP; las pruebas de seguridad cambian el encabezado.
        from tests.ayudas import crear_activo, iniciar_sesion

        crear_activo("coordinacion@ampip.mx", "coordinacion_ampip")
        c.headers["Authorization"] = "Bearer " + iniciar_sesion(c, "coordinacion@ampip.mx")
        yield c
    assert not errores, "Respuestas fuera de contrato:\n" + "\n".join(errores)
