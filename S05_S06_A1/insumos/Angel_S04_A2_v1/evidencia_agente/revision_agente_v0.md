# Revisión independiente de `openapi_v0.yaml` (SGPIS API 0.1.0)

Revisor: agente independiente; no participó en la generación del contrato.
Insumos: `openapi_v0.yaml` (3,643 líneas, leído completo) y `SRS_final.md` v1.4 (criterios de aceptación citados en `x-acceptance-criteria`).
Criterios de revisión: verbos HTTP, nombres de recursos, idempotencia, códigos de estado y consistencia con los AC del SRS; al final, problemas que aparecen al generar el backend en FastAPI.
No se modificó el YAML.

Orden: severidad alta, media y baja. Dentro de cada nivel, por impacto.

---

## Severidad alta

### O-01. Categoría: otro (seguridad). Severidad: alta
**Afecta:** `components.securitySchemes.bearerAuth`; `POST /auth/login` (`iniciarSesion`), `POST /auth/logout` (`cerrarSesion`), `GET /auth/me` (`obtenerSesionActual`); de forma indirecta `DELETE /usuarios/{usuarioId}` (`darDeBajaUsuario`) y `PUT /parques/{parqueId}/consultor` (`asignarConsultor`).

**Problema:** el contrato declara un JWT `bearer` y promete tres cosas que un JWT puramente stateless no puede cumplir:
1. RF-26-AC-5: que tras el logout cualquier solicitud con ese token responda 401. Un JWT sigue siendo válido hasta su `exp` mientras el servidor no consulte un estado de revocación.
2. RF-26-AC-6: expiración por **inactividad** de 60 minutos. El claim `exp` es absoluto y no se recorre con la actividad. Para una ventana deslizante hace falta guardar `ultimo_acceso` en el servidor o reemitir el token en cada respuesta, y el contrato no define ninguna de las dos cosas (no hay refresh token ni cabecera de token renovado).
3. RF-29-AC-1 y RF-10-AC-2: retirar el acceso "de inmediato". Si los roles y parques viajan como claims dentro del JWT, el consultor reasignado o dado de baja conserva el acceso hasta que el token expire.

Además, `GET /auth/me` se presenta como la operación que cumple RF-26-AC-6. Si la SPA lo consulta periódicamente para saber si la sesión sigue viva y esa consulta cuenta como actividad, la sesión no expira nunca.

**Propuesta:**
- Tabla `sesiones` (`id`, `usuario_id`, `creada`, `ultimo_acceso`, `revocada_en`). El token es opaco o es un JWT con claim `sid`; en cada solicitud, una dependencia de FastAPI valida la sesión contra la base, rechaza con 401 si está revocada o si `now - ultimo_acceso > 60 min`, y actualiza `ultimo_acceso` (con un debounce de ~1 minuto para no escribir en cada request).
- `POST /auth/logout` marca `revocada_en`. `DELETE /usuarios/{id}` revoca todas las sesiones del usuario.
- Los permisos por parque se resuelven siempre contra la base (asignaciones vigentes), nunca contra claims del token.
- Documentar en `bearerAuth.description` que el token se valida contra un estado de sesión en el servidor, y que `GET /auth/me` no renueva la actividad (o que la SPA no lo usa para polling).

### O-02. Categoría: idempotencia. Severidad: alta
**Afecta:** `POST /parques/{parqueId}/criterios/{criterioId}/evidencias` (`subirEvidencia`), `POST /evidencias/{evidenciaId}/versiones` (`subirVersionEvidencia`).

**Problema:** son POST no idempotentes con archivos de hasta 100 MB, subidos muchas veces desde el celular durante una inspección (RNF-09, sección 2.3 del SRS). Si la conexión se corta después de que el servidor confirmó y el cliente reintenta, el contrato no ofrece ningún mecanismo para detectar el duplicado. El duplicado tiene efectos de negocio, no solo de almacenamiento: por RF-27-AC-7, una evidencia nueva sobre un criterio "cumplido" lo regresa a "en revisión". Un reintento puede deshacer una calificación del consultor y sumar un registro de bitácora falso (RNF-03).

