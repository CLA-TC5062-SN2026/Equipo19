"""Reglas de dominio compartidas por varios routers: expediente vigente, tipo de PI, criterios
aplicables, cumplimiento y armado de las respuestas que combinan varias tablas."""

import uuid
from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import and_, func, select
from sqlalchemy.orm import Session

from app import esquemas as e
from app.comun import hoy
from app.errores import ErrorAPI, no_encontrado
from app.modelos import (
    AsignacionConsultor,
    ActualizacionAnual,
    ClasificacionTipoPI,
    Criterio,
    CriterioParque,
    Desarrollador,
    Estandar,
    Evidencia,
    Expediente,
    FaseExpediente,
    CatalogoFase,
    Generacion,
    MarcaPorTipo,
    Parque,
    RenglonPlanTrabajo,
    Subestandar,
    Usuario,
    VersionCatalogo,
    VinculoEvidencia,
)


# ------------------------------------------------------------------ búsquedas básicas
def obtener_parque(db: Session, parque_id: uuid.UUID) -> Parque:
    parque = db.get(Parque, parque_id)
    if parque is None:
        raise no_encontrado("parque")
    return parque


def expediente_actual(db: Session, parque_id: uuid.UUID) -> Expediente | None:
    """Expediente de la generación vigente del parque (la de fecha de inicio más reciente)."""
    return db.scalars(
        select(Expediente)
        .join(Generacion, Generacion.id == Expediente.generacion_id)
        .where(Expediente.parque_id == parque_id)
        .order_by(Generacion.fecha_inicio.desc(), Generacion.nombre.desc())
        .limit(1)
    ).first()


def exigir_expediente(db: Session, parque: Parque) -> Expediente:
    """Los parques históricos no tienen expediente (RF-31-AC-2): sus subrecursos no existen."""
    exp = expediente_actual(db, parque.id)
    if exp is None:
        raise ErrorAPI(404, "sin_expediente", "El parque no tiene expediente en el programa (alta histórica)")
    return exp


def clasificacion_vigente(db: Session, parque_id: uuid.UUID) -> ClasificacionTipoPI | None:
    return db.scalars(
        select(ClasificacionTipoPI).where(
            ClasificacionTipoPI.parque_id == parque_id, ClasificacionTipoPI.fecha_hasta.is_(None)
        )
    ).first()


def tipo_vigente(db: Session, parque_id: uuid.UUID) -> str | None:
    c = clasificacion_vigente(db, parque_id)
    return c.tipo_pi if c else None


def obtener_o_crear_desarrollador(db: Session, nombre: str) -> Desarrollador:
    nombre = nombre.strip()
    des = db.scalars(select(Desarrollador).where(Desarrollador.nombre == nombre)).first()
    if des is None:
        des = Desarrollador(nombre=nombre)
        db.add(des)
        db.flush()
    return des


def nombre_desarrollador(db: Session, desarrollador_id: uuid.UUID | None) -> str | None:
    if desarrollador_id is None:
        return None
    des = db.get(Desarrollador, desarrollador_id)
    return des.nombre if des else None


def generacion_de(db: Session, exp: Expediente) -> Generacion:
    return db.get(Generacion, exp.generacion_id)  # type: ignore[return-value]


def version_de(db: Session, exp: Expediente) -> VersionCatalogo:
    gen = generacion_de(db, exp)
    return db.get(VersionCatalogo, gen.version_catalogo_id)  # type: ignore[return-value]


# ------------------------------------------------------------------ respuestas compuestas
def usuario_a_esquema(db: Session, u: Usuario) -> e.Usuario:
    return e.Usuario(
        id=u.id,
        correo=u.correo,
        nombre=u.nombre,
        rol=u.rol,
        parque_id=u.parque_id,
        desarrollador=nombre_desarrollador(db, u.desarrollador_id),
        estado=u.estado,
        fecha_alta=u.fecha_alta,
    )


def fase_actual(db: Session, exp: Expediente) -> str | None:
    filas = db.execute(
        select(FaseExpediente.fase, FaseExpediente.estado, CatalogoFase.orden)
        .join(CatalogoFase, CatalogoFase.clave == FaseExpediente.fase)
        .where(FaseExpediente.expediente_id == exp.id)
        .order_by(CatalogoFase.orden)
    ).all()
    for fase, estado, _ in filas:
        if estado == "en_proceso":
            return fase
    iniciadas = [f for f, estado, _ in filas if estado != "pendiente"]
    return iniciadas[-1] if iniciadas else None


