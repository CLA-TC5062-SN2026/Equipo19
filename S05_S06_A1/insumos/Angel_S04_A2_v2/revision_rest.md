# Revisión de principios REST

**Proyecto:** SGPIS (AMPIP), Equipo 19, TC5062
**Actividad:** S04-A2, Parte 2
**Especificación revisada:** `evidencia_agente/openapi_v0.yaml` (primera pasada del agente)
**Revisión del agente, sin editar:** `evidencia_agente/revision_rest_agente.md` (21 hallazgos: 4 altos, 14 medios, 3 bajos)
**Resultado:** `openapi.yaml` v1.0.0

## Cómo se hizo

1. Un agente generó el v0 a partir de `SRS_equipo.md` y de las tareas del Sprint 1, con la instrucción de respetar las rutas que esos documentos ya nombraban.
2. Validé el v0 con `redocly lint` y `swagger-cli validate`.
3. Un segundo agente, con contexto separado, revisó el v0 contra cinco principios: verbos HTTP, naming de recursos, idempotencia, códigos de estado y que el contrato se pudiera implementar tal cual. No podía editar el YAML. Los prompts están en `evidencia_agente/prompts_agentes.md`.
4. Revisé cada hallazgo contra el SRS, lo adopté, lo adapté o lo rechacé, y apliqué los cambios en `openapi.yaml`.
5. Validé el archivo final con los mismos dos validadores: 0 errores.

Agrupé los 21 hallazgos en seis observaciones. Las seis se ven en el `openapi.yaml` entregado. La tabla del final dice qué pasó con cada hallazgo.

## Observación 1. Verbos en las rutas: transiciones de estado escritas como RPC

**Lo que observó el agente (R-01, R-04, R-06, R-07, R-09, R-17).** Siete rutas del v0 terminan en verbo: `/auth/login`, `/auth/logout`, `/evidencias/{id}/aceptar`, `/criterios/{id}/reabrir`, `/dictamenes/{id}/firmar`, `/usuarios/{id}/baja` y `/fases/{fase}/cierre`, más `/fases/{fase}/avance-excepcion`. Además, las transiciones del mismo campo usaban estilos distintos: calificar con PATCH y reabrir con POST a un verbo. `PATCH /firmar` ni siquiera tenía cuerpo.

**Principio.** En REST la ruta identifica un recurso y el método dice qué se hace con él. Un verbo en la ruta repite lo que ya dice el método, y cada acción nueva termina en un endpoint distinto que el cliente tiene que conocer.

**Acción correctiva.** Cada transición se volvió una de dos cosas:

| v0 | `openapi.yaml` | Criterio de modelado |
|---|---|---|
| `POST /auth/login` → 200 | `POST /sesiones` → 201 | La sesión es un recurso que se crea en el servidor. |
| `POST /auth/logout` | `DELETE /sesiones/actual` → 204 | Cerrar sesión es revocar ese recurso. |
| `POST /evidencias/{id}/aceptar` | `PATCH /evidencias/{evidencia_id}` `{estado: aceptada}` | Cambio de estado sin datos propios. |
| `PATCH /criterios/{id}` + `POST /criterios/{id}/reabrir` | `POST /parques/{parque_id}/criterios/{criterio_id}/calificaciones` | Cada calificación tiene autor, fecha y motivo que RD-14 obliga a conservar, así que es un registro de historial. Calificar y reabrir son la misma operación con distinto `estado`. |
| `PATCH /dictamenes/{id}/firmar` sin cuerpo | `POST /dictamenes/{dictamen_id}/firma` → 201, 409 si ya está firmado | La firma es un hecho con firmante y fecha. |
| `POST /usuarios/{id}/baja`, `POST /parques/{id}/baja` | `PATCH /usuarios/{usuario_id}` y `PATCH /parques/{parque_id}` con `{estado: inactivo}` | El estado ya existía en el esquema. Con PATCH la baja es idempotente y se puede reactivar. |
| `POST /fases/{fase}/cierre` y `POST /fases/{fase}/avance-excepcion` | `PATCH /parques/{parque_id}/fases/{fase}` con `estado: completada` o `avanzada_por_excepcion` | Las dos son transiciones de la misma fase. `{fase}` es siempre la fase actual: 404 si no existe y 422 si no es la actual. |

Para que la reapertura no aceptara un cuerpo vacío, `CalificacionCrear` quedó como `oneOf` con discriminador `estado`. La variante `en_revision` exige `motivo` (RF-27-AC-8).

## Observación 2. Naming: colecciones en plural, sustantivos y sin namespaces en singular

