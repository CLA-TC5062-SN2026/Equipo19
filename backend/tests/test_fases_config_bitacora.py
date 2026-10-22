"""Fases, configuración y bitácora (RF-06, RF-32, RF-35, RNF-03)."""

import psycopg

from tests.ayudas import escenario
from tests.conftest import ADMIN_URL, PRUEBA


def test_RF_32_AC_1_nueve_fases_y_fase_actual(cliente):
    e = escenario(cliente)
    fases = cliente.get(f"/api/parques/{e['parque']['id']}/fases").json()
    assert len(fases) == 9 and fases[0]["actual"] is True and fases[0]["estado"] == "en_proceso"
    assert [f["orden"] for f in fases] == list(range(1, 10))


def test_RF_32_cierre_de_fase(cliente):
    e = escenario(cliente)
    pid = e["parque"]["id"]
    r = cliente.post(f"/api/parques/{pid}/fases/diagnostico/cierre")
    assert r.status_code == 200 and r.json()["estado"] == "completada"
    fases = {f["fase"]: f for f in cliente.get(f"/api/parques/{pid}/fases").json()}
    assert fases["plan_trabajo"]["actual"] is True
    assert cliente.post(f"/api/parques/{pid}/fases/dictamen/cierre").status_code == 409
    assert cliente.get(f"/api/parques/{pid}").json()["fase"] == "plan_trabajo"


def test_RF_32_AC_4_AC_5_avance_por_excepcion(cliente):
    e = escenario(cliente)
    pid = e["parque"]["id"]
    r = cliente.post(f"/api/parques/{pid}/avances-fase", json={"faseDestino": "plan_trabajo"})
    assert r.status_code == 422
    assert r.json()["mensaje"] == "Para avanzar sin cerrar la fase actual registre el motivo de la excepción"
    r = cliente.post(f"/api/parques/{pid}/avances-fase", json={"faseDestino": "plan_trabajo",
                                                               "motivo": "Diagnóstico entregado; se revisa en visita"})
    assert r.status_code == 201
    fases = {f["fase"]: f for f in r.json()}
    assert fases["diagnostico"]["estado"] == "avanzada_por_excepcion" and fases["plan_trabajo"]["actual"]
    r = cliente.post(f"/api/parques/{pid}/avances-fase", json={"faseDestino": "dictamen", "motivo": "x"})
    assert r.status_code == 409


def test_RF_06_AC_6_AC_7_configuracion(cliente):
    r = cliente.get("/api/configuracion")
    assert r.status_code == 200 and r.json()["tamanoMaximoEvidenciaMB"] == 100
    r = cliente.patch("/api/configuracion", json={"tamanoMaximoEvidenciaMB": 50})
    assert r.status_code == 200 and r.json()["tamanoMaximoEvidenciaMB"] == 50
    r = cliente.patch("/api/configuracion", json={"tamanoMaximoEvidenciaMB": 500})
    assert r.status_code == 422 and r.json()["mensaje"] == "El límite máximo configurable es 100 MB"
    assert cliente.get("/api/configuracion").json()["tamanoMaximoEvidenciaMB"] == 50


def test_RF_35_AC_3_bitacora_filtrada_y_ordenada(cliente):
    e = escenario(cliente)
    pid = e["parque"]["id"]
    cliente.patch(f"/api/parques/{pid}", json={"nombre": "Parque X2"})
    r = cliente.get("/api/bitacora", params={"parqueId": pid})
    assert r.status_code == 200
    items = r.json()["items"]
    assert items and all(i["parqueId"] == pid for i in items)
    fechas = [i["fechaHora"] for i in items]
    assert fechas == sorted(fechas, reverse=True)
    assert cliente.get("/api/bitacora", params={"accion": "crear_usuario"}).json()["total"] == 2


def test_RNF_03_bitacora_no_se_modifica(cliente):
    escenario(cliente)
    with psycopg.connect(ADMIN_URL.rsplit("/", 1)[0] + "/" + PRUEBA, autocommit=True) as c:
        try:
            c.execute("UPDATE registro_bitacora SET accion='x'")
            assert False, "la base permitió modificar la bitácora"
        except psycopg.errors.RaiseException:
            pass


def test_esquema_identico():
    """backend/db/esquema_bd.sql debe ser copia exacta del entregable S05_S06_A1/esquema_bd.sql."""
    from tests.conftest import RAIZ

    entregable = RAIZ.parent / "S05_S06_A1" / "esquema_bd.sql"
    assert (RAIZ / "db" / "esquema_bd.sql").read_bytes() == entregable.read_bytes()


def test_integridad_check_responde_422_y_unicidad_409():
    """[C-05] Mapeo de violaciones de integridad al código del contrato."""
    import asyncio

    from psycopg import errors
    from sqlalchemy.exc import IntegrityError

    from app.main import app

    manejador = app.exception_handlers[IntegrityError]
    for orig, esperado in ((errors.UniqueViolation(), 409), (errors.CheckViolation(), 422),
                           (errors.ForeignKeyViolation(), 422)):
        resp = asyncio.run(manejador(None, IntegrityError("x", {}, orig)))
        assert resp.status_code == esperado
