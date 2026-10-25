"""Parques: alta, baja, tipo de PI y fechas del programa (RF-02, RF-11, RF-29, RF-30, RF-31)."""

import uuid
from decimal import Decimal
from typing import Annotated

from fastapi import APIRouter, Body, Query, Response
from sqlalchemy import select

from app import esquemas as e
from app.comun import DB, Actor, Paginacion, ahora, hoy, mas_un_anio, ordenar_lista, paginar, registrar_bitacora
from app.errores import ErrorAPI
from app.modelos import (
    ActualizacionAnual,
    CalificacionCriterio,
    ClasificacionTipoPI,
    CriterioParque,
    Expediente,
    Generacion,
    Parque,
)
from app.permisos import parques_visibles
from app.servicios import (
    calcular_cumplimiento,
    clasificacion_a_esquema,
    clasificacion_vigente,
    exigir_expediente,
    filas_criterios,
    inicializar_expediente,
    obtener_o_crear_desarrollador,
    obtener_parque,
    parque_a_esquema,
)

router = APIRouter(tags=["Parques"])


@router.get("/parques", response_model=e.Pagina[e.Parque])
def listar_parques(
    db: DB,
    actor: Actor,
    p: Paginacion,
    generacion_id: Annotated[uuid.UUID | None, Query(alias="generacionId")] = None,
    region: Annotated[e.Region | None, Query()] = None,
    estado: Annotated[e.EstadoParque | None, Query()] = None,
    atrasado: Annotated[bool | None, Query()] = None,
):
    q = select(Parque)
    # Coordinación y Director General ven todos; la APPI, su parque; el consultor, sus asignaciones vigentes; el
    # gerente corporativo, los de su desarrollador (contrato GET /parques, RNF-01).
    visibles = parques_visibles(db, actor)
    if visibles is not None:
        q = q.where(Parque.id.in_(visibles))
    if region:
        q = q.where(Parque.region == region)
    q = q.where(Parque.estado == estado) if estado else q.where(Parque.estado != "inactivo")
    items = [parque_a_esquema(db, parque) for parque in db.scalars(q)]
    if generacion_id is not None:
        items = [x for x in items if x.generacion_id == generacion_id]
    if atrasado is not None:
        items = [x for x in items if x.atrasado_actualizacion == atrasado]
    items = ordenar_lista(
        items,
        p.orden,
        {"nombre": lambda x: x.nombre.lower(), "fechaAlta": lambda x: x.fecha_alta, "region": lambda x: x.region},
        "nombre",
        lambda x: x.id,
    )
    return paginar(items, p)


@router.post("/parques", response_model=e.Parque, status_code=201)
def crear_parque(cuerpo: Annotated[e.ParqueAlta, Body()], db: DB, actor: Actor, response: Response):
    if isinstance(cuerpo, e.ParqueHistoricoCreate):
        parque = Parque(
            tipo_registro="historico",
            nombre=cuerpo.nombre.strip(),
            region=cuerpo.region,
            estado="historico",
            fecha_alta=hoy(),
            fecha_ultimo_dictamen=cuerpo.fecha_ultimo_dictamen,
            fecha_termino_historico=cuerpo.fecha_termino_programa,
        )
        db.add(parque)
        db.flush()
    else:
        generacion = db.get(Generacion, cuerpo.generacion_id)
        if generacion is None:
            raise ErrorAPI(422, "generacion_no_existe", "La generación indicada no existe")
        desarrollador = obtener_o_crear_desarrollador(db, cuerpo.desarrollador)
        parque = Parque(
            tipo_registro="activo",
            nombre=cuerpo.nombre.strip(),
            desarrollador_id=desarrollador.id,
            region=cuerpo.region,
            estado="activo",
            fecha_alta=hoy(),
        )
        db.add(parque)
        db.flush()
        db.add(ClasificacionTipoPI(parque_id=parque.id, tipo_pi=cuerpo.tipo_pi, fecha_desde=hoy(), cambiado_por=actor.id))
        exp = Expediente(parque_id=parque.id, generacion_id=generacion.id)
        db.add(exp)
        db.flush()
        inicializar_expediente(db, exp, ahora())
    registrar_bitacora(
        db, actor, "crear_parque", recurso_tipo="parque", recurso_id=parque.id, parque_id=parque.id,
        detalle=f"tipoRegistro={parque.tipo_registro}",
    )
    db.commit()
    response.headers["Location"] = f"/api/parques/{parque.id}"
    return parque_a_esquema(db, parque)


@router.get("/parques/{parqueId}", response_model=e.Parque)
def obtener_parque_endpoint(parqueId: uuid.UUID, db: DB):
    return parque_a_esquema(db, obtener_parque(db, parqueId))