**Lo que observó el agente (R-09, R-21; R-05 en parte).** `/catalogo/versiones` mete un namespace en singular antes de la colección. `/catalogo/exportar` es un verbo y además no dice qué versión exporta, aunque desde RF-01-AC-5 conviven varias. `/bitacora`, `/reportes/mensual` y `/parques/{id}/plan-trabajo` usan singular para colecciones.

**Principio.** Colecciones en plural, en minúsculas y en kebab-case. La ruta describe una jerarquía de recursos, no un menú de la aplicación.

**Acción correctiva.**

| v0 | `openapi.yaml` |
|---|---|
| `/catalogo/versiones`, `/catalogo/versiones/{id}` | `/versiones-catalogo`, `/versiones-catalogo/{version_id}` |
| `GET /catalogo/exportar` | `GET /versiones-catalogo/{version_id}/archivo-maestro` (una versión concreta) |
| `/catalogo/criterios/{id}/evidencia-suficiente` | `/versiones-catalogo/{version_id}/criterios/{criterio_id}/evidencia-suficiente` |
| `GET /bitacora` | `GET /eventos-bitacora`, con `accion` como enum `AccionBitacora` y orden descendente documentado (RF-35-AC-3) |
| `GET /reportes/mensual?generacion_id=&mes=` | `GET /generaciones/{generacion_id}/reportes-mensuales/{periodo}`: el reporte es un recurso de la generación |
| `/parques/{id}/plan-trabajo` | `/parques/{parque_id}/compromisos` y `/parques/{parque_id}/compromisos/{criterio_id}` |
| `/auth/recuperacion`, `/auth/restablecimiento`, `/auth/activacion` | `/solicitudes-recuperacion`, `/restablecimientos-contrasena`, `/activaciones` |

Excepciones que se quedan a propósito: `/configuracion` y `/parques/{parque_id}/contacto-principal` son recursos singulares (hay uno solo), y `/health` sigue la convención de los monitores de salud.

## Observación 3. Idempotencia: PUT que crea registros y POST con clave natural

**Lo que observó el agente (R-02, R-03, R-05, R-08, R-16).**

- `PUT /parques/{id}/tipo-pi` cierra el historial y crea un registro nuevo en cada llamada. Si la solicitud llega dos veces, quedan dos cambios de tipo y dos eventos en la bitácora: no es idempotente, así que no puede ser PUT.
- `POST /autoevaluaciones` y `POST /parques/{id}/plan-trabajo` crean recursos que el SRS define como únicos por criterio. Un reenvío del formulario los duplica y no hay forma de corregirlos.
- `PUT /configuracion` recibía un cuerpo parcial sin campos obligatorios, así que un PUT con `{}` tenía efecto indefinido.
- No se definía qué pasa con un segundo DELETE sobre una evidencia que, por RF-05-AC-9, no se borra físicamente.

**Principio.** GET, PUT y DELETE deben ser idempotentes: repetirlos deja el servidor igual. PUT reemplaza un recurso cuya URL conoce el cliente, así que es el verbo natural cuando hay clave natural. POST es para crear algo nuevo cada vez.

**Acción correctiva.**

| v0 | `openapi.yaml` | Comportamiento al repetir |
|---|---|---|
| `PUT /parques/{id}/tipo-pi` | `POST /parques/{parque_id}/cambios-tipo-pi` + `GET` del historial | Cada POST es un cambio nuevo. Si el tipo es igual al vigente responde 422 "El parque ya tiene ese tipo de PI", así que un reintento no ensucia el historial. |
| `POST /autoevaluaciones` (parque y criterio en el cuerpo) | `PUT /parques/{parque_id}/autoevaluaciones/{criterio_id}` | 201 la primera vez y 200 después; nunca duplica. |
| `POST /parques/{id}/plan-trabajo` | `PUT /parques/{parque_id}/compromisos/{criterio_id}` + `GET` + `DELETE` | Igual. DELETE sobre un compromiso inexistente responde 204. |
| `PUT /configuracion` parcial | `PATCH /configuracion` con `minProperties: 1` y `additionalProperties: false` | Aplicar el mismo PATCH dos veces deja el mismo valor. |
| `DELETE /evidencias/{id}` sin definir | Baja lógica del vínculo evidencia-criterio; el segundo DELETE responde 204 | Queda documentado que el objeto en el almacenamiento se conserva mientras otra evidencia lo use (RF-05-AC-7). |

Hago notar que `POST /parques/{parque_id}/asignaciones-consultor` sigue siendo POST a propósito: cada reasignación es un registro nuevo del historial que pide RF-10-AC-2.

