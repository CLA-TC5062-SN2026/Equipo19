"""CORS para el frontend en otro origen (S11). Cliente sin validación de contrato: OPTIONS no está en el OpenAPI."""

from fastapi.testclient import TestClient

from app.config import get_settings
from app.main import app

SPA = get_settings().url_spa


def test_preflight_del_frontend_permitido(bd):
    c = TestClient(app)
    r = c.options("/api/auth/login", headers={
        "Origin": SPA, "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "content-type"})
    assert r.status_code == 200
    assert r.headers["access-control-allow-origin"] == SPA


def test_error_401_tambien_lleva_encabezado_cors(bd):
    # Si el 401 no trae el encabezado, el navegador oculta la respuesta y el frontend no puede mostrar el mensaje.
    c = TestClient(app)
    r = c.get("/api/parques", headers={"Origin": SPA})
    assert r.status_code == 401
    assert r.headers["access-control-allow-origin"] == SPA


def test_origen_desconocido_sin_encabezado(bd):
    c = TestClient(app)
    r = c.get("/api/salud", headers={"Origin": "https://otro-sitio.example"})
    assert "access-control-allow-origin" not in r.headers
