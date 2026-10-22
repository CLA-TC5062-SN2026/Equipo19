"""Datos de arranque para desarrollo y para las demostraciones en Postman. Solo para entornos locales.

Uso:
    uv run python -m app.semilla          # catálogo sintético y generación 2027 (S05-S06-A1)
    uv run python -m app.semilla --demo   # además, cuentas de demostración para el flujo de autenticación (A2)

Lee del entorno SEMILLA_CORREO y SEMILLA_CONTRASENA (cuenta de Coordinación AMPIP con la que trabaja la semilla;
si no existe, la crea activa) y, con --demo, SEMILLA_APPI_CONTRASENA. Es idempotente. El catálogo es sintético,
no el de AMPIP.
"""

import argparse
import logging
import os
from pathlib import Path

import bcrypt
from fastapi.testclient import TestClient
from sqlalchemy import func, select, update

from app.alta_inicial import crear_invitacion
from app.db import SessionLocal
from app.main import app
from app.modelos import Generacion, Parque, Sesion, Usuario, VersionCatalogo

CSV = Path(__file__).resolve().parents[1] / "datos" / "catalogo_sintetico.csv"
APPI_DEMO = "appi.demo@parquedemo.mx"
COORDINACION_DEMO = "coordinacion.demo@ampip.mx"


def _usuario(db, correo):
    return db.scalars(select(Usuario).where(func.lower(Usuario.correo) == correo.lower())).first()


def _asegurar_coordinacion(correo: str, contrasena: str) -> None:
    with SessionLocal() as db:
        if _usuario(db, correo) is None:
            db.add(Usuario(nombre="Coordinación AMPIP (semilla)", correo=correo.lower(), rol="coordinacion_ampip",
                           estado="activo",
                           contrasena_hash=bcrypt.hashpw(contrasena.encode(), bcrypt.gensalt()).decode()))
            db.commit()


def _ok(r):
    if r.status_code >= 400:
        raise SystemExit(f"{r.request.method} {r.request.url.path} -> {r.status_code}: {r.text}")
    return r.json()


def main(argv: list[str] | None = None) -> None:
    logging.getLogger("httpx").setLevel(logging.WARNING)
    p = argparse.ArgumentParser(description="Datos de arranque locales")
    p.add_argument("--demo", action="store_true")
    args = p.parse_args(argv)

    correo, contrasena = os.environ["SEMILLA_CORREO"], os.environ["SEMILLA_CONTRASENA"]
    _asegurar_coordinacion(correo, contrasena)
    c = TestClient(app)
    c.headers["Authorization"] = "Bearer " + _ok(c.post("/api/auth/login", json={"correo": correo, "contrasena": contrasena}))["token"]

    with SessionLocal() as db:
        version = db.scalars(select(VersionCatalogo).where(VersionCatalogo.nombre == "catalogo-sintetico-v1")).first()
        generacion = db.scalars(select(Generacion).where(Generacion.nombre == "2027")).first()
    version_id = str(version.id) if version else _ok(c.post(
        "/api/versiones-catalogo", data={"nombreVersion": "catalogo-sintetico-v1"},
        files={"archivo": (CSV.name, CSV.read_bytes(), "text/csv")}))["id"]
    generacion_id = str(generacion.id) if generacion else _ok(c.post(
        "/api/generaciones", json={"nombre": "2027", "fechaInicio": "2027-02-01", "versionCatalogoId": version_id}))["id"]
    print(f"generacionId = {generacion_id}")
    if not args.demo:
        return

    with SessionLocal() as db:
        parque = db.scalars(select(Parque).where(Parque.nombre == "Parque Demo")).first()
    parque_id = str(parque.id) if parque else _ok(c.post("/api/parques", json={
        "tipoRegistro": "activo", "nombre": "Parque Demo", "desarrollador": "Desarrolladora Demo",
        "tipoPI": "operacion_cerrado", "region": "MX-NLE", "generacionId": generacion_id}))["id"]

    with SessionLocal() as db:
        appi = _usuario(db, APPI_DEMO)
    if appi is None:
        appi_id = _ok(c.post("/api/usuarios", json={"correo": APPI_DEMO, "nombre": "APPI demo", "rol": "appi",
                                                     "parqueId": parque_id}))["id"]
        with SessionLocal() as db:
            token = crear_invitacion(db, db.get(Usuario, appi_id))
            db.commit()
        _ok(c.post("/api/auth/register", headers={"Authorization": ""},
                   json={"tokenInvitacion": token, "contrasena": os.environ["SEMILLA_APPI_CONTRASENA"]}))
    print(f"APPI activa para la prueba de 403: {APPI_DEMO}")

    with SessionLocal() as db:
        coord_demo = _usuario(db, COORDINACION_DEMO)
        if coord_demo is not None and coord_demo.estado != "pendiente_activacion":
            # Otra toma del video: la cuenta demo vuelve a "pendiente de activación", sin contraseña y sin sesiones,
            # y se emite una invitación nueva. Solo desarrollo.
            coord_demo.estado, coord_demo.contrasena_hash = "pendiente_activacion", None
            db.execute(update(Sesion).where(Sesion.usuario_id == coord_demo.id, Sesion.revocada_en.is_(None))
                       .values(revocada_en=func.now()))
            db.commit()
            print(f"{COORDINACION_DEMO} regresó a pendiente de activación para repetir el registro.")
    if coord_demo is None:
        coord_demo_id = _ok(c.post("/api/usuarios", json={"correo": COORDINACION_DEMO, "nombre": "Coordinación demo",
                                                          "rol": "coordinacion_ampip"}))["id"]
    else:
        coord_demo_id = coord_demo.id
    with SessionLocal() as db:
        token = crear_invitacion(db, db.get(Usuario, coord_demo_id))
        db.commit()
    print(f"Invitación para {COORDINACION_DEMO}; pega este token en la variable tokenInvitacion de Postman:")
    print(token)


if __name__ == "__main__":
    main()
