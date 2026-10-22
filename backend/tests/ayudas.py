"""Datos de prueba sintéticos (no se usa información real de AMPIP)."""

from pathlib import Path

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


def escenario(c):
    """Catálogo, generación 2027 y Parque X (construcción cerrado) con una APPI y un consultor."""
    v = cargar_catalogo(c)
    g = crear_generacion(c, v["id"])
    p = crear_parque(c, g["id"])
    appi = crear_usuario(c, "gerente@parquex.mx", "appi", parqueId=p["id"])
    consultor = crear_usuario(c, "juan.perez@consultores.mx", "consultor")
    return {"version": v, "generacion": g, "parque": p, "appi": appi, "consultor": consultor}


def criterio_por_texto(c, parque_id, fragmento):
    r = c.get(f"/api/parques/{parque_id}/criterios", params={"tamanoPagina": 100})
    assert r.status_code == 200, r.text
    for item in r.json()["items"]:
        if fragmento in item["texto"]:
            return item
    return None
