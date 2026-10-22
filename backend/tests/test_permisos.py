"""Protección de rutas y control por rol (S05-S06-A2, parte 2; RNF-01, RNF-02, RF-35-AC-2)."""

import contextlib
import uuid

import pytest
import yaml

from tests.ayudas import (bearer, crear_activo, crear_generacion, crear_parque, crear_usuario, escenario,
                          iniciar_sesion, sql, activar)
from tests.conftest import CONTRATO


@contextlib.contextmanager
def sin_token(c):
    guardado = c.headers.pop("Authorization", None)
    try:
        yield c
    finally:
        c.headers["Authorization"] = guardado


def _rutas_protegidas_implementadas():
    """Operaciones del contrato sin `security: []` que el backend implementa."""
    from app.main import app

    contrato = yaml.safe_load(open(CONTRATO, encoding="utf-8"))
    implementadas = {(m.upper(), p.removeprefix("/api")) for p, it in app.openapi()["paths"].items() for m in it}
    for ruta, item in contrato["paths"].items():
        for metodo, op in item.items():
            if metodo in ("get", "post", "put", "patch", "delete") and op.get("security") != [] \
                    and (metodo.upper(), ruta) in implementadas:
                yield metodo.upper(), ruta


def _concreta(ruta):
    falso = str(uuid.uuid4())
    return "/api" + ruta.replace("{fase}", "diagnostico").replace("{parqueId}", falso).replace(
        "{criterioId}", falso).replace("{usuarioId}", falso).replace("{versionId}", falso).replace(
        "{generacionId}", falso).replace("{renglonId}", falso).replace("{revisionId}", falso).replace(
        "{asignacionId}", falso).replace("{actualizacionId}", falso)


def test_toda_ruta_protegida_responde_401_sin_token(cliente):
    rutas = list(_rutas_protegidas_implementadas())
    assert len(rutas) == 48  # 46 CRUD (sin /salud) + /auth/me + /auth/logout
    with sin_token(cliente):
        for metodo, ruta in rutas:
            r = cliente.request(metodo, _concreta(ruta), json={} if metodo in ("POST", "PUT", "PATCH") else None)
            assert r.status_code == 401, f"{metodo} {ruta} -> {r.status_code}"


def test_toda_ruta_protegida_responde_401_con_token_alterado(cliente):
    token = cliente.headers["Authorization"].split()[1]
    alterado = token[:-3] + ("aaa" if not token.endswith("aaa") else "bbb")
    for metodo, ruta in _rutas_protegidas_implementadas():
        r = cliente.request(metodo, _concreta(ruta), headers=bearer(alterado),
                            json={} if metodo in ("POST", "PUT", "PATCH") else None)
        assert r.status_code == 401, f"{metodo} {ruta} -> {r.status_code}"


def test_rutas_publicas_no_piden_token(cliente):
    with sin_token(cliente):
        assert cliente.get("/api/salud").status_code == 200
        assert cliente.post("/api/auth/login", json={"correo": "x@y.mx", "contrasena": "z"}).status_code == 401
        assert cliente.post("/api/auth/register", json={"tokenInvitacion": "x" * 40, "contrasena": "y" * 12}).status_code == 410


def test_rol_incorrecto_403_y_rol_correcto_201(cliente):
    e = escenario(cliente)
    cuerpo = {"tipoRegistro": "activo", "nombre": "Parque Nuevo", "desarrollador": "D", "tipoPI": "operacion_cerrado",
              "region": "MX-NLE", "generacionId": e["generacion"]["id"]}
    r = cliente.post("/api/parques", json=cuerpo, headers=e["h_appi"])
    assert r.status_code == 403 and r.json()["codigo"] == "sin_permiso"
    assert cliente.post("/api/parques", json=cuerpo, headers=e["h_consultor"]).status_code == 403
    assert cliente.post("/api/parques", json=cuerpo).status_code == 201  # Coordinación


@pytest.mark.parametrize("ruta,metodo,cuerpo", [
    ("/api/usuarios", "POST", {"correo": "z@z.mx", "nombre": "z", "rol": "consultor"}),
    ("/api/configuracion", "PATCH", {"tamanoMaximoEvidenciaMB": 10}),
    ("/api/bitacora", "GET", None),
    ("/api/generaciones", "POST", {"nombre": "2028", "fechaInicio": "2028-02-01",
                                   "versionCatalogoId": "00000000-0000-0000-0000-000000000000"}),
])
def test_solo_coordinacion(cliente, ruta, metodo, cuerpo):
    e = escenario(cliente)
    for h in (e["h_appi"], e["h_consultor"]):
        assert cliente.request(metodo, ruta, json=cuerpo, headers=h).status_code == 403


def test_RNF_01_aislamiento_entre_parques(cliente):
    e = escenario(cliente)
    otro = crear_parque(cliente, e["generacion"]["id"], nombre="Parque Y", region="MX-JAL")
    for h in (e["h_appi"], e["h_consultor"]):
        assert cliente.get(f"/api/parques/{e['parque']['id']}/criterios", headers=h).status_code == 200
        r = cliente.get(f"/api/parques/{otro['id']}/criterios", headers=h)
        assert r.status_code == 403
    visibles = cliente.get("/api/parques", headers=e["h_appi"]).json()["items"]
    assert [p["id"] for p in visibles] == [e["parque"]["id"]]