**Propuesta:** cabecera `Idempotency-Key` (UUID generado por el cliente) obligatoria en ambas operaciones. El servidor guarda `(usuario_id, clave) -> (hash del request, código, cuerpo de la respuesta)` durante 24 horas. Un reintento con la misma clave devuelve la respuesta original sin crear otra evidencia; la misma clave con un cuerpo distinto responde 422. Declarar la cabecera en `components.parameters` y referenciarla en las dos operaciones.

### O-03. Categoría: naming / verbos. Severidad: alta
**Afecta:** `POST /usuarios` (`crearUsuario`), `PUT /usuarios/{usuarioId}/roles` (`asignarRolesUsuario`), esquema `AsignacionRol`, `PUT /parques/{parqueId}/consultor` (`asignarConsultor`), `GET /parques/{parqueId}/asignaciones` (`listarAsignacionesConsultor`).

**Problema:** la relación consultor-parque tiene dos rutas de escritura distintas:
1. `AsignacionRol` con `rol: consultor_asignado` y `parqueId`, por `POST /usuarios` o `PUT /usuarios/{id}/roles`;
2. `PUT /parques/{parqueId}/consultor`.

Ninguna de las dos dice cómo se sincroniza con la otra. Asignar con la primera no cierra la asignación anterior ni deja historial (RF-10-AC-2), y no hay generación en `AsignacionRol`, aunque RF-10 define la asignación por parque **y** generación. Lo mismo ocurre con `consultor_comite`, que en el SRS es un acceso temporal ligado a una sesión de comité (RF-13) y no un rol permanente con `parqueId`.

Además, `PUT /parques/{parqueId}/consultor` lleva `generacionId` en el cuerpo. La URI no identifica el recurso que se reemplaza: dos PUT al mismo URI con generaciones distintas afectan recursos diferentes, lo que rompe la semántica de PUT.

**Propuesta:**
- Los roles de usuario quedan globales (`consultor`, `appi` con su parque, etc.). La asignación consultor-parque-generación se escribe **solo** por `POST /parques/{parqueId}/asignaciones` (crea la nueva, cierra la vigente y devuelve 201 + `Location`) o por `PUT /parques/{parqueId}/generaciones/{generacionId}/consultor`, idempotente: si el consultor ya es el vigente, responde 200 sin crear historial.
- Eliminar `PUT /parques/{parqueId}/consultor`, o dejarlo como alias documentado de la ruta anterior.
- El consultor de comité se modela solo dentro de `SesionComite`, no como `AsignacionRol`.
- RF-03-AC-2 (APPI y consultor del mismo parque) se valida contra las asignaciones, no contra la lista de roles.

### O-04. Categoría: códigos / otro (FastAPI). Severidad: alta
**Afecta:** todas las operaciones con cuerpo; en especial `POST /parques` (`crearParque`), `PUT /parques/{parqueId}/tipo-pi` (`cambiarTipoPI`), `components.responses.BadRequest`, `components.responses.UnprocessableEntity`, esquema `Error`.

**Problema:**
1. FastAPI valida el cuerpo con Pydantic **antes** de ejecutar el handler. Ante un enum inválido o un campo requerido faltante responde 422 con su propio esquema (`{"detail": [{"loc", "msg", "type"}]}`), no con `Error {codigo, mensaje}`. Varios AC exigen texto literal precisamente en esos casos:
   - RF-02-AC-2: "Debe seleccionar un tipo de PI válido" (`tipoPI` es enum `TipoPI`);
   - RF-02-AC-3: "Debe seleccionar una región válida" (`region` es enum `Region`);
   - RF-28-AC-3: "Debe indicar la generación del parque" (`generacionId` es `required`);
   - RF-11-AC-3: 422 con "Tipo de PI inválido".

   Si el código se genera tal cual, ninguno de estos mensajes llega al cliente.
2. Casi todas las operaciones declaran 400 **y** 422 sin decir qué produce cada uno. En FastAPI, incluso un JSON mal formado responde 422 por defecto, así que 400 no lo emite nadie a menos que se escriba un handler. En `crearParque` no se sabe si el tipo de PI inválido devuelve 400 o 422.
3. `HTTPException` produce `{"detail": ...}`. El contrato promete `Error` en todos los errores, incluidos 401 y 403.

