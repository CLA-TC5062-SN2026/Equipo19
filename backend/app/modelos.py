"""Mapeo ORM (SQLAlchemy 2.0, estilo Mapped[...]) de las tablas de db/esquema_bd.sql.

Las tablas ya existen: este módulo no crea ni altera nada (no se llama a create_all). Los tipos
enumerados de PostgreSQL se declaran con create_type=False. No se definen relationship(): las
consultas se escriben explícitas en los routers y servicios.
"""

import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    BigInteger,
    Boolean,
    Date,
    ForeignKey,
    Identity,
    Integer,
    Numeric,
    SmallInteger,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import ENUM, TIMESTAMP, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

# ----------------------------------------------------------------- valores de enumeración
ROLES = (
    "coordinacion_ampip", "director_general_ampip", "appi", "consultor",
    "gerente_corporativo", "administrador_tecnico",
)
TIPOS_PI = ("construccion_abierto", "construccion_cerrado", "operacion_abierto", "operacion_cerrado")
MARCAS = ("O", "R", "NA")
ESTADOS_CALIFICACION = ("pendiente", "en_revision", "cumplido", "no_cumplido")
ESTADOS_VINCULO = ("enviada", "observada", "aceptada")
CATEGORIAS_EVIDENCIA = ("seguridad", "administrativa")
ESTADOS_FASE = ("pendiente", "en_proceso", "completada", "avanzada_por_excepcion")
TIPOS_DICTAMEN = ("otorgar", "no_otorgar")
ESTADOS_DICTAMEN = ("borrador", "firmado")
RESPUESTAS_AUTOEVALUACION = ("cumple", "cumple_parcial", "no_cumple")
ESTADOS_USUARIO = ("pendiente_activacion", "activo", "inactivo")
ESTADOS_PARQUE = ("activo", "inactivo", "historico")
TIPOS_OPINION = ("intermedia", "final")
REGIONES = (
    "MX-AGU", "MX-BCN", "MX-BCS", "MX-CAM", "MX-CHP", "MX-CHH", "MX-CMX", "MX-COA",
    "MX-COL", "MX-DUR", "MX-GUA", "MX-GRO", "MX-HID", "MX-JAL", "MX-MEX", "MX-MIC",
    "MX-MOR", "MX-NAY", "MX-NLE", "MX-OAX", "MX-PUE", "MX-QUE", "MX-ROO", "MX-SLP",
    "MX-SIN", "MX-SON", "MX-TAB", "MX-TAM", "MX-TLA", "MX-VER", "MX-YUC", "MX-ZAC",
)
FASES = (
    "diagnostico", "plan_trabajo", "politica_seguridad", "analisis_riesgos",
    "implementacion_estandares", "opinion_intermedia_emitida", "opinion_final_emitida",
    "evaluacion_desempeno", "dictamen",
)


def _enum(nombre: str, valores: tuple[str, ...]) -> ENUM:
    return ENUM(*valores, name=nombre, create_type=False)


RolEnum = _enum("rol", ROLES)
TipoPIEnum = _enum("tipo_pi", TIPOS_PI)
MarcaEnum = _enum("marca", MARCAS)
EstadoCalificacionEnum = _enum("estado_calificacion", ESTADOS_CALIFICACION)
EstadoVinculoEnum = _enum("estado_vinculo", ESTADOS_VINCULO)
CategoriaEvidenciaEnum = _enum("categoria_evidencia", CATEGORIAS_EVIDENCIA)
EstadoFaseEnum = _enum("estado_fase", ESTADOS_FASE)
TipoDictamenEnum = _enum("tipo_dictamen", TIPOS_DICTAMEN)
EstadoDictamenEnum = _enum("estado_dictamen", ESTADOS_DICTAMEN)
RespuestaAutoevaluacionEnum = _enum("respuesta_autoevaluacion", RESPUESTAS_AUTOEVALUACION)
EstadoUsuarioEnum = _enum("estado_usuario", ESTADOS_USUARIO)
EstadoParqueEnum = _enum("estado_parque", ESTADOS_PARQUE)
TipoOpinionEnum = _enum("tipo_opinion", TIPOS_OPINION)
RegionEnum = _enum("region", REGIONES)

