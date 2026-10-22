"""Parques, tipo de PI, fechas del programa e historial (RF-02, RF-11, RF-28, RF-29, RF-30, RF-31)."""

from tests.ayudas import cargar_catalogo, criterio_por_texto, crear_generacion, crear_parque, escenario


def _base(c):
    v = cargar_catalogo(c)
    return crear_generacion(c, v["id"])


def test_RF_02_AC_1_alta_de_parque(cliente):
    g = _base(cliente)
    r = cliente.post("/api/parques", json={"tipoRegistro": "activo", "nombre": "Parque X", "desarrollador": "D1",
                                           "tipoPI": "operacion_cerrado", "region": "MX-NLE", "generacionId": g["id"]})
    assert r.status_code == 201
    p = r.json()
    assert p["estado"] == "activo" and p["tipoPI"] == "operacion_cerrado" and p["fase"] == "diagnostico"
    assert r.headers["location"].endswith(p["id"])
    assert cliente.get(f"/api/parques/{p['id']}").json()["nombre"] == "Parque X"


def test_RF_02_AC_2_tipo_pi_invalido(cliente):
    g = _base(cliente)
    r = cliente.post("/api/parques", json={"tipoRegistro": "activo", "nombre": "P", "desarrollador": "D",
                                           "tipoPI": "mixto", "region": "MX-NLE", "generacionId": g["id"]})
    assert r.status_code == 422 and r.json()["mensaje"] == "Debe seleccionar un tipo de PI válido"


def test_RF_02_AC_3_region_invalida(cliente):
    g = _base(cliente)
    r = cliente.post("/api/parques", json={"tipoRegistro": "activo", "nombre": "P", "desarrollador": "D",
                                           "tipoPI": "operacion_cerrado", "region": "Nuevo León", "generacionId": g["id"]})
    assert r.status_code == 422 and r.json()["mensaje"] == "Debe seleccionar una región válida"


def test_RF_28_AC_3_parque_sin_generacion(cliente):
    _base(cliente)
    r = cliente.post("/api/parques", json={"tipoRegistro": "activo", "nombre": "P", "desarrollador": "D",
                                           "tipoPI": "operacion_cerrado", "region": "MX-NLE"})
    assert r.status_code == 422 and r.json()["mensaje"] == "Debe indicar la generación del parque"


def test_RF_31_AC_2_alta_parque_historico(cliente):
    r = cliente.post("/api/parques", json={"tipoRegistro": "historico", "nombre": "Parque Y", "region": "MX-JAL",
                                           "fechaUltimoDictamen": "2022-03-15", "fechaTerminoPrograma": "2022-01-10"})
    assert r.status_code == 201
    p = r.json()
    assert p["estado"] == "historico" and p["fechaTerminoPrograma"] == "2022-01-10"


def test_listado_paginado_y_filtros(cliente):
    g = _base(cliente)
    for i in range(3):
        crear_parque(cliente, g["id"], nombre=f"Parque {i}", region="MX-JAL" if i else "MX-NLE")
    r = cliente.get("/api/parques", params={"tamanoPagina": 2, "pagina": 1})
    assert r.status_code == 200 and r.json()["total"] == 3 and len(r.json()["items"]) == 2
    assert cliente.get("/api/parques", params={"region": "MX-JAL"}).json()["total"] == 2
    assert cliente.get("/api/parques", params={"orden": "noExiste"}).status_code == 422


def test_RF_30_AC_1_fechas_del_programa(cliente):
    g = _base(cliente)
    p = crear_parque(cliente, g["id"])
    r = cliente.patch(f"/api/parques/{p['id']}", json={"fechaTerminoPrograma": "2027-11-30",
                                                       "fechaProximaActualizacion": "2028-02-01"})
    assert r.status_code == 200
    assert r.json()["fechaTerminoPrograma"] == "2027-11-30" and r.json()["fechaProximaActualizacion"] == "2028-02-01"


def test_RF_30_AC_2_y_AC_3_atraso_y_actualizacion_anual(cliente):
    g = _base(cliente)
    p = crear_parque(cliente, g["id"])
    cliente.patch(f"/api/parques/{p['id']}", json={"fechaProximaActualizacion": "2020-02-01"})
    assert cliente.get(f"/api/parques/{p['id']}").json()["atrasadoActualizacion"] is True
    r = cliente.post(f"/api/parques/{p['id']}/actualizaciones-anuales", json={"fecha": "2030-01-15"})
    assert r.status_code == 201 and r.json()["fechaProximaActualizacion"] == "2031-01-15"
    assert cliente.get(f"/api/parques/{p['id']}/actualizaciones-anuales/{r.json()['id']}").status_code == 200
    parque = cliente.get(f"/api/parques/{p['id']}").json()
    assert parque["atrasadoActualizacion"] is False and parque["fechaProximaActualizacion"] == "2031-01-15"


def test_RF_29_AC_3_baja_de_parque(cliente):
    g = _base(cliente)
    p = crear_parque(cliente, g["id"])
    r = cliente.patch(f"/api/parques/{p['id']}", json={"estado": "inactivo"})
    assert r.status_code == 422
    r = cliente.patch(f"/api/parques/{p['id']}", json={"estado": "inactivo", "motivo": "Salió del programa"})
    assert r.status_code == 200 and r.json()["estado"] == "inactivo"
    assert cliente.get("/api/parques").json()["total"] == 0
    assert cliente.patch(f"/api/parques/{p['id']}", json={"estado": "inactivo", "motivo": "x"}).status_code == 200


def test_RF_11_AC_1_AC_4_cambio_de_tipo_recalcula(cliente):
    e = escenario(cliente)
    pid = e["parque"]["id"]
    assert criterio_por_texto(cliente, pid, "cámara en cada caseta") is None
    r = cliente.put(f"/api/parques/{pid}/tipo-pi", json={"tipoPI": "operacion_cerrado", "fechaCambio": "2027-06-01",
                                                         "motivo": "Inició operaciones"})
    assert r.status_code == 200, r.text
    cuerpo = r.json()
    assert cuerpo["cambio"] is True and cuerpo["clasificacionCerrada"]["fechaHasta"] == "2027-06-01"
    camara = criterio_por_texto(cliente, pid, "cámara en cada caseta")
    assert camara is not None and camara["estadoCalificacion"] == "pendiente"
    assert camara["criterioId"] in cuerpo["criteriosQueDejanDeSerNA"]
    assert len(cliente.get(f"/api/parques/{pid}/tipos-pi").json()) == 2


def test_RF_11_AC_3_AC_5_validaciones(cliente):
    e = escenario(cliente)
    pid = e["parque"]["id"]
    r = cliente.put(f"/api/parques/{pid}/tipo-pi", json={"tipoPI": "otro", "fechaCambio": "2027-06-01", "motivo": "x"})
    assert r.status_code == 422 and r.json()["mensaje"] == "Tipo de PI inválido"
    r = cliente.put(f"/api/parques/{pid}/tipo-pi", json={"tipoPI": "operacion_cerrado", "fechaCambio": "2027-06-01"})
    assert r.status_code == 422 and r.json()["mensaje"] == "Indique el motivo del cambio de tipo de PI"
    assert len(cliente.get(f"/api/parques/{pid}/tipos-pi").json()) == 1


def test_RF_31_AC_1_historial(cliente):
    e = escenario(cliente)
    r = cliente.get(f"/api/parques/{e['parque']['id']}/historial")
    assert r.status_code == 200
    assert len(r.json()["generaciones"]) == 1
