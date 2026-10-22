"""Esquemas Pydantic v2 de openapi_equipo.yaml (solo los de las operaciones implementadas).

Todos heredan de `Esquema`, con alias camelCase. Donde el contrato no sigue la conversión
automática (tipoPI, tamanoMaximoEvidenciaMB) el alias va explícito.
"""

import uuid
from datetime import date, datetime
from typing import Annotated, Generic, Literal, TypeVar, Union

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

from app import modelos as m

Rol = Literal[m.ROLES]  # type: ignore[valid-type]
TipoPI = Literal[m.TIPOS_PI]  # type: ignore[valid-type]
Marca = Literal[m.MARCAS]  # type: ignore[valid-type]
MarcaAplicable = Literal["O", "R"]
Region = Literal[m.REGIONES]  # type: ignore[valid-type]
EstadoParque = Literal[m.ESTADOS_PARQUE]  # type: ignore[valid-type]
EstadoUsuario = Literal[m.ESTADOS_USUARIO]  # type: ignore[valid-type]
EstadoCalificacion = Literal[m.ESTADOS_CALIFICACION]  # type: ignore[valid-type]
CategoriaEvidencia = Literal[m.CATEGORIAS_EVIDENCIA]  # type: ignore[valid-type]
Fase = Literal[m.FASES]  # type: ignore[valid-type]
EstadoFase = Literal[m.ESTADOS_FASE]  # type: ignore[valid-type]
RespuestaAutoevaluacion = Literal[m.RESPUESTAS_AUTOEVALUACION]  # type: ignore[valid-type]

PATRON_CORREO = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"


class Esquema(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, from_attributes=True)


T = TypeVar("T")


class Pagina(Esquema, Generic[T]):
    pagina: int = Field(ge=1)
    tamano_pagina: int = Field(ge=1, le=100)
    total: int = Field(ge=0)
    items: list[T]


# ---------------------------------------------------------------- comunes
class DetalleError(Esquema):
    campo: str
    problema: str


class Error(Esquema):
    codigo: str
    mensaje: str
    detalles: list[DetalleError] | None = None


class Salud(Esquema):
    estado: Literal["ok", "degradado"]
    base_datos: Literal["ok", "sin_respuesta"]
    ultima_corrida_worker: datetime | None


# ---------------------------------------------------------------- catálogo
class VersionCatalogo(Esquema):
    id: uuid.UUID
    nombre: str
    vigente: bool
    total_criterios: int
    fecha_carga: datetime
    cargado_por: uuid.UUID
    estado: Literal["activa", "solo_lectura"]


class MarcasPorTipo(Esquema):
    construccion_abierto: Marca
    construccion_cerrado: Marca
    operacion_abierto: Marca
    operacion_cerrado: Marca


class Criterio(Esquema):
    id: uuid.UUID
    version_catalogo_id: uuid.UUID
    estandar: int = Field(ge=1, le=10)
    subestandar: str
    clave: str
    texto: str
    metodo_verificacion: str
    categoria_evidencia: CategoriaEvidencia
    evidencia_suficiente: str | None
    marcas: MarcasPorTipo | None = None


class CriterioUpdate(Esquema):
    evidencia_suficiente: str = Field(min_length=1, max_length=4000)


# ---------------------------------------------------------------- generaciones
class GeneracionCreate(Esquema):
    nombre: str = Field(min_length=1, max_length=100)
    fecha_inicio: date
    version_catalogo_id: uuid.UUID


class Generacion(Esquema):
    id: uuid.UUID
    nombre: str
    fecha_inicio: date
    version_catalogo_id: uuid.UUID
    version_catalogo_nombre: str
    total_parques: int


# ---------------------------------------------------------------- parques
class ParqueCreate(Esquema):
    tipo_registro: Literal["activo"]
    nombre: str = Field(min_length=1, max_length=200)
    desarrollador: str = Field(min_length=1, max_length=200)
    tipo_pi: TipoPI = Field(alias="tipoPI")
    region: Region
    generacion_id: uuid.UUID


class ParqueHistoricoCreate(Esquema):
    tipo_registro: Literal["historico"]
    nombre: str = Field(min_length=1, max_length=200)
    region: Region
    fecha_ultimo_dictamen: date
    fecha_termino_programa: date


ParqueAlta = Annotated[Union[ParqueCreate, ParqueHistoricoCreate], Field(discriminator="tipo_registro")]


