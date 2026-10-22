-- =====================================================================
-- SGPIS: esquema físico de la base de datos (PostgreSQL 16)
-- Equipo 19, S05-S06-A1. Fuentes: diagrama_clases_equipo.puml y openapi_equipo.yaml v2.0.0
-- Parte del borrador del agente (evidencia_agente/esquema_bd_v0.sql); cada corrección
-- del equipo está marcada con [R-xx] y explicada en revision_sql.md.
-- Ejecutar sobre una base vacía:  psql -v ON_ERROR_STOP=1 -f esquema_bd.sql
-- Convenciones: snake_case en español sin acentos; ids uuid con
-- gen_random_uuid(); fechas de negocio en date; marcas de tiempo en
-- timestamptz; porcentajes en numeric(5,2).
-- =====================================================================

BEGIN;

-- ===================== Tipos enumerados =====================
CREATE TYPE rol AS ENUM (
  'coordinacion_ampip', 'director_general_ampip', 'appi', 'consultor',
  'gerente_corporativo', 'administrador_tecnico'
);
CREATE TYPE tipo_pi AS ENUM (
  'construccion_abierto', 'construccion_cerrado', 'operacion_abierto', 'operacion_cerrado'
);
CREATE TYPE marca AS ENUM ('O', 'R', 'NA');
CREATE TYPE estado_calificacion AS ENUM ('pendiente', 'en_revision', 'cumplido', 'no_cumplido');
CREATE TYPE estado_vinculo AS ENUM ('enviada', 'observada', 'aceptada');
CREATE TYPE categoria_evidencia AS ENUM ('seguridad', 'administrativa');
CREATE TYPE estado_fase AS ENUM ('pendiente', 'en_proceso', 'completada', 'avanzada_por_excepcion');
CREATE TYPE tipo_dictamen AS ENUM ('otorgar', 'no_otorgar');
CREATE TYPE estado_dictamen AS ENUM ('borrador', 'firmado');
CREATE TYPE respuesta_autoevaluacion AS ENUM ('cumple', 'cumple_parcial', 'no_cumple');
CREATE TYPE estado_usuario AS ENUM ('pendiente_activacion', 'activo', 'inactivo');
CREATE TYPE estado_parque AS ENUM ('activo', 'inactivo', 'historico');
CREATE TYPE tipo_opinion AS ENUM ('intermedia', 'final');
CREATE TYPE region AS ENUM (
  'MX-AGU', 'MX-BCN', 'MX-BCS', 'MX-CAM', 'MX-CHP', 'MX-CHH', 'MX-CMX', 'MX-COA',
  'MX-COL', 'MX-DUR', 'MX-GUA', 'MX-GRO', 'MX-HID', 'MX-JAL', 'MX-MEX', 'MX-MIC',
  'MX-MOR', 'MX-NAY', 'MX-NLE', 'MX-OAX', 'MX-PUE', 'MX-QUE', 'MX-ROO', 'MX-SLP',
  'MX-SIN', 'MX-SON', 'MX-TAB', 'MX-TAM', 'MX-TLA', 'MX-VER', 'MX-YUC', 'MX-ZAC'
);

-- ===================== Organización (parte 1) =====================
CREATE TABLE desarrollador (
  id      uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  nombre  varchar(200) NOT NULL,
  CONSTRAINT uq_desarrollador_nombre UNIQUE (nombre)
);

