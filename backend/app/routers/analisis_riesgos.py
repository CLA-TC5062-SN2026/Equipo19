"""Revisiones del análisis de riesgos (RF-16). El documento opcional queda fuera de esta entrega."""

import uuid

from fastapi import APIRouter, Response
from sqlalchemy import select

from app import esquemas as e
from app.comun import DB, Actor, registrar_bitacora
from app.errores import ErrorAPI
from app.modelos import Expediente, RevisionAnalisisRiesgos
from app.servicios import exigir_expediente, generacion_de, obtener_parque

router = APIRouter(tags=["Análisis de riesgos"])


def _ciclo_actual(db, exp: Expediente) -> str:
    """El ciclo es la generación en curso del parque."""
    return generacion_de(db, exp).nombre


def _id_vigente(db, exp: Expediente) -> uuid.UUID | None:
    """Vigente: la revisión más reciente (por fecha de revisión) del ciclo actual."""
    return db.scalar(
        select(RevisionAnalisisRiesgos.id)
        .where(RevisionAnalisisRiesgos.expediente_id == exp.id, RevisionAnalisisRiesgos.ciclo == _ciclo_actual(db, exp))
        .order_by(RevisionAnalisisRiesgos.fecha_revision.desc(), RevisionAnalisisRiesgos.id.desc())
        .limit(1)
    )


def _a_esquema(r: RevisionAnalisisRiesgos, parque_id: uuid.UUID, vigente_id) -> e.RevisionAnalisisRiesgos:
    return e.RevisionAnalisisRiesgos(
        id=r.id, parque_id=parque_id, fecha_revision=r.fecha_revision, version=r.version, firmante=r.firmante,
        resumen=r.resumen, ciclo=r.ciclo, vigente=r.id == vigente_id, registrado_por=r.registrado_por,
    )


@router.get("/parques/{parqueId}/revisiones-analisis-riesgos", response_model=list[e.RevisionAnalisisRiesgos])
def listar_revisiones_analisis_riesgos(parqueId: uuid.UUID, db: DB):
    parque = obtener_parque(db, parqueId)
    exp = exigir_expediente(db, parque)
    vigente = _id_vigente(db, exp)
    revisiones = db.scalars(
        select(RevisionAnalisisRiesgos)
        .where(RevisionAnalisisRiesgos.expediente_id == exp.id)
        .order_by(RevisionAnalisisRiesgos.fecha_revision.desc(), RevisionAnalisisRiesgos.id.desc())
    )
    return [_a_esquema(r, parque.id, vigente) for r in revisiones]


@router.post("/parques/{parqueId}/revisiones-analisis-riesgos", response_model=e.RevisionAnalisisRiesgos,
             status_code=201)
def crear_revision_analisis_riesgos(
    parqueId: uuid.UUID, cuerpo: e.RevisionAnalisisRiesgosCreate, db: DB, actor: Actor, response: Response
):
    parque = obtener_parque(db, parqueId)
    exp = exigir_expediente(db, parque)
    r = RevisionAnalisisRiesgos(
        expediente_id=exp.id,
        fecha_revision=cuerpo.fecha_revision,
        version=cuerpo.version.strip(),
        firmante=cuerpo.firmante.strip(),
        resumen=cuerpo.resumen,
        ciclo=_ciclo_actual(db, exp),
        registrado_por=actor.id,
    )
    db.add(r)
    db.flush()
    registrar_bitacora(
        db, actor, "registrar_revision_analisis_riesgos", recurso_tipo="revision_analisis_riesgos",
        recurso_id=r.id, parque_id=parque.id,
    )
    db.commit()
    response.headers["Location"] = f"/api/parques/{parque.id}/revisiones-analisis-riesgos/{r.id}"
    return _a_esquema(r, parque.id, _id_vigente(db, exp))


@router.get("/parques/{parqueId}/revisiones-analisis-riesgos/{revisionId}", response_model=e.RevisionAnalisisRiesgos)
def obtener_revision_analisis_riesgos(parqueId: uuid.UUID, revisionId: uuid.UUID, db: DB):
    parque = obtener_parque(db, parqueId)
    r = db.scalars(
        select(RevisionAnalisisRiesgos)
        .join(Expediente, Expediente.id == RevisionAnalisisRiesgos.expediente_id)
        .where(RevisionAnalisisRiesgos.id == revisionId, Expediente.parque_id == parque.id)
    ).first()
    if r is None:
        raise ErrorAPI(404, "no_encontrado", "No existe la revisión del análisis de riesgos solicitada")
    exp = db.get(Expediente, r.expediente_id)
    actual = exigir_expediente(db, parque)
    return _a_esquema(r, parque.id, _id_vigente(db, exp) if exp.id == actual.id else None)
