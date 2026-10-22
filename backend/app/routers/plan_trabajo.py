"""Plan de trabajo: responsable y fecha comprometida por criterio (RF-09)."""

import uuid
from typing import Annotated

from fastapi import APIRouter, Query, Response
from sqlalchemy import select

from app import esquemas as e
from app.comun import DB, Actor, Paginacion, clave_natural, ordenar_lista, paginar, registrar_bitacora
from app.errores import ErrorAPI
from app.modelos import Criterio, CriterioParque, Expediente, Parque, RenglonPlanTrabajo, Usuario
from app.servicios import es_atrasado, exigir_expediente, filas_criterios, obtener_parque, tipo_vigente

router = APIRouter(tags=["Plan de trabajo"])

RESPONSABLE_NO_APPI = ("responsable_no_appi", "El responsable debe ser un usuario APPI de este parque")


def _validar_responsable(db, responsable_id: uuid.UUID, parque: Parque) -> Usuario:
    u = db.get(Usuario, responsable_id)
    if u is None:
        raise ErrorAPI(422, "usuario_no_existe", "El usuario indicado no existe")
    if u.rol != "appi" or u.parque_id != parque.id or u.estado == "inactivo":
        raise ErrorAPI(422, *RESPONSABLE_NO_APPI)
    return u


def _filas(db, exp: Expediente, renglon_id: uuid.UUID | None = None):
    q = (
        select(RenglonPlanTrabajo, CriterioParque, Criterio.clave, Usuario.nombre)
        .join(CriterioParque, CriterioParque.id == RenglonPlanTrabajo.criterio_parque_id)
        .join(Criterio, Criterio.id == CriterioParque.criterio_id)
        .join(Usuario, Usuario.id == RenglonPlanTrabajo.responsable_id)
        .where(RenglonPlanTrabajo.expediente_id == exp.id)
    )
    if renglon_id is not None:
        q = q.where(RenglonPlanTrabajo.id == renglon_id)
    return db.execute(q).all()


def _a_esquema(r: RenglonPlanTrabajo, cp: CriterioParque, nombre_responsable: str, parque_id) -> e.RenglonPlanTrabajo:
    return e.RenglonPlanTrabajo(
        id=r.id,
        parque_id=parque_id,
        criterio_id=cp.criterio_id,
        responsable_id=r.responsable_id,
        responsable_nombre=nombre_responsable,
        fecha_comprometida=r.fecha_comprometida,
        estado_criterio=cp.estado_calificacion,
        atrasado=es_atrasado(cp.estado_calificacion, r),
        fecha_marca_atraso=r.fecha_marca_atraso,
    )


def _renglon(db, parque: Parque, renglon_id: uuid.UUID):
    exp = exigir_expediente(db, parque)
    filas = _filas(db, exp, renglon_id)
    if not filas:
        raise ErrorAPI(404, "no_encontrado", "No existe el renglón del plan de trabajo solicitado")
    return exp, filas[0]


@router.get("/parques/{parqueId}/plan-trabajo", response_model=e.Pagina[e.RenglonPlanTrabajo])
def listar_plan_trabajo(
    parqueId: uuid.UUID, db: DB, p: Paginacion, atrasado: Annotated[bool | None, Query()] = None
):
    parque = obtener_parque(db, parqueId)
    exp = exigir_expediente(db, parque)
    filas = _filas(db, exp)
    items = [(_a_esquema(r, cp, nombre, parque.id), clave) for r, cp, clave, nombre in filas]
    if atrasado is not None:
        items = [x for x in items if x[0].atrasado == atrasado]
    items = ordenar_lista(
        items,
        p.orden,
        {"fechaComprometida": lambda x: x[0].fecha_comprometida, "clave": lambda x: clave_natural(x[1])},
        "fechaComprometida",
        lambda x: x[0].id,
    )
    return paginar([x[0] for x in items], p)


