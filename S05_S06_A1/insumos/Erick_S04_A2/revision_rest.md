# Revision REST de SGPIS

## Evaluacion general

La especificacion tiene una base REST adecuada: utiliza HTTPS, versiona la API en `/api/v1`, aplica JWT de forma global, usa recursos de dominio identificables y conserva las operaciones automaticas fuera de la API. Los recursos principales (`usuarios`, `generaciones`, `parques`, `evidencias`, `dictamenes` y `distintivos`) se expresan en minusculas y, en general, en plural.

## Uso de metodos HTTP

### Cumple

- `GET` se usa correctamente para recuperar colecciones, recursos, expedientes, reportes, bitacora y URLs firmadas, sin declarar cambios de estado.
- `POST` se usa correctamente para crear recursos: usuarios, versiones de catalogo, generaciones, parques, planes, opiniones, evaluaciones, sesiones de comite, dictamenes, evidencias, recomendaciones, auditorias, visitas y renovaciones.
- `PATCH` es adecuado en `usuarios/{usuarioId}`, `parques/{parqueId}`, criterios, vinculos APPI, evaluaciones de criterio y configuracion, porque modifica parcialmente el recurso existente.
- `PUT /parques/{parqueId}/asignacion-consultor` es adecuado. La asignacion vigente es un subrecurso unico y reemplazarla con el mismo cuerpo es idempotente.
- `DELETE /auth/sesiones/actual` y `DELETE /evidencias/{evidenciaId}` son elecciones adecuadas para invalidar una sesion y efectuar una baja logica.

### Hallazgos

1. **Alta: `PUT /auth/recuperaciones-contrasena/{token}` no es idempotente.** El token es de un solo uso: una segunda solicitud equivalente falla porque el primer uso lo invalida. Esto contradice la semantica esperada de `PUT`.
   Correccion sugerida: usar `POST /auth/recuperaciones-contrasena/{token}/confirmaciones` para confirmar el uso unico del token. Conserva el flujo y el criterio RF-26-AC-4, pero no promete idempotencia.

2. **Media: varias transiciones se modelan como acciones en vez de modificar el estado de un recurso.** Afecta a `POST /parques/{parqueId}/fases/{faseId}/cierre`, `POST /parques/{parqueId}/fases/avance-excepcion`, `POST /dictamenes/{dictamenId}/firma` y `PUT /evidencias/{evidenciaId}/aceptacion`.
   Correccion sugerida: cuando se implemente la siguiente iteracion, preferir `PATCH` sobre el recurso de estado correspondiente. Ejemplos: `PATCH /parques/{parqueId}/fases/{faseId}` con `estado` y `motivoExcepcion`; `PATCH /dictamenes/{dictamenId}` con `estado: firmado`; y `PATCH` sobre el vinculo evidencia-criterio con `estado: aceptada`. Estas operaciones pueden ser idempotentes. Si se mantienen los paths actuales para conservar las referencias literales del SRS, se debe documentar que son comandos de dominio y definir que repetirlos no crea efectos adicionales.

3. **Baja: `POST /evidencias` admite carga parcial, pero responde siempre `201`.** El SRS permite aceptar unos archivos y rechazar otros en una misma solicitud. Un `201` sin distincion puede sugerir que todo fue creado.
   Correccion sugerida: mantener `201` cuando todos los archivos se crean y documentar `207 Multi-Status` cuando `rechazadas` no esta vacio. El cuerpo actual `EvidenceUploadResult` ya permite describir ambos resultados.

## Naming de recursos

### Cumple

- Los recursos de negocio principales son sustantivos, minusculas y plurales: `/usuarios`, `/generaciones`, `/parques`, `/evidencias`, `/auditorias`, `/visitas-validacion`, `/dictamenes` y `/distintivos`.
- Los subrecursos de parque expresan correctamente su relacion de pertenencia, por ejemplo `/parques/{parqueId}/expediente`, `/autoevaluaciones`, `/planes-trabajo` y `/opiniones-cumplimiento`.
- `expediente`, `asignacion-consultor` y `configuracion/cargas` pueden ser subrecursos singulares porque representan un estado unico por parque o por instalacion. No requieren cambio solo por no estar en plural.

### Hallazgos

1. **Media: algunos segmentos son acciones o adjetivos, no recursos.** `cierre`, `avance-excepcion`, `firma` y `aceptacion` revelan la operacion en la URL.
   Correccion sugerida: aplicar las rutas con `PATCH` descritas en la seccion anterior. Esto elimina verbos de la URL sin agregar funcionalidades.

2. **Baja: `/reporte-asociados` es inconsistente con `/reportes/mensual`.** Ambos son reportes, pero el primero usa singular y no comparte el prefijo.
   Correccion sugerida: normalizar a `GET /reportes/asociados`. Debido a que RF-22-AC-2 menciona literalmente `GET /reporte-asociados`, este cambio debe coordinarse con la actualizacion del SRS y de sus pruebas; no debe hacerse de forma aislada.

