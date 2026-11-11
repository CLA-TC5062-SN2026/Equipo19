"""S09_A1, pruebas de los hallazgos que se corrigieron (S09_A1/refactorizacion.md).

Estas dos pruebas fallan sobre el código original: reproducen los defectos CR-04 (condición de carrera al crear el
desarrollador) y CR-03 (una tanda de consultas por cada parque en GET /parques). Pasan después de R1 y R2.
"""

import threading
import time

from sqlalchemy import event

from tests.ayudas import cargar_catalogo, crear_generacion, crear_parque, sql


def _esperar_bloqueo(segundos=10.0):
    """Espera a que otra transacción quede detenida esperando un candado de PostgreSQL. No mide tiempos: solo
    sincroniza los dos hilos en el punto exacto donde el código original fallaba."""
    limite = time.monotonic() + segundos
    while time.monotonic() < limite:
        ((esperando,),) = sql("SELECT count(*) FROM pg_stat_activity "
                              "WHERE datname = current_database() AND wait_event_type = 'Lock'")
        if esperando:
            return
        time.sleep(0.02)
    raise AssertionError("la segunda transacción nunca quedó esperando el candado")


def test_R1_dos_altas_simultaneas_con_el_mismo_desarrollador_nuevo(bd):
    """CR-04. Dos solicitudes dan de alta parques del mismo desarrollador, que todavía no existe. La primera inserta
    el desarrollador y aún no confirma; la segunda no lo ve, intenta insertarlo y espera el índice único. Cuando la
    primera confirma, el código original lanzaba IntegrityError y la API respondía 409 a un alta válida."""
    from app.db import SessionLocal
    from app.servicios import obtener_o_crear_desarrollador

    primera, segunda = SessionLocal(), SessionLocal()
    resultado: dict = {}

    def alta_concurrente():
        try:
            resultado["id"] = obtener_o_crear_desarrollador(segunda, "Desarrolladora Nueva").id
            segunda.commit()
        except Exception as exc:  # noqa: BLE001 - se reporta en la aserción
            segunda.rollback()
            resultado["error"] = exc

    try:
        creado = obtener_o_crear_desarrollador(primera, "Desarrolladora Nueva")
        hilo = threading.Thread(target=alta_concurrente)
        hilo.start()
        _esperar_bloqueo()
        primera.commit()
        hilo.join(timeout=10)
        assert not hilo.is_alive()
        assert "error" not in resultado, f"la segunda alta falló: {resultado.get('error')!r}"
        assert resultado["id"] == creado.id
        assert sql("SELECT count(*) FROM desarrollador WHERE nombre = 'Desarrolladora Nueva'") == [(1,)]
    finally:
        primera.close()
        segunda.close()


def _consultas_del_listado(c):
    from app.db import engine

    cuenta = 0

    def contar(*_):
        nonlocal cuenta
        cuenta += 1

    event.listen(engine, "before_cursor_execute", contar)
    try:
        r = c.get("/api/parques", params={"tamanoPagina": 100})
    finally:
        event.remove(engine, "before_cursor_execute", contar)
    assert r.status_code == 200, r.text
    return cuenta, r.json()["total"]


def test_R2_el_listado_de_parques_no_hace_consultas_por_parque(cliente):
    """CR-03 y RNF-10. El número de sentencias SQL de GET /parques no debe crecer con el número de parques."""
    v = cargar_catalogo(cliente)
    g = crear_generacion(cliente, v["id"])
    for i in range(2):
        crear_parque(cliente, g["id"], nombre=f"Parque {i:02d}")
    con_2, total = _consultas_del_listado(cliente)
    assert total == 2
    for i in range(2, 12):
        crear_parque(cliente, g["id"], nombre=f"Parque {i:02d}")
    con_12, total = _consultas_del_listado(cliente)
    assert total == 12
    assert con_12 == con_2, f"GET /parques hizo {con_2} consultas con 2 parques y {con_12} con 12"
