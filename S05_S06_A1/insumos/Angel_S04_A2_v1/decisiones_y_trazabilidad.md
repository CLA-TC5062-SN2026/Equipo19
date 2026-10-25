# Decisiones de diseño y trazabilidad de la API de SGPIS

**Actividad:** S04_A2
**Alumno:** Ángel Sebastián Kociankowski Montelongo (A01379225)
**Curso:** TC5062, Análisis, diseño y construcción de software (Gpo 10)
**Contrato:** `openapi.yaml`, OpenAPI 3.0.3, versión 1.1.0, base `/api/v1`

`openapi.yaml` es el contrato que precede al código. De él salen los endpoints de FastAPI en S05-S06 y las pruebas de S09. Cada operación declara en `x-acceptance-criteria` los criterios Given-When-Then del SRS que satisface, y la tabla de la sección 4 se generó con un script a partir de esas extensiones. Cada vez que cambia el YAML, la tabla se regenera con el mismo script.

## 1. Insumos y alcance

**Orden de las actividades.** Hice esta actividad antes que S04_A1, así que el agente generó la v0 del contrato solo con el SRS y el stack, sin el diagrama de clases ni el de componentes que pide la Parte 1. Después de terminar S04_A1 concilié los dos entregables: las enumeraciones del contrato y del diagrama de clases usan los mismos valores, agregué `GET /salud` (lo usa el diagrama de despliegue) y documenté que las rutas bajo `/parques/{parqueId}` operan sobre el expediente de la generación vigente, que es como el diagrama de clases modela el dominio. Por agregar una ruta, el contrato pasó de 1.0.0 a 1.1.0. La tabla clase por clase está en `S04_A1/decisiones_diagramas.md`.

El contrato parte del `SRS_final.md` v1.4 (31 RF, 110 criterios de aceptación), de la matriz RF ↔ casos de uso que trae su anexo y del stack de `stack_decision.md`: FastAPI, PostgreSQL y una SPA en React. Los identificadores RF-01 a RF-31 y sus AC no cambiaron de significado en el `SRS_equipo.md` v2.0 de S03-A1, así que la trazabilidad vale contra los dos documentos.

Cubre los RF con prioridad "MVP feb-2027" y "2027": 27 RF y 101 criterios de aceptación. Los 101 tienen al menos un endpoint.

## 2. Sección B. Decisiones de diseño

### 2.1 ¿Por qué estos recursos y endpoints? ¿Cuáles quedaron fuera?

Los recursos salen de los sustantivos del dominio que el SRS ya define en su glosario y que tienen ciclo de vida propio: versión del catálogo, criterio, generación, parque, usuario, asignación de consultor, autoevaluación, evidencia, observación, plan de trabajo, revisión del análisis de riesgos, Opinión de Cumplimiento, sesión de comité y dictamen. A eso se suman `sesiones` para la autenticación y tres lecturas calculadas: cumplimiento, elegibilidad para comité y reportes. Son 17 grupos (tags), 51 rutas y 75 operaciones; el grupo 17 es `GET /salud`, que usa el monitoreo externo.

Tres criterios ordenaron el diseño:

1. **El parque es la raíz del expediente.** Casi todo lo que el SRS describe pertenece a un parque, y casi todas las reglas de permiso dependen de la relación del usuario con ese parque: la APPI del parque, el consultor asignado vigente, el consultor de comité con sesión abierta. Por eso los recursos del expediente se anidan bajo `/parques/{parqueId}`. Con esa jerarquía, el aislamiento entre parques de RNF-01 se resuelve en un solo punto del backend: una dependencia de FastAPI que valida la relación usuario-parque antes de entrar a cualquier ruta anidada.
2. **Lo que tiene id propio también tiene URI de primer nivel.** Evidencias, Opiniones, sesiones de comité y dictámenes se crean bajo el parque, pero se leen y se modifican en `/evidencias/{id}`, `/dictamenes/{id}`, etc. El consultor que revisa una evidencia o el Director General que firma un dictamen ya tienen el id; obligarlos a reconstruir la ruta completa no agrega nada.
3. **Un solo camino de escritura por recurso.** La v0 tenía dos formas de asignar un consultor y dos colecciones para crear un parque. Las dos permitían saltarse una regla del SRS (el historial de RF-10-AC-2 en el primer caso). La revisión las dejó en una.