-- ===================== Usuarios, acceso y configuración =====================
CREATE TABLE usuario (
  id                uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  nombre            varchar(200) NOT NULL,
  correo            varchar(254) NOT NULL,
  contrasena_hash   varchar(255),
  rol               rol NOT NULL,
  estado            estado_usuario NOT NULL DEFAULT 'pendiente_activacion',
  fecha_alta        timestamptz NOT NULL DEFAULT now(),
  motivo_baja       text,
  parque_id         uuid,            -- APPI de (FK agregada después de crear parque)
  desarrollador_id  uuid REFERENCES desarrollador (id),  -- gerente corporativo de
  CONSTRAINT ck_usuario_activo_con_contrasena
    CHECK (estado <> 'activo' OR contrasena_hash IS NOT NULL),
  CONSTRAINT ck_usuario_baja_con_motivo
    CHECK (estado <> 'inactivo' OR motivo_baja IS NOT NULL),
  -- [R-06] El parque solo existe para APPI y el desarrollador solo para gerente corporativo.
  CONSTRAINT ck_usuario_appi_con_parque
    CHECK ((rol = 'appi') = (parque_id IS NOT NULL)),
  CONSTRAINT ck_usuario_gerente_con_desarrollador
    CHECK ((rol = 'gerente_corporativo') = (desarrollador_id IS NOT NULL)),
  -- [R-05] Destino de la FK compuesta del contacto principal.
  CONSTRAINT uq_usuario_id_parque UNIQUE (id, parque_id)
);
CREATE UNIQUE INDEX uq_usuario_correo ON usuario (lower(correo));
CREATE INDEX ix_usuario_nombre ON usuario (nombre);
CREATE INDEX ix_usuario_rol_estado ON usuario (rol, estado);
CREATE INDEX ix_usuario_parque ON usuario (parque_id);
CREATE INDEX ix_usuario_desarrollador ON usuario (desarrollador_id);

CREATE TABLE sesion (
  sid               uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  usuario_id        uuid NOT NULL REFERENCES usuario (id) ON DELETE CASCADE,
  creada            timestamptz NOT NULL DEFAULT now(),
  ultima_actividad  timestamptz NOT NULL DEFAULT now(),
  expira_en         timestamptz NOT NULL,
  revocada_en       timestamptz,
  CONSTRAINT ck_sesion_expira CHECK (expira_en > creada)
);
CREATE INDEX ix_sesion_usuario ON sesion (usuario_id) WHERE revocada_en IS NULL;

CREATE TABLE enlace_un_solo_uso (
  id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  usuario_id  uuid NOT NULL REFERENCES usuario (id) ON DELETE CASCADE,
  token_hash  varchar(255) NOT NULL,
  tipo        varchar(20) NOT NULL CHECK (tipo IN ('invitacion', 'recuperacion')),
  creado      timestamptz NOT NULL DEFAULT now(),
  expira_en   timestamptz NOT NULL,
  usado_en    timestamptz,
  CONSTRAINT uq_enlace_token_hash UNIQUE (token_hash),
  CONSTRAINT ck_enlace_expira CHECK (expira_en > creado)
);
CREATE INDEX ix_enlace_usuario ON enlace_un_solo_uso (usuario_id);

-- Sin FK a usuario: el contador corre también para correos inexistentes.
CREATE TABLE intento_login (
  -- [R-09] El contador se busca por correo en minúsculas; sin esto "A@x.mx" y "a@x.mx" contarían aparte.
  correo             varchar(254) PRIMARY KEY CHECK (correo = lower(correo)),
  intentos_fallidos  integer NOT NULL DEFAULT 0 CHECK (intentos_fallidos >= 0),
  bloqueado_hasta    timestamptz
);

-- Registro único (C-05, C-10).
CREATE TABLE configuracion (
  id                            smallint PRIMARY KEY DEFAULT 1 CHECK (id = 1),
  tamano_maximo_evidencia_mb    integer NOT NULL DEFAULT 100
                                CHECK (tamano_maximo_evidencia_mb BETWEEN 1 AND 100),
  vigencia_distintivo_anios     integer NOT NULL DEFAULT 3
                                CHECK (vigencia_distintivo_anios BETWEEN 1 AND 10),
  actualizado_en                timestamptz NOT NULL DEFAULT now(),
  actualizado_por               uuid REFERENCES usuario (id)
);

-- ===================== Catálogo =====================
CREATE TABLE version_catalogo (
  id           uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  nombre       varchar(100) NOT NULL,
  estado       varchar(20) NOT NULL DEFAULT 'activa'
               CHECK (estado IN ('activa', 'solo_lectura')),
  fecha_carga  timestamptz NOT NULL DEFAULT now(),
  cargado_por  uuid NOT NULL REFERENCES usuario (id),
  CONSTRAINT uq_version_catalogo_nombre UNIQUE (nombre)
);
-- Una sola versión vigente ("activa") a la vez.
CREATE UNIQUE INDEX uq_version_catalogo_activa ON version_catalogo (estado) WHERE estado = 'activa';

