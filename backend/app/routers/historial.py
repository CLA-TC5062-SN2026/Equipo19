"""Historial de un parque en el programa (RF-31-AC-1). [C-04] El v0 no implementó esta operación, que es MVP."""

import uuid

from fastapi import APIRouter
from sqlalchemy import select

from app import esquemas as e
from app.comun import DB, mas_un_anio
from app.modelos import (
    ActualizacionAnual,
    Autoevaluacion,
    Dictamen,
    Expediente,
    Generacion,
    OpinionCumplimiento,
    SesionComite,
    VersionCatalogo,
)
from app.routers.generaciones import _generacion_a_esquema
from app.servicios import obtener_parque, parque_a_esquema

router = APIRouter(tags=["Parques"])


@router.get("/parques/{parqueId}/historial", response_model=e.HistorialParque)
def obtener_historial_parque(parqueId: uuid.UUID, db: DB):
    parque = obtener_parque(db, parqueId)
    filas = db.execute(
        select(Expediente, Generacion)
        .join(Generacion, Generacion.id == Expediente.generacion_id)
        .where(Expediente.parque_id == parque.id)
        .order_by(Generacion.fecha_inicio)
    ).all()
    gen_de = {exp.id: gen for exp, gen in filas}
    ids = list(gen_de)

    actualizaciones = [
        e.ActualizacionAnual(id=a.id, parque_id=parque.id, fecha=a.fecha,
                             fecha_proxima_actualizacion=mas_un_anio(a.fecha), notas=a.notas,
                             registrado_por=a.registrado_por)
        for a in db.scalars(select(ActualizacionAnual).where(ActualizacionAnual.expediente_id.in_(ids))
                            .order_by(ActualizacionAnual.fecha))
    ]
    nombres_version = dict(db.execute(select(VersionCatalogo.id, VersionCatalogo.nombre)).all())
    autoevaluaciones = [
        e.Autoevaluacion(parque_id=parque.id, generacion_id=gen_de[a.expediente_id].id, criterio_id=a.criterio_id,
                         respuesta=a.respuesta, comentario=a.comentario,
                         version_catalogo=nombres_version[gen_de[a.expediente_id].version_catalogo_id],
                         registrado_por=a.registrado_por, fecha=a.fecha)
        for a in db.scalars(select(Autoevaluacion).where(Autoevaluacion.expediente_id.in_(ids)))
    ]
    opiniones = [
        e.OpinionCumplimiento(id=o.id, parque_id=parque.id, generacion_id=gen_de[o.expediente_id].id, tipo=o.tipo,
                              favorable=o.favorable,
                              porcentaje_obligatorios=float(o.porcentaje_obligatorios) if o.porcentaje_obligatorios is not None else None,
                              porcentaje_avance_general=float(o.porcentaje_avance_general) if o.porcentaje_avance_general is not None else None,
                              consultor_id=o.consultor_id, fecha=o.fecha, comentarios=o.comentarios)
        for o in db.scalars(select(OpinionCumplimiento).where(OpinionCumplimiento.expediente_id.in_(ids))
                            .order_by(OpinionCumplimiento.fecha))
    ]
    dictamenes = [
        e.Dictamen(id=d.id, parque_id=parque.id, generacion_id=gen_de[s.expediente_id].id, sesion_comite_id=s.id,
                   tipo=d.tipo, motivo=d.motivo, estado=d.estado, capturado_por=d.capturado_por,
                   fecha_captura=d.fecha_captura, firmado_por=d.firmado_por, fecha_firma=d.fecha_firma,
                   vigencia_hasta=d.vigencia_hasta)
        for d, s in db.execute(select(Dictamen, SesionComite).join(SesionComite, SesionComite.id == Dictamen.sesion_comite_id)
                               .where(SesionComite.expediente_id.in_(ids)).order_by(Dictamen.fecha_captura)).all()
    ]
    return e.HistorialParque(
        parque=parque_a_esquema(db, parque),
        generaciones=[_generacion_a_esquema(db, gen) for _, gen in filas],
        actualizaciones_anuales=actualizaciones,
        autoevaluaciones=autoevaluaciones,
        opiniones=opiniones,
        dictamenes=dictamenes,
    )