class ParqueUpdate(Esquema):
    nombre: str | None = Field(default=None, min_length=1, max_length=200)
    desarrollador: str | None = Field(default=None, min_length=1, max_length=200)
    region: Region | None = None
    fecha_termino_programa: date | None = None
    fecha_proxima_actualizacion: date | None = None
    estado: Literal["inactivo"] | None = None
    motivo: str | None = Field(default=None, min_length=1)


class Parque(Esquema):
    id: uuid.UUID
    tipo_registro: Literal["activo", "historico"]
    nombre: str
    desarrollador: str | None = None
    tipo_pi: TipoPI | None = Field(default=None, alias="tipoPI")
    region: Region
    generacion_id: uuid.UUID | None = None
    estado: EstadoParque
    fase: Fase | None = None
    fecha_alta: date
    version_catalogo: str | None = None
    consultor_asignado_id: uuid.UUID | None = None
    fecha_termino_programa: date | None = None
    fecha_proxima_actualizacion: date | None = None
    fecha_ultima_actualizacion: date | None = None
    fecha_ultimo_dictamen: date | None = None
    atrasado_actualizacion: bool
    motivo_baja: str | None = None
    contacto_principal_id: uuid.UUID | None = None


class CambioTipoPI(Esquema):
    tipo_pi: TipoPI = Field(alias="tipoPI")
    fecha_cambio: date
    motivo: str = Field(min_length=1)


class ClasificacionTipoPI(Esquema):
    id: uuid.UUID
    tipo_pi: TipoPI = Field(alias="tipoPI")
    fecha_desde: date
    fecha_hasta: date | None
    porcentaje_obligatorios_al_cierre: float | None = None
    porcentaje_avance_general_al_cierre: float | None = None
    motivo: str | None = None
    cambiado_por: uuid.UUID | None = None


class CambioTipoPIResultado(Esquema):
    parque: Parque
    cambio: bool
    clasificacion_cerrada: ClasificacionTipoPI | None = None
    clasificacion_nueva: ClasificacionTipoPI | None = None
    criterios_que_dejan_de_ser_na: list[uuid.UUID] = Field(alias="criteriosQueDejanDeSerNA")
    criterios_que_pasan_a_na: list[uuid.UUID] = Field(alias="criteriosQuePasanANA")


class ActualizacionAnualCreate(Esquema):
    fecha: date
    notas: str | None = None


class ActualizacionAnual(Esquema):
    id: uuid.UUID
    parque_id: uuid.UUID
    fecha: date
    fecha_proxima_actualizacion: date
    notas: str | None = None
    registrado_por: uuid.UUID


# ---------------------------------------------------------------- usuarios
class UsuarioCreate(Esquema):
    correo: str = Field(max_length=254, pattern=PATRON_CORREO)
    nombre: str = Field(min_length=1, max_length=200)
    rol: Rol
    parque_id: uuid.UUID | None = None
    desarrollador: str | None = Field(default=None, max_length=200)


class UsuarioUpdate(Esquema):
    nombre: str | None = Field(default=None, min_length=1, max_length=200)
    rol: Rol | None = None
    parque_id: uuid.UUID | None = None
    desarrollador: str | None = Field(default=None, max_length=200)
    estado: Literal["inactivo"] | None = None
    motivo: str | None = Field(default=None, min_length=1)


class Usuario(Esquema):
    id: uuid.UUID
    correo: str
    nombre: str
    rol: Rol
    parque_id: uuid.UUID | None = None
    desarrollador: str | None = None
    estado: EstadoUsuario
    fecha_alta: datetime


class UsuarioParque(Usuario):
    contacto_principal: bool


class ContactoPrincipalUpdate(Esquema):
    usuario_id: uuid.UUID


# ---------------------------------------------------------------- asignaciones
class AsignacionConsultorCreate(Esquema):
    consultor_id: uuid.UUID


class AsignacionConsultor(Esquema):
    id: uuid.UUID
    parque_id: uuid.UUID
    generacion_id: uuid.UUID
    consultor_id: uuid.UUID
    consultor_nombre: str
    vigente_desde: datetime
    vigente_hasta: datetime | None
    vigente: bool


