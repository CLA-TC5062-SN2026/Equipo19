"""Usuarios, contacto principal y asignaciones (RF-03, RF-10, RF-29, RF-34)."""

import psycopg

from tests.ayudas import crear_usuario, escenario
from tests.conftest import ADMIN_URL, PRUEBA


def _activar(usuario_id):
    """Simula el registro (S05-S06-A2) para poder probar RF-34."""
    with psycopg.connect(ADMIN_URL.rsplit("/", 1)[0] + "/" + PRUEBA, autocommit=True) as c:
        c.execute("UPDATE usuario SET estado='activo', contrasena_hash='x' WHERE id=%s", (usuario_id,))


def test_RF_03_AC_1_alta_pendiente_con_invitacion(cliente):
    e = escenario(cliente)
    assert e["appi"]["estado"] == "pendiente_activacion" and e["appi"]["parqueId"] == e["parque"]["id"]
    with psycopg.connect(ADMIN_URL.rsplit("/", 1)[0] + "/" + PRUEBA) as c:
        n = c.execute("SELECT count(*) FROM mensaje_correo WHERE destinatario='gerente@parquex.mx' AND tipo='invitacion'").fetchone()[0]
        enlaces = c.execute("SELECT count(*) FROM enlace_un_solo_uso e JOIN usuario u ON u.id=e.usuario_id WHERE u.correo='gerente@parquex.mx'").fetchone()[0]
    assert n == 1 and enlaces == 1
    r = cliente.get(f"/api/usuarios/{e['appi']['id']}")
    assert r.status_code == 200 and "contrasena" not in r.text.lower()


def test_correo_duplicado_sin_mayusculas(cliente):
    e = escenario(cliente)
    r = cliente.post("/api/usuarios", json={"correo": "GERENTE@parquex.mx", "nombre": "x", "rol": "appi",
                                            "parqueId": e["parque"]["id"]})
    assert r.status_code == 409


def test_RF_03_AC_3_administrador_tecnico_sin_parque(cliente):
    u = crear_usuario(cliente, "ops@sgpis.mx", "administrador_tecnico")
    assert u["parqueId"] is None


def test_appi_sin_parque_o_parque_inexistente(cliente):
    r = cliente.post("/api/usuarios", json={"correo": "a@b.mx", "nombre": "a", "rol": "appi"})
    assert r.status_code == 422
    r = cliente.post("/api/usuarios", json={"correo": "a@b.mx", "nombre": "a", "rol": "appi",
                                            "parqueId": "00000000-0000-0000-0000-000000000000"})
    assert r.status_code == 422 and r.json()["codigo"] == "parque_no_existe"


def test_listado_y_actualizacion_de_usuario(cliente):
    e = escenario(cliente)
    r = cliente.get("/api/usuarios", params={"rol": "appi"})
    assert r.status_code == 200 and r.json()["total"] == 1
    r = cliente.patch(f"/api/usuarios/{e['consultor']['id']}", json={"nombre": "Juan Pérez"})
    assert r.status_code == 200 and r.json()["nombre"] == "Juan Pérez"


def test_RF_29_AC_1_baja_de_consultor_cierra_asignaciones(cliente):
    e = escenario(cliente)
    pid = e["parque"]["id"]
    cliente.post(f"/api/parques/{pid}/asignaciones-consultor", json={"consultorId": e["consultor"]["id"]})
    r = cliente.patch(f"/api/usuarios/{e['consultor']['id']}", json={"estado": "inactivo", "motivo": "Ya no colabora"})
    assert r.status_code == 200 and r.json()["estado"] == "inactivo"
    asignaciones = cliente.get(f"/api/parques/{pid}/asignaciones-consultor").json()
    assert all(a["vigente"] is False for a in asignaciones)


def test_RF_10_AC_1_AC_2_asignar_y_reasignar(cliente):
    e = escenario(cliente)
    pid = e["parque"]["id"]
    r = cliente.post(f"/api/parques/{pid}/asignaciones-consultor", json={"consultorId": e["consultor"]["id"]})
    assert r.status_code == 201 and r.json()["vigente"] is True
    primera = r.json()
    assert cliente.get(f"/api/parques/{pid}/asignaciones-consultor/{primera['id']}").status_code == 200
    r = cliente.post(f"/api/parques/{pid}/asignaciones-consultor", json={"consultorId": e["consultor"]["id"]})
    assert r.status_code == 409 and r.json()["codigo"] == "consultor_ya_asignado"
    ana = crear_usuario(cliente, "ana.ruiz@consultores.mx", "consultor")
    r = cliente.post(f"/api/parques/{pid}/asignaciones-consultor", json={"consultorId": ana["id"]})
    assert r.status_code == 201
    historial = {a["consultorId"]: a for a in cliente.get(f"/api/parques/{pid}/asignaciones-consultor").json()}
    assert historial[e["consultor"]["id"]]["vigente"] is False and historial[e["consultor"]["id"]]["vigenteHasta"]
    assert historial[ana["id"]]["vigente"] is True
    assert cliente.get(f"/api/parques/{pid}").json()["consultorAsignadoId"] == ana["id"]


def test_asignar_usuario_que_no_es_consultor(cliente):
    e = escenario(cliente)
    r = cliente.post(f"/api/parques/{e['parque']['id']}/asignaciones-consultor", json={"consultorId": e["appi"]["id"]})
    assert r.status_code == 422 and r.json()["codigo"] == "usuario_no_es_consultor"


def test_RF_34_AC_1_AC_2_contacto_principal(cliente):
    e = escenario(cliente)
    pid = e["parque"]["id"]
    asistente = crear_usuario(cliente, "asistente@parquex.mx", "appi", parqueId=pid)
    r = cliente.put(f"/api/parques/{pid}/contacto-principal", json={"usuarioId": e["appi"]["id"]})
    assert r.status_code == 422  # todavía pendiente de activación
    _activar(e["appi"]["id"])
    _activar(asistente["id"])
    assert cliente.put(f"/api/parques/{pid}/contacto-principal", json={"usuarioId": e["appi"]["id"]}).status_code == 200
    r = cliente.put(f"/api/parques/{pid}/contacto-principal", json={"usuarioId": asistente["id"]})
    assert r.status_code == 200 and r.json()["contactoPrincipal"] is True
    lista = cliente.get(f"/api/parques/{pid}/usuarios").json()
    assert [u["correo"] for u in lista if u["contactoPrincipal"]] == ["asistente@parquex.mx"]
    assert cliente.get(f"/api/parques/{pid}").json()["contactoPrincipalId"] == asistente["id"]


def test_RF_34_AC_3_baja_del_contacto_deja_parque_sin_contacto(cliente):
    e = escenario(cliente)
    pid = e["parque"]["id"]
    _activar(e["appi"]["id"])
    cliente.put(f"/api/parques/{pid}/contacto-principal", json={"usuarioId": e["appi"]["id"]})
    cliente.patch(f"/api/usuarios/{e['appi']['id']}", json={"estado": "inactivo", "motivo": "Renunció"})
    assert cliente.get(f"/api/parques/{pid}").json()["contactoPrincipalId"] is None


def test_no_se_asigna_consultor_a_parque_dado_de_baja(cliente):
    e = escenario(cliente)
    pid = e["parque"]["id"]
    cliente.patch(f"/api/parques/{pid}", json={"estado": "inactivo", "motivo": "Salió"})
    r = cliente.post(f"/api/parques/{pid}/asignaciones-consultor", json={"consultorId": e["consultor"]["id"]})
    assert r.status_code == 409 and r.json()["codigo"] == "parque_inactivo"