**Lo que quedó fuera del alcance del contrato:**

| Fuera | Motivo |
|---|---|
| RF-18 Registrar auditorías del subestándar 1.4 | Prioridad "Posterior" en el SRS. |
| RF-19 Avisar vencimiento del distintivo | Prioridad "Posterior". Depende además de la vigencia de tres años, que el cliente real no ha confirmado (RD-08). |
| RF-20 Avisar auditoría interna pendiente | Prioridad "Posterior". Depende de RF-18. |
| RF-22 Reporte agregado para asociados | Prioridad "Posterior". |
| RF-32 a RF-39 del SRS de equipo (fases del expediente, Evaluación de Desempeño, contacto principal de la APPI, bitácora consultable, recomendaciones del consultor, visita de validación, estado del distintivo y renovación, vencimiento de documentos críticos) | Los agregó la consolidación de S03-A1 y ninguno entra en el Sprint 1. Se incorporan al contrato cuando el backlog los traiga a un sprint, con una versión menor del contrato (1.x), porque agregar rutas no rompe a los clientes existentes. |
| Endpoints para el Administrador técnico (respaldos de RNF-13, depuración de RNF-14) | Las herramientas técnicas de RF-03-AC-3 son de infraestructura y se usan por SSH en el servidor (ver `S04_A1/decision_arquitectonica.md`). Ninguna ruta de la API las expone. |
| Carga de video, pagos y cuotas, firma electrónica avanzada, integración con terceros | Fuera del alcance del semestre según la sección 1.2 del SRS. |

Los criterios de las cuatro filas "Posterior" son los únicos 9 de los 110 sin endpoint. Aparecen en la tabla de la sección 4 marcados como gap.

### 2.2 ¿Qué patrones de diseño de API se incluyeron y cuáles se excluyeron?

**Incluidos**

| Patrón | Cómo quedó | Por qué |
|---|---|---|
| Versionado en la URI | Prefijo `/api/v1` en el servidor. `info.version` sigue SemVer: una versión menor agrega rutas o campos opcionales; una versión mayor cambia rutas o semántica y abriría `/api/v2`. | El versionado por cabecera (`Accept: application/vnd...`) es más purista, pero esconde la versión en un lugar que ni la SPA ni Swagger UI muestran a simple vista. Con un solo cliente propio, el prefijo es suficiente y es lo que FastAPI resuelve con un `APIRouter(prefix=...)`. |
| Paginación por página | `pagina`, `tamanoPagina` (máximo 100) y `orden` en los listados que crecen: parques, usuarios, criterios del parque, autoevaluaciones, evidencias y plan de trabajo. Responden con un sobre `{pagina, tamanoPagina, total, items}`. | RNF-06 pide que la lista de evidencias de un expediente con 1,500 registros responda en 2 segundos o menos. Un tope de 100 por página lo hace posible sin depender del cliente. `total` es lo que la SPA necesita para pintar el paginador. |
| Arreglo simple en colecciones acotadas | Versiones del catálogo, generaciones, historial de tipo de PI, asignaciones, revisiones del análisis de riesgos, Opiniones, sesiones de comité y dictámenes de un parque. | Ninguna de estas colecciones pasa de unas decenas de elementos por parque. Paginarlas solo agregaría parámetros que nadie usa. |
| Filtrado con parámetros específicos | Filtros con nombre por caso de uso: `estado`, `estandar`, `marca` y `atrasado` en criterios; `generacionId`, `region`, `estado` y `atrasado` en parques; `mes` en el reporte mensual. | Cada filtro responde a una pantalla del SRS. Por ejemplo, la detección de atraso de RF-09 es `GET /parques/{parqueId}/criterios?atrasado=true`; antes era una ruta aparte (`/atrasos`) que devolvía el mismo recurso. |
| Idempotencia explícita | `Idempotency-Key` en la carga de evidencias y de nuevas versiones; PUT idempotentes (`tipo-pi`, autoevaluación, documento del análisis de riesgos). | La APPI sube evidencia desde el celular con señal irregular. Un reintento no debe duplicar la evidencia ni regresar a "en revisión" un criterio ya cumplido (RF-27-AC-7). |
| Transiciones de estado como `PATCH` del campo `estado` | Un solo patrón para aceptar evidencias, calificar y reabrir criterios, firmar dictámenes y cerrar sesiones de comité, con 409 si la transición no está permitida. | Las dos máquinas de estado de RF-27 quedan visibles en el contrato y el backend las valida en un solo lugar. Ver `revision_rest.md`, O-11. |
| Error uniforme | Esquema `Error {codigo, mensaje, detalles}` en todas las respuestas 4xx y 5xx, con el texto literal del SRS en `mensaje`. | Las pruebas de S09 pueden comparar `codigo` sin depender de la redacción, y el usuario ve exactamente el mensaje que pide el SRS. |
| `Location` en todo 201 | Cada recurso creado devuelve su URI. | Es la convención HTTP para una creación, y la SPA navega al recurso nuevo sin construir la ruta. |

