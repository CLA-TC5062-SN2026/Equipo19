"""Criterios del parque, autoevaluación, cumplimiento, plan de trabajo y análisis de riesgos
(RF-04, RF-08, RF-09, RF-16, RF-25)."""

import psycopg

from tests.ayudas import criterio_por_texto, crear_usuario, escenario
from tests.conftest import ADMIN_URL, PRUEBA


def _sql(q, *args):
    with psycopg.connect(ADMIN_URL.rsplit("/", 1)[0] + "/" + PRUEBA, autocommit=True) as c:
        return c.execute(q, args)


def test_RF_04_AC_1_solo_criterios_aplicables(cliente):
    e = escenario(cliente)
    pid = e["parque"]["id"]
    items = cliente.get(f"/api/parques/{pid}/criterios", params={"tamanoPagina": 100}).json()["items"]
    assert len(items) == 22  # 24 del CSV menos 2 NA en construcción cerrado
    assert all(i["marca"] in ("O", "R") for i in items)
    assert criterio_por_texto(cliente, pid, "barreras físicas")["marca"] == "O"
    uno = cliente.get(f"/api/parques/{pid}/criterios/{items[0]['criterioId']}")
    assert uno.status_code == 200


def test_RF_04_AC_2_autoevaluar_criterio_na(cliente):
    e = escenario(cliente)
    pid = e["parque"]["id"]
    with psycopg.connect(ADMIN_URL.rsplit("/", 1)[0] + "/" + PRUEBA) as c:
        na = c.execute("SELECT c.id FROM criterio c WHERE c.texto LIKE '%cámara en cada caseta%'").fetchone()[0]
    r = cliente.put(f"/api/parques/{pid}/autoevaluaciones/{na}", json={"respuesta": "cumple"}, headers=e["h_appi"])
    assert r.status_code == 422 and r.json()["mensaje"] == "Este criterio no aplica al tipo de PI del parque"


def test_autoevaluacion_upsert_201_luego_200(cliente):
    e = escenario(cliente)
    pid = e["parque"]["id"]
    crit = criterio_por_texto(cliente, pid, "barreras físicas")["criterioId"]
    r = cliente.put(f"/api/parques/{pid}/autoevaluaciones/{crit}", json={"respuesta": "cumple_parcial"}, headers=e["h_appi"])
    assert r.status_code == 201
    r = cliente.put(f"/api/parques/{pid}/autoevaluaciones/{crit}", json={"respuesta": "cumple", "comentario": "Listo"}, headers=e["h_appi"])
    assert r.status_code == 200 and r.json()["respuesta"] == "cumple"
    assert cliente.get(f"/api/parques/{pid}/autoevaluaciones").json()["total"] == 1
    assert cliente.get(f"/api/parques/{pid}/autoevaluaciones/{crit}").json()["comentario"] == "Listo"


def test_RF_08_cumplimiento_por_suma_de_criterios(cliente):
    e = escenario(cliente)
    pid = e["parque"]["id"]
    r = cliente.get(f"/api/parques/{pid}/cumplimiento")
    assert r.status_code == 200
    total = r.json()["total"]
    assert total["porcentajeObligatorios"] == 0 and total["obligatoriosAplicables"] > 0
    obligatorios = [i for i in cliente.get(f"/api/parques/{pid}/criterios", params={"tamanoPagina": 100}).json()["items"]
                    if i["marca"] == "O"]
    _sql("UPDATE criterio_parque SET estado_calificacion='cumplido' WHERE criterio_id = %s", obligatorios[0]["criterioId"])
    total = cliente.get(f"/api/parques/{pid}/cumplimiento").json()["total"]
    esperado = round(100 / total["obligatoriosAplicables"], 2)
    assert total["obligatoriosCumplidos"] == 1 and abs(total["porcentajeObligatorios"] - esperado) < 0.01
    assert total["porcentajeRecomendados"] == 0


