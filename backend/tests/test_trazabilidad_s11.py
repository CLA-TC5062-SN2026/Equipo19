"""Criterios de aceptación que el código ya cumplía pero ninguna prueba nombraba (S11, matriz de trazabilidad).

Cada prueba lleva el ID del AC que verifica. No cambian el comportamiento de la API.
"""

import pytest

from tests.ayudas import CSV, crear_parque, criterio_por_texto, escenario, sql

PARQUE_Y = {"nombre": "Parque Y", "region": "MX-JAL"}


def _otro_parque(c, e):
    return crear_parque(c, e["generacion"]["id"], **PARQUE_Y)


@pytest.mark.parametrize("ac,metodo,ruta,cuerpo", [
    ("RF-01-AC-2", "POST", "/api/versiones-catalogo", None),
    ("RF-10-AC-3", "POST", "/api/parques/{pid}/asignaciones-consultor", {"consultorId": "{consultor}"}),
    ("RF-24-AC-2", "PATCH", "/api/criterios/{crit}", {"evidenciaSuficiente": "Otro texto"}),
    ("RF-29-AC-2", "PATCH", "/api/usuarios/{appi}", {"estado": "inactivo", "motivo": "Me voy"}),
    ("RF-32-AC-3", "POST", "/api/parques/{pid}/fases/diagnostico/cierre", None),
])
def test_RF_operaciones_de_coordinacion_rechazadas_a_appi_y_consultor(cliente, ac, metodo, ruta, cuerpo):
    e = escenario(cliente)
    pid = e["parque"]["id"]
    crit = cliente.get(f"/api/parques/{pid}/criterios").json()["items"][0]["criterioId"]
    valores = {"pid": pid, "crit": crit, "consultor": e["consultor"]["id"], "appi": e["appi"]["id"]}
    ruta = ruta.format(**valores)
    if cuerpo:
        cuerpo = {k: v.format(**valores) if isinstance(v, str) else v for k, v in cuerpo.items()}
    for h in (e["h_appi"], e["h_consultor"]):
        if ac == "RF-01-AC-2":
            r = cliente.post(ruta, headers=h, data={"nombreVersion": "intento"},
                             files={"archivo": ("c.csv", CSV, "text/csv")})
        else:
            r = cliente.request(metodo, ruta, json=cuerpo, headers=h)
        assert r.status_code == 403, f"{ac}: {r.status_code} {r.text}"
    # Nada cambió: la fase sigue en curso, la APPI sigue activa, no hay versión nueva.
    assert cliente.get(f"/api/parques/{pid}/fases").json()[0]["estado"] == "en_proceso"
    assert cliente.get(f"/api/usuarios/{e['appi']['id']}").json()["estado"] == "activo"
    assert len(cliente.get("/api/versiones-catalogo").json()) == 1


def test_RF_31_AC_3_appi_no_ve_historial_de_otro_parque(cliente):
    e = escenario(cliente)
    otro = _otro_parque(cliente, e)
    assert cliente.get(f"/api/parques/{e['parque']['id']}/historial", headers=e["h_appi"]).status_code == 200
    assert cliente.get(f"/api/parques/{otro['id']}/historial", headers=e["h_appi"]).status_code == 403


def test_RF_11_AC_2_conserva_porcentaje_de_la_clasificacion_anterior(cliente):
    e = escenario(cliente)
    pid = e["parque"]["id"]
    obligatorios = [i for i in cliente.get(f"/api/parques/{pid}/criterios", params={"tamanoPagina": 100})
                    .json()["items"] if i["marca"] == "O"]
    for x in obligatorios[:3]:
        sql("UPDATE criterio_parque SET estado_calificacion='cumplido' WHERE criterio_id = %s", x["criterioId"])
    antes = cliente.get(f"/api/parques/{pid}/cumplimiento").json()["total"]["porcentajeObligatorios"]
    r = cliente.put(f"/api/parques/{pid}/tipo-pi", json={"tipoPI": "operacion_cerrado", "fechaCambio": "2027-06-01",
                                                         "motivo": "Inició operaciones"})
    assert r.status_code == 200
    assert r.json()["clasificacionCerrada"]["porcentajeObligatoriosAlCierre"] == pytest.approx(antes, abs=0.01)
    despues = cliente.get(f"/api/parques/{pid}/cumplimiento").json()["total"]["porcentajeObligatorios"]
    assert despues != antes  # el nuevo tipo suma criterios O: el porcentaje nuevo se calcula aparte
    historial = cliente.get(f"/api/parques/{pid}/tipos-pi").json()
    cerrada = next(x for x in historial if x["fechaHasta"] is not None)
    assert cerrada["porcentajeObligatoriosAlCierre"] == pytest.approx(antes, abs=0.01)


