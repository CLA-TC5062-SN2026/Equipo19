# Revisión del SQL y del código generados por el agente

**Equipo:** 19
**Actividad:** S05-S06-A1, Partes 1 y 2
**Salidas del agente sin editar:** `evidencia_agente/esquema_bd_v0.sql` y el commit "v0 generado por el agente" del backend. Prompts en `evidencia_agente/prompts.md`.

## 1. Cómo revisamos el esquema

El agente recibió `diagrama_clases_equipo.puml` y `openapi_equipo.yaml` y entregó 35 tablas y 14 tipos ENUM. El script corrió a la primera sobre una base vacía. Que corra no dice nada de si modela bien el dominio, así que lo revisamos con las cinco preguntas de la actividad y después probamos cada corrección con un caso que la base debe rechazar (`pruebas/pruebas_restricciones.sql` y su salida en `pruebas/pruebas_restricciones.txt`).

| Pregunta | Respuesta |
|---|---|
| ¿Están todas las entidades del diagrama? | Sí. Cada clase que no es enumeración tiene su tabla. `OpinionIntermedia` y `OpinionFinal` quedaron en una sola tabla, `opinion_cumplimiento`, con columna `tipo`; lo aceptamos porque el contrato ya las expone con un solo schema y `tipo`, y el CHECK impide `favorable` en la intermedia. |
| ¿Están todos los atributos? | Faltaba uno que no estaba ni en nuestro diagrama: la fecha de término de un parque histórico (R-01). Sobraba `version_evidencia.comentario` (R-12). |
| ¿Las FK reflejan bien las relaciones? | Las simples sí. Fallaban las que cruzan dos caminos hacia el mismo expediente (R-02, R-03), la del contacto principal (R-05) y el borrado en cascada desde parque (R-04). |
| ¿Los tipos son coherentes con el contrato? | Sí: `uuid`, `date`, `timestamptz`, `numeric(5,2)` para porcentajes y `bigint` para tamaños. Donde el diagrama y el contrato usaban nombres distintos, el agente siguió al contrato (`texto`, `firmante`, `fecha_apertura`); ajustamos el diagrama (sección 2.3). |
| ¿Faltan restricciones del negocio? | Sí: R-06, R-07, R-08, R-09 y los datos iniciales (R-11). |

## 2. Correcciones al esquema

Cada corrección está marcada con `[R-xx]` en `esquema_bd.sql`.

### 2.1 Correcciones

