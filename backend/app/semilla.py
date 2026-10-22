"""Datos de arranque para desarrollo y para la demostración en Postman.

Uso: SEMILLA_CORREO=... SEMILLA_CONTRASENA=... uv run python -m app.semilla
Carga el catálogo sintético de datos/catalogo_sintetico.csv (no es el catálogo real de AMPIP) y crea la
generación "2027" si todavía no existen. Es idempotente: correrlo dos veces no duplica nada.
Las rutas exigen token y rol de Coordinación AMPIP: el script inicia sesión con una cuenta activa de ese rol.
"""

import os
from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy import select

from app.db import SessionLocal
from app.main import app
from app.modelos import Generacion, VersionCatalogo

CSV = Path(__file__).resolve().parents[1] / "datos" / "catalogo_sintetico.csv"


def main() -> None:
    with SessionLocal() as db:
        version = db.scalars(select(VersionCatalogo).where(VersionCatalogo.nombre == "catalogo-sintetico-v1")).first()
        generacion = db.scalars(select(Generacion).where(Generacion.nombre == "2027")).first()
    cliente = TestClient(app)
    login = cliente.post(
        "/api/auth/login",
        json={"correo": os.environ["SEMILLA_CORREO"], "contrasena": os.environ["SEMILLA_CONTRASENA"]},
    )
    login.raise_for_status()
    cliente.headers["Authorization"] = f"Bearer {login.json()['token']}"
    if version is None:
        r = cliente.post("/api/versiones-catalogo", data={"nombreVersion": "catalogo-sintetico-v1"},
                         files={"archivo": (CSV.name, CSV.read_bytes(), "text/csv")})
        r.raise_for_status()
        version_id = r.json()["id"]
        print(f"Catálogo cargado: {r.json()['totalCriterios']} criterios")
    else:
        version_id = str(version.id)
    if generacion is None:
        r = cliente.post("/api/generaciones", json={"nombre": "2027", "fechaInicio": "2027-02-01",
                                                    "versionCatalogoId": version_id})
        r.raise_for_status()
        generacion_id = r.json()["id"]
    else:
        generacion_id = str(generacion.id)
    print(f"generacionId = {generacion_id}")


if __name__ == "__main__":
    main()