CREATE TABLE estandar (
  id                   uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  version_catalogo_id  uuid NOT NULL REFERENCES version_catalogo (id) ON DELETE CASCADE,
  numero               integer NOT NULL CHECK (numero BETWEEN 1 AND 10),
  nombre               varchar(300) NOT NULL,
  CONSTRAINT uq_estandar_version_numero UNIQUE (version_catalogo_id, numero)
);

CREATE TABLE subestandar (
  id           uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  estandar_id  uuid NOT NULL REFERENCES estandar (id) ON DELETE CASCADE,
  numero       varchar(20) NOT NULL,
  nombre       varchar(300) NOT NULL,
  CONSTRAINT uq_subestandar_estandar_numero UNIQUE (estandar_id, numero)
);

CREATE TABLE criterio (
  id                    uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  subestandar_id        uuid NOT NULL REFERENCES subestandar (id) ON DELETE CASCADE,
  clave                 varchar(20) NOT NULL,
  texto                 text NOT NULL,
  metodo_verificacion   text NOT NULL,
  evidencia_suficiente  varchar(4000),
  categoria_evidencia   categoria_evidencia NOT NULL,
  asterisco             boolean NOT NULL DEFAULT false,
  CONSTRAINT uq_criterio_subestandar_clave UNIQUE (subestandar_id, clave)
);
CREATE INDEX ix_criterio_clave ON criterio (clave);

CREATE TABLE marca_por_tipo (
  criterio_id  uuid NOT NULL REFERENCES criterio (id) ON DELETE CASCADE,
  tipo_pi      tipo_pi NOT NULL,
  marca        marca NOT NULL,
  PRIMARY KEY (criterio_id, tipo_pi)
);
CREATE INDEX ix_marca_por_tipo_tipo_marca ON marca_por_tipo (tipo_pi, marca);

-- Secuencia de fases guardada como datos (C-15, RF-32).
CREATE TABLE catalogo_fase (
  clave   varchar(40) PRIMARY KEY,
  orden   integer NOT NULL CHECK (orden BETWEEN 1 AND 9),
  nombre  varchar(100) NOT NULL,
  CONSTRAINT uq_catalogo_fase_orden UNIQUE (orden)
);

-- ===================== Organización (parte 2) =====================
CREATE TABLE generacion (
  id                   uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  nombre               varchar(100) NOT NULL,
  fecha_inicio         date NOT NULL,
  version_catalogo_id  uuid NOT NULL REFERENCES version_catalogo (id),
  CONSTRAINT uq_generacion_nombre UNIQUE (nombre)
);
CREATE INDEX ix_generacion_version_catalogo ON generacion (version_catalogo_id);

CREATE TABLE parque (
  id                     uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  tipo_registro          varchar(10) NOT NULL CHECK (tipo_registro IN ('activo', 'historico')),
  nombre                 varchar(200) NOT NULL,
  desarrollador_id       uuid REFERENCES desarrollador (id),
  region                 region NOT NULL,
  estado                 estado_parque NOT NULL DEFAULT 'activo',
  fecha_alta             date NOT NULL DEFAULT CURRENT_DATE,
  motivo_baja            text,
  fecha_ultimo_dictamen  date,
  -- [R-01] El parque histórico no tiene expediente; su fecha de término vive aquí (RF-31-AC-2).
  fecha_termino_historico date,
  -- [R-05] FK compuesta al final del script: el contacto debe ser APPI de este parque.
  contacto_principal_id  uuid,
  CONSTRAINT ck_parque_historico_coherente
    CHECK ((tipo_registro = 'historico') = (estado = 'historico')),
  CONSTRAINT ck_parque_historico_datos
    CHECK (tipo_registro <> 'historico'
           OR (fecha_ultimo_dictamen IS NOT NULL AND fecha_termino_historico IS NOT NULL)),
  CONSTRAINT ck_parque_baja_con_motivo
    CHECK (estado <> 'inactivo' OR motivo_baja IS NOT NULL)
);
CREATE INDEX ix_parque_nombre ON parque (nombre);
CREATE INDEX ix_parque_region ON parque (region);
CREATE INDEX ix_parque_estado ON parque (estado);
CREATE INDEX ix_parque_desarrollador ON parque (desarrollador_id);

ALTER TABLE usuario
  ADD CONSTRAINT fk_usuario_parque FOREIGN KEY (parque_id) REFERENCES parque (id);