TZ = TIMESTAMP(timezone=True)


def _pk() -> Mapped[uuid.UUID]:
    return mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)


def _fk(destino: str, **kw) -> Mapped:
    return mapped_column(UUID(as_uuid=True), ForeignKey(destino), **kw)


class Base(DeclarativeBase):
    pass


# ================================================================ Organización y usuarios
class Desarrollador(Base):
    __tablename__ = "desarrollador"
    id: Mapped[uuid.UUID] = _pk()
    nombre: Mapped[str] = mapped_column(String(200))


class Usuario(Base):
    __tablename__ = "usuario"
    id: Mapped[uuid.UUID] = _pk()
    nombre: Mapped[str] = mapped_column(String(200))
    correo: Mapped[str] = mapped_column(String(254))
    contrasena_hash: Mapped[str | None] = mapped_column(String(255))
    rol: Mapped[str] = mapped_column(RolEnum)
    estado: Mapped[str] = mapped_column(EstadoUsuarioEnum, server_default="pendiente_activacion")
    fecha_alta: Mapped[datetime] = mapped_column(TZ, server_default=func.now())
    motivo_baja: Mapped[str | None] = mapped_column(Text)
    # FK a parque declarada en la base con ALTER TABLE (ciclo usuario <-> parque).
    parque_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    desarrollador_id: Mapped[uuid.UUID | None] = _fk("desarrollador.id")


class Sesion(Base):
    __tablename__ = "sesion"
    sid: Mapped[uuid.UUID] = _pk()
    usuario_id: Mapped[uuid.UUID] = _fk("usuario.id")
    creada: Mapped[datetime] = mapped_column(TZ, server_default=func.now())
    ultima_actividad: Mapped[datetime] = mapped_column(TZ, server_default=func.now())
    expira_en: Mapped[datetime] = mapped_column(TZ)
    revocada_en: Mapped[datetime | None] = mapped_column(TZ)


class EnlaceUnSoloUso(Base):
    __tablename__ = "enlace_un_solo_uso"
    id: Mapped[uuid.UUID] = _pk()
    usuario_id: Mapped[uuid.UUID] = _fk("usuario.id")
    token_hash: Mapped[str] = mapped_column(String(255))
    tipo: Mapped[str] = mapped_column(String(20))
    creado: Mapped[datetime] = mapped_column(TZ, server_default=func.now())
    expira_en: Mapped[datetime] = mapped_column(TZ)
    usado_en: Mapped[datetime | None] = mapped_column(TZ)


class IntentoLogin(Base):
    __tablename__ = "intento_login"
    correo: Mapped[str] = mapped_column(String(254), primary_key=True)
    intentos_fallidos: Mapped[int] = mapped_column(Integer, server_default="0")
    bloqueado_hasta: Mapped[datetime | None] = mapped_column(TZ)


class Configuracion(Base):
    __tablename__ = "configuracion"
    id: Mapped[int] = mapped_column(SmallInteger, primary_key=True, default=1)
    tamano_maximo_evidencia_mb: Mapped[int] = mapped_column(Integer, server_default="100")
    vigencia_distintivo_anios: Mapped[int] = mapped_column(Integer, server_default="3")
    actualizado_en: Mapped[datetime] = mapped_column(TZ, server_default=func.now())
    actualizado_por: Mapped[uuid.UUID | None] = _fk("usuario.id")


# ================================================================ Catálogo
class VersionCatalogo(Base):
    __tablename__ = "version_catalogo"
    id: Mapped[uuid.UUID] = _pk()
    nombre: Mapped[str] = mapped_column(String(100))
    estado: Mapped[str] = mapped_column(String(20), server_default="activa")
    fecha_carga: Mapped[datetime] = mapped_column(TZ, server_default=func.now())
    cargado_por: Mapped[uuid.UUID] = _fk("usuario.id")


class Estandar(Base):
    __tablename__ = "estandar"
    id: Mapped[uuid.UUID] = _pk()
    version_catalogo_id: Mapped[uuid.UUID] = _fk("version_catalogo.id")
    numero: Mapped[int] = mapped_column(Integer)
    nombre: Mapped[str] = mapped_column(String(300))