**Excluidos**

| Patrón | Por qué no |
|---|---|
| Paginación por cursor | Sirve para feeds grandes que cambian mientras se recorren. Aquí los listados son chicos y la SPA necesita saltar a la página N y mostrar el total, que el cursor no da. |
| Lenguaje genérico de filtros (OData, RSQL, `?filter=...`) | Abre consultas arbitrarias sobre datos de seguridad y complica la validación de permisos por campo. Los filtros con nombre cubren todas las pantallas del SRS. |
| Selección de campos (`?fields=`) y expansión de relaciones (`?expand=`) | Las respuestas ya son chicas y hay un solo cliente. Además, cada campo expandible sería un punto más donde revisar que no se filtre contenido de evidencias de seguridad (RNF-02). |
| HATEOAS (enlaces en las respuestas) | La SPA conoce las rutas por el contrato. Los enlaces agregarían volumen sin un consumidor que los aproveche. |
| Control de concurrencia con `ETag` / `If-Match` | Cada parque tiene un solo consultor asignado y las escrituras de la APPI son altas de evidencia, no ediciones del mismo recurso. El caso que sí tenía carrera, la Opinión duplicada, se cubre con un índice único y 409. Si en el uso real aparecen ediciones simultáneas, por ejemplo dos personas de Coordinación sobre el mismo parque, se agrega en una versión menor. |
| Operaciones masivas | Fuera de la carga del catálogo en CSV (RF-01), el SRS no pide crear ni modificar en lote. |
| Límite de solicitudes general | Solo se limita el inicio de sesión (5 intentos, 429 con `Retry-After`), porque es lo que pide RF-26. Un límite general se configura en el proxy. |

### 2.3 ¿En qué aspectos el agente propuso algo que no seguía buenas prácticas REST? ¿Cómo lo detecté?

El detalle completo está en `revision_rest.md`. En resumen, la v0 del agente tenía cuatro tipos de problema:

1. **Acciones en la URI.** `/auth/login`, `/auth/logout`, `/catalogo/exportar` y `/recuperacion/confirmar` son verbos. `/evidencias/{id}/aceptacion`, `/dictamenes/{id}/firma` y `/criterios/{id}/reapertura` son acciones con nombre de sustantivo, modeladas como `POST` sobre un subrecurso que no existe. Las primeras quedaron como recursos (`sesiones`, `archivo`, `recuperaciones-contrasena/{token}`) y las segundas como `PATCH` del estado.
2. **Verbos con semántica equivocada.** `DELETE` que no borraba (bajas lógicas que dejaban el recurso visible), un `PUT` no idempotente (`tipo-pi`) y creaciones por `POST` sin protección contra reintentos.
3. **Códigos inconsistentes.** 404 para ids del cuerpo, 422 y 409 intercambiados para el mismo tipo de error, 201 sin `Location` y un 401 para la cuenta bloqueada, que no le dice al cliente cuándo reintentar.
4. **Una promesa que el diseño no podía cumplir.** El JWT stateless no invalida el token al cerrar sesión ni expira por inactividad, y sin embargo la descripción lo prometía.

