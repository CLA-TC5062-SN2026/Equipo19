"""Fases del expediente: consulta, cierre y avance por excepción (RF-32)."""

import uuid
from typing import Annotated

from fastapi import APIRouter, Path
from sqlalchemy import select

from app import esquemas as e
from app.comun import DB, Actor, ahora, registrar_bitacora
from app.errores import ErrorAPI
from app.modelos import CatalogoFase, Expediente, FaseExpediente
from app.servicios import exigir_expediente, fase_a_esquema, fases_a_esquema, obtener_parque

router = APIRouter(tags=["Fases"])


def _fases(db, exp: Expediente) -> list[tuple[CatalogoFase, FaseExpediente]]:
    return [
        tuple(f)
        for f in db.execute(
            select(CatalogoFase, FaseExpediente)
            .join(FaseExpediente, FaseExpediente.fase == CatalogoFase.clave)
            .where(FaseExpediente.expediente_id == exp.id)
            .order_by(CatalogoFase.orden)
        ).all()
    ]


def _iniciar_siguiente(db, fases, indice_actual: int, momento) -> None:
    if indice_actual + 1 < len(fases):
        _, siguiente = fases[indice_actual + 1]
        siguiente.estado = "en_proceso"
        siguiente.fecha_inicio = momento


@router.get("/parques/{parqueId}/fases", response_model=list[e.FaseExpediente])
def listar_fases_parque(parqueId: uuid.UUID, db: DB):
    parque = obtener_parque(db, parqueId)
    return fases_a_esquema(db, exigir_expediente(db, parque))


@router.post("/parques/{parqueId}/fases/{fase}/cierre", response_model=e.FaseExpediente)
def cerrar_fase(parqueId: uuid.UUID, fase: Annotated[e.Fase, Path()], db: DB, actor: Actor):
    parque = obtener_parque(db, parqueId)
    exp = exigir_expediente(db, parque)
    fases = _fases(db, exp)
    indice = next((i for i, (cat, _) in enumerate(fases) if cat.clave == fase), None)
    if indice is None or fases[indice][1].estado != "en_proceso":
        raise ErrorAPI(409, "fase_no_actual", "Solo se puede cerrar la fase en curso")
    cat, actual = fases[indice]
    momento = ahora()
    actual.estado = "completada"
    actual.fecha_cierre = momento
    actual.cerrada_por = actor.id
    db.flush()  # libera el índice único de fase en proceso
    _iniciar_siguiente(db, fases, indice, momento)
    registrar_bitacora(
        db, actor, "cerrar_fase", recurso_tipo="fase_expediente", recurso_id=f"{exp.id}:{fase}", parque_id=parque.id
    )
    db.commit()
    return fase_a_esquema(cat, actual)


@router.post("/parques/{parqueId}/avances-fase", response_model=list[e.FaseExpediente], status_code=201)
def crear_avance_fase(parqueId: uuid.UUID, cuerpo: e.AvanceFaseCreate, db: DB, actor: Actor):
    parque = obtener_parque(db, parqueId)
    exp = exigir_expediente(db, parque)
    if not cuerpo.motivo or not cuerpo.motivo.strip():
        raise ErrorAPI(
            422, "motivo_requerido", "Para avanzar sin cerrar la fase actual registre el motivo de la excepción"
        )
    fases = _fases(db, exp)
    indice = next((i for i, (_, fe) in enumerate(fases) if fe.estado == "en_proceso"), None)
    if indice is None or indice + 1 >= len(fases) or fases[indice + 1][0].clave != cuerpo.fase_destino:
        raise ErrorAPI(409, "fase_destino_invalida", "La fase destino no es la siguiente de la secuencia")
    cat, actual = fases[indice]
    momento = ahora()
    actual.estado = "avanzada_por_excepcion"
    actual.motivo_excepcion = cuerpo.motivo.strip()
    actual.fecha_cierre = momento
    actual.cerrada_por = actor.id
    db.flush()
    _iniciar_siguiente(db, fases, indice, momento)
    registrar_bitacora(
        db, actor, "avanzar_fase_por_excepcion", recurso_tipo="fase_expediente",
        recurso_id=f"{exp.id}:{cat.clave}", parque_id=parque.id,
        detalle=f"{cat.clave} -> {cuerpo.fase_destino}: {cuerpo.motivo.strip()}",
    )
    db.commit()
    return fases_a_esquema(db, exp)