class Subestandar(Base):
    __tablename__ = "subestandar"
    id: Mapped[uuid.UUID] = _pk()
    estandar_id: Mapped[uuid.UUID] = _fk("estandar.id")
    numero: Mapped[str] = mapped_column(String(20))
    nombre: Mapped[str] = mapped_column(String(300))


class Criterio(Base):
    __tablename__ = "criterio"
    id: Mapped[uuid.UUID] = _pk()
    subestandar_id: Mapped[uuid.UUID] = _fk("subestandar.id")
    clave: Mapped[str] = mapped_column(String(20))
    texto: Mapped[str] = mapped_column(Text)
    metodo_verificacion: Mapped[str] = mapped_column(Text)
    evidencia_suficiente: Mapped[str | None] = mapped_column(String(4000))
    categoria_evidencia: Mapped[str] = mapped_column(CategoriaEvidenciaEnum)
    asterisco: Mapped[bool] = mapped_column(Boolean, server_default="false")


class MarcaPorTipo(Base):
    __tablename__ = "marca_por_tipo"
    criterio_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("criterio.id"), primary_key=True
    )
    tipo_pi: Mapped[str] = mapped_column(TipoPIEnum, primary_key=True)
    marca: Mapped[str] = mapped_column(MarcaEnum)


class CatalogoFase(Base):
    __tablename__ = "catalogo_fase"
    clave: Mapped[str] = mapped_column(String(40), primary_key=True)
    orden: Mapped[int] = mapped_column(Integer)
    nombre: Mapped[str] = mapped_column(String(100))


# ================================================================ Organización (parte 2)
class Generacion(Base):
    __tablename__ = "generacion"
    id: Mapped[uuid.UUID] = _pk()
    nombre: Mapped[str] = mapped_column(String(100))
    fecha_inicio: Mapped[date] = mapped_column(Date)
    version_catalogo_id: Mapped[uuid.UUID] = _fk("version_catalogo.id")


class Parque(Base):
    __tablename__ = "parque"
    id: Mapped[uuid.UUID] = _pk()
    tipo_registro: Mapped[str] = mapped_column(String(10))
    nombre: Mapped[str] = mapped_column(String(200))
    desarrollador_id: Mapped[uuid.UUID | None] = _fk("desarrollador.id")
    region: Mapped[str] = mapped_column(RegionEnum)
    estado: Mapped[str] = mapped_column(EstadoParqueEnum, server_default="activo")
    fecha_alta: Mapped[date] = mapped_column(Date, server_default=func.current_date())
    motivo_baja: Mapped[str | None] = mapped_column(Text)
    fecha_ultimo_dictamen: Mapped[date | None] = mapped_column(Date)
    fecha_termino_historico: Mapped[date | None] = mapped_column(Date)
    # FK compuesta (contacto_principal_id, id) -> usuario (id, parque_id), declarada en la base.
    contacto_principal_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))


class ClasificacionTipoPI(Base):
    __tablename__ = "clasificacion_tipo_pi"
    id: Mapped[uuid.UUID] = _pk()
    parque_id: Mapped[uuid.UUID] = _fk("parque.id")
    tipo_pi: Mapped[str] = mapped_column(TipoPIEnum)
    fecha_desde: Mapped[date] = mapped_column(Date)
    fecha_hasta: Mapped[date | None] = mapped_column(Date)
    motivo: Mapped[str | None] = mapped_column(Text)
    porcentaje_obligatorios_al_cierre: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    porcentaje_avance_general_al_cierre: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    cambiado_por: Mapped[uuid.UUID | None] = _fk("usuario.id")


# ================================================================ Expediente
class Expediente(Base):
    __tablename__ = "expediente"
    id: Mapped[uuid.UUID] = _pk()
    parque_id: Mapped[uuid.UUID] = _fk("parque.id")
    generacion_id: Mapped[uuid.UUID] = _fk("generacion.id")
    fecha_termino_programa: Mapped[date | None] = mapped_column(Date)
    fecha_proxima_actualizacion: Mapped[date | None] = mapped_column(Date)