**Cómo lo detecté.** Primero validé la v0 con las herramientas. Pasó el parser de Swagger sin errores, y Redocly solo marcó dos de sintaxis. Con eso confirmé que la validación automática no iba a encontrar problemas de diseño. Después pedí una revisión a un segundo agente que no participó en la generación, con instrucción de cruzar cada código de error contra el AC del SRS que la operación dice cumplir. Separé generación y revisión porque el agente que genera tiende a defender su propio diseño. De sus 20 observaciones adopté 19 tal como venían y ajusté una (O-18: elegí 429 en lugar de 423).

El problema del JWT ya lo conocía: el equipo descartó el token stateless para HU-01 en el Sprint 1 (S03_A2). El revisor llegó a la misma conclusión por su cuenta, y eso le dio peso a la observación.

Lo que el revisor no detectó es que el SRS escribe rutas dentro de tres AC (RF-01-AC-2, RF-04-AC-2, RF-25-AC-2) que ya no existen en el contrato corregido. El revisor comparó códigos contra el SRS, pero no rutas. Queda como cambio pendiente del SRS (ver `revision_rest.md`).

## 3. Otras decisiones del contrato

- **Autenticación.** Bearer JWT, como pide la actividad, amarrado a una sesión en el servidor: el token lleva `sub` y `sid`, y cada solicitud valida la sesión en la base. Así se cumplen RF-26-AC-5 y AC-6 y el retiro inmediato de acceso de RF-10 y RF-29. La recuperación de contraseña siempre responde 202, exista o no el correo, y el contador de intentos fallidos corre también para correos inexistentes. Las dos medidas evitan que la API sirva para averiguar qué cuentas existen.
- **Activación de cuenta.** RF-03-AC-1 deja la cuenta "pendiente de activación" y el SRS no decía cómo se activa. Se agregó `PATCH /invitaciones/{token}`, con el mismo mecanismo de enlace de un solo uso que la recuperación de contraseña.
- **Límite de 100 MB.** Se mide sobre el archivo, no sobre el cuerpo multipart, para que el caso frontera de RF-06-AC-3 (exactamente 100 MB se acepta) no falle por los bytes del encabezado.
- **Región.** Las 32 entidades federativas como claves ISO 3166-2:MX (`MX-NLE`). Un enum con acentos y espacios como valores se rompe en la primera diferencia de codificación entre la SPA y el backend. La SPA muestra el nombre.
- **Procesos sin endpoint.** La revisión diaria de plazos (RF-09-AC-2, AC-3; RF-30-AC-2, AC-3) es un job del backend que corta a las 00:00 de Ciudad de México (RNF-11). Su resultado se expone en las lecturas de criterios y de avance. Las transiciones automáticas del criterio (RF-27-AC-4, AC-7; RF-11-AC-4) y los correos (RNF-12) son efectos laterales de la operación que los origina. La tabla los marca así.

## 4. Tabla de trazabilidad: criterios de aceptación ↔ endpoints

Generada a partir de `x-acceptance-criteria` en `openapi.yaml`. Rutas relativas a `/api/v1`.