@router.post("/parques/{parqueId}/plan-trabajo", response_model=e.RenglonPlanTrabajo, status_code=201)
def crear_renglon_plan_trabajo(
    parqueId: uuid.UUID, cuerpo: e.RenglonPlanTrabajoCreate, db: DB, actor: Actor, response: Response
):
    parque = obtener_parque(db, parqueId)
    exp = exigir_expediente(db, parque)
    filas = filas_criterios(db, exp, tipo_vigente(db, parque.id), criterio_id=cuerpo.criterio_id)
    if not filas:
        raise ErrorAPI(422, "criterio_no_existe", "El criterio indicado no existe en el catálogo del parque")
    fila = filas[0]
    if fila.marca not in ("O", "R"):
        raise ErrorAPI(422, "criterio_no_aplica", "Este criterio no aplica al tipo de PI del parque")
    # [C-07] RF-09 y el contrato hablan de criterios pendientes; el v0 aceptaba un renglón sobre un criterio ya
    # cumplido, que nunca podría marcarse atrasado.
    if fila.cp.estado_calificacion == "cumplido":
        raise ErrorAPI(409, "criterio_cumplido", "El criterio ya está cumplido; no requiere plan de trabajo")
    responsable = _validar_responsable(db, cuerpo.responsable_id, parque)
    if db.scalar(select(RenglonPlanTrabajo.id).where(RenglonPlanTrabajo.criterio_parque_id == fila.cp.id)):
        raise ErrorAPI(409, "renglon_duplicado", "El criterio ya tiene un renglón en el plan de trabajo del parque")

    r = RenglonPlanTrabajo(
        expediente_id=exp.id,
        criterio_parque_id=fila.cp.id,
        responsable_id=responsable.id,
        fecha_comprometida=cuerpo.fecha_comprometida,
    )
    db.add(r)
    db.flush()
    registrar_bitacora(
        db, actor, "crear_renglon_plan_trabajo", recurso_tipo="renglon_plan_trabajo", recurso_id=r.id,
        parque_id=parque.id,
    )
    db.commit()
    response.headers["Location"] = f"/api/parques/{parque.id}/plan-trabajo/{r.id}"
    return _a_esquema(r, fila.cp, responsable.nombre, parque.id)


@router.get("/parques/{parqueId}/plan-trabajo/{renglonId}", response_model=e.RenglonPlanTrabajo)
def obtener_renglon_plan_trabajo(parqueId: uuid.UUID, renglonId: uuid.UUID, db: DB):
    parque = obtener_parque(db, parqueId)
    _, (r, cp, _, nombre) = _renglon(db, parque, renglonId)
    return _a_esquema(r, cp, nombre, parque.id)


@router.patch("/parques/{parqueId}/plan-trabajo/{renglonId}", response_model=e.RenglonPlanTrabajo)
def actualizar_renglon_plan_trabajo(
    parqueId: uuid.UUID, renglonId: uuid.UUID, cuerpo: e.RenglonPlanTrabajoUpdate, db: DB, actor: Actor
):
    parque = obtener_parque(db, parqueId)
    _, (r, cp, _, nombre) = _renglon(db, parque, renglonId)
    campos = cuerpo.model_fields_set
    if not campos:
        raise ErrorAPI(422, "datos_invalidos", "Indique el responsable o la fecha comprometida")
    if any(getattr(cuerpo, c) is None for c in campos):
        raise ErrorAPI(422, "datos_invalidos", "Los campos del renglón no admiten nulo")
    if cuerpo.responsable_id is not None:
        nombre = _validar_responsable(db, cuerpo.responsable_id, parque).nombre
        r.responsable_id = cuerpo.responsable_id
    if cuerpo.fecha_comprometida is not None and cuerpo.fecha_comprometida != r.fecha_comprometida:
        r.fecha_comprometida = cuerpo.fecha_comprometida
        r.fecha_marca_atraso = None  # la revisión diaria vuelve a evaluar la nueva fecha
    registrar_bitacora(
        db, actor, "actualizar_renglon_plan_trabajo", recurso_tipo="renglon_plan_trabajo", recurso_id=r.id,
        parque_id=parque.id,
    )
    db.commit()
    return _a_esquema(r, cp, nombre, parque.id)


@router.delete("/parques/{parqueId}/plan-trabajo/{renglonId}", status_code=204)
def eliminar_renglon_plan_trabajo(parqueId: uuid.UUID, renglonId: uuid.UUID, db: DB, actor: Actor):
    parque = obtener_parque(db, parqueId)
    _, (r, cp, clave, _) = _renglon(db, parque, renglonId)
    db.delete(r)
    registrar_bitacora(
        db, actor, "eliminar_renglon_plan_trabajo", recurso_tipo="renglon_plan_trabajo", recurso_id=r.id,
        parque_id=parque.id, detalle=f"criterio {clave}",
    )
    db.commit()
    return Response(status_code=204)