| ID | Problema en el v0 | Riesgo | Corrección | Prueba |
|---|---|---|---|---|
| R-01 | El parque histórico (RF-31-AC-2) no tiene expediente, porque `expediente.generacion_id` es obligatorio, y su `fechaTerminoPrograma` no tenía dónde guardarse. | El alta de parque histórico del contrato no se podía implementar sin perder un dato. | `parque.fecha_termino_historico` y un CHECK que exige esa fecha y la del último dictamen en los históricos. | Alta histórica sin fecha de término: rechazada por `ck_parque_historico_datos`. |
| R-02 | `vinculo_evidencia` apuntaba a `evidencia` y a `criterio_parque` por separado. Nada impedía vincular una evidencia del parque X con un criterio del parque Y. | Fuga entre parques en la base misma, justo lo que RNF-01 prohíbe. | Columna `expediente_id` en el vínculo y dos FK compuestas: `(evidencia_id, expediente_id)` y `(criterio_parque_id, expediente_id)`. | Vínculo cruzado X→Y: rechazado por `fk_vinculo_criterio_parque`. |
| R-03 | `renglon_plan_trabajo` guardaba `expediente_id` y `criterio_parque_id` sin amarrarlos. | Un renglón del parque X apuntando a un criterio del parque Y. | FK compuesta `(criterio_parque_id, expediente_id)`. | Renglón cruzado: rechazado. |
| R-04 | `ON DELETE CASCADE` de parque a expediente, de expediente a sesión de comité y de sesión a dictamen. | Un `DELETE` por error sobre un parque borraba sus dictámenes, que RNF-14 dice que no se eliminan nunca. Las bajas del sistema son lógicas (RF-29), así que el cascade no tenía ningún uso legítimo. | Sin cascade en esas tres FK. Dentro del expediente (evidencias, criterios, plan) el cascade se queda, porque solo se dispara si se borra el expediente, y eso ya no puede pasar mientras tenga dictamen. | Borrar un parque con expediente: rechazado por `expediente_parque_id_fkey`. |
| R-05 | `parque.contacto_principal_id` apuntaba a cualquier usuario. | RF-34 pide que el contacto sea APPI de ese parque; con el v0, el contacto del parque X podía ser la APPI del parque Y o un consultor. | `UNIQUE (id, parque_id)` en `usuario` y FK compuesta `(contacto_principal_id, id) → usuario (id, parque_id)`. | Contacto de otro parque: rechazado. Contacto correcto: aceptado. |
| R-06 | Los CHECK de usuario exigían parque para APPI y desarrollador para gerente, pero no prohibían lo contrario. | Un consultor con `parque_id` se contaría como APPI de ese parque en cualquier consulta por `parque_id`. | CHECK de igualdad: `(rol = 'appi') = (parque_id IS NOT NULL)`, igual para gerente y desarrollador. | Consultor con parque: rechazado. |
| R-07 | Nada impedía dos fases "en proceso" en el mismo expediente. | RF-32-AC-1 habla de "la fase actual"; con dos, la vista de avance mostraría cualquiera. | Índice único parcial `WHERE estado = 'en_proceso'`. | Segunda fase en proceso: rechazada. |
| R-08 | El trigger de solo append cubría `UPDATE` y `DELETE` por renglón, no `TRUNCATE`. | `TRUNCATE registro_bitacora` borraba toda la bitácora sin pasar por el trigger (RNF-03). | Trigger `BEFORE TRUNCATE ... FOR EACH STATEMENT`. | `TRUNCATE`: rechazado. |
| R-09 | `intento_login.correo` aceptaba mayúsculas. | "Appi@X.mx" y "appi@x.mx" tendrían contadores separados y el bloqueo de RF-26-AC-3 se podía brincar cambiando mayúsculas. | `CHECK (correo = lower(correo))`; el servicio normaliza antes de buscar. | Correo con mayúsculas: rechazado. |
| R-10 | `mensaje_correo` no guardaba el cuerpo ni el error del último intento. | La outbox no tenía qué enviar y RNF-12 pide registrar la falla definitiva. | `cuerpo`, `creado_en`, `ultimo_error`; `intentos` entre 0 y 3. | Revisión. |
| R-11 | Sin datos iniciales. | `fase_expediente.fase` es FK a `catalogo_fase`, así que no se podía crear ningún expediente; tampoco existía el renglón de configuración. | `INSERT` de las 9 fases (1.3 del SRS) y del renglón de configuración con 100 MB y 3 años. | 9 fases y configuración presentes después de cargar. |
| R-12 | `version_evidencia.comentario`. | Columna que no está en el diagrama ni en ningún schema: nadie la escribe ni la lee. | Se quitó. | Revisión. |

### 2.2 Decisiones del agente que aceptamos

- Índices únicos parciales para una sola versión de catálogo activa, una asignación vigente por expediente, una clasificación de tipo de PI abierta por parque y una sesión de comité abierta por expediente. Son reglas de RF-01, RF-10, RF-11 y RF-13 que así no dependen del código.
- Correo único sin distinguir mayúsculas con un índice sobre `lower(correo)`.
- `intento_login` sin FK a usuario, porque el contador corre también para correos que no existen (decisión de S04_A2).
- `dictamen.vigencia_hasta` guardada al firmar: la vigencia del distintivo es configurable (C-10) y, si Coordinación la cambia después, un dictamen ya firmado no debe cambiar de fecha.
- `configuracion` limitada a un renglón con `CHECK (id = 1)`.

### 2.3 Lo que no se puede expresar en el esquema y queda en el código

| Regla | Dónde se valida |
|---|---|
| El consultor de una asignación tiene rol `consultor` (RF-10). | Servicio de asignaciones. |
| El responsable de un renglón del plan es APPI de ese parque (RF-09-AC-4). | Servicio del plan de trabajo. |
| Cada criterio del catálogo tiene exactamente cuatro marcas (una por tipo de PI). | Validación del CSV completo antes de insertar (RF-01-AC-4). |
| El motivo del cambio de tipo de PI es obligatorio desde la segunda clasificación (RF-11-AC-5). | Servicio de tipo de PI; la primera clasificación nace con el alta. |

### 2.4 Archivos que actualizamos por los ajustes

La actividad pregunta qué otros archivos hay que actualizar si cambian las tablas. Estos:

- `diagrama_clases_equipo.puml`: `Criterio.texto`, `RevisionAnalisisRiesgos.firmante`, `SesionComite.fechaApertura/fechaCierre`, `Parque.fechaTerminoHistorico`, `ActualizacionAnual.notas`, `Dictamen.vigenciaHasta`, `OpinionCumplimiento.comentarios`, campos de la outbox y las relaciones "registrada por" y "subido por" que el contrato ya exponía.
- `openapi_equipo.yaml`: sin cambios. La fecha de término del histórico ya estaba en `ParqueHistoricoCreate` y en `Parque.fechaTerminoPrograma`; solo cambió dónde se guarda.
- `backend/db/esquema_bd.sql`: es una copia de `S05_S06_A1/esquema_bd.sql`; la prueba `test_esquema_identico` falla si difieren.
- `er_sgpis.puml`: se regenera desde la base cargada, no se edita a mano.

