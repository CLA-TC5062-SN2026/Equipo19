"""Criterios aplicables del parque con su estado de calificación (RF-04, RF-07, RF-09, RF-25)."""

import uuid
from typing import Annotated

from fastapi import APIRouter, Query

from app import esquemas as e
from app.comun import DB, Paginacion, clave_natural, ordenar_lista, paginar
from app.errores import ErrorAPI
from app.servicios import criterios_parque_a_esquema, exigir_expediente, filas_criterios, obtener_parque, tipo_vigente

router = APIRouter(tags=["Criterios del parque"])


@router.get("/parques/{parqueId}/criterios", response_model=e.Pagina[e.CriterioParque])
def listar_criterios_parque(
    parqueId: uuid.UUID,
    db: DB,
    p: Paginacion,
    estandar: Annotated[int | None, Query(ge=1, le=10)] = None,
    marca: Annotated[e.MarcaAplicable | None, Query()] = None,
    estado: Annotated[e.EstadoCalificacion | None, Query()] = None,
    atrasado: Annotated[bool | None, Query()] = None,
):
    parque = obtener_parque(db, parqueId)
    exp = exigir_expediente(db, parque)
    filas = [f for f in filas_criterios(db, exp, tipo_vigente(db, parque.id)) if f.marca in ("O", "R")]
    if estandar is not None:
        filas = [f for f in filas if f.estandar == estandar]
    if marca is not None:
        filas = [f for f in filas if f.marca == marca]
    if estado is not None:
        filas = [f for f in filas if f.cp.estado_calificacion == estado]
    items = criterios_parque_a_esquema(db, filas)
    if atrasado is not None:
        items = [x for x in items if x.atrasado == atrasado]
    items = ordenar_lista(
        items,
        p.orden,
        {
            "clave": lambda x: clave_natural(x.clave),
            "estandar": lambda x: x.estandar,
            "fechaUltimoCambio": lambda x: x.fecha_ultimo_cambio,
        },
        "clave",
        lambda x: x.criterio_id,
    )
    return paginar(items, p)


@router.get("/parques/{parqueId}/criterios/{criterioId}", response_model=e.CriterioParque)
def obtener_criterio_parque(parqueId: uuid.UUID, criterioId: uuid.UUID, db: DB):
    parque = obtener_parque(db, parqueId)
    exp = exigir_expediente(db, parque)
    filas = [
        f for f in filas_criterios(db, exp, tipo_vigente(db, parque.id), criterio_id=criterioId) if f.marca in ("O", "R")
    ]
    if not filas:
        # Un criterio NA para el tipo de PI no forma parte de los aplicables del parque.
        raise ErrorAPI(404, "no_encontrado", "El criterio no forma parte de los criterios aplicables del parque")
    return criterios_parque_a_esquema(db, filas)[0]
