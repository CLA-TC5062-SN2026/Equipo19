"""Control de acceso por rol y aislamiento entre parques (RNF-01, RNF-02, RF-35-AC-2).

Todo lo que decide quién puede ejecutar qué está en este módulo:

- `PERMISOS`: el mapa ruta -> perfiles autorizados. Es la única fuente; si una ruta protegida no aparece aquí la
  API no arranca (`verificar_mapa`).
- `autorizar`: dependencia que `main.py` aplica a todos los routers protegidos. Exige token válido (401 si no) y
  después comprueba el perfil contra el mapa; si no pasa, registra el intento en la bitácora con resultado
  "denegado" y responde 403 con el schema `Error`.
- `parques_visibles` y `exigir_criterio_visible`: las dos reglas que dependen del dato y no solo de la ruta
  (listado de parques filtrado por rol y criterio del catálogo restringido a los aplicables del parque).

El rol, el parque de la APPI, el desarrollador del gerente y las asignaciones del consultor se leen de la base en
cada solicitud, nunca del token: una reasignación o una baja retira el acceso en la solicitud siguiente.
"""

import logging
import uuid
from collections.abc import Iterable

from fastapi import Request
from fastapi.routing import APIRoute
from sqlalchemy import select

from app.comun import DB, registrar_bitacora
from app.errores import ErrorAPI, no_encontrado
from app.modelos import (
    AsignacionConsultor,
    Criterio,
    Estandar,
    Expediente,
    Generacion,
    MarcaPorTipo,
    Parque,
    SesionComite,
    Subestandar,
    Usuario,
)
from app.seguridad import UsuarioAutenticado
from app.servicios import expediente_actual, tipo_vigente

log = logging.getLogger("sgpis.permisos")

# ------------------------------------------------------------------ perfiles
# Perfiles globales: basta el rol.
COORDINACION = "coordinacion_ampip"
DIRECTOR = "director_general_ampip"
APPI = "appi"
CONSULTOR = "consultor"
GERENTE = "gerente_corporativo"
# administrador_tecnico no aparece en el mapa: no tiene acceso a ninguna ruta de negocio (RF-03, RNF-02).

# Perfiles relativos a un parque: el rol más una relación vigente con el `parqueId` de la ruta.
APPI_DEL_PARQUE = "appi_del_parque"                    # usuario.parque_id = parqueId
CONSULTOR_ASIGNADO = "consultor_asignado"              # asignación vigente en el parque
CONSULTOR_COMITE = "consultor_comite"                  # sesión de comité abierta del parque (solo lectura, RF-13)
GERENTE_DEL_DESARROLLADOR = "gerente_del_desarrollador"  # parque.desarrollador_id = usuario.desarrollador_id

# Perfil relativo a un usuario: el `usuarioId` de la ruta es el propio usuario autenticado.
EL_PROPIO_USUARIO = "el_propio_usuario"

PERFILES_DE_PARQUE = frozenset({APPI_DEL_PARQUE, CONSULTOR_ASIGNADO, CONSULTOR_COMITE, GERENTE_DEL_DESARROLLADOR})

# Grupos que se repiten en el mapa.
SOLO_COORDINACION = frozenset({COORDINACION})
LECTURA_EXPEDIENTE = frozenset({
    COORDINACION, DIRECTOR, APPI_DEL_PARQUE, CONSULTOR_ASIGNADO, CONSULTOR_COMITE, GERENTE_DEL_DESARROLLADOR,
})
LECTURA_PROGRAMA = frozenset({COORDINACION, DIRECTOR, APPI, CONSULTOR, GERENTE})
# [P-01] El gerente corporativo solo consulta el avance de sus parques (2.3 y RF-23 del SRS de equipo): ficha del
# parque, cumplimiento y fases. El v0 le abría todo el expediente (autoevaluaciones con comentarios, plan de trabajo
# con responsables, asignaciones, historial), que es más de lo que el SRS le da.
LECTURA_DETALLE = LECTURA_EXPEDIENTE - {GERENTE_DEL_DESARROLLADOR}