class FaseExpediente(Base):
    __tablename__ = "fase_expediente"
    expediente_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("expediente.id"), primary_key=True
    )
    fase: Mapped[str] = mapped_column(String(40), ForeignKey("catalogo_fase.clave"), primary_key=True)
    estado: Mapped[str] = mapped_column(EstadoFaseEnum, server_default="pendiente")
    fecha_inicio: Mapped[datetime | None] = mapped_column(TZ)
    fecha_cierre: Mapped[datetime | None] = mapped_column(TZ)
    motivo_excepcion: Mapped[str | None] = mapped_column(Text)
    cerrada_por: Mapped[uuid.UUID | None] = _fk("usuario.id")


class ActualizacionAnual(Base):
    __tablename__ = "actualizacion_anual"
    id: Mapped[uuid.UUID] = _pk()
    expediente_id: Mapped[uuid.UUID] = _fk("expediente.id")
    fecha: Mapped[date] = mapped_column(Date)
    notas: Mapped[str | None] = mapped_column(Text)
    registrado_por: Mapped[uuid.UUID] = _fk("usuario.id")


class AsignacionConsultor(Base):
    __tablename__ = "asignacion_consultor"
    id: Mapped[uuid.UUID] = _pk()
    expediente_id: Mapped[uuid.UUID] = _fk("expediente.id")
    consultor_id: Mapped[uuid.UUID] = _fk("usuario.id")
    vigente_desde: Mapped[datetime] = mapped_column(TZ, server_default=func.now())
    vigente_hasta: Mapped[datetime | None] = mapped_column(TZ)


# ================================================================ Autoevaluación, criterios, evidencias
class Autoevaluacion(Base):
    __tablename__ = "autoevaluacion"
    id: Mapped[uuid.UUID] = _pk()
    expediente_id: Mapped[uuid.UUID] = _fk("expediente.id")
    criterio_id: Mapped[uuid.UUID] = _fk("criterio.id")
    respuesta: Mapped[str] = mapped_column(RespuestaAutoevaluacionEnum)
    comentario: Mapped[str | None] = mapped_column(Text)
    fecha: Mapped[datetime] = mapped_column(TZ, server_default=func.now())
    registrado_por: Mapped[uuid.UUID] = _fk("usuario.id")


class CriterioParque(Base):
    __tablename__ = "criterio_parque"
    id: Mapped[uuid.UUID] = _pk()
    expediente_id: Mapped[uuid.UUID] = _fk("expediente.id")
    criterio_id: Mapped[uuid.UUID] = _fk("criterio.id")
    estado_calificacion: Mapped[str] = mapped_column(EstadoCalificacionEnum, server_default="pendiente")
    fecha_ultimo_cambio: Mapped[datetime | None] = mapped_column(TZ)
    motivo_reapertura: Mapped[str | None] = mapped_column(Text)
    calificado_por: Mapped[uuid.UUID | None] = _fk("usuario.id")


class CalificacionCriterio(Base):
    """[D-19] Historial de calificaciones (RD-14). Solo se insertan renglones; la base rechaza UPDATE y DELETE."""

    __tablename__ = "calificacion_criterio"
    id: Mapped[uuid.UUID] = _pk()
    criterio_parque_id: Mapped[uuid.UUID] = _fk("criterio_parque.id")
    estado_anterior: Mapped[str] = mapped_column(EstadoCalificacionEnum)
    estado_nuevo: Mapped[str] = mapped_column(EstadoCalificacionEnum)
    motivo: Mapped[str | None] = mapped_column(Text)
    origen: Mapped[str] = mapped_column(String(10))
    consultor_id: Mapped[uuid.UUID | None] = _fk("usuario.id")
    fecha: Mapped[datetime] = mapped_column(TZ, server_default=func.now())


class Evidencia(Base):
    __tablename__ = "evidencia"
    id: Mapped[uuid.UUID] = _pk()
    expediente_id: Mapped[uuid.UUID] = _fk("expediente.id")
    fase: Mapped[str] = mapped_column(String(40), ForeignKey("catalogo_fase.clave"))
    categoria: Mapped[str] = mapped_column(CategoriaEvidenciaEnum)
    descripcion: Mapped[str | None] = mapped_column(Text)
    fecha_carga: Mapped[datetime] = mapped_column(TZ, server_default=func.now())
    eliminada_en: Mapped[datetime | None] = mapped_column(TZ)
    eliminada_por: Mapped[uuid.UUID | None] = _fk("usuario.id")


