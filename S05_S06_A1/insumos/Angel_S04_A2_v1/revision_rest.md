# Revisión de principios REST de la API de SGPIS

**Actividad:** S04_A2, Parte 2
**Alumno:** Ángel Sebastián Kociankowski Montelongo (A01379225)
**Curso:** TC5062, Análisis, diseño y construcción de software (Gpo 10)
**Agente:** Claude (Anthropic)

## Cómo se hizo la revisión

1. Un agente generó la primera versión del contrato con el prompt de `evidencia_agente/prompt_generacion.md`. Esa salida se conserva sin editar en `evidencia_agente/openapi_v0.yaml` (3,643 líneas, 54 rutas, 70 operaciones).
2. Un segundo agente, en una sesión aparte y sin haber participado en la generación, revisó la v0 contra los principios REST que pide la actividad: verbos HTTP, naming de recursos, idempotencia y códigos de estado. También cruzó cada código de error contra el criterio de aceptación del SRS que la operación dice cumplir. Su reporte completo, sin editar, está en `evidencia_agente/revision_agente_v0.md`: 20 observaciones (4 altas, 10 medias, 6 bajas).
3. Decidí qué hacer con cada observación, apliqué los cambios y validé el resultado (`openapi.yaml`, versión 1.0.0) con tres herramientas: `openapi-spec-validator`, Redocly CLI y `swagger-cli` (el parser de Swagger). La salida de las tres está en `evidencia_agente/validacion.txt`.

La v0 pasaba el parser de Swagger sin errores, y Redocly solo le encontró dos, los dos de sintaxis (`nullable` sin `type`). Ninguna de las tres herramientas detectó uno solo de los 20 problemas de diseño: revisan que el YAML sea OpenAPI válido, y eso no dice nada sobre si la API es REST o si cumple el SRS.

## Observaciones principales y acciones correctivas

### O-01. Un JWT stateless no cumple el SRS (alta, seguridad)

**Observación del agente.** La v0 declaraba seguridad Bearer con JWT y prometía en las descripciones que el token "se invalida al cerrar sesión" y "expira tras 60 minutos de inactividad". Un JWT puro no puede hacer ninguna de las dos cosas: sigue siendo válido hasta su `exp` aunque el usuario cierre sesión (RF-26-AC-5), y `exp` es una fecha absoluta, no una ventana que se recorre con la actividad (RF-26-AC-6). Además, si los roles viajan como claims, un consultor reasignado (RF-10-AC-2) o dado de baja (RF-29-AC-1) conserva el acceso hasta que el token expire.

**Acción.** La actividad exige Bearer Token con JWT, así que mantuve el JWT, pero lo amarré a una sesión en el servidor. El token lleva `sub` y `sid`; en cada solicitud el backend busca la sesión `sid`, rechaza con 401 si está revocada o lleva más de 60 minutos sin actividad, y actualiza la última actividad. Rol, parques y estado del usuario se leen de la base, nunca de los claims. Es la misma decisión que el equipo tomó en el Sprint 1 (S03_A2) al descartar el JWT stateless para HU-01. La autenticación quedó modelada como el recurso `sesiones`: `POST /sesiones` (inicio), `GET /sesiones/actual` y `DELETE /sesiones/actual` (cierre, 204). El diagrama de secuencia del flujo 1 muestra esta validación paso por paso.

**Matiz que agregué.** El agente advirtió que si la SPA consulta `GET /sesiones/actual` cada cierto tiempo para saber si la sesión sigue viva, esa consulta cuenta como actividad y la sesión no expira nunca. Lo dejé escrito en la descripción de la operación: la SPA no la usa para sondear.

### O-03. Dos caminos para escribir la misma relación (alta, naming y verbos)

**Observación del agente.** La asignación consultor-parque se podía escribir por `PUT /usuarios/{id}/roles` (con un `parqueId` dentro del rol) y por `PUT /parques/{id}/consultor`. La primera ruta no guardaba generación ni historial, así que permitía saltarse RF-10-AC-2, que exige conservar quién fue consultor hasta qué fecha. La segunda usaba un sustantivo en singular y recibía en el cuerpo un `generacionId` que el parque ya determina.

**Acción.** La relación tiene un solo camino de escritura: la colección `POST /parques/{parqueId}/asignaciones-consultor`, que crea la asignación vigente y cierra la anterior, y `GET` de la misma colección para el historial. La generación se deriva del parque. El rol "consultor" en `/usuarios` quedó como rol global, sin parque. La regla de RF-03-AC-2 (nadie puede ser APPI y consultor del mismo parque) ahora se valida en las asignaciones, que es donde existe la relación con el parque.