## Observación 4. Códigos de estado

**Lo que observó el agente (R-11, R-12, R-13, R-15, R-20).**

- Ninguna de las 18 respuestas 201 declaraba `Location`.
- No había regla para elegir entre 409 y 422, y los duplicados caían en 422.
- La carga múltiple de evidencias no decía qué responder si se rechazaban todos los archivos.
- `POST /auth/recuperacion` podía responder 422 si el correo no existía, lo que permite enumerar cuentas.
- El 423 de bloqueo no decía cuándo reintentar.
- El primer PUT de un documento respondía 200 aunque lo creara.

**Acción correctiva.**

- `components.headers.Location` se referencia en cada 201 cuyo recurso tiene GET propio. Para que esos destinos existieran agregué siete GET de elemento que faltaban (hallazgo R-10): `/desarrolladores/{id}`, `/opiniones/{id}`, `/evaluaciones-desempeno/{id}` y su `/archivo`, `/revisiones-analisis-riesgos/{id}`, y los GET por criterio de autoevaluación y de compromiso. Donde el registro creado no tiene GET propio (calificaciones, observaciones, recomendaciones, cambios de tipo) el 201 devuelve el recurso en el cuerpo, en vez de apuntar a una URL que no existe.
- **Convención fija** en `info.description`: 400 = JSON mal formado o tipo de dato incorrecto; 422 = validación o regla de negocio; 409 = solo duplicados. La segunda Opinión final de RF-12-AC-3 pasó de 422 a 409, y también el dictamen ya firmado, el correo repetido y la sesión de comité ya abierta. Adopté el hallazgo en parte: el revisor quería 409 también para las transiciones inválidas, y lo rechacé porque el SRS las trata como reglas de negocio con mensaje propio (ver `decisiones_y_trazabilidad.md`, Sección B.2).
- Carga múltiple: 201 con `creadas` y `rechazadas` si al menos un archivo pasa (RF-05-AC-8), y 422 con un error por archivo si no pasa ninguno. Agregué `encoding` al multipart para `criterio_ids` y los tipos de archivo.
- Recuperación: siempre 202, exista o no el correo. El 422 queda solo para un correo mal escrito. El contador de bloqueo se lleva por correo aunque la cuenta no exista, para que el 423 tampoco revele qué cuentas hay.
- 423 con cabecera `Retry-After` (segundos restantes del bloqueo de 15 minutos).
- `PUT /revisiones-analisis-riesgos/{revision_id}/documento`: 201 al crear y 200 al reemplazar.
- Rechacé 413 y 415 para archivos: el límite es configurable y el SRS fija mensajes exactos que un 413 del proxy no lleva. Rechacé también el 303 para la URL firmada, porque con `fetch` y la cabecera `Authorization` el redireccionamiento a otro origen falla.

## Observación 5. Contrato de errores y esquemas que no se podían implementar tal cual

**Lo que observó el agente (R-14, R-18, R-19).** El error solo tenía un `mensaje` libre, así que una prueba no podía distinguir los diez distintos 422 sin comparar texto. Ningún esquema de respuesta declaraba `required`, así que un cliente generado tendría todo opcional, incluso `id`. Reglas condicionales del SRS, como `favorable` obligatorio solo en la Opinión final, no estaban en el esquema.

**Acción correctiva.**

- Errores en `application/problem+json` (RFC 9457), con un `type` estable por regla (por ejemplo `.../problemas/analisis-riesgos-no-vigente`) y `detail` con el mensaje exacto del SRS. Las pruebas de S09 comparan `type`. Prefiero esto a la propiedad `codigo` que propuso el agente porque el RFC ya define `type` para ese uso.
- `required` en todos los esquemas de salida y de entrada, `readOnly` en los campos que calcula el servidor (`atrasado`, `fecha_alta`, `version_catalogo`, `id`), `minLength: 1` en todo `motivo` y `texto`, y `additionalProperties: false` en los cuerpos de transición.
- `OpinionCrear` como `oneOf` con discriminador `tipo`: la variante final exige `favorable` (RF-12-AC-6). `CalificacionCrear` igual con `estado` (Observación 1).
- Rechacé un `oneOf` por cada uno de los seis roles en `RolAsignado`. La regla "Un usuario no puede ser APPI y Consultor del mismo parque" necesita su mensaje exacto, y un error de esquema no lo da. Queda descrita en la operación y se valida en el servicio.

## Observación 6. Validación de sintaxis

Esto no vino del agente revisor. Salió de los validadores, y es justo lo que el revisor no vio.