class VersionEvidencia(Base):
    __tablename__ = "version_evidencia"
    evidencia_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("evidencia.id"), primary_key=True
    )
    numero: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombre_archivo: Mapped[str] = mapped_column(String(255))
    tipo_mime: Mapped[str] = mapped_column(String(100))
    tamano_bytes: Mapped[int] = mapped_column(BigInteger)
    ruta_objeto: Mapped[str] = mapped_column(String(1024))
    fecha_carga: Mapped[datetime] = mapped_column(TZ, server_default=func.now())
    autor_id: Mapped[uuid.UUID] = _fk("usuario.id")


class VinculoEvidencia(Base):
    __tablename__ = "vinculo_evidencia"
    evidencia_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    criterio_parque_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    expediente_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True))
    estado: Mapped[str] = mapped_column(EstadoVinculoEnum, server_default="enviada")
    fecha_estado: Mapped[datetime] = mapped_column(TZ, server_default=func.now())


class Observacion(Base):
    __tablename__ = "observacion"
    id: Mapped[uuid.UUID] = _pk()
    evidencia_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True))
    criterio_parque_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True))
    version: Mapped[int] = mapped_column(Integer)
    motivo: Mapped[str] = mapped_column(Text)
    fecha: Mapped[datetime] = mapped_column(TZ, server_default=func.now())
    notificado_a_appi: Mapped[bool] = mapped_column(Boolean, server_default="false")
    consultor_id: Mapped[uuid.UUID] = _fk("usuario.id")


class Recomendacion(Base):
    __tablename__ = "recomendacion"
    id: Mapped[uuid.UUID] = _pk()
    criterio_parque_id: Mapped[uuid.UUID] = _fk("criterio_parque.id")
    texto: Mapped[str] = mapped_column(Text)
    fecha: Mapped[datetime] = mapped_column(TZ, server_default=func.now())
    consultor_id: Mapped[uuid.UUID] = _fk("usuario.id")


# ================================================================ Plan de trabajo y análisis de riesgos
class RenglonPlanTrabajo(Base):
    __tablename__ = "renglon_plan_trabajo"
    id: Mapped[uuid.UUID] = _pk()
    expediente_id: Mapped[uuid.UUID] = _fk("expediente.id")
    criterio_parque_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True))
    responsable_id: Mapped[uuid.UUID] = _fk("usuario.id")
    fecha_comprometida: Mapped[date] = mapped_column(Date)
    fecha_marca_atraso: Mapped[date | None] = mapped_column(Date)


class RevisionAnalisisRiesgos(Base):
    __tablename__ = "revision_analisis_riesgos"
    id: Mapped[uuid.UUID] = _pk()
    expediente_id: Mapped[uuid.UUID] = _fk("expediente.id")
    fecha_revision: Mapped[date] = mapped_column(Date)
    version: Mapped[str] = mapped_column(String(50))
    firmante: Mapped[str] = mapped_column(String(300))
    resumen: Mapped[str] = mapped_column(Text)
    ciclo: Mapped[str] = mapped_column(String(50))
    registrado_por: Mapped[uuid.UUID] = _fk("usuario.id")


class DocumentoAnalisisRiesgos(Base):
    __tablename__ = "documento_analisis_riesgos"
    expediente_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("expediente.id"), primary_key=True
    )
    nombre_archivo: Mapped[str] = mapped_column(String(255))
    ruta_objeto: Mapped[str] = mapped_column(String(1024))
    tamano_bytes: Mapped[int] = mapped_column(BigInteger)
    fecha_carga: Mapped[datetime] = mapped_column(TZ, server_default=func.now())
    subido_por: Mapped[uuid.UUID] = _fk("usuario.id")