def test_RF_09_AC_1_AC_4_plan_de_trabajo(cliente):
    e = escenario(cliente)
    pid = e["parque"]["id"]
    crit = criterio_por_texto(cliente, pid, "barreras físicas")["criterioId"]
    r = cliente.post(f"/api/parques/{pid}/plan-trabajo", json={"criterioId": crit, "responsableId": e["appi"]["id"],
                                                               "fechaComprometida": "2027-04-15"}, headers=e["h_consultor"])
    assert r.status_code == 201, r.text
    renglon = r.json()
    assert cliente.get(f"/api/parques/{pid}/plan-trabajo/{renglon['id']}").status_code == 200
    assert cliente.get(f"/api/parques/{pid}/plan-trabajo").json()["total"] == 1
    r = cliente.post(f"/api/parques/{pid}/plan-trabajo", json={"criterioId": crit, "responsableId": e["appi"]["id"],
                                                               "fechaComprometida": "2027-04-15"}, headers=e["h_consultor"])
    assert r.status_code == 409
    otro_parque = cliente.post("/api/parques", json={"tipoRegistro": "activo", "nombre": "Parque Y", "desarrollador": "D",
                                                     "tipoPI": "construccion_cerrado", "region": "MX-JAL",
                                                     "generacionId": e["generacion"]["id"]}).json()
    appi_y = crear_usuario(cliente, "appi@parquey.mx", "appi", parqueId=otro_parque["id"])
    crit2 = criterio_por_texto(cliente, pid, "alumbrado")["criterioId"]
    r = cliente.post(f"/api/parques/{pid}/plan-trabajo", json={"criterioId": crit2, "responsableId": appi_y["id"],
                                                               "fechaComprometida": "2027-04-15"}, headers=e["h_consultor"])
    assert r.status_code == 422 and r.json()["mensaje"] == "El responsable debe ser un usuario APPI de este parque"
    r = cliente.patch(f"/api/parques/{pid}/plan-trabajo/{renglon['id']}", json={"fechaComprometida": "2027-05-01"}, headers=e["h_consultor"])
    assert r.status_code == 200 and r.json()["fechaComprometida"] == "2027-05-01"
    assert cliente.delete(f"/api/parques/{pid}/plan-trabajo/{renglon['id']}", headers=e["h_consultor"]).status_code == 204
    assert cliente.get(f"/api/parques/{pid}/plan-trabajo/{renglon['id']}").status_code == 404


def test_RF_09_AC_2_atraso_en_listado(cliente):
    e = escenario(cliente)
    pid = e["parque"]["id"]
    crit = criterio_por_texto(cliente, pid, "barreras físicas")["criterioId"]
    cliente.post(f"/api/parques/{pid}/plan-trabajo", json={"criterioId": crit, "responsableId": e["appi"]["id"],
                                                           "fechaComprometida": "2020-01-01"}, headers=e["h_consultor"])
    atrasados = cliente.get(f"/api/parques/{pid}/criterios", params={"atrasado": "true"}).json()["items"]
    assert [a["criterioId"] for a in atrasados] == [crit]


def test_RF_16_AC_1_revision_analisis_riesgos(cliente):
    e = escenario(cliente)
    pid = e["parque"]["id"]
    cuerpo = {"fechaRevision": "2027-03-10", "version": "1.0", "firmante": "María López", "resumen": "12 riesgos"}
    r = cliente.post(f"/api/parques/{pid}/revisiones-analisis-riesgos", json=cuerpo, headers=e["h_consultor"])
    assert r.status_code == 201 and r.json()["vigente"] is True
    primera = r.json()
    r = cliente.post(f"/api/parques/{pid}/revisiones-analisis-riesgos", json={**cuerpo, "version": "2.0",
                                                                             "fechaRevision": "2027-05-10"}, headers=e["h_consultor"])
    assert r.status_code == 201
    lista = {x["id"]: x for x in cliente.get(f"/api/parques/{pid}/revisiones-analisis-riesgos", headers=e["h_appi"]).json()}
    assert lista[primera["id"]]["vigente"] is False and lista[r.json()["id"]]["vigente"] is True
    assert cliente.get(f"/api/parques/{pid}/revisiones-analisis-riesgos/{primera['id']}", headers=e["h_consultor"]).status_code == 200
    # RF-16-AC-1: visible solo para la APPI y el consultor asignado; Coordinación recibe 403.
    assert cliente.get(f"/api/parques/{pid}/revisiones-analisis-riesgos").status_code == 403


def test_parque_historico_sin_subrecursos(cliente):
    p = cliente.post("/api/parques", json={"tipoRegistro": "historico", "nombre": "Parque Y", "region": "MX-JAL",
                                           "fechaUltimoDictamen": "2022-03-15", "fechaTerminoPrograma": "2022-01-10"}).json()
    assert cliente.get(f"/api/parques/{p['id']}/criterios").status_code == 404


def test_plan_de_trabajo_no_admite_criterio_cumplido(cliente):
    e = escenario(cliente)
    pid = e["parque"]["id"]
    crit = criterio_por_texto(cliente, pid, "barreras físicas")["criterioId"]
    _sql("UPDATE criterio_parque SET estado_calificacion='cumplido' WHERE criterio_id = %s", crit)
    r = cliente.post(f"/api/parques/{pid}/plan-trabajo", json={"criterioId": crit, "responsableId": e["appi"]["id"],
                                                               "fechaComprometida": "2027-04-15"}, headers=e["h_consultor"])
    assert r.status_code == 409 and r.json()["codigo"] == "criterio_cumplido"