def parque_a_esquema(db: Session, parque: Parque) -> e.Parque:
    exp = expediente_actual(db, parque.id)
    datos: dict = dict(
        id=parque.id,
        tipo_registro=parque.tipo_registro,
        nombre=parque.nombre,
        desarrollador=nombre_desarrollador(db, parque.desarrollador_id),
        tipo_pi=tipo_vigente(db, parque.id),
        region=parque.region,
        estado=parque.estado,
        fecha_alta=parque.fecha_alta,
        fecha_ultimo_dictamen=parque.fecha_ultimo_dictamen,
        motivo_baja=parque.motivo_baja,
        contacto_principal_id=parque.contacto_principal_id,
        fecha_termino_programa=parque.fecha_termino_historico,
        atrasado_actualizacion=False,
    )
    if exp is not None:
        gen = generacion_de(db, exp)
        version = db.get(VersionCatalogo, gen.version_catalogo_id)
        asignacion = db.scalars(
            select(AsignacionConsultor).where(
                AsignacionConsultor.expediente_id == exp.id, AsignacionConsultor.vigente_hasta.is_(None)
            )
        ).first()
        ultima = db.scalar(
            select(func.max(ActualizacionAnual.fecha))
            .join(Expediente, Expediente.id == ActualizacionAnual.expediente_id)
            .where(Expediente.parque_id == parque.id)
        )
        datos.update(
            generacion_id=gen.id,
            fase=fase_actual(db, exp),
            version_catalogo=version.nombre if version else None,
            consultor_asignado_id=asignacion.consultor_id if asignacion else None,
            fecha_termino_programa=exp.fecha_termino_programa,
            fecha_proxima_actualizacion=exp.fecha_proxima_actualizacion,
            fecha_ultima_actualizacion=ultima,
            atrasado_actualizacion=bool(
                exp.fecha_proxima_actualizacion and exp.fecha_proxima_actualizacion < hoy()
            ),
        )
    return e.Parque(**datos)


def clasificacion_a_esquema(c: ClasificacionTipoPI) -> e.ClasificacionTipoPI:
    return e.ClasificacionTipoPI(
        id=c.id,
        tipo_pi=c.tipo_pi,
        fecha_desde=c.fecha_desde,
        fecha_hasta=c.fecha_hasta,
        porcentaje_obligatorios_al_cierre=(
            float(c.porcentaje_obligatorios_al_cierre) if c.porcentaje_obligatorios_al_cierre is not None else None
        ),
        porcentaje_avance_general_al_cierre=(
            float(c.porcentaje_avance_general_al_cierre)
            if c.porcentaje_avance_general_al_cierre is not None
            else None
        ),
        motivo=c.motivo,
        cambiado_por=c.cambiado_por,
    )


# ------------------------------------------------------------------ criterios del parque
@dataclass
class FilaCriterio:
    cp: CriterioParque
    criterio: Criterio
    estandar: int
    marca: str | None  # None si el criterio no tiene marca para el tipo (no debería ocurrir)


def filas_criterios(db: Session, exp: Expediente, tipo: str | None, criterio_id: uuid.UUID | None = None
                    ) -> list[FilaCriterio]:
    """Todos los criterios del expediente con su marca para el tipo de PI indicado."""
    q = (
        select(CriterioParque, Criterio, Estandar.numero, MarcaPorTipo.marca)
        .join(Criterio, Criterio.id == CriterioParque.criterio_id)
        .join(Subestandar, Subestandar.id == Criterio.subestandar_id)
        .join(Estandar, Estandar.id == Subestandar.estandar_id)
        .outerjoin(MarcaPorTipo, and_(MarcaPorTipo.criterio_id == Criterio.id, MarcaPorTipo.tipo_pi == tipo))
        .where(CriterioParque.expediente_id == exp.id)
    )
    if criterio_id is not None:
        q = q.where(CriterioParque.criterio_id == criterio_id)
    return [FilaCriterio(cp, cr, num, marca) for cp, cr, num, marca in db.execute(q).all()]


def es_atrasado(estado_criterio: str, renglon: RenglonPlanTrabajo | None) -> bool:
    """Fecha comprometida vencida sin llegar a "cumplido" (RF-09-AC-2). Además de la marca que deja
    la revisión diaria, se compara contra hoy para no depender de que el worker ya exista."""
    if renglon is None or estado_criterio == "cumplido":
        return False
    return renglon.fecha_marca_atraso is not None or renglon.fecha_comprometida < hoy()


def criterios_parque_a_esquema(db: Session, filas: list[FilaCriterio]) -> list[e.CriterioParque]:
    if not filas:
        return []
    ids_cp = [f.cp.id for f in filas]
    evidencias = dict(
        db.execute(
            select(VinculoEvidencia.criterio_parque_id, func.count())
            .join(Evidencia, Evidencia.id == VinculoEvidencia.evidencia_id)
            .where(VinculoEvidencia.criterio_parque_id.in_(ids_cp), Evidencia.eliminada_en.is_(None))
            .group_by(VinculoEvidencia.criterio_parque_id)
        ).all()
    )
    renglones = {
        r.criterio_parque_id: r
        for r in db.scalars(select(RenglonPlanTrabajo).where(RenglonPlanTrabajo.criterio_parque_id.in_(ids_cp)))
    }
    ids_usuarios = {f.cp.calificado_por for f in filas if f.cp.calificado_por}
    nombres = (
        dict(db.execute(select(Usuario.id, Usuario.nombre).where(Usuario.id.in_(ids_usuarios))).all())
        if ids_usuarios
        else {}
    )
    return [
        e.CriterioParque(
            criterio_id=f.criterio.id,
            clave=f.criterio.clave,
            estandar=f.estandar,
            texto=f.criterio.texto,
            marca=f.marca,
            evidencia_suficiente=f.criterio.evidencia_suficiente,
            estado_calificacion=f.cp.estado_calificacion,
            fecha_ultimo_cambio=f.cp.fecha_ultimo_cambio,
            registrado_por=nombres.get(f.cp.calificado_por),
            atrasado=es_atrasado(f.cp.estado_calificacion, renglones.get(f.cp.id)),
            total_evidencias=evidencias.get(f.cp.id, 0),
        )
        for f in filas
    ]