### O-04 y O-06. Reglas de 400, 409 y 422 que no existían (alta y media, códigos)

**Observación del agente.** La v0 no definía cuándo responder 400 y cuándo 422, y FastAPI responde 422 con `{"detail": [...]}` en cuanto Pydantic falla, lo que no coincide con el esquema `Error` del contrato ni da los mensajes literales que exige el SRS (por ejemplo, "Debe seleccionar un tipo de PI válido" en RF-02-AC-2). Además, la misma situación (transición de estado no permitida) respondía 422 en cuatro operaciones y 409 en una.

**Acción.** Fijé una regla única en `info.description` y la apliqué a las 74 operaciones:
- 400 solo cuando el cuerpo no se puede parsear.
- 422 cuando el cuerpo es legible pero viola una regla de esquema o de negocio, incluido un id del cuerpo que no existe. Antes eso respondía 404, que en REST se reserva para el recurso de la ruta.
- 409 cuando la operación choca con el estado actual del recurso: duplicados y transiciones no permitidas.

Las respuestas de error quedaron como componentes reutilizables con el esquema `Error` (`codigo`, `mensaje`, `detalles`). El contrato obliga al backend a registrar exception handlers para que la validación de Pydantic también responda con ese esquema y con el texto del SRS.

### O-07, O-09 y O-11. Verbos con semántica equivocada (media, verbos e idempotencia)

**Observación del agente.** Tres problemas del mismo tipo:
- `DELETE /parques/{id}` y `DELETE /usuarios/{id}` hacían una baja lógica: respondían 200 y el recurso seguía visible con `GET`, así que en realidad no borraban nada.
- `PUT /parques/{id}/tipo-pi` no era idempotente: repetirlo con el mismo tipo abría otro registro de historial y recalculaba los criterios.
- Las transiciones de estado se modelaban de cuatro maneras distintas: subrecursos con nombre de acción (`/aceptacion`, `/firma`, `/reapertura`), un `/calificacion` con PATCH y un cierre de sesión de comité por PATCH.

**Acción.**
- Las bajas de RF-29 quedaron como `PATCH` del recurso con `estado: inactivo`. `DELETE` se usa solo donde algo se borra de verdad: un renglón del plan de trabajo, el documento del análisis de riesgos que la APPI decide retirar (RF-16) y el cierre de sesión.
- `PUT /parques/{id}/tipo-pi` con el mismo tipo vigente responde 200 sin abrir historial ni recalcular. Así cumple la idempotencia que promete PUT.
- Todas las transiciones siguen un solo patrón: `PATCH` del recurso con el campo `estado` (más `motivo` cuando aplica), y 409 si la transición no está permitida desde el estado actual. Aceptar una evidencia es `PATCH /evidencias/{id}`; calificar y reabrir un criterio es `PATCH /parques/{parqueId}/criterios/{criterioId}`; firmar un dictamen es `PATCH /dictamenes/{id}`; cerrar una sesión de comité es `PATCH /sesiones-comite/{id}`. Dejé una sola excepción, documentada: registrar una observación es `POST /evidencias/{id}/observaciones`, porque sí crea un recurso Observación.

### O-02. Reintentos de carga desde el celular (alta, idempotencia)

**Observación del agente.** La APPI sube evidencias desde el celular durante la inspección (sección 2.3 del SRS), con señal irregular. Si la conexión se corta después de que el servidor guardó el archivo, el reintento crea una segunda evidencia. Por RF-27-AC-7, eso además regresa a "en revisión" un criterio que ya estaba "cumplido".

**Acción.** `POST` de evidencias y de nuevas versiones aceptan la cabecera `Idempotency-Key`. El servidor guarda la clave por usuario durante 24 horas: un reintento con la misma clave devuelve 200 con la evidencia ya creada y no repite el efecto sobre el criterio. La misma clave con otro cuerpo responde 422.

## Resto de las observaciones

