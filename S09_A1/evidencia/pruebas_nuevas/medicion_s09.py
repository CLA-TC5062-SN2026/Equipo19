"""S09_A1: medición de GET /parques con 10, 41 y 80 parques (RNF-10). No forma parte de la suite (el nombre no
empieza con test_); se corre a mano:  uv run pytest tests/medicion_s09.py -s -q
Imprime, para cada tamaño, las sentencias SQL que ejecuta una llamada y la mediana de 21 llamadas en milisegundos."""

import statistics
import time

from sqlalchemy import event

from tests.ayudas import cargar_catalogo, crear_generacion, crear_parque


def test_medicion_listado_parques(cliente):
    from app.db import engine

    v = cargar_catalogo(cliente)
    g = crear_generacion(cliente, v["id"])
    creados = 0
    print("\nparques | sentencias SQL | mediana ms (21 llamadas)")
    for meta in (10, 41, 80):
        while creados < meta:
            crear_parque(cliente, g["id"], nombre=f"Parque {creados:03d}")
            creados += 1
        cuenta = 0

        def contar(*_):
            nonlocal cuenta
            cuenta += 1

        event.listen(engine, "before_cursor_execute", contar)
        r = cliente.get("/api/parques", params={"tamanoPagina": 100})
        event.remove(engine, "before_cursor_execute", contar)
        assert r.json()["total"] == meta
        tiempos = []
        for _ in range(21):
            inicio = time.perf_counter()
            cliente.get("/api/parques", params={"tamanoPagina": 100})
            tiempos.append((time.perf_counter() - inicio) * 1000)
        print(f"{meta:7d} | {cuenta:14d} | {statistics.median(tiempos):10.1f}")
