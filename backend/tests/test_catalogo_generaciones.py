"""Catálogo y generaciones (RF-01, RF-24, RF-28)."""

from tests.ayudas import CSV, cargar_catalogo, crear_generacion


def test_RF_01_AC_1_carga_csv_crea_version_activa(cliente):
    v = cargar_catalogo(cliente)
    assert v["nombre"] == "catalogo-prueba-v1"
    assert v["vigente"] is True and v["estado"] == "activa"
    assert v["totalCriterios"] == 24
    r = cliente.get(f"/api/versiones-catalogo/{v['id']}")
    assert r.status_code == 200 and r.json()["id"] == v["id"]
    assert any(x["id"] == v["id"] for x in cliente.get("/api/versiones-catalogo").json())


def test_RF_01_AC_4_marca_invalida_rechaza_archivo_completo(cliente):
    malo = CSV.replace(b",O,O,O,O\n", b",O,X,O,O\n", 1)
    r = cliente.post("/api/versiones-catalogo", data={"nombreVersion": "mala"},
                     files={"archivo": ("c.csv", malo, "text/csv")})
    assert r.status_code == 422
    assert r.json()["codigo"] == "catalogo_invalido"
    assert "fila" in r.json()["mensaje"].lower()
    assert cliente.get("/api/versiones-catalogo").json() == []


def test_RF_01_AC_4_columna_faltante(cliente):
    sin_columna = b"\n".join(l.rsplit(b",", 1)[0] for l in CSV.splitlines())
    r = cliente.post("/api/versiones-catalogo", data={"nombreVersion": "mala"},
                     files={"archivo": ("c.csv", sin_columna, "text/csv")})
    assert r.status_code == 422


def test_version_duplicada_409(cliente):
    cargar_catalogo(cliente)
    r = cliente.post("/api/versiones-catalogo", data={"nombreVersion": "catalogo-prueba-v1"},
                     files={"archivo": ("c.csv", CSV, "text/csv")})
    assert r.status_code == 409


def test_RF_01_AC_5_version_anterior_queda_en_solo_lectura(cliente):
    v1 = cargar_catalogo(cliente)
    crear_generacion(cliente, v1["id"])
    v2 = cargar_catalogo(cliente, "catalogo-prueba-v2")
    assert v2["estado"] == "activa"
    v1b = cliente.get(f"/api/versiones-catalogo/{v1['id']}").json()
    assert v1b["estado"] == "solo_lectura" and v1b["vigente"] is False


def test_RF_24_AC_1_evidencia_suficiente_y_solo_lectura(cliente):
    v1 = cargar_catalogo(cliente)
    g = crear_generacion(cliente, v1["id"])
    parque = cliente.post("/api/parques", json={"tipoRegistro": "activo", "nombre": "P", "desarrollador": "D",
                                                "tipoPI": "operacion_cerrado", "region": "MX-NLE",
                                                "generacionId": g["id"]}).json()
    crit = cliente.get(f"/api/parques/{parque['id']}/criterios").json()["items"][0]
    r = cliente.patch(f"/api/criterios/{crit['criterioId']}", json={"evidenciaSuficiente": "Plano firmado"})
    assert r.status_code == 200 and r.json()["evidenciaSuficiente"] == "Plano firmado"
    assert cliente.get(f"/api/criterios/{crit['criterioId']}").json()["evidenciaSuficiente"] == "Plano firmado"
    cargar_catalogo(cliente, "catalogo-prueba-v2")
    r = cliente.patch(f"/api/criterios/{crit['criterioId']}", json={"evidenciaSuficiente": "Otra"})
    assert r.status_code == 409


def test_RF_28_AC_1_crear_y_consultar_generacion(cliente):
    v = cargar_catalogo(cliente)
    g = crear_generacion(cliente, v["id"])
    assert g["versionCatalogoNombre"] == "catalogo-prueba-v1" and g["totalParques"] == 0
    assert cliente.get(f"/api/generaciones/{g['id']}").status_code == 200
    assert len(cliente.get("/api/generaciones").json()) == 1


def test_generacion_duplicada_y_version_inexistente(cliente):
    v = cargar_catalogo(cliente)
    crear_generacion(cliente, v["id"])
    r = cliente.post("/api/generaciones", json={"nombre": "2027", "fechaInicio": "2027-02-01",
                                                "versionCatalogoId": v["id"]})
    assert r.status_code == 409 and r.json()["codigo"] == "generacion_duplicada"
    r = cliente.post("/api/generaciones", json={"nombre": "2028", "fechaInicio": "2028-02-01",
                                                "versionCatalogoId": "00000000-0000-0000-0000-000000000000"})
    assert r.status_code == 422 and r.json()["codigo"] == "version_catalogo_no_existe"


def test_recursos_inexistentes_404(cliente):
    falso = "00000000-0000-0000-0000-000000000000"
    for ruta in (f"/api/versiones-catalogo/{falso}", f"/api/generaciones/{falso}", f"/api/criterios/{falso}",
                 f"/api/parques/{falso}", f"/api/usuarios/{falso}"):
        r = cliente.get(ruta)
        assert r.status_code == 404, ruta
        assert set(r.json()) >= {"codigo", "mensaje"}