**Propuesta:**
- Registrar handlers globales para `RequestValidationError` y `HTTPException` que siempre devuelvan `Error`. El handler de validación traduce el campo a `codigo`/`mensaje` con una tabla explícita: `tipoPI` -> `TIPO_PI_INVALIDO` / "Debe seleccionar un tipo de PI válido"; `region` -> `REGION_INVALIDA`; `generacionId` faltante -> `GENERACION_REQUERIDA`; etc. En `cambiarTipoPI` el mismo campo lleva el mensaje "Tipo de PI inválido", así que la tabla depende de la operación.
- Fijar la regla en `info.description`: 400 = cuerpo no parseable (JSON o multipart mal formado); 422 = cuerpo bien formado que no pasa validación de campos o reglas de negocio. Si no se va a implementar el 400, quitarlo del contrato.
- Sobrescribir el esquema `HTTPValidationError` que FastAPI inyecta en el OpenAPI generado, para que el contrato publicado y el código coincidan.
- Enumerar en el esquema `Error.codigo` los códigos posibles (enum), para que la SPA pueda distinguir casos sin comparar textos.

---

## Severidad media

### O-05. Categoría: idempotencia / códigos. Severidad: media
**Afecta:** `POST /parques/{parqueId}/opiniones` (`emitirOpinion`).

**Problema:** el glosario del SRS (1.3, "Opinión de Cumplimiento") dice que hay **una** intermedia y **una** final por parque en cada generación. El contrato solo impone unicidad a la final (409, RF-12-AC-3). Un reintento, o una segunda emisión de la intermedia, crea otro registro y vuelve a ejecutar el cambio de fase de RF-12-AC-1. Para la final, el 409 descrito como validación en el handler no resiste dos solicitudes concurrentes.

**Propuesta:** índice único `(parque_id, generacion_id, tipo)` en PostgreSQL, que traduzca la violación a 409 para ambos tipos con `codigo` distinto (`OPINION_INTERMEDIA_DUPLICADA`, `OPINION_FINAL_DUPLICADA`). La alternativa más REST: `PUT /parques/{parqueId}/generaciones/{generacionId}/opiniones/{tipo}` con `tipo` en `{intermedia, final}`, que devuelve 201 la primera vez y 409 si ya existe (las Opiniones no se editan).

### O-06. Categoría: códigos. Severidad: media
**Afecta:** `aceptarEvidencia` (422 "no está en enviada"), `registrarObservacion` (422 "no está en enviada"), `reabrirCriterio` (422 "no está en cumplido ni en no cumplido"), `firmarDictamen` (422 "ya está firmado"), `cerrarSesionComite` (422 genérico) frente a `emitirOpinion` (409 por duplicado).

**Problema:** se usa 422 y 409 sin una regla: un conflicto con el estado actual del recurso responde 409 en una operación y 422 en otras cuatro. "El dictamen ya está firmado" o "la evidencia ya no está en enviada" no son errores del payload; son conflictos con el estado del recurso destino, que se resuelven cuando ese estado cambia. Así, la SPA no puede decidir de forma genérica si el error se corrige en el formulario o recargando el recurso.

**Propuesta:** una regla escrita en `info.description` y aplicada en todo el contrato:
- **409**: transición inválida desde el estado actual del recurso destino, o violación de unicidad. Aplica a evidencia no "enviada" al aceptar u observar, dictamen ya firmado, criterio no reabrible, sesión ya cerrada, Opinión duplicada y correo duplicado (ver O-12).
- **422**: payload bien formado que viola una regla de negocio. Aplica a tipo de PI inválido (RF-11-AC-3, que el SRS fija en 422), criterio NA (RF-04-AC-2, también 422 en el SRS), responsable que no es APPI del parque (RF-09-AC-4), roles incompatibles (RF-03-AC-2), consultor de comité igual al asignado (RF-13-AC-2), y las precondiciones de expediente de RF-12-AC-4/5, RF-14-AC-3/4/5, RF-15-AC-2/3 y RF-17-AC-1.