def test_RF_08_AC_3_estandar_sin_obligatorios_aplicables_no_aplica(cliente):
    e = escenario(cliente)
    pid = e["parque"]["id"]
    por_estandar = cliente.get(f"/api/parques/{pid}/cumplimiento").json()["porEstandar"]
    sin_o = [x for x in por_estandar if x["obligatoriosAplicables"] == 0]
    con_o = [x for x in por_estandar if x["obligatoriosAplicables"] > 0]
    assert sin_o, "el catálogo sintético no tiene O en el estándar 9 para construcción cerrado"
    assert con_o and all(x["porcentajeObligatorios"] is not None for x in con_o)
    for x in sin_o:
        assert x["porcentajeObligatorios"] is None  # "No aplica", no 0 %
    assert criterio_por_texto(cliente, pid, "cámara en cada caseta") is None  # NA en construcción cerrado


def test_RF_23_AC_1_gerente_ve_solo_los_parques_de_su_desarrollador_en_una_vista(cliente):
    from tests.ayudas import bearer, crear_activo, iniciar_sesion

    e = escenario(cliente)
    segundo = crear_parque(cliente, e["generacion"]["id"], nombre="Parque X2")  # mismo desarrollador
    ajeno = cliente.post("/api/parques", json={"tipoRegistro": "activo", "nombre": "Ajeno", "desarrollador": "Otra",
                                               "tipoPI": "operacion_cerrado", "region": "MX-JAL",
                                               "generacionId": e["generacion"]["id"]}).json()
    desarrollador = sql("SELECT desarrollador_id FROM parque WHERE id = %s", e["parque"]["id"])[0][0]
    crear_activo("gerente@desarrolladora.mx", "gerente_corporativo", desarrollador_id=desarrollador)
    h = bearer(iniciar_sesion(cliente, "gerente@desarrolladora.mx"))
    ids = {p["id"] for p in cliente.get("/api/parques", headers=h).json()["items"]}
    assert ids == {e["parque"]["id"], segundo["id"]}
    assert cliente.get(f"/api/parques/{segundo['id']}/cumplimiento", headers=h).status_code == 200
    assert cliente.get(f"/api/parques/{ajeno['id']}/cumplimiento", headers=h).status_code == 403
    # RF-23-AC-2, parte disponible: el gerente no puede escribir en el expediente (no hay endpoints de evidencia aún).
    assert cliente.patch(f"/api/parques/{segundo['id']}", json={"nombre": "x"}, headers=h).status_code == 403


def test_RF_03_AC_2_consultor_asignado_no_puede_ser_appi_del_mismo_parque(cliente):
    e = escenario(cliente)
    pid = e["parque"]["id"]
    r = cliente.patch(f"/api/usuarios/{e['consultor']['id']}", json={"rol": "appi", "parqueId": pid})
    assert r.status_code == 422
    assert r.json()["mensaje"] == "Un usuario no puede ser APPI y Consultor del mismo parque"
    assert cliente.get(f"/api/usuarios/{e['consultor']['id']}").json()["rol"] == "consultor"


def test_RF_29_AC_3_baja_de_parque_retira_acceso_a_appi_y_consultor(cliente):
    e = escenario(cliente)
    pid = e["parque"]["id"]
    for h in (e["h_appi"], e["h_consultor"]):
        assert cliente.get(f"/api/parques/{pid}/fases", headers=h).status_code == 200
    r = cliente.patch(f"/api/parques/{pid}", json={"estado": "inactivo", "motivo": "Salió del programa"})
    assert r.status_code == 200
    for h in (e["h_appi"], e["h_consultor"]):
        assert cliente.get(f"/api/parques/{pid}/fases", headers=h).status_code == 403
        assert cliente.get("/api/parques", headers=h).json()["total"] == 0
    # Coordinación lo sigue consultando con el filtro de estado.
    assert cliente.get("/api/parques", params={"estado": "inactivo"}).json()["total"] == 1
