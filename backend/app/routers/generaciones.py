"""Generaciones del programa (RF-28)."""

import uuid

from fastapi import APIRouter, Response
from sqlalchemy import func, select

from app import esquemas as e
from app.comun import DB, Actor, registrar_bitacora
from app.errores import ErrorAPI, no_encontrado
from app.modelos import Expediente, Generacion, VersionCatalogo

router = APIRouter(tags=["Generaciones"])


def _generacion_a_esquema(db, g: Generacion) -> e.Generacion:
    version = db.get(VersionCatalogo, g.version_catalogo_id)
    total = db.scalar(select(func.count(Expediente.id)).where(Expediente.generacion_id == g.id))
    return e.Generacion(
        id=g.id,
        nombre=g.nombre,
        fecha_inicio=g.fecha_inicio,
        version_catalogo_id=g.version_catalogo_id,
        version_catalogo_nombre=version.nombre if version else "",
        total_parques=total or 0,
    )


@router.get("/generaciones", response_model=list[e.Generacion])
def listar_generaciones(db: DB):
    return [_generacion_a_esquema(db, g) for g in db.scalars(select(Generacion).order_by(Generacion.fecha_inicio.desc()))]


@router.post("/generaciones", response_model=e.Generacion, status_code=201)
def crear_generacion(cuerpo: e.GeneracionCreate, db: DB, actor: Actor, response: Response):
    nombre = cuerpo.nombre.strip()
    if db.scalar(select(Generacion.id).where(Generacion.nombre == nombre)):
        raise ErrorAPI(409, "generacion_duplicada", f"Ya existe una generación llamada {nombre}")
    if db.get(VersionCatalogo, cuerpo.version_catalogo_id) is None:
        raise ErrorAPI(422, "version_catalogo_no_existe", "La versión del catálogo indicada no existe")
    g = Generacion(nombre=nombre, fecha_inicio=cuerpo.fecha_inicio, version_catalogo_id=cuerpo.version_catalogo_id)
    db.add(g)
    db.flush()
    registrar_bitacora(db, actor, "crear_generacion", recurso_tipo="generacion", recurso_id=g.id)
    db.commit()
    response.headers["Location"] = f"/api/generaciones/{g.id}"
    return _generacion_a_esquema(db, g)


@router.get("/generaciones/{generacionId}", response_model=e.Generacion)
def obtener_generacion(generacionId: uuid.UUID, db: DB):
    g = db.get(Generacion, generacionId)
    if g is None:
        raise no_encontrado("generación")
    return _generacion_a_esquema(db, g)
