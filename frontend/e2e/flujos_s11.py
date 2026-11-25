"""Prueba de punta a punta de los flujos del video (S11): login, error 401, tablero, alta con error 422, edición,
baja con y sin motivo, filtro de dados de baja, aislamiento de la APPI, recarga y servidor caído.

Requisitos: backend en :8000 con `app.semilla` y `app.demo_s11` cargados, frontend en :5173 y
`pip install playwright && playwright install chromium`. Modifica datos (da de alta y de baja un parque).

    python e2e/flujos_s11.py            # E2E_CAPTURAS=docs/img guarda capturas de cada paso
"""
import os
import re

from playwright.sync_api import expect, sync_playwright

BASE = os.environ.get("E2E_URL", "http://localhost:5173")
API = os.environ.get("E2E_API", "http://localhost:8000")
COORD = os.environ.get("E2E_COORD_CORREO", os.environ.get("SEMILLA_CORREO", "coordinacion@ampip.local"))
COORD_PASS = os.environ.get("E2E_COORD_CONTRASENA", os.environ.get("SEMILLA_CONTRASENA", ""))
DEMO_PASS = os.environ.get("DEMO_CONTRASENA", "Demo-SGPIS-2026")
IMG = os.environ.get("E2E_CAPTURAS")
consola = []

def shot(page, nombre):
    if IMG:
        page.screenshot(path=f"{IMG}/{nombre}.png", full_page=True)

with sync_playwright() as pw:
    b = pw.chromium.launch()
    ctx = b.new_context(viewport={"width": 1366, "height": 860}, locale="es-MX")
    page = ctx.new_page()
    page.on("console", lambda m: consola.append(f"{m.type}: {m.text}") if m.type in ("error", "warning") else None)
    page.on("pageerror", lambda e: consola.append(f"pageerror: {e}"))

    # 1. Ruta protegida sin sesión -> login
    page.goto(BASE + "/")
    expect(page).to_have_url(re.compile("/login$"))
    shot(page, "01_login")

    # 2. Error manejado: contraseña incorrecta (401)
    page.fill("#correo", COORD)
    page.fill("#contrasena", "contrasena-equivocada")
    page.click("button[type=submit]")
    expect(page.get_by_role("alert")).to_contain_text("Correo o contraseña incorrectos")
    shot(page, "02_login_error")

    # 3. Login correcto
    page.fill("#contrasena", COORD_PASS)
    page.click("button[type=submit]")
    expect(page.get_by_role("heading", name="Parques del programa")).to_be_visible()
    expect(page.get_by_text("Parque Industrial Cumbres del Norte")).to_be_visible()
    page.wait_for_timeout(1200)
    shot(page, "03_tablero")

    # 4. Filtro por región
    page.select_option("#f-region", "MX-NLE")
    page.wait_for_timeout(800)
    n = page.locator("tbody tr").count()
    print("parques en NLE:", n)
    page.select_option("#f-region", "")
    page.wait_for_timeout(800)

    # 5. Detalle
    page.get_by_role("link", name="Parque Industrial Ramos Arizpe Sur").click()
    expect(page.get_by_role("heading", name=re.compile("Ramos Arizpe"))).to_be_visible()
    expect(page.get_by_text("Obligatorios cumplidos").first).to_be_visible()
    page.wait_for_timeout(600)
    shot(page, "04_detalle")
    page.get_by_role("link", name="← Parques").click()

    # 6. Alta con error de validación del backend (sin tipo de PI)
    page.get_by_role("link", name="Dar de alta parque").click()
    page.fill("#nombre", "Parque Industrial Apodaca Oriente")
    page.fill("#desarrollador", "Desarrollos Industriales del Norte")
    page.select_option("#region", "MX-NLE")
    page.select_option("#generacionId", label="2026 (catálogo catalogo-sintetico-v1)")
    page.click("button[type=submit]")
    expect(page.get_by_role("alert")).to_contain_text("Debe seleccionar un tipo de PI válido")
    expect(page.locator("#tipoPI")).to_have_attribute("aria-invalid", "true")
    shot(page, "05_alta_error")
    page.select_option("#tipoPI", "operacion_cerrado")
    page.click("button[type=submit]")
    expect(page.get_by_text("Se dio de alta Parque Industrial Apodaca Oriente.")).to_be_visible()
    expect(page.get_by_text("En curso").first).to_be_visible()
    shot(page, "06_alta_ok")

    # 7. Editar
    page.get_by_role("button", name="Editar datos").click()
    page.fill("#e-nombre", "Parque Industrial Apodaca Oriente II")
    page.fill("#e-actualizacion", "2026-10-01")
    page.get_by_role("button", name="Guardar cambios").click()
    expect(page.get_by_text("Se guardaron los cambios del parque.")).to_be_visible()
    expect(page.get_by_role("heading", name=re.compile("Apodaca Oriente II"))).to_be_visible()
    expect(page.get_by_text("Vencida")).to_be_visible()
    shot(page, "07_editado")

    # 8. Baja sin motivo (422) y con motivo
    page.get_by_role("button", name="Dar de baja").click()
    page.get_by_role("button", name="Confirmar baja").click()
    expect(page.locator("#motivo-error")).to_contain_text("motivo")
    shot(page, "08_baja_error")
    page.fill("#motivo", "Alta duplicada por error de captura")
    page.get_by_role("button", name="Confirmar baja").click()
    expect(page.get_by_text("quedó dado de baja")).to_be_visible()
    expect(page.get_by_text("Dado de baja").first).to_be_visible()
    shot(page, "09_baja_ok")

    # 9. Ya no aparece en activos; sí en "Dados de baja"
    page.get_by_role("link", name="← Parques").click()
    page.wait_for_timeout(800)
    assert page.get_by_text("Apodaca Oriente II").count() == 0
    page.select_option("#f-estado", "inactivo")
    expect(page.get_by_text("Parque Industrial Apodaca Oriente II")).to_be_visible()

    # 10. Cerrar sesión, entrar como APPI: solo su parque, sin botón de alta
    page.get_by_role("button", name="Cerrar sesión").click()
    expect(page).to_have_url(re.compile("/login$"))
    page.fill("#correo", "seguridad@cumbres-del-norte.demo.mx")
    page.fill("#contrasena", DEMO_PASS)
    page.click("button[type=submit]")
    expect(page.get_by_role("heading", name="Parques del programa")).to_be_visible()
    page.wait_for_timeout(1000)
    print("filas APPI:", page.locator("tbody tr").count())
    assert page.get_by_role("link", name="Dar de alta parque").count() == 0
    shot(page, "10_appi")

    # 11. Recargar conserva sesión
    page.reload()
    expect(page.get_by_role("heading", name="Parques del programa")).to_be_visible()

    # 12. Backend caído: mensaje de sin conexión (se simula bloqueando la red hacia :8000)
    page.route(f"{API}/**", lambda r: r.abort())
    page.select_option("#f-region", "MX-NLE")
    expect(page.get_by_role("alert")).to_contain_text("No hay conexión")
    page.unroute(f"{API}/**")
    b.close()

print("CONSOLA:", *consola, sep="\n  ")
print("OK")
