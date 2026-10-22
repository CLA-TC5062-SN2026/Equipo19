"""Módulo de autenticación (RF-03-AC-1, RF-26) y la revisión de seguridad de S05-S06-A2, parte 1."""

import contextlib
from datetime import datetime, timedelta, timezone

import jwt

from tests.ayudas import CONTRASENA, bearer, crear_activo, iniciar_sesion, invitacion, sql


@contextlib.contextmanager
def sin_token(c):
    guardado = c.headers.pop("Authorization", None)
    try:
        yield c
    finally:
        if guardado:
            c.headers["Authorization"] = guardado


def _pendiente(c, correo="nuevo@parquex.mx"):
    r = c.post("/api/usuarios", json={"correo": correo, "nombre": "Nuevo", "rol": "coordinacion_ampip"})
    assert r.status_code == 201, r.text
    return r.json()["id"]


def test_RF_03_AC_1_register_activa_cuenta_y_no_devuelve_contrasena(cliente):
    uid = _pendiente(cliente)
    token = invitacion(uid)
    with sin_token(cliente):
        r = cliente.post("/api/auth/register", json={"tokenInvitacion": token, "contrasena": "una-contrasena-larga"})
    assert r.status_code == 201
    cuerpo = r.text.lower()
    assert r.json()["estado"] == "activo"
    assert "contrasena" not in cuerpo and "hash" not in cuerpo and "una-contrasena-larga" not in cuerpo
    guardado = sql("SELECT contrasena_hash FROM usuario WHERE id=%s", uid)[0][0]
    assert guardado.startswith("$2") and "una-contrasena-larga" not in guardado  # bcrypt


def test_register_token_reusado_o_vencido_410_y_contrasena_corta_422(cliente):
    uid = _pendiente(cliente)
    token = invitacion(uid)
    with sin_token(cliente):
        assert cliente.post("/api/auth/register", json={"tokenInvitacion": token, "contrasena": "corta"}).status_code == 422
        assert cliente.post("/api/auth/register", json={"tokenInvitacion": token, "contrasena": "una-contrasena-larga"}).status_code == 201
        assert cliente.post("/api/auth/register", json={"tokenInvitacion": token, "contrasena": "otra-contrasena-larga"}).status_code == 410
        vencido = invitacion(_pendiente(cliente, "otro@x.mx"), vence_en=timedelta(minutes=-5))
        assert cliente.post("/api/auth/register", json={"tokenInvitacion": vencido, "contrasena": "una-contrasena-larga"}).status_code == 410


def test_RF_26_AC_1_login_entrega_jwt_con_expiracion_explicita(cliente):
    crear_activo("ana@ampip.mx", "coordinacion_ampip")
    with sin_token(cliente):
        r = cliente.post("/api/auth/login", json={"correo": "ana@ampip.mx", "contrasena": CONTRASENA})
    assert r.status_code == 200
    claims = jwt.decode(r.json()["token"], options={"verify_signature": False})
    assert set(claims) >= {"sub", "sid", "iat", "exp"}
    assert claims["exp"] - claims["iat"] == 28800  # JWT_EXPIRATION de las pruebas
    assert "rol" not in claims and "contrasena" not in r.text.lower()


def test_RF_26_AC_2_credenciales_incorrectas_401(cliente):
    crear_activo("ana@ampip.mx", "coordinacion_ampip")
    with sin_token(cliente):
        r = cliente.post("/api/auth/login", json={"correo": "ana@ampip.mx", "contrasena": "equivocada-123"})
        assert r.status_code == 401 and r.json()["mensaje"] == "Correo o contraseña incorrectos"
        r = cliente.post("/api/auth/login", json={"correo": "nadie@ampip.mx", "contrasena": "equivocada-123"})
        assert r.status_code == 401 and r.json()["mensaje"] == "Correo o contraseña incorrectos"


def test_RF_26_AC_3_bloqueo_tras_5_intentos(cliente):
    crear_activo("ana@ampip.mx", "coordinacion_ampip")
    with sin_token(cliente):
        for _ in range(5):
            cliente.post("/api/auth/login", json={"correo": "ana@ampip.mx", "contrasena": "equivocada-123"})
        r = cliente.post("/api/auth/login", json={"correo": "ANA@ampip.mx", "contrasena": CONTRASENA})
    assert r.status_code == 429 and int(r.headers["retry-after"]) > 0
    assert r.json()["mensaje"] == "Cuenta bloqueada temporalmente; intente de nuevo en 15 minutos"