# ------------------------------------------------------------------ cumplimiento (RF-08)
def _cifras(oa: int, oc: int, ra: int, rc: int) -> dict:
    def pct(a: int, b: int) -> float | None:
        return round(a * 100.0 / b, 2) if b else None

    return dict(
        obligatorios_aplicables=oa,
        obligatorios_cumplidos=oc,
        recomendados_aplicables=ra,
        recomendados_cumplidos=rc,
        porcentaje_obligatorios=pct(oc, oa),
        porcentaje_avance_general=pct(oc + rc, oa + ra),
        no_aplica=oa == 0,
        porcentaje_recomendados=pct(rc, ra),
    )


def calcular_cumplimiento(db: Session, exp: Expediente, tipo: str) -> tuple[dict, list[dict]]:
    """Totales por suma de criterios de los 10 estándares, nunca promediando porcentajes."""
    version = version_de(db, exp)
    numeros = sorted(
        db.scalars(select(Estandar.numero).where(Estandar.version_catalogo_id == version.id)).all()
    )
    conteo = {n: [0, 0, 0, 0] for n in numeros}  # oa, oc, ra, rc
    for f in filas_criterios(db, exp, tipo):
        if f.marca not in ("O", "R"):
            continue
        c = conteo.setdefault(f.estandar, [0, 0, 0, 0])
        cumplido = f.cp.estado_calificacion == "cumplido"
        if f.marca == "O":
            c[0] += 1
            c[1] += cumplido
        else:
            c[2] += 1
            c[3] += cumplido
    total = [sum(v[i] for v in conteo.values()) for i in range(4)]
    por_estandar = [dict(estandar=n, **_cifras(*conteo[n])) for n in sorted(conteo)]
    return _cifras(*total), por_estandar


def fases_a_esquema(db: Session, exp: Expediente) -> list[e.FaseExpediente]:
    filas = db.execute(
        select(CatalogoFase, FaseExpediente)
        .outerjoin(
            FaseExpediente,
            and_(FaseExpediente.fase == CatalogoFase.clave, FaseExpediente.expediente_id == exp.id),
        )
        .order_by(CatalogoFase.orden)
    ).all()
    return [fase_a_esquema(cat, fe) for cat, fe in filas]


def fase_a_esquema(cat: CatalogoFase, fe: FaseExpediente | None) -> e.FaseExpediente:
    estado = fe.estado if fe else "pendiente"
    return e.FaseExpediente(
        fase=cat.clave,
        orden=cat.orden,
        nombre=cat.nombre,
        estado=estado,
        actual=estado == "en_proceso",
        fecha_inicio=fe.fecha_inicio if fe else None,
        fecha_cierre=fe.fecha_cierre if fe else None,
        cerrada_por=fe.cerrada_por if fe else None,
        motivo_excepcion=fe.motivo_excepcion if fe else None,
    )


def inicializar_expediente(db: Session, exp: Expediente, inicio: datetime) -> None:
    """Crea las nueve fases (la primera en proceso) y un criterio_parque por cada criterio de la
    versión del catálogo de la generación. La aplicabilidad (O/R/NA) se resuelve con el tipo de PI
    vigente, así un cambio de tipo no borra calificaciones ni evidencias (RF-11-AC-6)."""
    fases = db.scalars(select(CatalogoFase).order_by(CatalogoFase.orden)).all()
    for i, cat in enumerate(fases):
        db.add(
            FaseExpediente(
                expediente_id=exp.id,
                fase=cat.clave,
                estado="en_proceso" if i == 0 else "pendiente",
                fecha_inicio=inicio if i == 0 else None,
            )
        )
    version = version_de(db, exp)
    ids = db.scalars(
        select(Criterio.id)
        .join(Subestandar, Subestandar.id == Criterio.subestandar_id)
        .join(Estandar, Estandar.id == Subestandar.estandar_id)
        .where(Estandar.version_catalogo_id == version.id)
    ).all()
    db.add_all(CriterioParque(expediente_id=exp.id, criterio_id=cid) for cid in ids)
    db.flush()
