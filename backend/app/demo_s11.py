"""Escenario de demostración para el video de S11 (solo desarrollo local).

Uso, después de `python -m app.semilla`:
    uv run python -m app.demo_s11

Crea la generación 2026 con ocho parques ficticios en distintas regiones y etapas del programa, una APPI por parque,
tres consultores asignados, un gerente corporativo y un parque histórico. Las fechas, fases, plan de trabajo y
atrasos se cargan con la API, igual que lo haría Coordinación o el consultor. Todas las cuentas comparten la
contraseña de DEMO_CONTRASENA (por omisión "Demo-SGPIS-2026").

Excepción declarada: la calificación de criterios (RF-27) todavía no tiene endpoint, así que el avance de cada parque
se escribe directo en criterio_parque y en su historial calificacion_criterio, con origen "consultor" y el consultor
asignado como autor. Sin eso todos los parques marcarían 0 % de cumplimiento. Es idempotente: si la generación 2026 ya
existe, no hace nada.

Nombres de parques, desarrolladores y personas son inventados; ningún dato viene de AMPIP.
"""

import logging
import os
import random
from datetime import date, timedelta

from fastapi.testclient import TestClient
from sqlalchemy import func, select, text

from app.alta_inicial import crear_invitacion
from app.db import SessionLocal
from app.main import app
from app.modelos import Generacion, Usuario, VersionCatalogo
from app.semilla import _ok

CONTRASENA = os.environ.get("DEMO_CONTRASENA", "Demo-SGPIS-2026")
HOY = date.today()

CONSULTORES = [
    ("mariana.trevino@consultores-demo.mx", "Mariana Treviño Garza"),
    ("hector.villarreal@consultores-demo.mx", "Héctor Villarreal Ochoa"),
    ("lucia.bermudez@consultores-demo.mx", "Lucía Bermúdez Salas"),
]

# nombre, desarrollador, tipo de PI, región, consultor, fases cerradas, % obligatorios cumplidos, atraso del plan,
# atraso de actualización anual
PARQUES = [
    ("Parque Industrial Cumbres del Norte", "Desarrollos Industriales del Norte", "operacion_cerrado", "MX-NLE",
     0, 5, 0.85, False, False),
    ("Parque Logístico Santa Catarina", "Desarrollos Industriales del Norte", "operacion_abierto", "MX-NLE",
     0, 4, 0.60, True, False),
    ("Parque Industrial Ramos Arizpe Sur", "Grupo Inmobiliario Coahuila", "operacion_cerrado", "MX-COA",
     1, 3, 0.45, True, True),
    ("Parque Industrial Bajío Oriente", "Grupo Inmobiliario Bajío", "construccion_cerrado", "MX-GUA",
     1, 2, 0.30, False, False),
    ("Parque Tecnológico El Marqués", "Grupo Inmobiliario Bajío", "operacion_cerrado", "MX-QUE",
     2, 4, 0.70, False, False),
    ("Parque Industrial Aguascalientes Poniente", "Naves y Parques del Centro", "operacion_abierto", "MX-AGU",
     2, 1, 0.15, True, False),
    ("Parque Industrial Logístico San Luis", "Naves y Parques del Centro", "construccion_abierto", "MX-SLP",
     0, 1, 0.10, False, True),
    ("Parque Industrial El Salto Norte", "Corporativo Industrial de Occidente", "operacion_cerrado", "MX-JAL",
     2, 6, 0.95, False, False),
]

GERENTE = ("gerente@dinorte-demo.mx", "Paola Garza Montemayor", "Desarrollos Industriales del Norte")
HISTORICO = ("Parque Industrial Toluca Uno", "MX-MEX", "2023-11-15", "2024-12-31")


def _correo_appi(nombre: str) -> str:
    base = nombre.lower().replace("parque industrial ", "").replace("parque logístico ", "").replace(
        "parque tecnológico ", "")
    base = (base.replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u")
            .replace(" ", "-"))
    return f"seguridad@{base}.demo.mx"