# ------------------------------------------------------------------ mapa de permisos
# Llave: (método, plantilla de la ruta sin el prefijo /api), igual que en openapi_equipo.yaml.
# Las rutas con `security: []` del contrato (/salud, /auth/login, /auth/register) no llevan esta dependencia;
# /auth/me y /auth/logout solo exigen sesión (SesionAutenticada) y tampoco pasan por aquí.
PERMISOS: dict[tuple[str, str], frozenset[str]] = {
    # Catálogo (RF-01, RF-24, RF-25)
    ("GET", "/versiones-catalogo"): SOLO_COORDINACION,
    ("POST", "/versiones-catalogo"): SOLO_COORDINACION,
    ("GET", "/versiones-catalogo/{versionId}"): SOLO_COORDINACION,
    # APPI y consultor: además, solo criterios aplicables a sus parques (exigir_criterio_visible).
    ("GET", "/criterios/{criterioId}"): frozenset({COORDINACION, DIRECTOR, APPI, CONSULTOR}),
    ("PATCH", "/criterios/{criterioId}"): SOLO_COORDINACION,
    # Generaciones (RF-28)
    ("GET", "/generaciones"): LECTURA_PROGRAMA,
    ("POST", "/generaciones"): SOLO_COORDINACION,
    ("GET", "/generaciones/{generacionId}"): LECTURA_PROGRAMA,
    # Parques (RF-02, RF-11, RF-29, RF-30, RF-31). El listado se filtra por rol (parques_visibles).
    ("GET", "/parques"): LECTURA_PROGRAMA,
    ("POST", "/parques"): SOLO_COORDINACION,
    ("GET", "/parques/{parqueId}"): LECTURA_EXPEDIENTE,
    ("PATCH", "/parques/{parqueId}"): SOLO_COORDINACION,
    ("PUT", "/parques/{parqueId}/tipo-pi"): SOLO_COORDINACION,
    ("GET", "/parques/{parqueId}/tipos-pi"): LECTURA_DETALLE,
    ("POST", "/parques/{parqueId}/actualizaciones-anuales"): SOLO_COORDINACION,
    ("GET", "/parques/{parqueId}/actualizaciones-anuales/{actualizacionId}"): LECTURA_DETALLE,
    ("GET", "/parques/{parqueId}/historial"): LECTURA_DETALLE,
    # Usuarios (RF-03, RF-29, RF-34)
    ("GET", "/usuarios"): SOLO_COORDINACION,
    ("POST", "/usuarios"): SOLO_COORDINACION,
    ("GET", "/usuarios/{usuarioId}"): frozenset({COORDINACION, EL_PROPIO_USUARIO}),
    ("PATCH", "/usuarios/{usuarioId}"): SOLO_COORDINACION,
    ("GET", "/parques/{parqueId}/usuarios"): SOLO_COORDINACION,
    ("PUT", "/parques/{parqueId}/contacto-principal"): SOLO_COORDINACION,
    # Asignaciones (RF-10)
    ("GET", "/parques/{parqueId}/asignaciones-consultor"): LECTURA_DETALLE,
    ("POST", "/parques/{parqueId}/asignaciones-consultor"): SOLO_COORDINACION,
    ("GET", "/parques/{parqueId}/asignaciones-consultor/{asignacionId}"): LECTURA_DETALLE,
    # Criterios del parque, autoevaluación y cumplimiento (RF-04, RF-07, RF-08)
    ("GET", "/parques/{parqueId}/criterios"): LECTURA_DETALLE,
    ("GET", "/parques/{parqueId}/criterios/{criterioId}"): LECTURA_DETALLE,
    ("GET", "/parques/{parqueId}/autoevaluaciones"): LECTURA_DETALLE,
    ("GET", "/parques/{parqueId}/autoevaluaciones/{criterioId}"): LECTURA_DETALLE,
    ("PUT", "/parques/{parqueId}/autoevaluaciones/{criterioId}"): frozenset({APPI_DEL_PARQUE}),
    ("GET", "/parques/{parqueId}/cumplimiento"): LECTURA_EXPEDIENTE,
    # Plan de trabajo (RF-09)
    ("GET", "/parques/{parqueId}/plan-trabajo"): LECTURA_DETALLE,
    ("POST", "/parques/{parqueId}/plan-trabajo"): frozenset({CONSULTOR_ASIGNADO}),
    ("GET", "/parques/{parqueId}/plan-trabajo/{renglonId}"): LECTURA_DETALLE,
    ("PATCH", "/parques/{parqueId}/plan-trabajo/{renglonId}"): frozenset({CONSULTOR_ASIGNADO}),
    ("DELETE", "/parques/{parqueId}/plan-trabajo/{renglonId}"): frozenset({CONSULTOR_ASIGNADO}),
    # Análisis de riesgos (RF-16, RNF-02): ni Coordinación ni consultor de comité.
    ("GET", "/parques/{parqueId}/revisiones-analisis-riesgos"): frozenset({APPI_DEL_PARQUE, CONSULTOR_ASIGNADO}),
    ("POST", "/parques/{parqueId}/revisiones-analisis-riesgos"): frozenset({CONSULTOR_ASIGNADO}),
    ("GET", "/parques/{parqueId}/revisiones-analisis-riesgos/{revisionId}"):
        frozenset({APPI_DEL_PARQUE, CONSULTOR_ASIGNADO}),
    # Fases (RF-32)
    ("GET", "/parques/{parqueId}/fases"): LECTURA_EXPEDIENTE,
    ("POST", "/parques/{parqueId}/fases/{fase}/cierre"): SOLO_COORDINACION,
    ("POST", "/parques/{parqueId}/avances-fase"): SOLO_COORDINACION,
    # Configuración (RF-06, RD-08) y bitácora (RF-35)
    ("GET", "/configuracion"): SOLO_COORDINACION,
    ("PATCH", "/configuracion"): SOLO_COORDINACION,
    ("GET", "/bitacora"): SOLO_COORDINACION,
}