-- [R-05] RF-34: el contacto principal es un usuario APPI de ESTE parque. La FK compuesta
-- (contacto_principal_id, id) -> usuario (id, parque_id) lo garantiza sin trigger.
ALTER TABLE parque
  ADD CONSTRAINT fk_parque_contacto_principal FOREIGN KEY (contacto_principal_id, id)
  REFERENCES usuario (id, parque_id);

CREATE TABLE clasificacion_tipo_pi (
  id                                  uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  parque_id                           uuid NOT NULL REFERENCES parque (id) ON DELETE CASCADE,
  tipo_pi                             tipo_pi NOT NULL,
  fecha_desde                         date NOT NULL,
  fecha_hasta                         date,
  motivo                              text,
  porcentaje_obligatorios_al_cierre   numeric(5,2) CHECK (porcentaje_obligatorios_al_cierre BETWEEN 0 AND 100),
  porcentaje_avance_general_al_cierre numeric(5,2) CHECK (porcentaje_avance_general_al_cierre BETWEEN 0 AND 100),
  cambiado_por                        uuid REFERENCES usuario (id),
  CONSTRAINT ck_clasificacion_fechas CHECK (fecha_hasta IS NULL OR fecha_hasta >= fecha_desde)
);
CREATE INDEX ix_clasificacion_parque ON clasificacion_tipo_pi (parque_id, fecha_desde);
-- Una sola clasificación abierta (vigente) por parque.
CREATE UNIQUE INDEX uq_clasificacion_vigente ON clasificacion_tipo_pi (parque_id) WHERE fecha_hasta IS NULL;

-- ===================== Expediente por generación =====================
CREATE TABLE expediente (
  id                           uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  -- [R-04] Sin CASCADE: borrar un parque por error no debe arrastrar dictámenes (RNF-14).
  parque_id                    uuid NOT NULL REFERENCES parque (id),
  generacion_id                uuid NOT NULL REFERENCES generacion (id),
  fecha_termino_programa       date,
  fecha_proxima_actualizacion  date,
  CONSTRAINT uq_expediente_parque_generacion UNIQUE (parque_id, generacion_id)
);
CREATE INDEX ix_expediente_generacion ON expediente (generacion_id);
CREATE INDEX ix_expediente_proxima_actualizacion ON expediente (fecha_proxima_actualizacion);

CREATE TABLE fase_expediente (
  expediente_id     uuid NOT NULL REFERENCES expediente (id) ON DELETE CASCADE,
  fase              varchar(40) NOT NULL REFERENCES catalogo_fase (clave),
  estado            estado_fase NOT NULL DEFAULT 'pendiente',
  fecha_inicio      timestamptz,
  fecha_cierre      timestamptz,
  motivo_excepcion  text,
  cerrada_por       uuid REFERENCES usuario (id),
  PRIMARY KEY (expediente_id, fase),
  CONSTRAINT ck_fase_excepcion_con_motivo
    CHECK (estado <> 'avanzada_por_excepcion' OR motivo_excepcion IS NOT NULL),
  CONSTRAINT ck_fase_fechas CHECK (fecha_cierre IS NULL OR fecha_inicio IS NULL OR fecha_cierre >= fecha_inicio)
);
CREATE INDEX ix_fase_expediente_estado ON fase_expediente (fase, estado);
-- [R-07] Una sola fase en proceso por expediente (RF-32-AC-1: "la fase actual").
CREATE UNIQUE INDEX uq_fase_expediente_en_proceso ON fase_expediente (expediente_id) WHERE estado = 'en_proceso';

CREATE TABLE actualizacion_anual (
  id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  expediente_id   uuid NOT NULL REFERENCES expediente (id) ON DELETE CASCADE,
  fecha           date NOT NULL,
  notas           text,
  registrado_por  uuid NOT NULL REFERENCES usuario (id)
);
CREATE INDEX ix_actualizacion_anual_expediente ON actualizacion_anual (expediente_id, fecha);