### 2.5 Carga en PostgreSQL

`psql -v ON_ERROR_STOP=1 -f esquema_bd.sql` sobre una base vacía crea las 35 tablas; la salida de `\dt` está en `pruebas/dt_postgres.txt`. El diagrama entidad-relación generado desde esa base está en `er_sgpis.puml` e `imagenes/er_sgpis.png`.

## 3. Correcciones al código generado

### 3.1 Qué se le pidió al agente y cómo lo revisamos

El prompt (completo en `evidencia_agente/prompts.md`) fijó el stack: Python 3.12, FastAPI, SQLAlchemy 2.0, psycopg 3, Pydantic v2 y PostgreSQL 16, con la conexión en `DATABASE_URL` y sin seguridad, como pide la actividad. Pidió 46 operaciones del contrato: salud, catálogo, generaciones, parques, usuarios y contacto principal, asignaciones, criterios del parque, autoevaluación, cumplimiento, plan de trabajo, análisis de riesgos, fases, configuración y bitácora. Evidencias, comité, dictamen y reportes dependen de almacenamiento de objetos y de reglas de los sprints siguientes, y la autenticación es la actividad S05-S06-A2.

El agente entregó 3,287 líneas de Python más la configuración (Docker, `pyproject.toml`, `.env.example`) y probó una sola ruta, `GET /api/salud`. Lo guardamos tal cual en el commit "v0 generado por el agente (sin editar)" y lo revisamos de tres formas:

1. Rutas contra el contrato. Comparamos el OpenAPI que genera FastAPI con `openapi_equipo.yaml`: las 46 rutas pedidas existen con el método correcto, ninguna ruta está fuera del contrato y los códigos de éxito coinciden.
2. Pruebas automatizadas contra PostgreSQL real. `backend/tests/` tiene 50 pruebas; cada una corre sobre una base nueva clonada de `esquema_bd.sql`. La infraestructura valida cada respuesta contra el contrato con `openapi-core`: si un código no está declarado para la operación o el cuerpo no cumple su schema, la prueba falla. Las pruebas llevan en el nombre el criterio de aceptación que verifican (`test_RF_02_AC_2_tipo_pi_invalido`).
3. Lectura del código de las reglas que el contrato describe y que las pruebas no alcanzan a cubrir.

La primera corrida del v0 dio 41 pruebas aprobadas, 6 fallidas y 2 con error. Las correcciones están marcadas con `[C-xx]` en el código.

### 3.2 Correcciones

| ID | Archivo | Divergencia | Cómo se detectó | Corrección |
|---|---|---|---|---|
| C-01 | `routers/catalogo.py` | `PATCH /criterios/{id}` editaba criterios de una versión en solo lectura. El contrato declara 409 (RF-01-AC-5, D-09). | Prueba `test_RF_24_AC_1...`: respondió 200. | Busca la versión del criterio y responde 409 `version_solo_lectura`. |
| C-02 | `errores.py` | Los mensajes literales del SRS en errores de validación nunca salían: "Debe seleccionar un tipo de PI válido", "Debe seleccionar una región válida", "Debe indicar la generación del parque", "Tipo de PI inválido", "Indique el motivo del cambio de tipo de PI". Todos respondían el genérico "Los datos enviados no son válidos". La tabla de traducción buscaba la ruta con el prefijo `/api`, pero FastAPI guarda la plantilla sin él. | Cuatro pruebas de RF-02, RF-11 y RF-28. | Se normaliza la plantilla con el prefijo antes de buscar en la tabla. Un solo cambio arregló los cinco mensajes. |
| C-03 | `openapi_equipo.yaml` (contrato) | `TipoPINulable` y `FaseNulable` tienen `nullable: true` pero su `enum` no incluye `null`. Un validador estricto rechaza el `null` que devuelve un parque histórico. El defecto venía del contrato individual de S04_A2; el código no tenía error. | El validador de respuestas marcó el alta de parque histórico (RF-31-AC-2). | `null` agregado al enum en `consolidar_openapi.py`; el contrato se regeneró y se volvió a validar. |
| C-04 | `routers/historial.py` (nuevo) | `GET /parques/{id}/historial` (RF-31-AC-1, prioridad MVP) no estaba implementado. Fue omisión nuestra en la lista del prompt, no del agente. | Prueba `test_RF_31_AC_1_historial`: 404. | Se implementó con generaciones, actualizaciones, autoevaluaciones, Opiniones y dictámenes del parque. |
| C-05 | `errores.py` | Toda violación de integridad de la base respondía 409. El contrato reserva 409 para conflictos con el estado (unicidad) y usa 422 para datos que violan una regla. | Lectura del handler. | Se distingue por `sqlstate`: 23505 (unicidad) → 409; FK, CHECK y NOT NULL → 422. Prueba del handler con los tres casos. |
| C-06 | `routers/asignaciones.py` | Se podía asignar un consultor a un parque dado de baja (RF-29-AC-3). | Lectura. | 409 `parque_inactivo`. |
| C-07 | `routers/plan_trabajo.py` | Se podía crear un renglón del plan sobre un criterio ya cumplido. RF-09 y el contrato hablan de criterios pendientes, y ese renglón nunca podría marcarse atrasado. | Lectura. | 409 `criterio_cumplido`. |