| Criterio | Endpoint(s) que lo satisfacen | Nota |
|---|---|---|
| **RF-01** | **Cargar catálogo con versión** |  |
| RF-01-AC-1 | `GET /versiones-catalogo`<br>`POST /versiones-catalogo`<br>`GET /versiones-catalogo/{versionId}` |  |
| RF-01-AC-2 | `POST /versiones-catalogo` |  |
| RF-01-AC-3 | `GET /parques/{parqueId}`<br>`PATCH /parques/{parqueId}` |  |
| RF-01-AC-4 | `POST /versiones-catalogo` |  |
| **RF-02** | **Dar de alta parque** |  |
| RF-02-AC-1 | `POST /parques` |  |
| RF-02-AC-2 | `POST /parques` |  |
| RF-02-AC-3 | `POST /parques`<br>`PATCH /parques/{parqueId}` |  |
| **RF-03** | **Dar de alta usuarios y roles** |  |
| RF-03-AC-1 | `PATCH /invitaciones/{token}`<br>`GET /usuarios`<br>`POST /usuarios`<br>`GET /usuarios/{usuarioId}` |  |
| RF-03-AC-2 | `POST /usuarios`<br>`PATCH /usuarios/{usuarioId}`<br>`POST /parques/{parqueId}/asignaciones-consultor` |  |
| RF-03-AC-3 | `POST /usuarios`<br>`PATCH /usuarios/{usuarioId}` |  |
| **RF-04** | **Autoevaluación filtrada por tipo de PI** |  |
| RF-04-AC-1 | `GET /parques/{parqueId}/criterios`<br>`GET /parques/{parqueId}/autoevaluaciones` |  |
| RF-04-AC-2 | `PUT /parques/{parqueId}/autoevaluaciones/{criterioId}` |  |
| **RF-05** | **Subir evidencia y registrar observación** |  |
| RF-05-AC-1 | `GET /parques/{parqueId}/criterios/{criterioId}/evidencias`<br>`POST /parques/{parqueId}/criterios/{criterioId}/evidencias`<br>`GET /parques/{parqueId}/evidencias` |  |
| RF-05-AC-2 | `GET /evidencias/{evidenciaId}`<br>`POST /evidencias/{evidenciaId}/observaciones`<br>`GET /evidencias/{evidenciaId}/observaciones/{observacionId}` |  |
| RF-05-AC-3 | `POST /evidencias/{evidenciaId}/observaciones` |  |
| RF-05-AC-4 | `GET /evidencias/{evidenciaId}`<br>`POST /evidencias/{evidenciaId}/versiones` |  |
| **RF-06** | **Rechazar archivo > 100 MB o de formato no permitido** |  |
| RF-06-AC-1 | `POST /parques/{parqueId}/criterios/{criterioId}/evidencias`<br>`POST /evidencias/{evidenciaId}/versiones` |  |
| RF-06-AC-2 | `POST /parques/{parqueId}/criterios/{criterioId}/evidencias` |  |
| RF-06-AC-3 | `POST /parques/{parqueId}/criterios/{criterioId}/evidencias`<br>`POST /evidencias/{evidenciaId}/versiones` |  |
| RF-06-AC-4 | `POST /parques/{parqueId}/criterios/{criterioId}/evidencias`<br>`POST /evidencias/{evidenciaId}/versiones` |  |
| RF-06-AC-5 | `POST /parques/{parqueId}/criterios/{criterioId}/evidencias`<br>`POST /evidencias/{evidenciaId}/versiones` |  |
| **RF-07** | **Vista de estado de criterio para AMPIP** |  |
| RF-07-AC-1 | `GET /parques/{parqueId}/criterios`<br>`GET /reportes/avance-parques` |  |
| RF-07-AC-2 | `GET /evidencias/{evidenciaId}/contenido` |  |
| RF-07-AC-3 | `GET /evidencias/{evidenciaId}/contenido` |  |
| **RF-08** | **Calcular dos cifras de cumplimiento** |  |
| RF-08-AC-1 | `GET /parques/{parqueId}/cumplimiento` |  |
| RF-08-AC-2 | `GET /parques/{parqueId}/cumplimiento` |  |
| RF-08-AC-3 | `GET /parques/{parqueId}/cumplimiento` |  |
| **RF-09** | **Plan de trabajo y detección de atraso** |  |
| RF-09-AC-1 | `GET /parques/{parqueId}/plan-trabajo`<br>`POST /parques/{parqueId}/plan-trabajo`<br>`GET /parques/{parqueId}/plan-trabajo/{renglonId}` |  |
| RF-09-AC-2 | `GET /parques/{parqueId}/criterios`<br>`GET /reportes/avance-parques` | Lo calcula el job diario; se expone en la lectura |
| RF-09-AC-3 | `GET /parques/{parqueId}/criterios` | Lo calcula el job diario; se expone en la lectura |
| RF-09-AC-4 | `POST /parques/{parqueId}/plan-trabajo`<br>`PATCH /parques/{parqueId}/plan-trabajo/{renglonId}` |  |
| **RF-10** | **Asignar consultor a parque** |  |
| RF-10-AC-1 | `POST /parques/{parqueId}/asignaciones-consultor`<br>`GET /parques/{parqueId}/asignaciones-consultor/{asignacionId}` |  |
| RF-10-AC-2 | `GET /parques/{parqueId}/asignaciones-consultor`<br>`POST /parques/{parqueId}/asignaciones-consultor` |  |
| RF-10-AC-3 | `POST /parques/{parqueId}/asignaciones-consultor` |  |
| **RF-11** | **Recalcular criterios al cambiar tipo de PI** |  |
| RF-11-AC-1 | `PUT /parques/{parqueId}/tipo-pi`<br>`GET /parques/{parqueId}/tipos-pi` |  |
| RF-11-AC-2 | `PUT /parques/{parqueId}/tipo-pi`<br>`GET /parques/{parqueId}/tipos-pi` |  |
| RF-11-AC-3 | `PUT /parques/{parqueId}/tipo-pi` |  |
| RF-11-AC-4 | `PUT /parques/{parqueId}/tipo-pi` | Efecto lateral automático de la operación |
| **RF-12** | **Emitir Opinión de Cumplimiento** |  |
| RF-12-AC-1 | `POST /parques/{parqueId}/opiniones-cumplimiento`<br>`GET /opiniones-cumplimiento/{opinionId}` |  |
| RF-12-AC-2 | `POST /parques/{parqueId}/opiniones-cumplimiento` |  |
| RF-12-AC-3 | `POST /parques/{parqueId}/opiniones-cumplimiento` |  |
| RF-12-AC-4 | `POST /parques/{parqueId}/opiniones-cumplimiento` |  |
| RF-12-AC-5 | `POST /parques/{parqueId}/opiniones-cumplimiento` |  |
| RF-12-AC-6 | `GET /parques/{parqueId}/opiniones-cumplimiento`<br>`POST /parques/{parqueId}/opiniones-cumplimiento`<br>`GET /opiniones-cumplimiento/{opinionId}`<br>`GET /sesiones-comite/{sesionId}/expediente` |  |
| **RF-13** | **Acceso temporal del consultor de comité** |  |
| RF-13-AC-1 | `GET /parques/{parqueId}/sesiones-comite`<br>`POST /parques/{parqueId}/sesiones-comite`<br>`GET /sesiones-comite/{sesionId}`<br>`GET /sesiones-comite/{sesionId}/expediente` |  |
| RF-13-AC-2 | `POST /parques/{parqueId}/sesiones-comite` |  |
| RF-13-AC-3 | `PATCH /sesiones-comite/{sesionId}`<br>`GET /sesiones-comite/{sesionId}/expediente` |  |
| **RF-14** | **Registrar dictamen** |  |
| RF-14-AC-1 | `GET /dictamenes/{dictamenId}`<br>`PATCH /dictamenes/{dictamenId}` |  |
| RF-14-AC-2 | `POST /parques/{parqueId}/dictamenes` |  |
| RF-14-AC-3 | `POST /parques/{parqueId}/dictamenes`<br>`PATCH /dictamenes/{dictamenId}` |  |
| RF-14-AC-4 | `POST /parques/{parqueId}/dictamenes`<br>`PATCH /dictamenes/{dictamenId}` |  |
| RF-14-AC-5 | `POST /parques/{parqueId}/dictamenes`<br>`PATCH /dictamenes/{dictamenId}` |  |
| RF-14-AC-6 | `GET /parques/{parqueId}/dictamenes`<br>`POST /parques/{parqueId}/dictamenes`<br>`GET /dictamenes/{dictamenId}` |  |
| RF-14-AC-7 | `PATCH /dictamenes/{dictamenId}` |  |
| RF-14-AC-8 | `POST /parques/{parqueId}/dictamenes` |  |
| **RF-15** | **Validar expediente para comité** |  |
| RF-15-AC-1 | `POST /parques/{parqueId}/sesiones-comite`<br>`GET /parques/{parqueId}/elegibilidad-comite` |  |
| RF-15-AC-2 | `POST /parques/{parqueId}/sesiones-comite`<br>`GET /parques/{parqueId}/elegibilidad-comite` |  |
| RF-15-AC-3 | `POST /parques/{parqueId}/sesiones-comite`<br>`GET /parques/{parqueId}/elegibilidad-comite` |  |
| **RF-16** | **Registrar revisión del análisis de riesgos** |  |
| RF-16-AC-1 | `GET /parques/{parqueId}/revisiones-analisis-riesgos`<br>`POST /parques/{parqueId}/revisiones-analisis-riesgos`<br>`GET /parques/{parqueId}/revisiones-analisis-riesgos/{revisionId}` |  |
| RF-16-AC-2 | `PUT /parques/{parqueId}/documento-analisis-riesgos`<br>`GET /parques/{parqueId}/documento-analisis-riesgos` |  |
| RF-16-AC-3 | `GET /parques/{parqueId}/documento-analisis-riesgos` |  |
| RF-16-AC-4 | `PATCH /parques/{parqueId}/criterios/{criterioId}`<br>`GET /parques/{parqueId}/revisiones-analisis-riesgos` |  |
| **RF-17** | **Bloquear calificación de estándares 2, 3 y 7** |  |
| RF-17-AC-1 | `PATCH /parques/{parqueId}/criterios/{criterioId}` |  |
| RF-17-AC-2 | `PATCH /parques/{parqueId}/criterios/{criterioId}` |  |
| RF-17-AC-3 | `POST /parques/{parqueId}/criterios/{criterioId}/evidencias` |  |
| **RF-18** | **Registrar auditorías del subestándar 1.4** | Prioridad Posterior |
| RF-18-AC-1 | Sin endpoint | **Gap**: RF con prioridad Posterior, fuera del alcance del contrato |
| RF-18-AC-2 | Sin endpoint | **Gap**: RF con prioridad Posterior, fuera del alcance del contrato |
| **RF-19** | **Avisar vencimiento del distintivo** | Prioridad Posterior |
| RF-19-AC-1 | Sin endpoint | **Gap**: RF con prioridad Posterior, fuera del alcance del contrato |
| RF-19-AC-2 | Sin endpoint | **Gap**: RF con prioridad Posterior, fuera del alcance del contrato |
| RF-19-AC-3 | Sin endpoint | **Gap**: RF con prioridad Posterior, fuera del alcance del contrato |
| **RF-20** | **Avisar auditoría interna pendiente** | Prioridad Posterior |
| RF-20-AC-1 | Sin endpoint | **Gap**: RF con prioridad Posterior, fuera del alcance del contrato |
| RF-20-AC-2 | Sin endpoint | **Gap**: RF con prioridad Posterior, fuera del alcance del contrato |
| **RF-21** | **Reporte mensual para Dirección** |  |
| RF-21-AC-1 | `GET /reportes/direccion-mensual` |  |
| RF-21-AC-2 | `GET /reportes/direccion-mensual` |  |
| **RF-22** | **Reporte agregado para asociados** | Prioridad Posterior |
| RF-22-AC-1 | Sin endpoint | **Gap**: RF con prioridad Posterior, fuera del alcance del contrato |
| RF-22-AC-2 | Sin endpoint | **Gap**: RF con prioridad Posterior, fuera del alcance del contrato |
| **RF-23** | **Vista consolidada para gerente corporativo** |  |
| RF-23-AC-1 | `GET /reportes/portafolio-corporativo` |  |
| RF-23-AC-2 | `POST /parques/{parqueId}/criterios/{criterioId}/evidencias`<br>`POST /evidencias/{evidenciaId}/versiones`<br>`POST /evidencias/{evidenciaId}/observaciones` |  |
| **RF-24** | **Definir evidencia suficiente por criterio** |  |
| RF-24-AC-1 | `GET /criterios/{criterioId}`<br>`PATCH /criterios/{criterioId}`<br>`GET /parques/{parqueId}/criterios/{criterioId}` |  |
| RF-24-AC-2 | `PATCH /criterios/{criterioId}` |  |
| **RF-25** | **Restringir descarga del archivo maestro** |  |
| RF-25-AC-1 | `GET /criterios/{criterioId}`<br>`GET /parques/{parqueId}/criterios`<br>`GET /parques/{parqueId}/criterios/{criterioId}` |  |
| RF-25-AC-2 | `GET /versiones-catalogo/{versionId}/archivo` |  |
| RF-25-AC-3 | `GET /versiones-catalogo/{versionId}/archivo` |  |
| RF-25-AC-4 | `GET /versiones-catalogo/{versionId}/archivo`<br>`GET /parques/{parqueId}/criterios` |  |
| **RF-26** | **Autenticación** |  |
| RF-26-AC-1 | `POST /sesiones` |  |
| RF-26-AC-2 | `POST /sesiones` |  |
| RF-26-AC-3 | `POST /sesiones` |  |
| RF-26-AC-4 | `POST /recuperaciones-contrasena`<br>`PATCH /recuperaciones-contrasena/{token}` |  |
| RF-26-AC-5 | `DELETE /sesiones/actual` |  |
| RF-26-AC-6 | `GET /sesiones/actual` |  |
| **RF-27** | **Calificar criterio** |  |
| RF-27-AC-1 | `GET /evidencias/{evidenciaId}`<br>`PATCH /evidencias/{evidenciaId}` |  |
| RF-27-AC-2 | `PATCH /parques/{parqueId}/criterios/{criterioId}`<br>`GET /parques/{parqueId}/cumplimiento` |  |
| RF-27-AC-3 | `PATCH /parques/{parqueId}/criterios/{criterioId}` |  |
| RF-27-AC-4 | `POST /parques/{parqueId}/criterios/{criterioId}/evidencias` | Efecto lateral automático de la operación |
| RF-27-AC-5 | `PATCH /parques/{parqueId}/criterios/{criterioId}`<br>`PATCH /evidencias/{evidenciaId}` |  |
| RF-27-AC-6 | `PATCH /parques/{parqueId}/criterios/{criterioId}`<br>`GET /parques/{parqueId}/cumplimiento` |  |
| RF-27-AC-7 | `POST /parques/{parqueId}/criterios/{criterioId}/evidencias` | Efecto lateral automático de la operación |
| RF-27-AC-8 | `PATCH /parques/{parqueId}/criterios/{criterioId}` |  |
| **RF-28** | **Crear generación** |  |
| RF-28-AC-1 | `GET /generaciones`<br>`POST /generaciones`<br>`GET /generaciones/{generacionId}` |  |
| RF-28-AC-2 | `POST /generaciones` |  |
| RF-28-AC-3 | `POST /parques` |  |
| **RF-29** | **Dar de baja usuario o parque** |  |
| RF-29-AC-1 | `PATCH /usuarios/{usuarioId}` |  |
| RF-29-AC-2 | `PATCH /usuarios/{usuarioId}` |  |
| RF-29-AC-3 | `GET /parques`<br>`PATCH /parques/{parqueId}`<br>`GET /reportes/avance-parques` |  |
| **RF-30** | **Fechas del programa y atraso por falta de actualización** |  |
| RF-30-AC-1 | `GET /parques/{parqueId}`<br>`PATCH /parques/{parqueId}` |  |
| RF-30-AC-2 | `GET /reportes/avance-parques` | Lo calcula el job diario; se expone en la lectura |
| RF-30-AC-3 | `POST /parques/{parqueId}/actualizaciones-anuales`<br>`GET /parques/{parqueId}/actualizaciones-anuales/{actualizacionId}`<br>`GET /reportes/avance-parques` | Lo calcula el job diario; se expone en la lectura |
| **RF-31** | **Historial de parques del programa** |  |
| RF-31-AC-1 | `GET /parques/{parqueId}/historial` |  |
| RF-31-AC-2 | `POST /parques` |  |
| RF-31-AC-3 | `GET /parques/{parqueId}/historial` |  |

### Resumen de cobertura

| | Criterios |
|---|---|
| Total en el SRS v1.4 | 110 |
| En el alcance del contrato (MVP feb-2027 y 2027) | 101 |
| Con al menos un endpoint | 101 |
| Gap: sin endpoint | 9, todos de RF con prioridad "Posterior" (RF-18, RF-19, RF-20, RF-22) |
| IDs en `x-acceptance-criteria` que no existen en el SRS | 0 |

Cuatro operaciones no satisfacen ningún criterio y lo declaran con `x-justificacion`: `GET /salud` (monitoreo de RNF-08), `GET /parques/{parqueId}/autoevaluaciones/{criterioId}` (existe para que el `Location` del PUT apunte a algo), `DELETE /parques/{parqueId}/plan-trabajo/{renglonId}` (corregir un renglón capturado por error) y `DELETE /parques/{parqueId}/documento-analisis-riesgos` (la descripción de RF-16 dice que la APPI puede eliminar el documento, pero no tiene AC). Este último sí es un hueco del SRS: falta el criterio de aceptación de esa eliminación, y lo agrego en la siguiente versión.