CREATE TABLE asignacion_consultor (
  id             uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  expediente_id  uuid NOT NULL REFERENCES expediente (id) ON DELETE CASCADE,
  consultor_id   uuid NOT NULL REFERENCES usuario (id),
  vigente_desde  timestamptz NOT NULL DEFAULT now(),
  vigente_hasta  timestamptz,
  CONSTRAINT ck_asignacion_fechas CHECK (vigente_hasta IS NULL OR vigente_hasta >= vigente_desde)
);
CREATE INDEX ix_asignacion_expediente ON asignacion_consultor (expediente_id);
CREATE INDEX ix_asignacion_consultor ON asignacion_consultor (consultor_id) WHERE vigente_hasta IS NULL;
-- Una sola asignación vigente por expediente (RF-10).
CREATE UNIQUE INDEX uq_asignacion_vigente ON asignacion_consultor (expediente_id) WHERE vigente_hasta IS NULL;

-- ===================== Autoevaluación, criterios y evidencias =====================
CREATE TABLE autoevaluacion (
  id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  expediente_id   uuid NOT NULL REFERENCES expediente (id) ON DELETE CASCADE,
  criterio_id     uuid NOT NULL REFERENCES criterio (id),
  respuesta       respuesta_autoevaluacion NOT NULL,
  comentario      text,
  fecha           timestamptz NOT NULL DEFAULT now(),
  registrado_por  uuid NOT NULL REFERENCES usuario (id),
  CONSTRAINT uq_autoevaluacion_expediente_criterio UNIQUE (expediente_id, criterio_id)
);
CREATE INDEX ix_autoevaluacion_criterio ON autoevaluacion (criterio_id);

CREATE TABLE criterio_parque (
  id                   uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  expediente_id        uuid NOT NULL REFERENCES expediente (id) ON DELETE CASCADE,
  criterio_id          uuid NOT NULL REFERENCES criterio (id),
  estado_calificacion  estado_calificacion NOT NULL DEFAULT 'pendiente',
  fecha_ultimo_cambio  timestamptz,
  motivo_reapertura    text,
  calificado_por       uuid REFERENCES usuario (id),
  CONSTRAINT uq_criterio_parque_expediente_criterio UNIQUE (expediente_id, criterio_id),
  -- [R-02] Destino de las FK compuestas que impiden mezclar expedientes.
  CONSTRAINT uq_criterio_parque_id_expediente UNIQUE (id, expediente_id)
);
CREATE INDEX ix_criterio_parque_criterio ON criterio_parque (criterio_id);
CREATE INDEX ix_criterio_parque_estado ON criterio_parque (expediente_id, estado_calificacion);

CREATE TABLE evidencia (
  id             uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  expediente_id  uuid NOT NULL REFERENCES expediente (id) ON DELETE CASCADE,
  fase           varchar(40) NOT NULL REFERENCES catalogo_fase (clave),
  categoria      categoria_evidencia NOT NULL,
  descripcion    text,
  fecha_carga    timestamptz NOT NULL DEFAULT now(),
  eliminada_en   timestamptz,
  eliminada_por  uuid REFERENCES usuario (id),
  CONSTRAINT ck_evidencia_baja_coherente CHECK ((eliminada_en IS NULL) = (eliminada_por IS NULL)),
  CONSTRAINT uq_evidencia_id_expediente UNIQUE (id, expediente_id)  -- [R-02]
);
CREATE INDEX ix_evidencia_expediente_fecha ON evidencia (expediente_id, fecha_carga DESC, id);
CREATE INDEX ix_evidencia_fase ON evidencia (expediente_id, fase);

CREATE TABLE version_evidencia (
  evidencia_id    uuid NOT NULL REFERENCES evidencia (id) ON DELETE CASCADE,
  numero          integer NOT NULL CHECK (numero >= 1),
  nombre_archivo  varchar(255) NOT NULL,
  tipo_mime       varchar(100) NOT NULL CHECK (tipo_mime IN (
                    'application/pdf', 'image/jpeg', 'image/png', 'image/heic',
                    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                    'application/vnd.openxmlformats-officedocument.wordprocessingml.document')),
  tamano_bytes    bigint NOT NULL CHECK (tamano_bytes BETWEEN 1 AND 104857600),
  ruta_objeto     varchar(1024) NOT NULL,
  fecha_carga     timestamptz NOT NULL DEFAULT now(),
  -- [R-12] Se quitó "comentario": no está en el diagrama ni en ningún schema del contrato.
  autor_id        uuid NOT NULL REFERENCES usuario (id),
  PRIMARY KEY (evidencia_id, numero),
  CONSTRAINT uq_version_evidencia_ruta UNIQUE (ruta_objeto)
);
CREATE INDEX ix_version_evidencia_autor ON version_evidencia (autor_id);