def test_RF_10_AC_2_reasignacion_retira_acceso_de_inmediato(cliente):
    e = escenario(cliente)
    pid = e["parque"]["id"]
    assert cliente.get(f"/api/parques/{pid}/fases", headers=e["h_consultor"]).status_code == 200
    ana = crear_usuario(cliente, "ana.ruiz@consultores.mx", "consultor")
    cliente.post(f"/api/parques/{pid}/asignaciones-consultor", json={"consultorId": ana["id"]})
    assert cliente.get(f"/api/parques/{pid}/fases", headers=e["h_consultor"]).status_code == 403


def test_RF_04_solo_la_appi_autoevalua(cliente):
    e = escenario(cliente)
    pid = e["parque"]["id"]
    crit = cliente.get(f"/api/parques/{pid}/criterios").json()["items"][0]["criterioId"]
    assert cliente.put(f"/api/parques/{pid}/autoevaluaciones/{crit}", json={"respuesta": "cumple"}).status_code == 403
    assert cliente.put(f"/api/parques/{pid}/autoevaluaciones/{crit}", json={"respuesta": "cumple"},
                       headers=e["h_consultor"]).status_code == 403
    assert cliente.put(f"/api/parques/{pid}/autoevaluaciones/{crit}", json={"respuesta": "cumple"},
                       headers=e["h_appi"]).status_code == 201


def test_RF_16_AC_1_revisiones_ar_no_visibles_para_coordinacion(cliente):
    e = escenario(cliente)
    pid = e["parque"]["id"]
    assert cliente.get(f"/api/parques/{pid}/revisiones-analisis-riesgos").status_code == 403
    assert cliente.get(f"/api/parques/{pid}/revisiones-analisis-riesgos", headers=e["h_appi"]).status_code == 200


def test_RF_35_AC_4_bitacora_solo_coordinacion(cliente):
    e = escenario(cliente)
    tecnico = crear_activo("ops@sgpis.mx", "administrador_tecnico")  # noqa: F841
    h_tecnico = bearer(iniciar_sesion(cliente, "ops@sgpis.mx"))
    for h in (e["h_appi"], e["h_consultor"], h_tecnico):
        assert cliente.get("/api/bitacora", headers=h).status_code == 403


def test_RF_35_AC_2_el_403_queda_en_bitacora(cliente):
    e = escenario(cliente)
    otro = crear_parque(cliente, e["generacion"]["id"], nombre="Parque Y", region="MX-JAL")
    cliente.get(f"/api/parques/{otro['id']}", headers=e["h_consultor"])
    filas = sql("SELECT usuario_id, parque_id, resultado FROM registro_bitacora WHERE accion='acceso_denegado'")
    assert (uuid.UUID(e["consultor"]["id"]), uuid.UUID(otro["id"]), "denegado") in filas
    r = cliente.get("/api/bitacora", params={"accion": "acceso_denegado"})
    assert r.json()["total"] >= 1


def test_P_01_gerente_solo_ve_el_avance_de_sus_parques(cliente):
    e = escenario(cliente)
    pid = e["parque"]["id"]
    des = sql("SELECT desarrollador_id FROM parque WHERE id=%s", pid)[0][0]
    crear_activo("gerente@corporativo.mx", "gerente_corporativo", desarrollador_id=des)
    h = bearer(iniciar_sesion(cliente, "gerente@corporativo.mx"))
    for ruta in ("", "/cumplimiento", "/fases"):
        assert cliente.get(f"/api/parques/{pid}{ruta}", headers=h).status_code == 200, ruta
    for ruta in ("/criterios", "/autoevaluaciones", "/plan-trabajo", "/asignaciones-consultor", "/historial"):
        assert cliente.get(f"/api/parques/{pid}{ruta}", headers=h).status_code == 403, ruta
    assert cliente.patch(f"/api/parques/{pid}", json={"nombre": "x"}, headers=h).status_code == 403


def test_P_02_alta_inicial_de_coordinacion(cliente, capsys):
    from app import alta_inicial

    assert alta_inicial.main(["--correo", "primera@ampip.mx", "--nombre", "Primera"]) == 0
    token = capsys.readouterr().out.strip().splitlines()[-1]
    with sin_token(cliente):
        r = cliente.post("/api/auth/register", json={"tokenInvitacion": token, "contrasena": "contrasena-segura-1"})
        assert r.status_code == 201 and r.json()["rol"] == "coordinacion_ampip"
        assert cliente.post("/api/auth/login", json={"correo": "primera@ampip.mx",
                                                     "contrasena": "contrasena-segura-1"}).status_code == 200
    assert alta_inicial.main(["--correo", "primera@ampip.mx", "--nombre", "Otra"]) == 1