@router.patch("/parques/{parqueId}", response_model=e.Parque)
def actualizar_parque(parqueId: uuid.UUID, cuerpo: e.ParqueUpdate, db: DB, actor: Actor):
    parque = obtener_parque(db, parqueId)
    campos = cuerpo.model_fields_set
    if not campos:
        raise ErrorAPI(422, "datos_invalidos", "Indique al menos un campo a actualizar")
    if "estado" in campos and cuerpo.estado is None:
        raise ErrorAPI(422, "datos_invalidos", "El único estado admitido es inactivo")
    for campo in ("nombre", "desarrollador", "region"):
        if campo in campos and getattr(cuerpo, campo) is None:
            raise ErrorAPI(422, "datos_invalidos", f"El campo {campo} no admite nulo")

    if cuerpo.estado == "inactivo":
        if parque.estado == "historico":
            raise ErrorAPI(409, "transicion_invalida", "Un parque histórico no se puede dar de baja")
        if not cuerpo.motivo:
            raise ErrorAPI(422, "motivo_requerido", "Indique el motivo de la baja del parque")

    exp = None
    if campos & {"fecha_termino_programa", "fecha_proxima_actualizacion"}:
        if parque.tipo_registro == "historico":
            if "fecha_proxima_actualizacion" in campos:
                raise ErrorAPI(422, "parque_historico", "Un parque histórico no tiene actualización anual")
        else:
            exp = exigir_expediente(db, parque)

    cambios = []
    if cuerpo.nombre is not None:
        parque.nombre = cuerpo.nombre.strip()
        cambios.append("nombre")
    if cuerpo.desarrollador is not None:
        parque.desarrollador_id = obtener_o_crear_desarrollador(db, cuerpo.desarrollador).id
        cambios.append("desarrollador")
    if cuerpo.region is not None:
        parque.region = cuerpo.region
        cambios.append("region")
    if "fecha_termino_programa" in campos:
        if exp is not None:
            exp.fecha_termino_programa = cuerpo.fecha_termino_programa
        elif cuerpo.fecha_termino_programa is not None:
            parque.fecha_termino_historico = cuerpo.fecha_termino_programa
        cambios.append("fechaTerminoPrograma")
    if "fecha_proxima_actualizacion" in campos and exp is not None:
        exp.fecha_proxima_actualizacion = cuerpo.fecha_proxima_actualizacion
        cambios.append("fechaProximaActualizacion")
    # Repetir la baja de un parque ya inactivo no tiene efectos.
    if cuerpo.estado == "inactivo" and parque.estado != "inactivo":
        parque.estado = "inactivo"
        parque.motivo_baja = cuerpo.motivo
        registrar_bitacora(
            db, actor, "baja_parque", recurso_tipo="parque", recurso_id=parque.id, parque_id=parque.id,
            detalle=cuerpo.motivo,
        )
    if cambios:
        registrar_bitacora(
            db, actor, "actualizar_parque", recurso_tipo="parque", recurso_id=parque.id, parque_id=parque.id,
            detalle=", ".join(cambios),
        )
    db.commit()
    return parque_a_esquema(db, parque)