# ------------------------------------------------------------------ relaciones con un parque
def _tiene_asignacion_vigente(db, usuario_id: uuid.UUID, parque_id: uuid.UUID) -> bool:
    return db.scalar(
        select(AsignacionConsultor.id)
        .join(Expediente, Expediente.id == AsignacionConsultor.expediente_id)
        .where(
            AsignacionConsultor.consultor_id == usuario_id,
            AsignacionConsultor.vigente_hasta.is_(None),
            Expediente.parque_id == parque_id,
        )
        .limit(1)
    ) is not None


def _tiene_comite_abierto(db, usuario_id: uuid.UUID, parque_id: uuid.UUID) -> bool:
    return db.scalar(
        select(SesionComite.id)
        .join(Expediente, Expediente.id == SesionComite.expediente_id)
        .where(
            SesionComite.consultor_comite_id == usuario_id,
            SesionComite.fecha_cierre.is_(None),
            Expediente.parque_id == parque_id,
        )
        .limit(1)
    ) is not None


def perfiles_en_parque(db, usuario: Usuario, parque: Parque) -> set[str]:
    """Perfiles relativos que el usuario tiene sobre el parque. Un parque dado de baja ya no da acceso a nadie
    por relación (contrato, PATCH /parques/{parqueId}: la baja retira de inmediato el acceso)."""
    if parque.estado == "inactivo":
        return set()
    perfiles: set[str] = set()
    if usuario.rol == APPI and usuario.parque_id == parque.id:
        perfiles.add(APPI_DEL_PARQUE)
    elif usuario.rol == CONSULTOR:
        if _tiene_asignacion_vigente(db, usuario.id, parque.id):
            perfiles.add(CONSULTOR_ASIGNADO)
        if _tiene_comite_abierto(db, usuario.id, parque.id):
            perfiles.add(CONSULTOR_COMITE)
    elif (
        usuario.rol == GERENTE
        and usuario.desarrollador_id is not None
        and parque.desarrollador_id == usuario.desarrollador_id
    ):
        perfiles.add(GERENTE_DEL_DESARROLLADOR)
    return perfiles


def parques_visibles(db, usuario: Usuario) -> set[uuid.UUID] | None:
    """Parques que el usuario puede ver en GET /parques; None = todos (Coordinación y Director General).
    Los parques inactivos quedan fuera para los perfiles con alcance por parque."""
    if usuario.rol in (COORDINACION, DIRECTOR):
        return None
    q = select(Parque.id).where(Parque.estado != "inactivo")
    if usuario.rol == APPI:
        q = q.where(Parque.id == usuario.parque_id)
    elif usuario.rol == CONSULTOR:
        q = q.where(
            Parque.id.in_(
                select(Expediente.parque_id)
                .join(AsignacionConsultor, AsignacionConsultor.expediente_id == Expediente.id)
                .where(AsignacionConsultor.consultor_id == usuario.id, AsignacionConsultor.vigente_hasta.is_(None))
            )
        )
    elif usuario.rol == GERENTE and usuario.desarrollador_id is not None:
        q = q.where(Parque.desarrollador_id == usuario.desarrollador_id)
    else:
        return set()
    return set(db.scalars(q))


# ------------------------------------------------------------------ denegación con bitácora
def denegar(db, request: Request, usuario: Usuario, motivo: str, parque_id: uuid.UUID | None = None) -> ErrorAPI:
    """Registra el intento con resultado "denegado" (RF-35-AC-2) y devuelve el 403 para lanzarlo."""
    db.rollback()  # nada pendiente de la solicitud debe confirmarse junto con el registro
    ruta = _plantilla(request) or request.url.path
    registrar_bitacora(
        db, usuario, "acceso_denegado",
        recurso_tipo="ruta", recurso_id=request.url.path[:100], parque_id=parque_id,
        detalle=f"{request.method} {ruta}: {motivo}", resultado="denegado",
    )
    db.commit()
    return ErrorAPI(403, "sin_permiso", "No tiene permiso para realizar esta operación")


def _plantilla(request: Request) -> str | None:
    # Según la versión de FastAPI, la ruta del scope trae o no el prefijo /api de include_router (ver errores.py).
    plantilla = getattr(request.scope.get("route"), "path_format", None)
    return plantilla.removeprefix("/api") if plantilla else None


def _uuid(valor: str | None) -> uuid.UUID | None:
    try:
        return uuid.UUID(str(valor))
    except ValueError:
        return None


