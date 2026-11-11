"""S09_A1, pruebas de caracterización.

Fijan el comportamiento actual de PATCH /parques, PATCH /usuarios y GET /parques antes de refactorizar
(S09_A1/refactorizacion.md). Cubren ramas que la suite no tocaba: validaciones del cuerpo del PATCH, cambios de
desarrollador y región, parque histórico, filtros generacionId y atrasado, y el expediente de la generación más
reciente. Pasan sobre el código original y tienen que seguir pasando después de cada refactorización.
"""

from tests.ayudas import cargar_catalogo, crear_generacion, crear_parque, escenario, sql


def _parque_activo(c):
    v = cargar_catalogo(c)
    g = crear_generacion(c, v["id"])
    return crear_parque(c, g["id"])


def _parque_historico(c):
    r = c.post("/api/parques", json={"tipoRegistro": "historico", "nombre": "Parque H", "region": "MX-JAL",
                                     "fechaUltimoDictamen": "2022-03-15", "fechaTerminoPrograma": "2022-01-10"})
    assert r.status_code == 201, r.text
    return r.json()


def _bitacora(parque_id, accion):
    filas = sql("SELECT detalle FROM registro_bitacora WHERE parque_id = %s AND accion = %s ORDER BY id",
                parque_id, accion)
    return [detalle for (detalle,) in filas]


# ------------------------------------------------------------------ PATCH /parques/{parqueId}
def test_patch_parque_validaciones_del_cuerpo(cliente):
    p = _parque_activo(cliente)
    casos = [
        ({}, "Indique al menos un campo a actualizar"),
        ({"estado": None}, "El único estado admitido es inactivo"),
        ({"nombre": None}, "El campo nombre no admite nulo"),
        ({"desarrollador": None}, "El campo desarrollador no admite nulo"),
        ({"region": None}, "El campo region no admite nulo"),
    ]
    for cuerpo, mensaje in casos:
        r = cliente.patch(f"/api/parques/{p['id']}", json=cuerpo)
        assert r.status_code == 422, (cuerpo, r.text)
        assert (r.json()["codigo"], r.json()["mensaje"]) == ("datos_invalidos", mensaje), cuerpo


def test_patch_parque_datos_generales_y_bitacora(cliente):
    p = _parque_activo(cliente)
    r = cliente.patch(f"/api/parques/{p['id']}",
                      json={"nombre": "  Parque Norte ", "desarrollador": "Desarrolladora Dos", "region": "MX-COA"})
    assert r.status_code == 200, r.text
    assert (r.json()["nombre"], r.json()["desarrollador"], r.json()["region"]) == (
        "Parque Norte", "Desarrolladora Dos", "MX-COA")
    assert _bitacora(p["id"], "actualizar_parque") == ["nombre, desarrollador, region"]


def test_patch_parque_baja_una_sola_vez(cliente):
    p = _parque_activo(cliente)
    url = f"/api/parques/{p['id']}"
    r = cliente.patch(url, json={"estado": "inactivo", "motivo": "Salió del programa"})
    assert r.status_code == 200 and r.json()["motivoBaja"] == "Salió del programa"
    assert _bitacora(p["id"], "baja_parque") == ["Salió del programa"]
    assert _bitacora(p["id"], "actualizar_parque") == []  # la baja sola no cuenta como actualización de datos
    # Repetir la baja no cambia nada ni deja otro registro, pero hoy sí exige el motivo.
    r = cliente.patch(url, json={"estado": "inactivo", "motivo": "Otra vez"})
    assert r.status_code == 200 and r.json()["motivoBaja"] == "Salió del programa"
    assert _bitacora(p["id"], "baja_parque") == ["Salió del programa"]
    r = cliente.patch(url, json={"estado": "inactivo"})
    assert r.status_code == 422 and r.json()["codigo"] == "motivo_requerido"


def test_patch_parque_historico(cliente):
    h = _parque_historico(cliente)
    url = f"/api/parques/{h['id']}"
    # La regla del histórico va antes que la del motivo: 409 aunque falte el motivo.
    r = cliente.patch(url, json={"estado": "inactivo"})
    assert r.status_code == 409 and r.json()["codigo"] == "transicion_invalida"
    r = cliente.patch(url, json={"fechaProximaActualizacion": "2028-01-01"})
    assert r.status_code == 422 and r.json()["codigo"] == "parque_historico"
    r = cliente.patch(url, json={"fechaTerminoPrograma": "2022-06-30"})
    assert r.status_code == 200 and r.json()["fechaTerminoPrograma"] == "2022-06-30"
    # Comportamiento actual, documentado como CR-06 en code_review.md: el null se ignora en silencio y la bitácora
    # lo registra como si hubiera cambiado. Esta prueba se ajusta cuando se corrija CR-06.
    r = cliente.patch(url, json={"fechaTerminoPrograma": None})
    assert r.status_code == 200 and r.json()["fechaTerminoPrograma"] == "2022-06-30"
    assert _bitacora(h["id"], "actualizar_parque") == ["fechaTerminoPrograma", "fechaTerminoPrograma"]