Después de las correcciones: 50 de 50 pruebas aprobadas, sin respuestas fuera de contrato.

### 3.3 Decisiones del agente que aceptamos

- Usuario técnico para "quién registró". Sin autenticación no hay usuario en la solicitud, y las columnas `registrado_por`, `cargado_por` y similares son `NOT NULL`. El agente resolvió todo en una sola dependencia, `usuario_actual`, que devuelve un usuario técnico fijo. Así no hubo que relajar restricciones de la base, y S05-S06-A2 solo reemplaza esa dependencia por la que lee el JWT.
- Criterio del parque para todo el catálogo. Se crea un renglón `criterio_parque` por cada criterio de la versión, incluidos los NA, y la aplicabilidad se calcula con el tipo de PI vigente. Un cambio de tipo no borra calificaciones ni evidencias (RF-11-AC-6) y el NA que vuelve a aplicar entra en "pendiente" (RF-11-AC-4). En el diagrama de S04_A1 el criterio del parque solo existía para O y R; lo dejamos anotado en `CriterioParque` del diagrama consolidado.
- Clave y categoría del criterio al cargar el CSV. El CSV del contrato no trae clave ni categoría; la clave se arma como `subestándar.n` y la categoría queda en "seguridad", la más restrictiva para RNF-02.

### 3.4 Deuda que dejamos registrada

- `GET /parques` arma cada parque con varias consultas y pagina en memoria. Con 80 parques responde bien, pero hay que medirlo contra RNF-17 antes de la vista de cartera.
- El usuario técnico se crea la primera vez que alguna ruta lo necesita, incluso en un GET. Desaparece en S05-S06-A2.
- `atrasado` se calcula al consultar porque todavía no existe el worker de la revisión diaria.

### 3.5 Operaciones implementadas y pendientes

| Grupo | Estado | Operaciones |
|---|---|---|
| Salud, catálogo, generaciones, parques e historial, usuarios y contacto principal, asignaciones, criterios del parque, autoevaluación, cumplimiento, plan de trabajo, análisis de riesgos (revisiones), fases, configuración, bitácora | Implementado y probado | 47 |
| `/auth/*` | S05-S06-A2 | 4 |
| Evidencias y vínculos, documento de análisis de riesgos, recomendaciones, calificación de criterio | Sprint con almacenamiento de objetos | 16 |
| Opiniones, Evaluación de Desempeño, comité, dictamen, reportes, recuperación de contraseña, archivo maestro | Sprints de 2027 según prioridad del SRS | 21 |

### 3.6 Ejecución

Con el servidor corriendo contra la base cargada con `esquema_bd.sql` y la semilla (`uv run python -m app.semilla`), `GET /api/salud` responde `{"estado":"ok","baseDatos":"ok"}`. Con el backend de esta actividad, sin autenticación, la colección corrió 8 peticiones con GET, POST, PUT y DELETE y 13 aserciones aprobadas (`postman/corrida_newman_A1.txt`). Después de la corrida, la consulta directa a la base mostró el parque con sus dos clasificaciones de tipo de PI: los datos persisten.

En S05-S06-A2 las rutas pasaron a exigir token y rol, y el plan de trabajo quedó reservado al consultor asignado. Ajustamos la colección `postman/SGPIS_S05_S06_A1.postman_collection.json` para que funcione con el backend actual: el primer request inicia sesión con la cuenta de Coordinación de la semilla, y el renglón del plan (POST y DELETE) se cambió por la captura de fechas del programa (PATCH) y la consulta de usuarios del parque. La corrida actual tiene 8 endpoints, 15 aserciones y ninguna falla (`postman/corrida_newman_A1_con_token.txt`).