El SRS no fija código para ninguno de los casos de 409, así que el cambio no contradice ningún AC.

### O-07. Categoría: verbos / idempotencia. Severidad: media
**Afecta:** `DELETE /parques/{parqueId}` (`darDeBajaParque`), `DELETE /usuarios/{usuarioId}` (`darDeBajaUsuario`).

**Problema:** las dos son bajas **lógicas**. Después del DELETE, `GET` al mismo URI sigue respondiendo 200 con `estado: baja`/`inactivo`, y el DELETE responde 200 con el recurso completo. Eso contradice lo que un cliente espera de DELETE (el recurso deja de estar disponible en ese URI). Tampoco se define el resultado de un segundo DELETE: ¿200, 204, 404 o 409? No hay forma de reactivar, ni dónde registrar el motivo de la baja, que es un dato que AMPIP necesita para auditoría (el SRS deja abierto si el historial del parque dado de baja sigue visible).

**Propuesta:** modelar la baja como cambio de estado: `PATCH /parques/{parqueId}` con `{ "estado": "baja", "motivo": "..." }`, o `POST /parques/{parqueId}/bajas`, que crea un registro con fecha, autor y motivo y responde 201. El equivalente para usuarios es `PATCH /usuarios/{usuarioId}` con `{ "estado": "inactivo" }`. Repetir la baja de un recurso ya dado de baja responde 200 sin efectos. Si el equipo prefiere conservar DELETE, documentar que es idempotente (204 en el primero y en los siguientes) y que el GET posterior sigue devolviendo 200 con `estado: baja`.

### O-08. Categoría: idempotencia / naming. Severidad: media
**Afecta:** `POST /autoevaluaciones` (`registrarAutoevaluacion`), `GET /parques/{parqueId}/autoevaluaciones` (`listarAutoevaluaciones`).

**Problema:**
1. La respuesta de autoevaluación se crea en una colección plana (`/autoevaluaciones`, con `parqueId` en el cuerpo) y se lista en una colección anidada (`/parques/{parqueId}/autoevaluaciones`). Son dos URIs para la misma colección.
2. No hay URI de elemento: el 201 no puede llevar `Location` y una respuesta no se puede consultar ni corregir.
3. La respuesta de un parque a un criterio en una generación es única por naturaleza, pero un segundo POST (por reintento o por corrección) crea otro registro. Nada indica cuál vale para RF-31 (historial con autoevaluaciones).

**Propuesta:** `PUT /parques/{parqueId}/autoevaluaciones/{criterioId}` como upsert idempotente sobre la clave natural `(parque, generación en curso, criterio)`, que devuelve 201 al crear y 200 al reemplazar, más `GET` del mismo URI. Conservar el 422 de RF-04-AC-2 para criterio NA. Eliminar `POST /autoevaluaciones`.

### O-09. Categoría: verbos / idempotencia. Severidad: media
**Afecta:** `PUT /parques/{parqueId}/tipo-pi` (`cambiarTipoPI`).

**Problema:** el PUT tiene efectos que no son idempotentes tal como están descritos: cierra el historial vigente, abre uno nuevo, recalcula O/R/NA y pone en "pendiente" los criterios que dejan de ser NA (RF-11-AC-1/4). Si se repite el mismo PUT (mismo `tipoPI`), una implementación directa cerraría y abriría otro periodo con el mismo tipo y volvería a recalcular. El contrato no dice que eso deba ser un no-op. Además, `fechaCambio` va en el cuerpo, así que dos PUT con el mismo tipo y fechas distintas dan resultados distintos sobre el mismo URI.

**Propuesta:** opción A: conservar el PUT y documentar que, si `tipoPI` es igual al vigente, responde 200 sin crear historial ni recalcular (no-op). Opción B, más fiel al modelo: `POST /parques/{parqueId}/historial-tipo-pi`, que crea un nuevo periodo y responde 201 + `Location`; si el tipo es igual al vigente, 409. En los dos casos, el 422 "Tipo de PI inválido" de RF-11-AC-3 pasa por el handler de O-04.