@router.put("/parques/{parqueId}/tipo-pi", response_model=e.CambioTipoPIResultado)
def reemplazar_tipo_pi(parqueId: uuid.UUID, cuerpo: e.CambioTipoPI, db: DB, actor: Actor):
    parque = obtener_parque(db, parqueId)
    exp = exigir_expediente(db, parque)
    vigente = clasificacion_vigente(db, parque.id)

    if vigente is not None and vigente.tipo_pi == cuerpo.tipo_pi:
        return e.CambioTipoPIResultado(
            parque=parque_a_esquema(db, parque), cambio=False,
            criterios_que_dejan_de_ser_na=[], criterios_que_pasan_a_na=[],
        )

    cerrada = None
    marcas_antes: dict[uuid.UUID, str | None] = {}
    if vigente is not None:
        if cuerpo.fecha_cambio < vigente.fecha_desde:
            raise ErrorAPI(
                422, "fecha_cambio_invalida",
                "La fecha de cambio no puede ser anterior al inicio de la clasificación vigente",
            )
        total, _ = calcular_cumplimiento(db, exp, vigente.tipo_pi)
        marcas_antes = {f.cp.criterio_id: f.marca for f in filas_criterios(db, exp, vigente.tipo_pi)}
        vigente.fecha_hasta = cuerpo.fecha_cambio
        vigente.porcentaje_obligatorios_al_cierre = (
            Decimal(str(total["porcentaje_obligatorios"])) if total["porcentaje_obligatorios"] is not None else None
        )
        vigente.porcentaje_avance_general_al_cierre = (
            Decimal(str(total["porcentaje_avance_general"])) if total["porcentaje_avance_general"] is not None else None
        )
        cerrada = vigente
        db.flush()  # libera el índice único de clasificación vigente

    nueva = ClasificacionTipoPI(
        parque_id=parque.id, tipo_pi=cuerpo.tipo_pi, fecha_desde=cuerpo.fecha_cambio,
        motivo=cuerpo.motivo, cambiado_por=actor.id,
    )
    db.add(nueva)
    db.flush()

    dejan_na, pasan_na = [], []
    momento = ahora()
    for f in filas_criterios(db, exp, cuerpo.tipo_pi):
        antes = marcas_antes.get(f.cp.criterio_id)
        aplica_antes = antes in ("O", "R")
        aplica_ahora = f.marca in ("O", "R")
        if aplica_ahora and not aplica_antes and vigente is not None:
            dejan_na.append(f.cp.criterio_id)
            cp: CriterioParque = f.cp
            if cp.estado_calificacion != "pendiente":
                # [D-19] RD-14: el regreso a "pendiente" queda en el historial como cambio del sistema.
                db.add(CalificacionCriterio(
                    criterio_parque_id=cp.id, estado_anterior=cp.estado_calificacion, estado_nuevo="pendiente",
                    motivo=f"Vuelve a aplicar por el cambio de tipo de PI a {cuerpo.tipo_pi} (RF-11-AC-4)",
                    origen="sistema",
                ))
            cp.estado_calificacion = "pendiente"
            cp.fecha_ultimo_cambio = momento
            cp.calificado_por = actor.id
        elif aplica_antes and not aplica_ahora:
            pasan_na.append(f.cp.criterio_id)

    registrar_bitacora(
        db, actor, "cambiar_tipo_pi", recurso_tipo="parque", recurso_id=parque.id, parque_id=parque.id,
        detalle=f"{cerrada.tipo_pi if cerrada else '-'} -> {cuerpo.tipo_pi}: {cuerpo.motivo}",
    )
    db.commit()
    return e.CambioTipoPIResultado(
        parque=parque_a_esquema(db, parque),
        cambio=True,
        clasificacion_cerrada=clasificacion_a_esquema(cerrada) if cerrada else None,
        clasificacion_nueva=clasificacion_a_esquema(nueva),
        criterios_que_dejan_de_ser_na=dejan_na,
        criterios_que_pasan_a_na=pasan_na,
    )


@router.get("/parques/{parqueId}/tipos-pi", response_model=list[e.ClasificacionTipoPI])
def listar_tipos_pi(parqueId: uuid.UUID, db: DB):
    obtener_parque(db, parqueId)
    clasificaciones = db.scalars(
        select(ClasificacionTipoPI)
        .where(ClasificacionTipoPI.parque_id == parqueId)
        .order_by(ClasificacionTipoPI.fecha_desde, ClasificacionTipoPI.fecha_hasta.asc().nulls_last())
    )
    return [clasificacion_a_esquema(c) for c in clasificaciones]


def _actualizacion_a_esquema(a: ActualizacionAnual, parque_id: uuid.UUID) -> e.ActualizacionAnual:
    return e.ActualizacionAnual(
        id=a.id, parque_id=parque_id, fecha=a.fecha, fecha_proxima_actualizacion=mas_un_anio(a.fecha),
        notas=a.notas, registrado_por=a.registrado_por,
    )


@router.post("/parques/{parqueId}/actualizaciones-anuales", response_model=e.ActualizacionAnual, status_code=201)
def crear_actualizacion_anual(
    parqueId: uuid.UUID, cuerpo: e.ActualizacionAnualCreate, db: DB, actor: Actor, response: Response
):
    parque = obtener_parque(db, parqueId)
    exp = exigir_expediente(db, parque)
    a = ActualizacionAnual(expediente_id=exp.id, fecha=cuerpo.fecha, notas=cuerpo.notas, registrado_por=actor.id)
    db.add(a)
    # La próxima actualización queda un año después; con eso se retira la marca de atraso (RF-30-AC-3).
    exp.fecha_proxima_actualizacion = mas_un_anio(cuerpo.fecha)
    db.flush()
    registrar_bitacora(
        db, actor, "registrar_actualizacion_anual", recurso_tipo="actualizacion_anual", recurso_id=a.id,
        parque_id=parque.id,
    )
    db.commit()
    response.headers["Location"] = f"/api/parques/{parque.id}/actualizaciones-anuales/{a.id}"
    return _actualizacion_a_esquema(a, parque.id)


@router.get("/parques/{parqueId}/actualizaciones-anuales/{actualizacionId}", response_model=e.ActualizacionAnual)
def obtener_actualizacion_anual(parqueId: uuid.UUID, actualizacionId: uuid.UUID, db: DB):
    obtener_parque(db, parqueId)
    a = db.scalars(
        select(ActualizacionAnual)
        .join(Expediente, Expediente.id == ActualizacionAnual.expediente_id)
        .where(ActualizacionAnual.id == actualizacionId, Expediente.parque_id == parqueId)
    ).first()
    if a is None:
        raise ErrorAPI(404, "no_encontrado", "No existe la actualización anual solicitada")
    return _actualizacion_a_esquema(a, parqueId)
