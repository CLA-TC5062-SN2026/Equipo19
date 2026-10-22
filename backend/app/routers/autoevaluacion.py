"""Autoevaluación de diagnóstico del parque (RF-04)."""

import uuid
from typing import Annotated

from fastapi import APIRouter, Query, Response
from sqlalchemy import select

from app import esquemas as e
from app.comun import DB, Actor, Paginacion, ahora, clave_natural, ordenar_lista, paginar, registrar_bitacora
from app.errores import ErrorAPI
from app.modelos import Autoevaluacion, Criterio, Estandar, Expediente, Subestandar
from app.servicios import exigir_expediente, filas_criterios, generacion_de, obtener_parque, tipo_vigente, version_de

router = APIRouter(tags=["Autoevaluación"])


def _a_esquema(a: Autoevaluacion, exp: Expediente, version_nombre: str) -> e.Autoevaluacion:
    return e.Autoevaluacion(
        parque_id=exp.parque_id,
        generacion_id=exp.generacion_id,
        criterio_id=a.criterio_id,
        respuesta=a.respuesta,
        comentario=a.comentario,
        version_catalogo=version_nombre,
        registrado_por=a.registrado_por,
        fecha=a.fecha,
    )


@router.get("/parques/{parqueId}/autoevaluaciones", response_model=e.Pagina[e.Autoevaluacion])
def listar_autoevaluaciones(
    parqueId: uuid.UUID,
    db: DB,
    p: Paginacion,
    estandar: Annotated[int | None, Query(ge=1, le=10)] = None,
):
    parque = obtener_parque(db, parqueId)
    exp = exigir_expediente(db, parque)
    version = version_de(db, exp).nombre
    q = (
        select(Autoevaluacion, Criterio.clave)
        .join(Criterio, Criterio.id == Autoevaluacion.criterio_id)
        .join(Subestandar, Subestandar.id == Criterio.subestandar_id)
        .join(Estandar, Estandar.id == Subestandar.estandar_id)
        .where(Autoevaluacion.expediente_id == exp.id)
    )
    if estandar is not None:
        q = q.where(Estandar.numero == estandar)
    filas = [(a, clave) for a, clave in db.execute(q).all()]
    filas = ordenar_lista(
        filas,
        p.orden,
        {"clave": lambda f: clave_natural(f[1]), "fecha": lambda f: f[0].fecha},
        "clave",
        lambda f: f[0].id,
    )
    pagina = paginar(filas, p)
    pagina["items"] = [_a_esquema(a, exp, version) for a, _ in pagina["items"]]
    return pagina


@router.get("/parques/{parqueId}/autoevaluaciones/{criterioId}", response_model=e.Autoevaluacion)
def obtener_autoevaluacion(parqueId: uuid.UUID, criterioId: uuid.UUID, db: DB):
    parque = obtener_parque(db, parqueId)
    exp = exigir_expediente(db, parque)
    a = db.scalars(
        select(Autoevaluacion).where(Autoevaluacion.expediente_id == exp.id, Autoevaluacion.criterio_id == criterioId)
    ).first()
    if a is None:
        raise ErrorAPI(404, "no_encontrado", "No hay respuesta de autoevaluación para ese criterio")
    return _a_esquema(a, exp, version_de(db, exp).nombre)


@router.put("/parques/{parqueId}/autoevaluaciones/{criterioId}", response_model=e.Autoevaluacion,
            responses={201: {"model": e.Autoevaluacion, "description": "Respuesta creada."}})
def reemplazar_autoevaluacion(
    parqueId: uuid.UUID, criterioId: uuid.UUID, cuerpo: e.AutoevaluacionUpsert, db: DB, actor: Actor,
    response: Response,
):
    parque = obtener_parque(db, parqueId)
    exp = exigir_expediente(db, parque)
    filas = filas_criterios(db, exp, tipo_vigente(db, parque.id), criterio_id=criterioId)
    if not filas:
        raise ErrorAPI(404, "no_encontrado", "El criterio no existe en el catálogo de la generación del parque")
    if filas[0].marca not in ("O", "R"):
        raise ErrorAPI(422, "criterio_no_aplica", "Este criterio no aplica al tipo de PI del parque")

    a = db.scalars(
        select(Autoevaluacion).where(Autoevaluacion.expediente_id == exp.id, Autoevaluacion.criterio_id == criterioId)
    ).first()
    creada = a is None
    if creada:
        a = Autoevaluacion(expediente_id=exp.id, criterio_id=criterioId, respuesta=cuerpo.respuesta,
                           registrado_por=actor.id)
        db.add(a)
    a.respuesta = cuerpo.respuesta
    a.comentario = cuerpo.comentario
    a.fecha = ahora()
    a.registrado_por = actor.id
    db.flush()
    registrar_bitacora(
        db, actor, "registrar_autoevaluacion" if creada else "corregir_autoevaluacion",
        recurso_tipo="autoevaluacion", recurso_id=a.id, parque_id=parque.id,
    )
    db.commit()
    if creada:
        response.status_code = 201
        response.headers["Location"] = f"/api/parques/{parque.id}/autoevaluaciones/{criterioId}"
    return _a_esquema(a, exp, version_de(db, exp).nombre)