### O-10. Categoría: códigos. Severidad: media
**Afecta:** todas las respuestas 201: `cargarVersionCatalogo`, `crearGeneracion`, `crearParque`, `crearParqueHistorico`, `registrarActualizacionAnual`, `crearUsuario`, `registrarAutoevaluacion`, `subirEvidencia`, `subirVersionEvidencia`, `registrarObservacion`, `crearPlanTrabajoItem`, `registrarRevisionAnalisisRiesgos`, `emitirOpinion`, `abrirSesionComite`, `capturarDictamen`; además `PUT /parques/{parqueId}/analisis-riesgos/documento` (`subirDocumentoAnalisisRiesgos`).

**Problema:**
1. Ninguna respuesta 201 declara la cabecera `Location`.
2. Varios recursos creados no tienen un URI de elemento al que `Location` pueda apuntar. No existe `GET` para `/dictamenes/{dictamenId}` (solo `/firma`), `/sesiones-comite/{sesionId}` (solo PATCH), `/autoevaluaciones/{id}`, `/parques/{parqueId}/plan-trabajo/{planItemId}` (tiene PUT y DELETE, pero no GET), las observaciones, las revisiones del análisis de riesgos ni las actualizaciones anuales.
3. `subirDocumentoAnalisisRiesgos` es un PUT sobre un recurso singleton y solo declara 201. Al reemplazar un documento existente debería responder 200 (o 204), y 201 solo cuando lo crea.

**Propuesta:** agregar `headers.Location` (`format: uri-reference`) en cada 201. Agregar `GET /dictamenes/{dictamenId}`, `GET /sesiones-comite/{sesionId}`, `GET /parques/{parqueId}/plan-trabajo/{planItemId}` y GET de elemento para las colecciones que se mantengan. En el PUT del documento, declarar 201 (creado) y 200 (reemplazado).

### O-11. Categoría: verbos / códigos. Severidad: media
**Afecta:** `PATCH /parques/{parqueId}/criterios/{criterioId}/calificacion` (`calificarCriterio`), `POST /parques/{parqueId}/criterios/{criterioId}/reapertura` (`reabrirCriterio`), `POST /evidencias/{evidenciaId}/aceptacion` (`aceptarEvidencia`), `POST /evidencias/{evidenciaId}/observaciones` (`registrarObservacion`), `POST /dictamenes/{dictamenId}/firma` (`firmarDictamen`), `PATCH /sesiones-comite/{sesionId}` (`cerrarSesionComite`).

**Problema:**
1. Las transiciones de las dos máquinas de estado del SRS (tablas de RF-27) se modelan de cuatro formas: PATCH a un subrecurso (`/calificacion`), POST a un sustantivo de acción que responde 200 (`/aceptacion`, `/reapertura`, `/firma`), POST que crea un registro y responde 201 (`/observaciones`), y PATCH al recurso con un enum de un solo valor (`estado: [cerrada]`).
2. `calificarCriterio` solo declara el 422 del análisis de riesgos. Le faltan casos que el SRS sí define:
   - "cumplido" sin ninguna evidencia "aceptada" (regla de RF-27, que no tiene mensaje en el contrato);
   - calificar un criterio en "pendiente" (la tabla solo permite salir de "en revisión");
   - calificar como "cumplido" un criterio que ya está "cumplido".
3. `cerrarSesionComite` choca con `SesionComiteCreate.fechaCierre`: hay dos fuentes de verdad para el cierre (la fecha y el estado). No se sabe si el acceso del consultor de comité termina al llegar `fechaCierre` (RF-13-AC-3 habla de "se cerró el 2027-11-20") o al recibir el PATCH.

**Propuesta:**
- Usar un solo patrón. Recomiendo un subrecurso por transición, que cree un registro auditable y responda 201 + `Location`: `POST .../calificaciones`, `.../reaperturas`, `.../aceptaciones`, `.../observaciones`, `.../firmas`, `.../cierres`. Encaja con la bitácora de solo append de RNF-03. Si se prefiere PATCH de `estado`, que sea en todos los casos.
- En `calificarCriterio`: 409 `TRANSICION_INVALIDA` cuando el criterio no está en "en revisión"; 422 `SIN_EVIDENCIA_ACEPTADA` para "cumplido" sin evidencia aceptada; 422 `ANALISIS_RIESGOS_NO_VIGENTE` (ya existe). Repetir la misma calificación sobre el mismo estado responde 409, o 200 sin efectos, pero debe quedar escrito cuál de los dos.
- En la sesión de comité, definir una sola regla. Por ejemplo: `fechaCierre` es el límite automático y el cierre manual lo adelanta; la validación de acceso usa `min(fechaCierre, fecha de cierre manual)`.