| ID | Observación del agente | Decisión |
|---|---|---|
| O-05 | La Opinión intermedia también es única por parque y generación; solo se impedía duplicar la final. | Adoptada. 409 para ambas, respaldado por un índice único (parque, generación, tipo) que aguanta solicitudes concurrentes. |
| O-08 | La autoevaluación se creaba en `/autoevaluaciones` y se listaba bajo `/parques/{id}`, sin URI de elemento y sin idempotencia. | Adoptada. `PUT /parques/{parqueId}/autoevaluaciones/{criterioId}`: crea con 201 o actualiza con 200. |
| O-10 | Ningún 201 declaraba `Location`; varios recursos creados no tenían `GET` de elemento. | Adoptada. Todo 201 lleva `Location` y cada `Location` apunta a un `GET` que existe. |
| O-12 | Faltaban los 409 por duplicado y no había forma de corregir un dictamen en borrador. | Adoptada. 409 en usuario, versión de catálogo, generación, sesión de comité, dictamen y plan de trabajo; `PATCH` del dictamen en borrador, que vuelve a validar RD-09 si cambia a "otorgar". |
| O-13 | RF-03-AC-1 deja la cuenta "pendiente de activación" y no había forma de activarla, así que ningún usuario nuevo podía entrar. | Adoptada. `PATCH /invitaciones/{token}`. Igual que en la recuperación de contraseña, el enlace usado o vencido responde 410. |
| O-14 | Si el límite de 100 MB se mide sobre el cuerpo multipart, un archivo de exactamente 100 MB (RF-06-AC-3) se rechaza por los bytes del encabezado multipart. | Adoptada. El límite aplica a la parte `archivo`: 104,857,600 bytes se aceptan, uno más responde 413. |
| O-15 | `/parques-historicos` era una segunda colección para crear el mismo recurso. | Adoptada. `POST /parques` con discriminador `tipoRegistro` (activo o histórico). |
| O-16 | Un id inexistente dentro del cuerpo respondía 404. | Adoptada, ver O-04: responde 422. |
| O-17 | Verbos en URIs (`/catalogo/exportar`, `/recuperacion/confirmar`), prefijo `/catalogo` en singular y dos listados casi iguales de criterios del parque. | Adoptada. `GET /versiones-catalogo/{versionId}/archivo`, `PATCH /recuperaciones-contrasena/{token}` y un solo listado `GET /parques/{parqueId}/criterios` con filtros. El listado de atrasos se volvió el filtro `?atrasado=true`. |
| O-18 | La cuenta bloqueada respondía 401 sin decir cuándo reintentar. | Ajustada. El agente proponía 423 o 429; elegí 429 con `Retry-After`, porque 423 es un código de WebDAV y el cliente no lo maneja de forma estándar. |
| O-19 | No estaba definido quién puede abrir el contenido de una evidencia aparte de APPI, consultor y Coordinación. | Adoptada. La matriz de acceso al contenido quedó escrita en `GET /evidencias/{evidenciaId}/contenido`. |
| O-20 | Esquemas sin `required`, paginación sin orden estable y un enum de regiones con acentos y espacios como valores. | Adoptada. `required` en todas las respuestas, parámetro `orden` y regiones como claves ISO 3166-2:MX (`MX-NLE` para Nuevo León). |

## Lo que encontré yo y el agente no señaló

El SRS v1.4 escribe rutas dentro de algunos criterios de aceptación: RF-01-AC-2 (`POST /catalogo/versiones`), RF-04-AC-2 (`POST /autoevaluaciones`) y RF-25-AC-2 (`GET /catalogo/exportar`). Esas tres rutas cambiaron con la revisión, porque usaban un prefijo en singular, un recurso sin anidar o un verbo en la URI. RF-05-AC-3 y RF-07-AC-3 citan rutas que se mantienen igual. El revisor comparó los códigos de estado contra el SRS, pero no las rutas.

El contrato sigue cumpliendo esos criterios, porque lo que prueban es el código de respuesta (403 o 422). Aun así, el SRS y el contrato no pueden contradecirse si el contrato es la fuente de la que se van a derivar el código (S05-S06) y las pruebas (S09). Lo registro como cambio pendiente para la siguiente versión del SRS: retirar las rutas literales de los AC o actualizarlas a las de `openapi.yaml`.

## Resultado

| | v0 (agente) | v1.0.0 (entregada) |
|---|---|---|
| Rutas | 54 | 50 |
| Operaciones | 70 | 74 |
| Rutas con verbos o acciones en la URI | 8 (`/auth/login`, `/auth/logout`, `/recuperacion/confirmar`, `/catalogo/exportar`, `/calificacion`, `/reapertura`, `/aceptacion`, `/firma`) | 0 |
| Recursos con dos caminos de escritura | 2 (asignación de consultor; parque activo e histórico) | 0 |
| Respuestas 201 con `Location` | 0 de 16 | 17 de 17 |
| Operaciones sin criterio de aceptación | 2, sin justificar | 3, con `x-justificacion` |
| AC del alcance mapeados a una operación | 101 de 101 | 101 de 101 |
| Errores de validación (Redocly) | 2 | 0 |

Después de esta revisión, al conciliar el contrato con los diagramas de S04_A1, agregué `GET /salud` para el monitoreo externo. El contrato pasó a 1.1.0, con 51 rutas y 75 operaciones; ninguna de las correcciones de este documento cambió.