| Archivo | `redocly lint` | `swagger-cli validate` |
|---|---|---|
| `openapi_v0.yaml` | **5 errores**: `nullable: true` junto a `allOf` sin `type` en `Parque.contacto_principal`, `Parque.consultor_asignado`, `Fase.cerrada_por`, `CriterioParque.actualizado_por` y `Dictamen.firmado_por`. OpenAPI 3.0 exige `type` cuando se usa `nullable`. | Válido (no revisa esa regla). |
| `openapi.yaml`, primer intento | **6 errores**: comas dentro de descripciones en mapas YAML en línea (`{ ..., description: texto, con coma }`), que el parser lee como propiedades nuevas. | — |
| `openapi.yaml`, entregado | **0 errores.** Tres avisos de estilo aceptados: el servidor es `localhost`, la licencia no tiene URL y `/health` no tiene respuesta 4xx. | Válido. |

Correcciones: `type: object` junto a cada `nullable` + `allOf`, y comillas en las descripciones con comas.

## Tabla de hallazgos del agente y su resolución

| Hallazgo | Severidad | Resolución | Dónde se ve en `openapi.yaml` |
|---|---|---|---|
| R-01 `PATCH .../firmar` | Alta | Adoptado | `POST /dictamenes/{dictamen_id}/firma` |
| R-02 `PUT .../tipo-pi` no idempotente | Alta | Adoptado | `POST /parques/{parque_id}/cambios-tipo-pi` |
| R-03 `POST /autoevaluaciones` | Alta | Adoptado; rechazado conservar la ruta del SRS | `PUT /parques/{parque_id}/autoevaluaciones/{criterio_id}` |
| R-04 Calificar y reabrir | Alta | Adoptado con otro modelo (historial de calificaciones) | `POST .../criterios/{criterio_id}/calificaciones`, `CalificacionCrear` |
| R-05 Plan de trabajo | Media | Adoptado | `/parques/{parque_id}/compromisos/{criterio_id}` con GET, PUT y DELETE |
| R-06 `/aceptar` | Media | Adoptado (PATCH); 409 rechazado | `PATCH /evidencias/{evidencia_id}` |
| R-07 `/baja` | Baja | Adoptado | `PATCH /usuarios/{usuario_id}`, `PATCH /parques/{parque_id}` |
| R-08 `PUT /configuracion` | Media | Adoptado | `PATCH /configuracion`, `ConfiguracionActualizar` |
| R-09 Verbos en `/auth` y `/exportar` | Baja | Adoptado y ampliado | `/sesiones`, `/versiones-catalogo/{version_id}/archivo-maestro` |
| R-10 Recursos sin GET individual | Media | Adoptado | 7 GET nuevos (Observación 4) |
| R-11 `Location` en 201 | Media | Adoptado | `components.headers.Location` |
| R-12 409 frente a 422 | Media | Adoptado en parte | `info.description`, `POST .../opiniones` (409) |
| R-13 Archivos | Media | Adoptado en parte; 413 y 415 rechazados | `POST /parques/{parque_id}/evidencias` (201/422, `encoding`) |
| R-14 Esquema de error | Media | Adoptado con `type` en vez de `codigo` | `Problema`, `application/problem+json` |
| R-15 Enumeración y `Retry-After` | Media | Adoptado | `POST /solicitudes-recuperacion`, 423 en `POST /sesiones` |
| R-16 Semántica de DELETE | Media | Adoptado | `DELETE /evidencias/{evidencia_id}`, `POST .../versiones` |
| R-17 Fases | Media | Adoptado con PATCH en vez de conservar `/cierre` | `PATCH /parques/{parque_id}/fases/{fase}` |
| R-18 Reglas condicionales | Media | Adoptado en Opinión y calificación; rechazado en roles | `OpinionCrear`, `CalificacionCrear` |
| R-19 `required` y `readOnly` | Media | Adoptado | Todos los esquemas |
| R-20 Representación del documento | Baja | Adoptado el 201; 303 rechazado | `PUT /revisiones-analisis-riesgos/{revision_id}/documento` |
| R-21 Bitácora | Baja | Adoptado | `GET /eventos-bitacora`, `AccionBitacora` |

Resultado: 21 de 21 hallazgos atendidos. 12 se adoptaron tal como los propuso el agente, 4 con una solución distinta a la propuesta (R-03, R-04, R-14 y R-17) y 5 en parte (R-06, R-12, R-13, R-18 y R-20); cada parte rechazada tiene su justificación arriba. No quedan errores sin corregir en el contrato que se usará en S05-S06.