### O-12. Categoría: códigos / idempotencia. Severidad: media
**Afecta:** `crearUsuario`, `cargarVersionCatalogo`, `crearGeneracion`, `abrirSesionComite`, `capturarDictamen`, `crearPlanTrabajoItem`.

**Problema:** faltan conflictos de unicidad que el modelo implica:
- correo de usuario repetido;
- `nombreVersion` del catálogo repetido;
- nombre de generación repetido;
- abrir una segunda sesión de comité mientras otra está abierta para el mismo parque;
- capturar un segundo dictamen cuando ya existe uno en "borrador" o "firmado" para el parque y la generación;
- un segundo registro de plan de trabajo para el mismo criterio.

Ninguna de estas operaciones declara 409, así que un reintento de red crea duplicados. En dictámenes falta además cómo **corregir** un borrador: RF-14-AC-6 lo deja visible para los tres miembros del comité antes de la firma, pero no existe `PATCH /dictamenes/{id}`, y la única salida es crear otro.

**Propuesta:** declarar 409 con `codigo` específico en las seis operaciones, respaldado por índices únicos (en los dictámenes, un índice parcial `(parque_id, generacion_id)`). Agregar `PATCH /dictamenes/{dictamenId}` permitido solo en "borrador". Al editar a "otorgar" se repite la validación de RD-09, porque la validación ocurre "al capturar". Un PATCH sobre un dictamen "firmado" responde 409.

### O-13. Categoría: otro (flujo faltante). Severidad: media
**Afecta:** `POST /usuarios` (`crearUsuario`), `EstadoUsuario.pendiente_activacion`, `POST /auth/recuperacion/confirmar`.

**Problema:** RF-03-AC-1 crea la cuenta en "pendiente de activación" y envía una invitación por correo. El contrato no tiene ninguna operación para aceptar la invitación, fijar la primera contraseña y pasar a "activo". `POST /auth/login` no dice qué responde para una cuenta pendiente. Tal como está, un usuario recién dado de alta no tiene forma de iniciar sesión.

**Propuesta:** `POST /auth/activacion` (público, `security: []`) con `{token, contrasena}`. El token es de un solo uso y tiene vigencia definida, como el de recuperación. Responde 200; con token vencido o ya usado, 410 o 422. Otra opción es reutilizar `/auth/recuperacion/confirmar` con un `proposito` en el token, pero debe quedar documentado. En `iniciarSesion`, una cuenta en `pendiente_activacion` o `inactivo` responde 401 con un `codigo` propio, y el mensaje visible sigue siendo el de RF-26-AC-2 para no revelar qué cuentas existen.

### O-14. Categoría: códigos / otro (FastAPI). Severidad: media
**Afecta:** `subirEvidencia` y `subirVersionEvidencia` (respuesta 413).

**Problema:** RF-06-AC-3 exige aceptar un archivo de **exactamente** 100 MB. En `multipart/form-data` el cuerpo HTTP pesa más que el archivo (boundaries, cabeceras de parte, campo `fase`). Si el límite se configura sobre el cuerpo (por ejemplo `client_max_body_size 100m` en nginx, o un middleware que revisa `Content-Length`), el caso de 100 MB exactos responde 413 y el AC falla. Si no se configura ningún límite en el proxy, Starlette recibe y guarda en disco cuerpos de cualquier tamaño antes de que el handler pueda rechazarlos.

**Propuesta:** documentar en la operación que el límite de 104,857,600 bytes se aplica al tamaño de la **parte** `archivo`, no al cuerpo de la solicitud. Configurar el proxy con un margen (por ejemplo 101 MB) y validar el tamaño exacto de la parte en el handler, mientras se lee el stream, para responder 413 con el texto de RF-06-AC-1. Agregar casos de prueba de contrato con 104,857,600 y 104,857,601 bytes.