# ---------------------------------------------------------------- criterios del parque
class CriterioParque(Esquema):
    criterio_id: uuid.UUID
    clave: str
    estandar: int
    texto: str
    marca: MarcaAplicable
    evidencia_suficiente: str | None = None
    estado_calificacion: EstadoCalificacion
    fecha_ultimo_cambio: datetime | None
    registrado_por: str | None
    atrasado: bool
    total_evidencias: int = Field(ge=0)


# ---------------------------------------------------------------- autoevaluación
class AutoevaluacionUpsert(Esquema):
    respuesta: RespuestaAutoevaluacion
    comentario: str | None = None


class Autoevaluacion(Esquema):
    parque_id: uuid.UUID
    generacion_id: uuid.UUID
    criterio_id: uuid.UUID
    respuesta: RespuestaAutoevaluacion
    comentario: str | None = None
    version_catalogo: str
    registrado_por: uuid.UUID
    fecha: datetime


# ---------------------------------------------------------------- cumplimiento
class CifrasCumplimiento(Esquema):
    obligatorios_aplicables: int
    obligatorios_cumplidos: int
    recomendados_aplicables: int
    recomendados_cumplidos: int
    porcentaje_obligatorios: float | None
    porcentaje_avance_general: float | None
    no_aplica: bool
    porcentaje_recomendados: float | None


class CumplimientoEstandar(CifrasCumplimiento):
    estandar: int = Field(ge=1, le=10)


class Cumplimiento(Esquema):
    parque_id: uuid.UUID
    tipo_pi: TipoPI = Field(alias="tipoPI")
    fecha_calculo: datetime
    total: CifrasCumplimiento
    por_estandar: list[CumplimientoEstandar]


# ---------------------------------------------------------------- plan de trabajo
class RenglonPlanTrabajoCreate(Esquema):
    criterio_id: uuid.UUID
    responsable_id: uuid.UUID
    fecha_comprometida: date


class RenglonPlanTrabajoUpdate(Esquema):
    responsable_id: uuid.UUID | None = None
    fecha_comprometida: date | None = None


class RenglonPlanTrabajo(Esquema):
    id: uuid.UUID
    parque_id: uuid.UUID
    criterio_id: uuid.UUID
    responsable_id: uuid.UUID
    responsable_nombre: str
    fecha_comprometida: date
    estado_criterio: EstadoCalificacion
    atrasado: bool
    fecha_marca_atraso: date | None


# ---------------------------------------------------------------- análisis de riesgos
class RevisionAnalisisRiesgosCreate(Esquema):
    fecha_revision: date
    version: str = Field(min_length=1, max_length=50)
    firmante: str = Field(min_length=1, max_length=300)
    resumen: str = Field(min_length=1)


class RevisionAnalisisRiesgos(Esquema):
    id: uuid.UUID
    parque_id: uuid.UUID
    fecha_revision: date
    version: str
    firmante: str
    resumen: str
    ciclo: str
    vigente: bool
    registrado_por: uuid.UUID


# ---------------------------------------------------------------- fases
class FaseExpediente(Esquema):
    fase: Fase
    orden: int = Field(ge=1, le=9)
    nombre: str
    estado: EstadoFase
    actual: bool
    fecha_inicio: datetime | None = None
    fecha_cierre: datetime | None = None
    cerrada_por: uuid.UUID | None = None
    motivo_excepcion: str | None = None


class AvanceFaseCreate(Esquema):
    fase_destino: Fase
    motivo: str | None = None


# ---------------------------------------------------------------- configuración
class Configuracion(Esquema):
    tamano_maximo_evidencia_mb: int = Field(alias="tamanoMaximoEvidenciaMB")
    vigencia_distintivo_anios: int
    actualizado_en: datetime
    actualizado_por: uuid.UUID | None = None


class ConfiguracionUpdate(Esquema):
    # Mayor a 100 se rechaza en el router con 422 limite_excede_maximo y el texto literal.
    tamano_maximo_evidencia_mb: int | None = Field(default=None, ge=1, alias="tamanoMaximoEvidenciaMB")
    vigencia_distintivo_anios: int | None = Field(default=None, ge=1, le=10)


# ---------------------------------------------------------------- bitácora
class RegistroBitacora(Esquema):
    id: int
    fecha_hora: datetime
    usuario_id: uuid.UUID | None = None
    rol: Rol | None = None
    parque_id: uuid.UUID | None = None
    accion: str
    recurso_tipo: str | None = None
    recurso_id: str | None = None
    resultado: Literal["exitoso", "denegado", "fallido"]
    detalle: str | None = None