## Idempotencia

### Cumple

- Las lecturas `GET` son seguras e idempotentes.
- Los `PATCH` de atributos y el `PUT` de la asignacion vigente pueden definirse idempotentes con el mismo cuerpo.
- La baja logica de evidencia puede ser idempotente si una segunda eliminacion devuelve `204` sin cambiar el historial, o `404` si se opta por ocultar el recurso eliminado. La implementacion debe elegir y documentar una de esas dos respuestas.

### Hallazgos

1. **Media: las acciones de cierre, firma, avance y aceptacion no declaran su comportamiento ante reintentos.** Un cliente HTTP puede reintentar por timeout; sin una regla, puede haber eventos duplicados de bitacora o transiciones inconsistentes.
   Correccion sugerida: hacer las transiciones idempotentes por estado, o aceptar una clave de idempotencia en los `POST` de comando. La primera alternativa es preferible al cambiar a `PATCH`.

2. **Baja: los `POST` de creacion no describen proteccion contra duplicados.** Esto es aceptable por defecto para `POST`, pero es relevante para cargas de evidencia, sesiones de comite y dictamenes.
   Correccion sugerida: no cambiar el metodo. Aplicar las restricciones de unicidad ya indicadas por el SRS y el modelo de dominio, devolviendo `422` cuando corresponda.

## Codigos de respuesta HTTP

### Cumple

- `200`, `201`, `204`, `400`, `403`, `404`, `422` y `500` se usan con una semantica generalmente adecuada.
- `202` para solicitar recuperación de contraseña es correcto: el envio de correo es asincrono.
- `401` y `403` se distinguen correctamente en los endpoints que ya los declaran: token ausente, invalido o expirado frente a falta de permisos.
- El uso de `422` para reglas de negocio, como tipos de PI invalidos, estados no permitidos y precondiciones de dictamen, es coherente con FastAPI.

### Hallazgos

1. **Alta: falta documentar `401` en numerosos endpoints protegidos.** La seguridad JWT global los protege, pero las respuestas de `/usuarios/{usuarioId}`, catalogo, generaciones, varios recursos de parques, fases, cumplimiento, reportes y distintivos omiten `401`.
   Correccion sugerida: agregar `'401': {$ref: '#/components/responses/Unauthorized'}` a cada operacion que no tenga `security: []`. No modificar los tres endpoints publicos de autenticacion.

2. **Media: faltan `404` en operaciones sobre recursos identificados.** Por ejemplo, `PUT /parques/{parqueId}/asignacion-consultor`, `POST /parques/{parqueId}/analisis-riesgos`, `POST /parques/{parqueId}/planes-trabajo`, `POST /parques/{parqueId}/opiniones-cumplimiento`, `POST /parques/{parqueId}/sesiones-comite` y `POST /parques/{parqueId}/dictamenes` pueden referirse a un parque inexistente.
   Correccion sugerida: declarar `404` para el parque, distintivo o recurso padre inexistente en dichas operaciones. Mantener `422` para una regla de negocio que falle sobre un recurso existente.

3. **Baja: falta `Location` en las respuestas `201`.** No es obligatorio en OpenAPI, pero mejora la descubribilidad del recurso creado.
   Correccion sugerida: agregar un encabezado `Location` en las respuestas `201` de recursos que tengan URI propia. No es necesario para respuestas que devuelvan resultados de lote.

## Coherencia REST y trazabilidad

- La API mantiene estado en recursos y no expone como endpoints las tareas diarias; `x-background-processes` es una buena separacion entre la API y trabajos del backend.
- La seguridad JWT global y las excepciones explicitas de autenticacion son coherentes con un servicio sin estado de sesion HTTP.
- La traza de evidencias mediante `versionAnteriorId`, `historial` y vinculos evidencia-criterio representa correctamente un archivo reutilizable y revisable de forma independiente.
- `GET /distintivos/{distintivoId}` tiene `x-acceptance-criteria: []`. No es un problema REST, pero deja una operacion sin trazabilidad de criterio. Conviene asociarla al criterio de consulta que corresponda si existe; de lo contrario, documentarla como consulta de soporte sin criterio directo.

## Prioridad de correccion

1. Agregar `401` a todas las operaciones protegidas y `404` a las operaciones que reciben un identificador de recurso padre.
2. Reemplazar o documentar explícitamente la semantica de las operaciones de transicion y cambiar el `PUT` del token de recuperación por `POST`.
3. Distinguir la respuesta de carga parcial de evidencias y normalizar nombres solo si se actualiza en conjunto la referencia literal del SRS.


## Observaciones y acciones correctivas

A partir de la revisión realizada por el agente de IA, se identificaron las siguientes oportunidades de mejora en la especificación OpenAPI:

### 1. Códigos de respuesta HTTP incompletos
**Observación:** Algunos endpoints protegidos no incluyen respuestas `401` para usuarios no autenticados ni `404` para recursos inexistentes.

**Acción correctiva:** Agregar estos códigos donde corresponda, manteniendo `403` para usuarios sin permisos y `422` para errores de validación.

### 2. Idempotencia en recuperación de contraseña
**Observación:** El endpoint `PUT /auth/recuperaciones-contrasena/{token}` utiliza un token de un solo uso, lo que puede generar confusión sobre su comportamiento ante solicitudes repetidas.

**Acción correctiva:** Cambiar el método a `POST` y documentar que el token se invalida después de utilizarse correctamente.

### 3. Transiciones de estado
**Observación:** Algunas operaciones, como cerrar fases, firmar dictámenes y aceptar evidencias, están representadas como acciones en las rutas.

**Acción correctiva:** Mantener las rutas actuales cuando estén justificadas por el SRS, pero documentar su comportamiento ante solicitudes repetidas para evitar transiciones inválidas o efectos duplicados.

### 4. Carga parcial de evidencias
**Observación:** El endpoint `POST /evidencias` permite aceptar algunos archivos y rechazar otros, pero utiliza el código `201` para indicar el resultado.

**Acción correctiva:** Conservar `201 Created` y especificar que la respuesta `EvidenceUploadResult` identifica individualmente los archivos aceptados y rechazados.

## Conclusión

La revisión permitió identificar mejoras en el uso de códigos HTTP, la idempotencia y la definición de operaciones REST. Estas correcciones buscan mantener una API coherente, sencilla y alineada con los requerimientos del SRS, sin modificar innecesariamente su arquitectura.

## Correcciones aplicadas

Después de analizar las observaciones del agente, se realizaron las siguientes modificaciones en `openapi.yaml`:

1. **Códigos HTTP:** se agregaron respuestas `401` y `404` en los endpoints correspondientes para manejar correctamente errores de autenticación y recursos inexistentes.
2. **Recuperación de contraseña:** se cambió el método `PUT` por `POST` para representar mejor el uso de un token de un solo uso.
3. **Idempotencia:** se documentó el comportamiento ante solicitudes repetidas en operaciones como cierre de fases, firma de dictámenes y aceptación de evidencias, evitando cambios o registros duplicados.
4. **Carga de evidencias:** se conservó el código `201 Created` y se aclaró que la respuesta `EvidenceUploadResult` distingue los archivos aceptados de los rechazados.

### Resultado

Las correcciones quedaron reflejadas en la especificación OpenAPI, manteniendo la estructura original, la trazabilidad con el SRS y los principios REST. Estas mejoras permiten contar con un contrato más claro y consistente para la futura implementación del backend.

## Correcciones derivadas de la revisión de trazabilidad

La segunda revisión confirmó que los criterios inicialmente parciales se concentraban, sobre todo, en reglas de autorización, transiciones, precondiciones y procesos automáticos. No requieren rutas nuevas: el Backend debe aplicarlos y su detalle pertenece al contrato o a la lógica interna.

Se corrigieron los gaps de datos observables dentro del alcance: `Error.detalles` ahora puede informar fila y columna de un CSV; `Park` expone atraso de actualización e historial de tipos con su cumplimiento; `ParkPatch` permite registrar o programar la actualización anual; `RiskReview` identifica su documento restringido; y el expediente expone fase actual, opiniones, dictámenes y evidencias entregadas por fase. La evidencia incluye opcionalmente su fase.

Se mantuvieron los procesos diarios, expiración de sesión, bitácora de accesos denegados y selección de destinatarios como lógica interna, sin convertirlos en endpoints. También se conservaron sin ampliación los RF-18 a RF-20, RF-22 y RF-37 a RF-39, porque el SRS los clasifica como alcance posterior al semestre aunque el contrato incluya recursos preparatorios.

Permanecen pendientes de implementación y documentación las reglas de negocio específicas: autorizaciones por rol/parque/asignación, precondiciones de opiniones, comité, dictamen y calificación, transiciones de evidencia y cálculos de cumplimiento. Son pendientes de comportamiento del Backend, no de diseño de recursos REST.

## Cierre de sesión de comité y alcance posterior

Se incorporó `DELETE /sesiones-comite/{sesionId}` para cerrar una sesión de comité. La operación queda restringida a Coordinación AMPIP, retira el acceso temporal de solo lectura y es idempotente: repetirla sobre una sesión cerrada devuelve `204` sin generar un nuevo evento de bitácora.

RF-19-AC-4 permanece como **No cubierto — Fuera del alcance actual** y sin endpoint de configuración. El SRS ubica los avisos de vencimiento del distintivo en funcionalidad posterior al semestre, por lo que los plazos configurables se implementarán en una versión futura y no se amplía la API actual.