# ------------------------------------------------------------------ dependencia
def autorizar(request: Request, usuario: UsuarioAutenticado, db: DB) -> Usuario:
    """401 sin sesión válida (lo resuelve UsuarioAutenticado); 403 si el perfil no está en el mapa para la ruta."""
    plantilla = _plantilla(request)
    permitidos = PERMISOS.get((request.method, plantilla or ""))
    if permitidos is None:  # no debería pasar: verificar_mapa lo impide al arrancar. Falla cerrado.
        log.error("Ruta sin entrada en PERMISOS: %s %s", request.method, plantilla)
        raise denegar(db, request, usuario, "ruta sin permisos definidos")

    if usuario.rol in permitidos:
        return usuario

    if EL_PROPIO_USUARIO in permitidos and _uuid(request.path_params.get("usuarioId")) == usuario.id:
        return usuario

    if permitidos & PERFILES_DE_PARQUE:
        parque_id = _uuid(request.path_params.get("parqueId"))
        if parque_id is None:
            raise no_encontrado("parque")  # un id mal formado no identifica ningún parque
        parque = db.get(Parque, parque_id)
        if parque is None:
            raise no_encontrado("parque")
        if perfiles_en_parque(db, usuario, parque) & permitidos:
            return usuario
        raise denegar(db, request, usuario, f"rol {usuario.rol} sin permiso sobre el parque", parque_id=parque.id)

    parque_id = _uuid(request.path_params.get("parqueId"))
    if parque_id is not None and db.get(Parque, parque_id) is None:
        parque_id = None  # la bitácora tiene FK a parque
    raise denegar(db, request, usuario, f"rol {usuario.rol} sin permiso para la operación", parque_id=parque_id)


# ------------------------------------------------------------------ regla de dato: criterio del catálogo
def exigir_criterio_visible(db, request: Request, usuario: Usuario, criterio: Criterio) -> bool:
    """GET /criterios/{criterioId}. Devuelve si el usuario ve las cuatro marcas O/R/NA.

    Coordinación AMPIP (y el Director General) ven el criterio completo. La APPI y el consultor solo ven criterios
    O o R del tipo de PI vigente de alguno de sus parques, en la versión de catálogo de su generación, y sin
    `marcas`; cualquier otro criterio responde 403.
    """
    if usuario.rol in (COORDINACION, DIRECTOR):
        return True
    visibles = parques_visibles(db, usuario) or set()
    if visibles:
        version_id = db.scalar(
            select(Estandar.version_catalogo_id)
            .join(Subestandar, Subestandar.estandar_id == Estandar.id)
            .where(Subestandar.id == criterio.subestandar_id)
        )
        for parque_id in visibles:
            exp = expediente_actual(db, parque_id)
            tipo = tipo_vigente(db, parque_id)
            if exp is None or tipo is None:
                continue
            if db.scalar(select(Generacion.version_catalogo_id).where(Generacion.id == exp.generacion_id)) != version_id:
                continue
            marca = db.scalar(
                select(MarcaPorTipo.marca).where(MarcaPorTipo.criterio_id == criterio.id, MarcaPorTipo.tipo_pi == tipo)
            )
            if marca in ("O", "R"):
                return False
    raise denegar(db, request, usuario, "criterio no aplicable a los parques del usuario")


# ------------------------------------------------------------------ verificación al arrancar
def verificar_mapa(rutas: Iterable[APIRoute], prefijo: str = "/api") -> None:
    """Cada ruta protegida tiene entrada en PERMISOS, cada entrada corresponde a una ruta, y los perfiles relativos
    solo aparecen en rutas que traen el parámetro que necesitan. Si algo no cuadra, la API no arranca."""
    vistas: set[tuple[str, str]] = set()
    problemas: list[str] = []
    for ruta in rutas:
        plantilla = ruta.path_format.removeprefix(prefijo)
        for metodo in ruta.methods:
            clave = (metodo, plantilla)
            vistas.add(clave)
            if clave not in PERMISOS:
                problemas.append(f"ruta protegida sin permisos: {metodo} {plantilla}")
    for (metodo, plantilla), perfiles in PERMISOS.items():
        if (metodo, plantilla) not in vistas:
            problemas.append(f"permiso de una ruta que no existe: {metodo} {plantilla}")
        if perfiles & PERFILES_DE_PARQUE and "{parqueId}" not in plantilla:
            problemas.append(f"perfil de parque en una ruta sin parqueId: {metodo} {plantilla}")
        if EL_PROPIO_USUARIO in perfiles and "{usuarioId}" not in plantilla:
            problemas.append(f"perfil el_propio_usuario en una ruta sin usuarioId: {metodo} {plantilla}")
    if problemas:
        raise RuntimeError("Mapa de permisos inconsistente:\n- " + "\n- ".join(problemas))
