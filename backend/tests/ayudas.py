"""Datos de prueba sintéticos (no se usa información real de AMPIP)."""

import hashlib
import secrets
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

import bcrypt
import psycopg

CONTRASENA = "contrasena-de-prueba-123"

CSV = (Path(__file__).resolve().parents[1] / "datos" / "catalogo_sintetico.csv").read_bytes()


def cargar_catalogo(c, nombre="catalogo-prueba-v1", contenido=CSV):
    r = c.post("/api/versiones-catalogo", data={"nombreVersion": nombre},
               files={"archivo": ("catalogo.csv", contenido, "text/csv")})
    assert r.status_code == 201, r.text
    return r.json()


def crear_generacion(c, version_id, nombre="2027", inicio="2027-02-01"):
    r = c.post("/api/generaciones", json={"nombre": nombre, "fechaInicio": inicio, "versionCatalogoId": version_id})
    assert r.status_code == 201, r.text
    return r.json()


def crear_parque(c, generacion_id, nombre="Parque X", tipo="construccion_cerrado", region="MX-NLE"):
    r = c.post("/api/parques", json={"tipoRegistro": "activo", "nombre": nombre, "desarrollador": "Desarrolladora Uno",
                                     "tipoPI": tipo, "region": region, "generacionId": generacion_id})
    assert r.status_code == 201, r.text
    return r.json()


def crear_usuario(c, correo, rol, **extra):
    r = c.post("/api/usuarios", json={"correo": correo, "nombre": correo.split("@")[0], "rol": rol, **extra})
    assert r.status_code == 201, r.text
    return r.json()


def escenario(c, asignar=True):
    """Catálogo, generación 2027 y Parque X (construcción cerrado) con una APPI y un consultor, ambos invitados y
    activados, el consultor asignado al parque, y el token de cada uno."""
    v = cargar_catalogo(c)
    g = crear_generacion(c, v["id"])
    p = crear_parque(c, g["id"])
    appi = crear_usuario(c, "gerente@parquex.mx", "appi", parqueId=p["id"])
    consultor = crear_usuario(c, "juan.perez@consultores.mx", "consultor")
    activar(appi["id"])
    activar(consultor["id"])
    if asignar:
        r = c.post(f"/api/parques/{p['id']}/asignaciones-consultor", json={"consultorId": consultor["id"]})
        assert r.status_code == 201, r.text
    return {"version": v, "generacion": g, "parque": p, "appi": appi, "consultor": consultor,
            "h_appi": bearer(iniciar_sesion(c, appi["correo"])),
            "h_consultor": bearer(iniciar_sesion(c, consultor["correo"]))}


def criterio_por_texto(c, parque_id, fragmento):
    r = c.get(f"/api/parques/{parque_id}/criterios", params={"tamanoPagina": 100})
    assert r.status_code == 200, r.text
    for item in r.json()["items"]:
        if fragmento in item["texto"]:
            return item
    return None


# ------------------------------------------------------------------ autenticación
def _bd():
    from tests.conftest import ADMIN_URL, PRUEBA

    return psycopg.connect(ADMIN_URL.rsplit("/", 1)[0] + "/" + PRUEBA, autocommit=True)


def sql(q, *args):
    with _bd() as c:
        cur = c.execute(q, args)
        return cur.fetchall() if cur.description else None


def crear_activo(correo, rol, parque_id=None, contrasena=CONTRASENA, desarrollador_id=None):
    """Inserta un usuario activo con contraseña directo en la base (arranque de las pruebas)."""
    h = bcrypt.hashpw(contrasena.encode(), bcrypt.gensalt(rounds=4)).decode()
    uid = uuid.uuid4()
    sql("INSERT INTO usuario (id, nombre, correo, contrasena_hash, rol, estado, parque_id, desarrollador_id) "
        "VALUES (%s, %s, %s, %s, %s, 'activo', %s, %s)", uid, correo.split("@")[0], correo, h, rol, parque_id,
        desarrollador_id)
    return str(uid)


def invitacion(usuario_id, vence_en=timedelta(hours=72)):
    """Crea un enlace de invitación con token conocido (el real solo viaja por correo)."""
    token = secrets.token_urlsafe(32)
    sql("INSERT INTO enlace_un_solo_uso (usuario_id, token_hash, tipo, creado, expira_en) "
        "VALUES (%s, %s, 'invitacion', %s, %s)", usuario_id, hashlib.sha256(token.encode()).hexdigest(),
        datetime.now(timezone.utc) + min(vence_en, timedelta(0)) - timedelta(hours=1), datetime.now(timezone.utc) + vence_en)
    return token


def iniciar_sesion(c, correo, contrasena=CONTRASENA):
    r = c.post("/api/auth/login", json={"correo": correo, "contrasena": contrasena}, headers={"Authorization": ""})
    assert r.status_code == 200, r.text
    return r.json()["token"]


def bearer(token):
    return {"Authorization": f"Bearer {token}"}


SIN_TOKEN = {"Authorization": ""}


def activar(usuario_id, contrasena=CONTRASENA):
    """Equivale a que el usuario acepte su invitación con POST /auth/register."""
    h = bcrypt.hashpw(contrasena.encode(), bcrypt.gensalt(rounds=4)).decode()
    sql("UPDATE usuario SET estado='activo', contrasena_hash=%s WHERE id=%s", h, usuario_id)