# ================================================================ Opiniones, desempeño, comité y dictamen
class OpinionCumplimiento(Base):
    __tablename__ = "opinion_cumplimiento"
    id: Mapped[uuid.UUID] = _pk()
    expediente_id: Mapped[uuid.UUID] = _fk("expediente.id")
    tipo: Mapped[str] = mapped_column(TipoOpinionEnum)
    favorable: Mapped[bool | None] = mapped_column(Boolean)
    porcentaje_obligatorios: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    porcentaje_avance_general: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    comentarios: Mapped[str | None] = mapped_column(Text)
    fecha: Mapped[datetime] = mapped_column(TZ, server_default=func.now())
    consultor_id: Mapped[uuid.UUID] = _fk("usuario.id")


class EvaluacionDesempeno(Base):
    __tablename__ = "evaluacion_desempeno"
    id: Mapped[uuid.UUID] = _pk()
    expediente_id: Mapped[uuid.UUID] = _fk("expediente.id")
    folio: Mapped[str] = mapped_column(String(20))
    fecha: Mapped[datetime] = mapped_column(TZ, server_default=func.now())
    version_catalogo: Mapped[str] = mapped_column(String(100))
    resultado: Mapped[str] = mapped_column(Text)
    consultor_id: Mapped[uuid.UUID] = _fk("usuario.id")


class SesionComite(Base):
    __tablename__ = "sesion_comite"
    id: Mapped[uuid.UUID] = _pk()
    expediente_id: Mapped[uuid.UUID] = _fk("expediente.id")
    consultor_comite_id: Mapped[uuid.UUID] = _fk("usuario.id")
    fecha_apertura: Mapped[datetime] = mapped_column(TZ, server_default=func.now())
    fecha_cierre: Mapped[datetime | None] = mapped_column(TZ)


class Dictamen(Base):
    """[D-17] Pertenece al expediente; la sesión de comité es opcional (RF-14-AC-8)."""

    __tablename__ = "dictamen"
    id: Mapped[uuid.UUID] = _pk()
    expediente_id: Mapped[uuid.UUID] = _fk("expediente.id")
    sesion_comite_id: Mapped[uuid.UUID | None] = _fk("sesion_comite.id")
    tipo: Mapped[str] = mapped_column(TipoDictamenEnum)
    motivo: Mapped[str] = mapped_column(Text)
    estado: Mapped[str] = mapped_column(EstadoDictamenEnum, server_default="borrador")
    fecha_captura: Mapped[datetime] = mapped_column(TZ, server_default=func.now())
    capturado_por: Mapped[uuid.UUID] = _fk("usuario.id")
    fecha_firma: Mapped[datetime | None] = mapped_column(TZ)
    firmado_por: Mapped[uuid.UUID | None] = _fk("usuario.id")
    vigencia_hasta: Mapped[date | None] = mapped_column(Date)


# ================================================================ Bitácora y correo
class RegistroBitacora(Base):
    __tablename__ = "registro_bitacora"
    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    fecha_hora: Mapped[datetime] = mapped_column(TZ, server_default=func.now())
    usuario_id: Mapped[uuid.UUID | None] = _fk("usuario.id")
    rol: Mapped[str | None] = mapped_column(RolEnum)
    parque_id: Mapped[uuid.UUID | None] = _fk("parque.id")
    accion: Mapped[str] = mapped_column(String(100))
    recurso_tipo: Mapped[str | None] = mapped_column(String(50))
    recurso_id: Mapped[str | None] = mapped_column(String(100))
    resultado: Mapped[str] = mapped_column(String(10))
    detalle: Mapped[str | None] = mapped_column(Text)


class MensajeCorreo(Base):
    __tablename__ = "mensaje_correo"
    id: Mapped[uuid.UUID] = _pk()
    usuario_id: Mapped[uuid.UUID | None] = _fk("usuario.id")
    tipo: Mapped[str] = mapped_column(String(50))
    destinatario: Mapped[str] = mapped_column(String(254))
    asunto: Mapped[str] = mapped_column(String(300))
    cuerpo: Mapped[str] = mapped_column(Text)
    creado_en: Mapped[datetime] = mapped_column(TZ, server_default=func.now())
    intentos: Mapped[int] = mapped_column(Integer, server_default="0")
    ultimo_error: Mapped[str | None] = mapped_column(Text)
    enviado_en: Mapped[datetime | None] = mapped_column(TZ)