def test_me_con_token_valido_y_sin_token(cliente):
    r = cliente.get("/api/auth/me")
    assert r.status_code == 200 and r.json()["usuario"]["correo"] == "coordinacion@ampip.mx"
    with sin_token(cliente):
        r = cliente.get("/api/auth/me")
    assert r.status_code == 401 and r.headers["www-authenticate"] == "Bearer"


def test_token_con_firma_invalida_401(cliente):
    token = cliente.headers["Authorization"].split()[1]
    cabecera, carga, firma = token.split(".")
    alterado = f"{cabecera}.{carga}.{firma[:-2]}{'A' if firma[-2] != 'A' else 'B'}{firma[-1]}"
    assert cliente.get("/api/auth/me", headers=bearer(alterado)).status_code == 401
    otro_secreto = jwt.encode(jwt.decode(token, options={"verify_signature": False}), "otro-secreto-" + "y" * 40,
                              algorithm="HS256")
    assert cliente.get("/api/auth/me", headers=bearer(otro_secreto)).status_code == 401
    sin_firma = jwt.encode(jwt.decode(token, options={"verify_signature": False}), None, algorithm="none")
    assert cliente.get("/api/auth/me", headers=bearer(sin_firma)).status_code == 401


def test_token_expirado_401(cliente):
    import os

    token = cliente.headers["Authorization"].split()[1]
    claims = jwt.decode(token, options={"verify_signature": False})
    claims["exp"] = int((datetime.now(timezone.utc) - timedelta(seconds=5)).timestamp())
    vencido = jwt.encode(claims, os.environ["JWT_SECRET"], algorithm="HS256")
    assert cliente.get("/api/auth/me", headers=bearer(vencido)).status_code == 401


def test_RF_26_AC_5_logout_invalida_token(cliente):
    token = iniciar_sesion(cliente, "coordinacion@ampip.mx")
    assert cliente.post("/api/auth/logout", headers=bearer(token)).status_code == 204
    assert cliente.get("/api/auth/me", headers=bearer(token)).status_code == 401


def test_RF_26_AC_6_inactividad_de_60_minutos_401(cliente):
    token = iniciar_sesion(cliente, "coordinacion@ampip.mx")
    sid = jwt.decode(token, options={"verify_signature": False})["sid"]
    sql("UPDATE sesion SET ultima_actividad = now() - interval '61 minutes' WHERE sid=%s", sid)
    assert cliente.get("/api/auth/me", headers=bearer(token)).status_code == 401


def test_usuario_dado_de_baja_pierde_acceso_inmediato(cliente):
    uid = crear_activo("ana@ampip.mx", "coordinacion_ampip")
    token = iniciar_sesion(cliente, "ana@ampip.mx")
    cliente.patch(f"/api/usuarios/{uid}", json={"estado": "inactivo", "motivo": "Dejó AMPIP"})
    assert cliente.get("/api/auth/me", headers=bearer(token)).status_code == 401


def test_secreto_de_ejemplo_rechazado(monkeypatch):
    """[S-01] El secreto publicado en .env.example no sirve para firmar."""
    from pydantic import SecretStr

    from app import seguridad
    from app.config import get_settings

    monkeypatch.setattr(get_settings(), "jwt_secret", SecretStr("cambiar_por_un_secreto_aleatorio_de_al_menos_32_bytes"))
    try:
        seguridad._secreto()
        assert False, "aceptó el secreto de ejemplo"
    except seguridad.ErrorAPI as exc:
        assert exc.status == 500


def test_secreto_no_esta_en_el_codigo():
    """El secreto real solo vive en el entorno: ningún archivo de app/ lo contiene."""
    import os
    from pathlib import Path

    secreto = os.environ["JWT_SECRET"]
    for archivo in Path(__file__).resolve().parents[1].joinpath("app").rglob("*.py"):
        assert secreto not in archivo.read_text(encoding="utf-8"), archivo