-- [R-02] El v0 permitía vincular una evidencia del parque X a un criterio del parque Y (fuga
-- entre parques, RNF-01). Con expediente_id en ambas FK compuestas, la base lo rechaza.
CREATE TABLE vinculo_evidencia (
  evidencia_id        uuid NOT NULL,
  criterio_parque_id  uuid NOT NULL,
  expediente_id       uuid NOT NULL,
  estado              estado_vinculo NOT NULL DEFAULT 'enviada',
  fecha_estado        timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY (evidencia_id, criterio_parque_id),
  CONSTRAINT fk_vinculo_evidencia FOREIGN KEY (evidencia_id, expediente_id)
    REFERENCES evidencia (id, expediente_id) ON DELETE CASCADE,
  CONSTRAINT fk_vinculo_criterio_parque FOREIGN KEY (criterio_parque_id, expediente_id)
    REFERENCES criterio_parque (id, expediente_id) ON DELETE CASCADE
);
CREATE INDEX ix_vinculo_criterio_parque ON vinculo_evidencia (criterio_parque_id, estado);

CREATE TABLE observacion (
  id                  uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  evidencia_id        uuid NOT NULL,
  criterio_parque_id  uuid NOT NULL,
  version             integer NOT NULL,
  motivo              text NOT NULL,
  fecha               timestamptz NOT NULL DEFAULT now(),
  notificado_a_appi   boolean NOT NULL DEFAULT false,
  consultor_id        uuid NOT NULL REFERENCES usuario (id),
  CONSTRAINT fk_observacion_vinculo FOREIGN KEY (evidencia_id, criterio_parque_id)
    REFERENCES vinculo_evidencia (evidencia_id, criterio_parque_id) ON DELETE CASCADE,
  CONSTRAINT fk_observacion_version FOREIGN KEY (evidencia_id, version)
    REFERENCES version_evidencia (evidencia_id, numero)
);
CREATE INDEX ix_observacion_vinculo ON observacion (evidencia_id, criterio_parque_id);
CREATE INDEX ix_observacion_consultor ON observacion (consultor_id);

CREATE TABLE recomendacion (
  id                  uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  criterio_parque_id  uuid NOT NULL REFERENCES criterio_parque (id) ON DELETE CASCADE,
  texto               text NOT NULL,
  fecha               timestamptz NOT NULL DEFAULT now(),
  consultor_id        uuid NOT NULL REFERENCES usuario (id)
);
CREATE INDEX ix_recomendacion_criterio_parque ON recomendacion (criterio_parque_id, fecha);

-- ===================== Plan de trabajo y análisis de riesgos =====================
CREATE TABLE renglon_plan_trabajo (
  id                  uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  expediente_id       uuid NOT NULL REFERENCES expediente (id) ON DELETE CASCADE,
  criterio_parque_id  uuid NOT NULL,
  responsable_id      uuid NOT NULL REFERENCES usuario (id),
  fecha_comprometida  date NOT NULL,
  fecha_marca_atraso  date,
  CONSTRAINT uq_renglon_criterio_parque UNIQUE (criterio_parque_id),
  -- [R-03] El v0 guardaba expediente_id y criterio_parque_id sin amarrarlos entre sí.
  CONSTRAINT fk_renglon_criterio_parque FOREIGN KEY (criterio_parque_id, expediente_id)
    REFERENCES criterio_parque (id, expediente_id) ON DELETE CASCADE
);
CREATE INDEX ix_renglon_expediente_fecha ON renglon_plan_trabajo (expediente_id, fecha_comprometida);
CREATE INDEX ix_renglon_responsable ON renglon_plan_trabajo (responsable_id);

CREATE TABLE revision_analisis_riesgos (
  id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  expediente_id   uuid NOT NULL REFERENCES expediente (id) ON DELETE CASCADE,
  fecha_revision  date NOT NULL,
  version         varchar(50) NOT NULL,
  firmante        varchar(300) NOT NULL,
  resumen         text NOT NULL,
  ciclo           varchar(50) NOT NULL,
  registrado_por  uuid NOT NULL REFERENCES usuario (id)
);
CREATE INDEX ix_revision_ar_expediente_ciclo ON revision_analisis_riesgos (expediente_id, ciclo, fecha_revision DESC);

