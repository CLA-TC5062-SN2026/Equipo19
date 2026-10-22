"""Asignación y reasignación del consultor de un parque (RF-10)."""

import uuid

from fastapi import APIRouter, Response
from sqlalchemy import select

from app import esquemas as e
from app.comun import DB, Actor, ahora, registrar_bitacora
from app.errores import ErrorAPI
from app.modelos import AsignacionConsultor, Expediente, Usuario
from app.servicios import exigir_expediente, obtener_parque

router = APIRouter(tags=["Asignaciones"])


def _asignacion_a_esquema(db, a: AsignacionConsultor, exp: Expediente) -> e.AsignacionConsultor:
    consultor = db.get(Usuario, a.consultor_id)
    return e.AsignacionConsultor(
        id=a.id,
        parque_id=exp.parque_id,
        generacion_id=exp.generacion_id,
        consultor_id=a.consultor_id,
        consultor_nombre=consultor.nombre if consultor else "",
        vigente_desde=a.vigente_desde,
        vigente_hasta=a.vigente_hasta,
        vigente=a.vigente_hasta is None,
    )


@router.get("/parques/{parqueId}/asignaciones-consultor", response_model=list[e.AsignacionConsultor])
def listar_asignaciones_consultor(parqueId: uuid.UUID, db: DB):
    obtener_parque(db, parqueId)
    filas = db.execute(
        select(AsignacionConsultor, Expediente)
        .join(Expediente, Expediente.id == AsignacionConsultor.expediente_id)
        .where(Expediente.parque_id == parqueId)
        .order_by(AsignacionConsultor.vigente_desde.desc(), AsignacionConsultor.id)
    ).all()
    return [_asignacion_a_esquema(db, a, exp) for a, exp in filas]


@router.post("/parques/{parqueId}/asignaciones-consultor", response_model=e.AsignacionConsultor, status_code=201)
def crear_asignacion_consultor(
    parqueId: uuid.UUID, cuerpo: e.AsignacionConsultorCreate, db: DB, actor: Actor, response: Response
):
    parque = obtener_parque(db, parqueId)
    exp = exigir_expediente(db, parque)
    consultor = db.get(Usuario, cuerpo.consultor_id)
    if consultor is None:
        raise ErrorAPI(422, "consultor_no_existe", "El consultor indicado no existe")
    if consultor.rol != "consultor" or consultor.estado == "inactivo":
        raise ErrorAPI(422, "usuario_no_es_consultor", "El usuario indicado no es un consultor activo")
    if consultor.parque_id == parque.id:
        raise ErrorAPI(422, "roles_incompatibles", "Un usuario no puede ser APPI y Consultor del mismo parque")

    vigente = db.scalars(
        select(AsignacionConsultor).where(
            AsignacionConsultor.expediente_id == exp.id, AsignacionConsultor.vigente_hasta.is_(None)
        )
    ).first()
    if vigente is not None and vigente.consultor_id == consultor.id:
        raise ErrorAPI(409, "consultor_ya_asignado", "El consultor indicado ya es el asignado vigente del parque")

    momento = ahora()
    if vigente is not None:
        vigente.vigente_hasta = momento
        db.flush()  # libera el índice único de asignación vigente
    nueva = AsignacionConsultor(expediente_id=exp.id, consultor_id=consultor.id, vigente_desde=momento)
    db.add(nueva)
    db.flush()
    registrar_bitacora(
        db, actor, "asignar_consultor", recurso_tipo="asignacion_consultor", recurso_id=nueva.id,
        parque_id=parque.id,
        detalle=f"anterior={vigente.consultor_id if vigente else '-'}, nuevo={consultor.id}",
    )
    db.commit()
    response.headers["Location"] = f"/api/parques/{parque.id}/asignaciones-consultor/{nueva.id}"
    return _asignacion_a_esquema(db, nueva, exp)


@router.get("/parques/{parqueId}/asignaciones-consultor/{asignacionId}", response_model=e.AsignacionConsultor)
def obtener_asignacion_consultor(parqueId: uuid.UUID, asignacionId: uuid.UUID, db: DB):
    obtener_parque(db, parqueId)
    fila = db.execute(
        select(AsignacionConsultor, Expediente)
        .join(Expediente, Expediente.id == AsignacionConsultor.expediente_id)
        .where(AsignacionConsultor.id == asignacionId, Expediente.parque_id == parqueId)
    ).first()
    if fila is None:
        raise ErrorAPI(404, "no_encontrado", "No existe la asignación solicitada")
    return _asignacion_a_esquema(db, *fila)