---

## Severidad baja

### O-15. Categoría: naming. Severidad: baja
**Afecta:** `POST /parques-historicos` (`crearParqueHistorico`), `GET /parques` (`listarParques`, parámetro `incluirHistoricos`).

**Problema:** `/parques-historicos` crea un `Parque` (devuelve el esquema `Parque` con `estado: historico`) que luego vive en `/parques/{parqueId}` y se lista en `/parques`. Son dos URIs de colección para un mismo tipo de recurso, y `/parques-historicos` no tiene GET.

**Propuesta:** `POST /parques` con un cuerpo `oneOf: [ParqueCreate, ParqueHistoricoCreate]` y discriminador `origen: programa | historico`, que responde 201 + `Location: /parques/{id}`. Eliminar `/parques-historicos`.

### O-16. Categoría: códigos. Severidad: baja
**Afecta:** `crearParque` (404 si la generación no existe), `crearGeneracion` (404 si la versión no existe); también, sin 404 documentado pero con el mismo caso, `asignarConsultor` (`consultorId`), `crearPlanTrabajoItem` (`criterioId`, `responsableId`) y `abrirSesionComite` (`consultorComiteId`).

**Problema:** 404 significa que no existe el recurso del **URI** solicitado. Aquí `/parques` y `/generaciones` sí existen; lo que no existe es un id referenciado dentro del cuerpo. Responder 404 hace creer al cliente que equivocó la ruta.

**Propuesta:** un id referenciado en el cuerpo que no existe responde 422 con `codigo` específico (`GENERACION_NO_EXISTE`, `VERSION_CATALOGO_NO_EXISTE`, `CONSULTOR_NO_EXISTE`). El 404 queda solo para los parámetros de ruta.

### O-17. Categoría: naming. Severidad: baja
**Afecta:** `GET /catalogo/exportar` (`exportarCatalogoMaestro`), `POST /auth/recuperacion/confirmar`, `GET /parques/{parqueId}/autoevaluacion/criterios`, `GET /parques/{parqueId}/criterios`, `GET /parques/{parqueId}/criterios/{criterioId}/evidencias` frente a `GET /parques/{parqueId}/evidencias`, y `/parques/{parqueId}/plan-trabajo/{planItemId}` frente a `/evidencias/{id}`, `/dictamenes/{id}` y `/sesiones-comite/{id}`.

**Problema:**
- Hay verbos en las URIs: `exportar`, `confirmar`. En `/auth/login` y `/auth/logout` es una convención aceptada.
- `exportar` recibe la versión por query, mientras que el resto del catálogo la recibe en la ruta (`/catalogo/versiones/{versionId}`).
- Hay dos listas de criterios del mismo parque con casi el mismo conjunto (O+R aplicables): una sin estado (`autoevaluacion/criterios`, con el segmento en singular) y otra con estado (`criterios`).
- La regla de anidamiento no es uniforme. Evidencias, dictámenes y sesiones usan anidamiento superficial (se crean bajo el parque y el elemento queda en la raíz), pero el plan de trabajo anida el elemento.

**Propuesta:**
- `GET /catalogo/versiones/{versionId}/archivo` (`text/csv`), con `/catalogo/versiones/vigente/archivo` como alias.
- `POST /auth/recuperacion/confirmar` -> `POST /auth/restablecimientos`.
- Unificar en `GET /parques/{parqueId}/criterios` con un parámetro `incluirEstado` y retirar `/autoevaluacion/criterios`.
- Elegir una regla de anidamiento (recomiendo la superficial: `/planes-trabajo/{id}`) y aplicarla a todos los recursos.
- `/parques/{parqueId}/criterios/{criterioId}/evidencias` puede quedarse como atajo de `/parques/{parqueId}/evidencias?criterioId=`, siempre que se documente como filtro de la misma colección.

### O-18. Categoría: códigos. Severidad: baja
**Afecta:** `POST /auth/login` (`iniciarSesion`), respuesta 401 para cuenta bloqueada.