-- 0..1 por expediente: la PK es la FK.
CREATE TABLE documento_analisis_riesgos (
  expediente_id   uuid PRIMARY KEY REFERENCES expediente (id) ON DELETE CASCADE,
  nombre_archivo  varchar(255) NOT NULL,
  ruta_objeto     varchar(1024) NOT NULL,
  tamano_bytes    bigint NOT NULL CHECK (tamano_bytes >= 1),
  fecha_carga     timestamptz NOT NULL DEFAULT now(),
  subido_por      uuid NOT NULL REFERENCES usuario (id),
  CONSTRAINT uq_documento_ar_ruta UNIQUE (ruta_objeto)
);

-- ===================== Opiniones, desempeño, comité y dictamen =====================
-- OpinionIntermedia y OpinionFinal en una sola tabla con discriminador "tipo".
CREATE TABLE opinion_cumplimiento (
  id                         uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  expediente_id              uuid NOT NULL REFERENCES expediente (id) ON DELETE CASCADE,
  tipo                       tipo_opinion NOT NULL,
  favorable                  boolean,
  porcentaje_obligatorios    numeric(5,2) CHECK (porcentaje_obligatorios BETWEEN 0 AND 100),
  porcentaje_avance_general  numeric(5,2) CHECK (porcentaje_avance_general BETWEEN 0 AND 100),
  comentarios                text,
  fecha                      timestamptz NOT NULL DEFAULT now(),
  consultor_id               uuid NOT NULL REFERENCES usuario (id),
  CONSTRAINT uq_opinion_expediente_tipo UNIQUE (expediente_id, tipo),
  CONSTRAINT ck_opinion_favorable_solo_final CHECK ((tipo = 'final') = (favorable IS NOT NULL))
);
CREATE INDEX ix_opinion_consultor ON opinion_cumplimiento (consultor_id);

CREATE TABLE evaluacion_desempeno (
  id                uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  expediente_id     uuid NOT NULL REFERENCES expediente (id) ON DELETE CASCADE,
  folio             varchar(20) NOT NULL CHECK (folio ~ '^ED-\d{4}-\d{4}$'),
  fecha             timestamptz NOT NULL DEFAULT now(),
  version_catalogo  varchar(100) NOT NULL,
  resultado         text NOT NULL,
  consultor_id      uuid NOT NULL REFERENCES usuario (id),
  CONSTRAINT uq_evaluacion_expediente UNIQUE (expediente_id),
  CONSTRAINT uq_evaluacion_folio UNIQUE (folio)
);

CREATE TABLE sesion_comite (
  id                   uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  expediente_id        uuid NOT NULL REFERENCES expediente (id),  -- [R-04] sin CASCADE
  consultor_comite_id  uuid NOT NULL REFERENCES usuario (id),
  fecha_apertura       timestamptz NOT NULL DEFAULT now(),
  fecha_cierre         timestamptz,
  CONSTRAINT ck_sesion_comite_fechas CHECK (fecha_cierre IS NULL OR fecha_cierre >= fecha_apertura)
);
CREATE INDEX ix_sesion_comite_expediente ON sesion_comite (expediente_id);
CREATE INDEX ix_sesion_comite_consultor ON sesion_comite (consultor_comite_id) WHERE fecha_cierre IS NULL;
-- A lo sumo una sesión abierta por expediente.
CREATE UNIQUE INDEX uq_sesion_comite_abierta ON sesion_comite (expediente_id) WHERE fecha_cierre IS NULL;

CREATE TABLE dictamen (
  id                uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  sesion_comite_id  uuid NOT NULL REFERENCES sesion_comite (id),  -- [R-04] el dictamen no se borra nunca
  tipo              tipo_dictamen NOT NULL,
  motivo            text NOT NULL,
  estado            estado_dictamen NOT NULL DEFAULT 'borrador',
  fecha_captura     timestamptz NOT NULL DEFAULT now(),
  capturado_por     uuid NOT NULL REFERENCES usuario (id),
  fecha_firma       timestamptz,
  firmado_por       uuid REFERENCES usuario (id),
  vigencia_hasta    date,
  CONSTRAINT uq_dictamen_sesion UNIQUE (sesion_comite_id),
  CONSTRAINT ck_dictamen_firma_coherente
    CHECK ((estado = 'firmado') = (fecha_firma IS NOT NULL AND firmado_por IS NOT NULL)),
  CONSTRAINT ck_dictamen_vigencia
    CHECK (vigencia_hasta IS NULL OR (estado = 'firmado' AND tipo = 'otorgar'))
);
CREATE INDEX ix_dictamen_estado ON dictamen (estado);

