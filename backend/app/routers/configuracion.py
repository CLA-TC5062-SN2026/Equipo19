"""Parámetros del programa: límite de archivo de evidencia y vigencia del distintivo (RF-06, RD-08)."""

from fastapi import APIRouter

from app import esquemas as e
from app.comun import DB, Actor, ahora, registrar_bitacora
from app.errores import ErrorAPI
from app.modelos import Configuracion

router = APIRouter(tags=["Configuración"])


def _obtener(db) -> Configuracion:
    conf = db.get(Configuracion, 1)
    if conf is None:  # el esquema la siembra; esto solo cubre una base sembrada a medias
        conf = Configuracion(id=1)
        db.add(conf)
        db.flush()
    return conf


def _a_esquema(c: Configuracion) -> e.Configuracion:
    return e.Configuracion(
        tamano_maximo_evidencia_mb=c.tamano_maximo_evidencia_mb,
        vigencia_distintivo_anios=c.vigencia_distintivo_anios,
        actualizado_en=c.actualizado_en,
        actualizado_por=c.actualizado_por,
    )


@router.get("/configuracion", response_model=e.Configuracion)
def obtener_configuracion(db: DB):
    conf = _obtener(db)
    db.commit()
    return _a_esquema(conf)


@router.patch("/configuracion", response_model=e.Configuracion)
def actualizar_configuracion(cuerpo: e.ConfiguracionUpdate, db: DB, actor: Actor):
    campos = cuerpo.model_fields_set
    if not campos:
        raise ErrorAPI(422, "datos_invalidos", "Indique al menos un parámetro a cambiar")
    if any(getattr(cuerpo, c) is None for c in campos):
        raise ErrorAPI(422, "datos_invalidos", "Los parámetros no admiten nulo")
    if cuerpo.tamano_maximo_evidencia_mb is not None and cuerpo.tamano_maximo_evidencia_mb > 100:
        raise ErrorAPI(422, "limite_excede_maximo", "El límite máximo configurable es 100 MB")

    conf = _obtener(db)
    cambios = []
    if cuerpo.tamano_maximo_evidencia_mb is not None:
        cambios.append(f"tamanoMaximoEvidenciaMB {conf.tamano_maximo_evidencia_mb} -> {cuerpo.tamano_maximo_evidencia_mb}")
        conf.tamano_maximo_evidencia_mb = cuerpo.tamano_maximo_evidencia_mb
    if cuerpo.vigencia_distintivo_anios is not None:
        cambios.append(f"vigenciaDistintivoAnios {conf.vigencia_distintivo_anios} -> {cuerpo.vigencia_distintivo_anios}")
        conf.vigencia_distintivo_anios = cuerpo.vigencia_distintivo_anios
    conf.actualizado_en = ahora()
    conf.actualizado_por = actor.id
    registrar_bitacora(db, actor, "actualizar_configuracion", recurso_tipo="configuracion", recurso_id="1",
                       detalle="; ".join(cambios))
    db.commit()
    return _a_esquema(conf)