**Problema:** las credenciales inválidas (RF-26-AC-2) y la cuenta bloqueada (RF-26-AC-3) comparten el 401 y solo se distinguen por el texto. El bloqueo no es un fallo de autenticación de esa solicitud (puede llegar con la contraseña correcta); es una restricción temporal. Falta `Retry-After`. Tampoco se dice si el contador de intentos corre para correos que no existen. Si no corre, el mensaje de bloqueo revela qué cuentas existen.

**Propuesta:** el SRS no fija código, así que se puede usar 423 Locked o 429 Too Many Requests con `Retry-After: <segundos restantes>` y `codigo: CUENTA_BLOQUEADA`, manteniendo el texto literal de RF-26-AC-3. Si se prefiere 401, al menos un `codigo` distinto y `Retry-After`. Documentar que el contador también corre para correos inexistentes.

### O-19. Categoría: otro (control de acceso). Severidad: baja
**Afecta:** `GET /evidencias/{evidenciaId}/contenido` (`descargarContenidoEvidencia`), `GET /sesiones-comite/{sesionId}/expediente` (`consultarExpedienteComite`), esquema `ExpedienteComite.evidencias`.

**Problema:** `ExpedienteComite` incluye metadatos de evidencias, pero `descargarContenidoEvidencia` solo dice qué hacen Coordinación AMPIP y el Administrador técnico. No dice si el consultor de comité y el Director General pueden abrir el contenido durante la sesión, ni si el acceso termina al cerrarla (RF-13-AC-3). Tampoco dice que el gerente corporativo reciba 403 (RF-23 le da solo lectura de avance, no de evidencias). La matriz de permisos queda a criterio de quien implemente, en un endpoint cubierto por RNF-02 y RNF-04.

**Propuesta:** agregar a `descargarContenidoEvidencia` una tabla de acceso por rol: APPI del parque y consultor asignado sí; consultor de comité y Director General sí, mientras la sesión esté abierta (o no, si así se decide con AMPIP); Coordinación AMPIP solo evidencias `administrativa`; gerente corporativo y Administrador técnico, 403. Agregar una extensión `x-roles` por operación para generar las dependencias de autorización en FastAPI.

### O-20. Categoría: otro (FastAPI / generación de código). Severidad: baja
**Afecta:** esquemas `Paginacion`, `PaginaParques`, `PaginaUsuarios`, `PaginaEvidencias`, `Parque`, `Usuario`, `Evidencia` y demás esquemas de respuesta; enum `Region`; listas `listarEvidenciasCriterio`, `listarPlanTrabajo`, `listarDictamenes` y `obtenerVistaAvance`.

**Problema:**
1. Ningún esquema de respuesta declara `required`. Los generadores (`datamodel-code-generator`, `openapi-typescript`) producen todos los campos como opcionales, y la SPA tiene que validar contra `undefined` campos que siempre vienen.
2. La paginación no tiene parámetro de orden. `listarEvidenciasParque` (hasta 1,500 registros, RNF-06) pagina sin un orden estable, así que una página puede repetir o saltarse elementos.
3. Las propiedades están en camelCase (`tipoPI`, `generacionId`) y los valores de enum en snake_case. Pydantic usa snake_case por defecto, así que hace falta `alias_generator=to_camel` y `populate_by_name=True` en un modelo base. Si se omite, el contrato y el código divergen en silencio.
4. `Region` usa como valores textos con espacios y acentos ("Ciudad de México", "Nuevo León"). Funciona, pero los generadores producen nombres de miembro poco estables. Es preferible enviar claves (`CDMX`, `NL` o la clave INEGI) y presentar el nombre en la SPA.

**Propuesta:** declarar `required` en los esquemas de respuesta; agregar `orden` (por ejemplo `fechaCarga:desc`) con un desempate por `id`; fijar en `info.description` la convención camelCase y crear un `BaseModel` común con alias; cambiar `Region` a claves estables.

---

## Resumen de severidades

| Severidad | Observaciones |
|---|---|
| Alta | O-01, O-02, O-03, O-04 |
| Media | O-05 a O-14 |
| Baja | O-15 a O-20 |