-- ===================== Bitácora y correo =====================
CREATE TABLE registro_bitacora (
  id            bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  fecha_hora    timestamptz NOT NULL DEFAULT now(),
  usuario_id    uuid REFERENCES usuario (id),
  rol           rol,
  parque_id     uuid REFERENCES parque (id),
  accion        varchar(100) NOT NULL,
  recurso_tipo  varchar(50),
  recurso_id    varchar(100),
  resultado     varchar(10) NOT NULL CHECK (resultado IN ('exitoso', 'denegado', 'fallido')),
  detalle       text
);
CREATE INDEX ix_bitacora_fecha ON registro_bitacora (fecha_hora DESC);
CREATE INDEX ix_bitacora_parque_fecha ON registro_bitacora (parque_id, fecha_hora DESC);
CREATE INDEX ix_bitacora_usuario_fecha ON registro_bitacora (usuario_id, fecha_hora DESC);
CREATE INDEX ix_bitacora_accion ON registro_bitacora (accion);

-- Solo append (RNF-03, RF-35): se rechaza cualquier UPDATE o DELETE.
CREATE FUNCTION bitacora_solo_append() RETURNS trigger
LANGUAGE plpgsql AS $$
BEGIN
  RAISE EXCEPTION 'registro_bitacora es de solo append: % no permitido', TG_OP;
END;
$$;
CREATE TRIGGER tg_bitacora_solo_append
  BEFORE UPDATE OR DELETE ON registro_bitacora
  FOR EACH ROW EXECUTE FUNCTION bitacora_solo_append();
-- [R-08] El trigger por renglón no detiene TRUNCATE, que borra todo de un golpe.
CREATE TRIGGER tg_bitacora_sin_truncate
  BEFORE TRUNCATE ON registro_bitacora
  FOR EACH STATEMENT EXECUTE FUNCTION bitacora_solo_append();

-- [R-10] Outbox de correo (RNF-12): el v0 no guardaba el cuerpo, así que el worker no
-- tendría qué enviar, ni el error del último intento.
CREATE TABLE mensaje_correo (
  id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  usuario_id    uuid REFERENCES usuario (id),
  tipo          varchar(50) NOT NULL,
  destinatario  varchar(254) NOT NULL,
  asunto        varchar(300) NOT NULL,
  cuerpo        text NOT NULL,
  creado_en     timestamptz NOT NULL DEFAULT now(),
  intentos      integer NOT NULL DEFAULT 0 CHECK (intentos BETWEEN 0 AND 3),
  ultimo_error  text,
  enviado_en    timestamptz
);
CREATE INDEX ix_mensaje_correo_pendiente ON mensaje_correo (intentos) WHERE enviado_en IS NULL;
CREATE INDEX ix_mensaje_correo_usuario ON mensaje_correo (usuario_id);

-- ===================== Datos iniciales =====================
-- [R-11] Sin estos renglones no se puede crear ningún expediente (FK de fase_expediente)
-- ni leer la configuración. Las 9 fases son las de 1.3 del SRS de equipo (C-15).
INSERT INTO catalogo_fase (clave, orden, nombre) VALUES
  ('diagnostico',                1, 'Diagnóstico'),
  ('plan_trabajo',               2, 'Plan de trabajo'),
  ('politica_seguridad',         3, 'Política de seguridad'),
  ('analisis_riesgos',           4, 'Análisis de riesgos'),
  ('implementacion_estandares',  5, 'Implementación de estándares'),
  ('opinion_intermedia_emitida', 6, 'Opinión intermedia'),
  ('opinion_final_emitida',      7, 'Opinión final'),
  ('evaluacion_desempeno',       8, 'Evaluación de Desempeño'),
  ('dictamen',                   9, 'Dictamen');

INSERT INTO configuracion (id) VALUES (1);

COMMIT;