# ------------------------------------------------------------------ PATCH /usuarios/{usuarioId}
def test_patch_usuario_validaciones_del_cuerpo(cliente):
    e = escenario(cliente)
    casos = [
        ({}, "Indique al menos un campo a actualizar"),
        ({"nombre": None}, "El campo nombre no admite nulo"),
        ({"rol": None}, "El campo rol no admite nulo"),
        ({"estado": None}, "El campo estado no admite nulo"),
    ]
    for cuerpo, mensaje in casos:
        r = cliente.patch(f"/api/usuarios/{e['consultor']['id']}", json=cuerpo)
        assert r.status_code == 422, (cuerpo, r.text)
        assert (r.json()["codigo"], r.json()["mensaje"]) == ("datos_invalidos", mensaje), cuerpo


# ------------------------------------------------------------------ GET /parques
def _nombres(c, **params):
    r = c.get("/api/parques", params=params)
    assert r.status_code == 200, r.text
    return [p["nombre"] for p in r.json()["items"]]


def test_listado_de_parques_campos_y_filtros(cliente):
    e = escenario(cliente)  # Parque X, generación 2027, consultor asignado
    v, g, px = e["version"], e["generacion"], e["parque"]["id"]
    assert cliente.post(f"/api/parques/{px}/actualizaciones-anuales", json={"fecha": "2030-01-15"}).status_code == 201
    g28 = crear_generacion(cliente, v["id"], nombre="2028", inicio="2028-02-01")
    py = crear_parque(cliente, g28["id"], nombre="Parque Y", tipo="operacion_abierto", region="MX-JAL")
    assert cliente.patch(f"/api/parques/{py['id']}", json={"fechaProximaActualizacion": "2020-02-01"}).status_code == 200
    _parque_historico(cliente)

    items = {p["nombre"]: p for p in cliente.get("/api/parques").json()["items"]}
    assert set(items) == {"Parque X", "Parque Y", "Parque H"}
    x, y, h = items["Parque X"], items["Parque Y"], items["Parque H"]
    assert (x["generacionId"], x["fase"], x["versionCatalogo"], x["tipoPI"], x["desarrollador"]) == (
        g["id"], "diagnostico", v["nombre"], "construccion_cerrado", "Desarrolladora Uno")
    assert x["consultorAsignadoId"] == e["consultor"]["id"]
    assert x["fechaUltimaActualizacion"] == "2030-01-15" and x["atrasadoActualizacion"] is False
    assert y["generacionId"] == g28["id"] and y.get("consultorAsignadoId") is None
    assert y["atrasadoActualizacion"] is True
    assert h.get("tipoPI") is None and h.get("fase") is None and h.get("generacionId") is None
    assert h.get("desarrollador") is None and h["fechaTerminoPrograma"] == "2022-01-10"

    # Cada elemento del listado es idéntico a la consulta individual del parque.
    for p in items.values():
        assert cliente.get(f"/api/parques/{p['id']}").json() == p

    # Filtros y orden que la suite original no cubría.
    assert _nombres(cliente, generacionId=g["id"]) == ["Parque X"]
    assert _nombres(cliente, atrasado="true") == ["Parque Y"]
    assert _nombres(cliente, atrasado="false", orden="-nombre") == ["Parque X", "Parque H"]
    assert _nombres(cliente, orden="-nombre") == ["Parque Y", "Parque X", "Parque H"]


def test_listado_usa_el_expediente_de_la_generacion_mas_reciente(cliente):
    e = escenario(cliente)
    px = e["parque"]["id"]
    g28 = crear_generacion(cliente, e["version"]["id"], nombre="2028", inicio="2028-02-01")
    sql("INSERT INTO expediente (parque_id, generacion_id) VALUES (%s, %s)", px, g28["id"])
    (p,) = cliente.get("/api/parques").json()["items"]
    # El expediente nuevo no tiene fases ni consultor; la asignación vigente es del expediente anterior.
    assert p["generacionId"] == g28["id"]
    assert p.get("fase") is None and p.get("consultorAsignadoId") is None
    assert p["tipoPI"] == "construccion_cerrado"  # la clasificación es del parque, no del expediente
    assert cliente.get(f"/api/parques/{px}").json() == p