def _activar(c: TestClient, usuario_id: str) -> None:
    with SessionLocal() as db:
        usuario = db.get(Usuario, usuario_id)
        assert usuario is not None  # recién creado por POST /usuarios
        token = crear_invitacion(db, usuario)
        db.commit()
    _ok(c.post("/api/auth/register", headers={"Authorization": ""},
               json={"tokenInvitacion": token, "contrasena": CONTRASENA}))


def _usuario(c: TestClient, correo: str, nombre: str, rol: str, **extra) -> str:
    with SessionLocal() as db:
        u = db.scalars(select(Usuario).where(func.lower(Usuario.correo) == correo)).first()
    if u is not None:
        return str(u.id)
    uid = _ok(c.post("/api/usuarios", json={"correo": correo, "nombre": nombre, "rol": rol, **extra}))["id"]
    _activar(c, uid)
    return str(uid)


def _token(c: TestClient, correo: str) -> dict:
    t = _ok(c.post("/api/auth/login", headers={"Authorization": ""},
                   json={"correo": correo, "contrasena": CONTRASENA}))["token"]
    return {"Authorization": f"Bearer {t}"}


def _calificar(parque_id: str, consultor_id: str, criterios: list[dict], porcentaje: float, rnd: random.Random) -> None:
    """RF-27 sin endpoint: deja el estado que habría dejado el consultor y su historial."""
    obligatorios = [x for x in criterios if x["marca"] == "O"]
    recomendados = [x for x in criterios if x["marca"] == "R"]
    cumplidos = set(x["criterioId"] for x in rnd.sample(obligatorios, round(len(obligatorios) * porcentaje)))
    cumplidos |= set(x["criterioId"] for x in rnd.sample(recomendados, round(len(recomendados) * porcentaje * 0.6)))
    restantes = [x["criterioId"] for x in criterios if x["criterioId"] not in cumplidos]
    en_revision = set(restantes[: len(restantes) // 3])
    no_cumplidos = set(restantes[len(restantes) // 3: len(restantes) // 3 + 1]) if porcentaje > 0.3 else set()
    with SessionLocal() as db:
        for criterio_id in [*cumplidos, *en_revision, *no_cumplidos]:
            nuevo = ("cumplido" if criterio_id in cumplidos else
                     "no_cumplido" if criterio_id in no_cumplidos else "en_revision")
            fecha = HOY - timedelta(days=rnd.randint(3, 120))
            cp = db.execute(text(
                "UPDATE criterio_parque cp SET estado_calificacion = :e, fecha_ultimo_cambio = :f, calificado_por = :u "
                "FROM expediente x WHERE cp.expediente_id = x.id AND x.parque_id = :p AND cp.criterio_id = :c "
                "RETURNING cp.id"), {"e": nuevo, "f": fecha, "u": consultor_id, "p": parque_id, "c": criterio_id}
            ).scalar_one()
            if nuevo != "en_revision":
                db.execute(text(
                    "INSERT INTO calificacion_criterio (criterio_parque_id, estado_anterior, estado_nuevo, origen, "
                    "consultor_id, fecha) VALUES (:cp, 'en_revision', :e, 'consultor', :u, :f)"),
                    {"cp": cp, "e": nuevo, "u": consultor_id, "f": fecha})
        db.commit()


def main() -> None:  # pylint: disable=too-many-locals  # guion lineal de carga, más claro sin partirlo
    """Carga el escenario completo con la API; ver el docstring del módulo."""
    logging.getLogger("httpx").setLevel(logging.WARNING)
    rnd = random.Random(2026)
    c = TestClient(app)
    c.headers["Authorization"] = "Bearer " + _ok(c.post("/api/auth/login", json={
        "correo": os.environ["SEMILLA_CORREO"], "contrasena": os.environ["SEMILLA_CONTRASENA"]}))["token"]

    with SessionLocal() as db:
        if db.scalars(select(Generacion).where(Generacion.nombre == "2026")).first():
            print("La generación 2026 ya existe; el escenario de demostración ya está cargado.")
            return
        version = db.scalars(select(VersionCatalogo).where(VersionCatalogo.estado == "activa")).first()
        if version is None:
            raise SystemExit("Corre antes: uv run python -m app.semilla")
    # La cuenta de la semilla se llama "Coordinación AMPIP (semilla)"; para la demo se le pone nombre de persona.
    yo = _ok(c.get("/api/auth/me"))["usuario"]
    if yo["nombre"].endswith("(semilla)"):
        _ok(c.patch(f"/api/usuarios/{yo['id']}", json={"nombre": "Laura Méndez Ríos"}))
    generacion = _ok(c.post("/api/generaciones", json={
        "nombre": "2026", "fechaInicio": "2026-02-02", "versionCatalogoId": str(version.id)}))

    consultores = [_usuario(c, correo, nombre, "consultor") for correo, nombre in CONSULTORES]

    for nombre, desarrollador, tipo, region, i_cons, fases, pct, atraso_plan, atraso_anual in PARQUES:
        p = _ok(c.post("/api/parques", json={"tipoRegistro": "activo", "nombre": nombre, "desarrollador": desarrollador,
                                             "tipoPI": tipo, "region": region, "generacionId": generacion["id"]}))
        pid = p["id"]
        appi = _usuario(c, _correo_appi(nombre), f"Jefatura de seguridad {nombre.split()[-2]} {nombre.split()[-1]}",
                        "appi", parqueId=pid)
        _ok(c.put(f"/api/parques/{pid}/contacto-principal", json={"usuarioId": appi}))
        _ok(c.post(f"/api/parques/{pid}/asignaciones-consultor", json={"consultorId": consultores[i_cons]}))

        fases_parque = _ok(c.get(f"/api/parques/{pid}/fases"))
        for fase in fases_parque[:fases]:
            _ok(c.post(f"/api/parques/{pid}/fases/{fase['fase']}/cierre"))

        _ok(c.patch(f"/api/parques/{pid}", json={
            "fechaTerminoPrograma": "2027-06-30",
            "fechaProximaActualizacion": str(HOY - timedelta(days=20) if atraso_anual else HOY + timedelta(days=150)),
        }))

        criterios = _ok(c.get(f"/api/parques/{pid}/criterios", params={"tamanoPagina": 100}))["items"]
        _calificar(pid, consultores[i_cons], criterios, pct, rnd)

        h_cons = _token(c, CONSULTORES[i_cons][0])
        pendientes = [x for x in _ok(c.get(f"/api/parques/{pid}/criterios", params={"tamanoPagina": 100}))["items"]
                      if x["estadoCalificacion"] in ("pendiente", "no_cumplido") and x["marca"] == "O"]
        for k, x in enumerate(pendientes[:3]):
            vence = HOY - timedelta(days=10 + k * 5) if (atraso_plan and k == 0) else HOY + timedelta(days=30 + 15 * k)
            _ok(c.post(f"/api/parques/{pid}/plan-trabajo", headers=h_cons, json={
                "criterioId": x["criterioId"], "responsableId": appi, "fechaComprometida": str(vence)}))
        print(f"{nombre}: {fases} fases cerradas, {round(pct * 100)} % objetivo de obligatorios")

    nombre, region, dictamen, termino = HISTORICO
    _ok(c.post("/api/parques", json={"tipoRegistro": "historico", "nombre": nombre, "region": region,
                                     "fechaUltimoDictamen": dictamen, "fechaTerminoPrograma": termino}))

    correo, nombre_g, desarrollador = GERENTE
    _usuario(c, correo, nombre_g, "gerente_corporativo", desarrollador=desarrollador)

    print("\nCuentas de demostración (contraseña", CONTRASENA + "):")
    print("  Coordinación AMPIP:", os.environ["SEMILLA_CORREO"], "(contraseña SEMILLA_CONTRASENA)")
    print("  Consultor:         ", CONSULTORES[0][0])
    print("  APPI:              ", _correo_appi(PARQUES[0][0]))
    print("  Gerente corporativo:", correo)


if __name__ == "__main__":
    main()
