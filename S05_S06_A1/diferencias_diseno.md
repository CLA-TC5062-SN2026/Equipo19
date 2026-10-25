# Diferencias de diseño y consolidación del equipo

**Equipo:** 19 (Ángel Kociankowski, Leonardo Cossío, Erick Ramírez)
**Actividad:** S05-S06-A1, Parte 0
**Resultado:** `openapi_equipo.yaml` v2.0.0, `diagrama_clases_equipo.puml`, `arquitectura_equipo.md`
**Análisis de diferencias del agente (sin editar):** `evidencia_agente/analisis_diferencias_agente.md`. Los IDs O-xx (contrato), K-xx (clases) y Q-xx (arquitectura) de este documento son los de ese análisis.
**Script que aplica los cambios al contrato:** `consolidacion/consolidar_openapi.py` (cada bloque cita la decisión D-xx que aplica)

## 1. Insumos y cómo comparamos

Los diseños individuales de S04 de los tres están en `insumos/`, tal como los entregó cada uno:

| Artefacto (S04) | Ángel | Leonardo | Erick |
|---|---|---|---|
| `openapi.yaml` (S04_A2) | `Angel_S04_A2_v1` (75 operaciones, contra su SRS individual v1.4) y `Angel_S04_A2_v2` (86, contra el SRS de equipo) | `Leonardo_S04_A2` (46 operaciones) | `Erick_S04_A2` (47 operaciones) |
| Diagrama de clases (S04_A1) | `Angel_S04_A1_v1` y `_v2` | `Leonardo_S04_A1/diagrama_clases.puml` | `Erick_S04_A1/diagrama_clases_agente.puml` |
| Componentes, despliegue y ADR (S04_A1) | `Angel_S04_A1_v1` y `_v2` | `Leonardo_S04_A1` | `Erick_S04_A1` |

Ángel tiene dos versiones de S04. La v1 es la que se usó como base del borrador de contrato (`consolidar_openapi.py` parte de ella). La v2 la rehízo contra el SRS de equipo y es la que entró a la comparación, para no comparar a Leonardo y Erick contra un diseño que respondía a otro SRS.

Trabajamos en dos pasos:

1. Borrador. Con solo el diseño de Ángel a la mano, lo consolidamos contra el `SRS_equipo.md` v2.0 (`../S03_A1/SRS_equipo.md`) y contra lo que el curso fija para S05-S06-A2. De ahí salieron D-01 a D-16 (secciones 3 a 5).
2. Tres diseños. Cuando subimos los S04 de Leonardo y Erick, el agente comparó los tres contratos, los tres diagramas de clases y las tres arquitecturas contra el SRS de equipo y marcó, para cada consenso, gap y conflicto, si el borrador ya lo resolvía. El prompt está en `evidencia_agente/prompts.md` (Prompt 0). Revisamos cada conflicto y decidimos; donde el borrador estaba mal o se quedaba corto, lo cambiamos (D-17 a D-23). Todo eso está en la sección 6.

## 2. Qué aportó cada integrante

Separamos dos cosas: lo que el diseño de cada uno cambió en el consolidado, y lo que coincidió con el borrador y sirvió para confirmarlo. Lo segundo cuenta como consenso, no como aporte nuevo. Los requerimientos que cada uno metió al SRS de equipo en S03-A1 están en la tabla 3.2 y en `../S03_A1/diferencias_SRS.md`.

| Integrante | Lo que su diseño cambió en el consolidado | Coincidencias que confirmaron el borrador |
|---|---|---|
| Ángel | Es la base de todo el borrador (v1): convenciones REST, códigos de estado, paginación, formato `Error {codigo, mensaje, detalles}`, sesión validada en servidor, recursos propios para tipo de PI, asignaciones y contacto principal, versiones de evidencia, catálogo en cuatro niveles, expediente por parque y generación, ADR con C4 2 y 3. De su v2 salieron el dictamen colgado del expediente con el argumento de RF-14-AC-8 (D-17), la Opinión en una sola clase (D-18), el historial de calificaciones (D-19), el token de recuperación en el cuerpo (D-20), las dos consultas de D-21, la outbox y el módulo de reportes en el nivel 3, la base gestionada en producción (Q-04) y CI con MinIO (Q-09, pendiente). | Su v2 coincidió con el borrador en carga múltiple con `{creadas, rechazadas}`, fases como datos y `/configuracion`. |
| Leonardo | La frontera del módulo de notificaciones en la arquitectura: los demás módulos le piden el correo y él lo escribe (Q-06). Su diagrama de clases no trajo clases que el consolidado no tuviera; la comparación sirvió para descartar la herencia de roles (K-01) y para confirmar los 13 conceptos que modelaron los tres. | `POST /auth/login` con 200 dentro de `/auth` y el nombre `BearerAuth`, que ya estaban por D-01 (los pide el curso); propiedades JSON en camelCase; 409 para conflictos con el estado del recurso; estilo de monolito modular. |
| Erick | El dictamen del expediente con multiplicidad 0..1, que tomamos sobre el 0..* de Ángel (D-17); los procesos programados declarados en el contrato (D-23); las rutas literales del SRS como referencia para SC-01 (D-22); las rutas de los RF "Posterior" para el backlog. | Vínculo entre evidencia y criterio con estado propio (`EvidenciaCriterio`, igual que `VinculoEvidencia` de D-03); carga múltiple con `{creadas, rechazadas}`; aceptación y observación que dicen sobre qué criterio actúan; cierre de fase y `GET /bitacora` en las rutas del SRS; formato `Error {codigo, mensaje, detalles}`; reportes bajo `/reportes`; carga vía API y estáticos en el proxy. |

## 3. Contrato OpenAPI (borrador, D-01 a D-12)

### 3.1 Consenso

Las 75 operaciones del contrato v1 de Ángel cubren los 31 RF que el SRS de equipo conservó con el mismo ID (`../S03_A1/diferencias_SRS.md`, sección 1: ningún ID cambió de significado). Se conservaron sin cambio de ruta ni de método, salvo las de autenticación (D-01) y las de evidencias (D-03). El consenso entre los tres diseños está en la sección 6.1.

### 3.2 Gaps: criterios del SRS de equipo sin endpoint

| Criterios | Origen | Resolución |
|---|---|---|
| RF-01-AC-5 | C-14 | D-07 |
| RF-05-AC-5 a AC-10 | Leonardo (AC-5, AC-6, AC-10), Erick (AC-7 a AC-9) | D-03 |
| RF-06-AC-6, AC-7 | C-05 | D-04 |
| RF-08-AC-4, AC-5 | C-11 | D-05 |
| RF-11-AC-5, AC-6 | C-04 | D-06 |
| RF-32-AC-1 a AC-5 | Leonardo y Erick | D-08 |
| RF-33-AC-1 a AC-3 | Leonardo | D-09 |
| RF-34-AC-1 a AC-3 | Erick | D-10 |
| RF-35-AC-1 a AC-4 | Leonardo y Erick | D-11 |
| RF-36-AC-1, AC-2 | Erick | D-12 |

### 3.3 Conflictos y resoluciones

| ID | Tema | Diseño de base | Problema | Resolución en `openapi_equipo.yaml` |
|---|---|---|---|---|
| D-01 | Autenticación | `POST /sesiones` (201), `GET` y `DELETE /sesiones/actual`, `PATCH /invitaciones/{token}`; base `/api/v1`; esquema `bearerAuth` | El curso pide `/api/auth/register`, `/api/auth/login`, `/api/auth/me` y `securitySchemes: BearerAuth`. T-10 del Sprint 1 ya decía `POST /auth/logout`. | Base `/api`. `POST /auth/register`, `POST /auth/login` (200), `GET /auth/me`, `POST /auth/logout`. Esquema `BearerAuth`. Se conserva la sesión en servidor validada en cada solicitud y se agrega `exp` absoluto con `JWT_EXPIRATION`. Aceptamos la forma RPC solo dentro de `/auth`; el resto del contrato sigue con sustantivos. |
| D-02 | Registro abierto | Alta de cuentas solo por Coordinación AMPIP (RF-03) | Un `register` público dejaría a cualquiera crear una cuenta, y el SRS no lo permite. | `POST /auth/register` exige el token de la invitación que genera `POST /usuarios`. Fija la contraseña (bcrypt) y activa la cuenta; responde 201 sin contraseña. Reemplaza a `PATCH /invitaciones/{token}`. |
| D-03 | Evidencia y criterio | Una evidencia pertenece a un criterio y lleva el estado | C-19 pide un archivo vinculado a varios criterios, cada vínculo con su estado. Con el estado en el archivo, aceptarlo para 3.1 lo aceptaría para 3.4. | Una sola ruta de escritura, `POST /parques/{parqueId}/evidencias`, con `archivos[]` y `criterioIds[]`; responde `{creadas, rechazadas}` (RF-05-AC-8). El estado pasa al vínculo: `PATCH /evidencias/{id}/vinculos/{criterioId}` acepta y `POST /evidencias/{id}/observaciones` recibe `criterioId`. `DELETE /evidencias/{id}` hace baja lógica y responde 409 si hay un vínculo aceptado. Se retiran `POST /parques/{p}/criterios/{c}/evidencias` y `PATCH /evidencias/{id}`. |
| D-04 | Límite de archivo | 100 MB fijo en el contrato | C-05 lo hizo configurable. | `GET` y `PATCH /configuracion`; 413 con el límite vigente en el mensaje. También guarda la vigencia del distintivo (C-10). |
| D-05 | Cifras de cumplimiento | Obligatorios y avance general | C-11 agrega recomendados y fija el cálculo por suma de criterios. | `porcentajeRecomendados` en `CifrasCumplimiento`. |
| D-06 | Cambio de tipo de PI | Sin motivo | C-04 lo exige. | `motivo` obligatorio en `CambioTipoPI`; `motivo` y `cambiadoPor` en el historial. |
| D-07 | Versiones de catálogo | `vigente` booleano | C-14: las anteriores quedan en solo lectura. | `estado: activa / solo_lectura`; `PATCH /criterios/{id}` responde 409 sobre una versión en solo lectura. |
| D-08 | Fases | Solo `fase` en `Parque` | RF-32 pide estado por fase, cierre por Coordinación y avance por excepción con motivo. | `GET /parques/{p}/fases`, `POST /parques/{p}/fases/{fase}/cierre` (la ruta que cita RF-32-AC-3), `POST /parques/{p}/avances-fase`. |
| D-09 | Evaluación de Desempeño | No existía | RF-33. | `GET` y `POST /parques/{p}/evaluaciones-desempeno` con folio `ED-AAAA-NNNN`. |
| D-10 | Usuarios APPI | Hasta 3 por parque, sin contacto principal | RF-34. | `GET /parques/{p}/usuarios` y `PUT /parques/{p}/contacto-principal`; `contactoPrincipalId` en `Parque`. |
| D-11 | Bitácora | Solo se escribía | RF-35 pide consulta con filtros, solo para Coordinación. | `GET /bitacora` con filtros por parque, usuario, acción y fechas. Sigue sin operación de escritura. |
| D-12 | Recomendaciones | No existían | RF-36: no cambian estados y no son observaciones. | `GET` y `POST /parques/{p}/criterios/{c}/recomendaciones`. |

Resultado final, ya con la sección 6: 64 rutas, 91 operaciones, 111 schemas. Los 150 criterios del SRS de equipo, menos los 19 de RF con prioridad "Posterior", tienen al menos una operación; ningún `x-acceptance-criteria` cita un ID que no exista. `openapi-spec-validator` lo valida y Redocly deja 3 advertencias, las mismas que tenía el contrato individual (licencia, servidor en localhost, `/salud` sin respuesta 4xx).

## 4. Diagrama de clases

### 4.1 Consenso

Se conserva la estructura del diagrama de S04_A1 de Ángel: catálogo en cuatro niveles con marca por tipo de PI, parque con historial de clasificación, expediente por parque y generación, criterio del parque con estado de calificación, plan de trabajo, análisis de riesgos, Opiniones, comité y dictamen. El consenso entre los tres está en la sección 6.2.

### 4.2 Cambios

| ID | Clase | Antes | Ahora | Motivo |
|---|---|---|---|---|
| D-03 | `Evidencia`, `VinculoEvidencia`, `Observacion` | `CriterioParque` *-- `Evidencia {estado}`; `Observacion` colgaba de la evidencia | `Expediente` *-- `Evidencia`; `Evidencia` *-- `VinculoEvidencia {estado}` --> `CriterioParque`; `Observacion` cuelga del vínculo y guarda la versión observada | C-19, RF-05-AC-6 y AC-7 |
| D-03 | `Evidencia` | Sin baja | `eliminadaEn`, eliminada por | RF-05-AC-9 |
| D-04 | `Configuracion` | No existía | Un registro con límite y vigencia | C-05, C-10 |
| D-06 | `ClasificacionTipoPI` | Sin motivo | `motivo`, cambiado por | C-04 |
| D-07 | `VersionCatalogo` | `activa: boolean` | `estado {activa, solo_lectura}` | C-14 |
| D-08 | `CatalogoFase`, `FaseExpediente` | `fase` como enumeración en `Expediente` | Secuencia como datos; nueve `FaseExpediente` por expediente con estado, fechas y motivo | C-15, RF-32 |
| D-09 | `EvaluacionDesempeno` | No existía | Folio, fecha, versión de catálogo, resultado | RF-33 |
| D-10 | `Usuario`/`Parque` | APPI 0..3 por parque | APPI 0..*; `Parque` --> contacto principal 0..1 | RF-34 |
| D-11 | `RegistroBitacora` | Fecha, acción, resultado | Más rol, parque, tipo e id de recurso, detalle | RF-35 |
| D-12 | `Recomendacion` | No existía | Cuelga de `CriterioParque` | RF-36 |
| D-13 | `Sesion`, `EnlaceUnSoloUso` | Token en claro; sin expiración absoluta | `tokenHash`; `expiraEn` en ambos | Una fuga de la base no debe entregar invitaciones usables |
| D-17 | `Dictamen` | `SesionComite` *-- `Dictamen` 0..1 | `Expediente` *-- `Dictamen` 0..1; `Dictamen` --> `SesionComite` 0..1 ("capturado en") | RF-14-AC-8 (sección 6.4) |
| D-18 | `OpinionCumplimiento` | Abstracta con `OpinionIntermedia` y `OpinionFinal` | Una clase con `tipo` y `favorable [0..1]`; `Expediente` *-- 0..2 | K-10 (sección 6.4) |
| D-19 | `CalificacionCriterio` | No existía | Cuelga de `CriterioParque`: estado anterior y nuevo, motivo, origen, consultor, fecha | RD-14, RF-27-AC-8 (sección 6.4) |

### 4.3 Coherencia con el contrato

Revisamos que cada atributo de las clases que el contrato expone tenga su campo en un schema, con el mismo nombre en camelCase:

| Clase | Schema | Diferencias aceptadas |
|---|---|---|
| `Usuario` | `Usuario` | `contrasenaHash` nunca sale en una respuesta. |
| `Parque` + `Expediente` vigente | `Parque` | El schema aplana datos del expediente vigente (fase, fechas del programa, generación), como dice la convención del contrato. |
| `Evidencia` + `VersionEvidencia` vigente | `Evidencia` | `nombreArchivo`, `tipoMime` y `tamanoBytes` vienen de la versión vigente; `rutaObjeto` es interna. |
| `VinculoEvidencia` | `VinculoEvidencia` | `claveCriterio` y `estadoCriterio` se leen de `CriterioParque` para que la SPA no haga otra llamada. |
| `FaseExpediente` + `CatalogoFase` | `FaseExpediente` | `actual` es derivado. |
| `Dictamen` | `Dictamen` | `parqueId` y `generacionId` salen del expediente. |
| `CalificacionCriterio` | `CalificacionCriterio` | `criterioId` sale de `CriterioParque`. |
| `Configuracion`, `EvaluacionDesempeno`, `Recomendacion`, `RegistroBitacora`, `ClasificacionTipoPI`, `OpinionCumplimiento` | Mismo nombre | Ninguna. |

## 5. Arquitectura (borrador)

| ID | Tema | Diseño de base | Resolución en `arquitectura_equipo.md` |
|---|---|---|---|
| D-14 | Tamaño del equipo | ADR-001 suponía un desarrollador | Se mantiene el estilo; la regla de fronteras entre módulos se revisa en cada PR. |
| D-15 | Ruta y autenticación | `/api/v1`, `bearerAuth` | `/api`, `BearerAuth`, `exp` absoluto más sesión en servidor (D-01). |
| D-16 | Entorno local | Solo producción descrita | `docker compose` con PostgreSQL 16 y la API; el esquema se crea con `esquema_bd.sql`. Worker y Mailpit entran con correo y plazos. |

## 6. Integración de los diseños de Leonardo y Erick

El agente encontró, entre los tres contratos, 19 consensos, 50 gaps y 26 conflictos más 12 diferencias transversales; entre los tres diagramas de clases, 13 consensos, 23 gaps y 16 conflictos; y en arquitectura, 8 aspectos de consenso y 9 conflictos. Las tablas completas, con lo que propuso cada uno, están en el análisis del agente. Aquí va lo que decidimos.

Criterio para decidir: primero el SRS de equipo; después, lo que ya está implementado y probado en el backend, porque cambiarlo cuesta más que en un documento; al final, la forma que comparten dos de los tres diseños.

### 6.1 Contrato: conflictos

| ID | Tema | Decisión | Razón |
|---|---|---|---|
| O-01 | Inicio, cierre y consulta de sesión | Se queda `/auth/login` (200), `/auth/logout` y `/auth/me` (D-01). La ruta de login es la de Leonardo. El bloqueo por intentos responde 429, no 423 como en el diseño de Ángel. | 423 es "recurso bloqueado" de WebDAV; 429 con `Retry-After` es lo que un cliente HTTP ya sabe manejar. Sin logout (Leonardo) no se cumple RF-26-AC-5. |
| O-02 | Recuperación de contraseña | Cambia: el token va en el cuerpo de `POST /restablecimientos-contrasena` (D-20). La activación ya era `POST /auth/register` con token en el cuerpo (D-02). | Ángel lo propuso así: un token en la ruta queda en los registros de acceso del proxy. |
| O-03 | Alta de usuario y roles | Se queda el borrador: un `rol` por usuario con 6 valores y `parqueId` o `desarrolladorId` según el rol. "Consultor asignado" y "consultor de comité" no son roles: son la asignación vigente y la sesión de comité abierta. No se adopta `GET`/`PUT /usuarios/{id}/roles` de Leonardo. | Con un solo `consultor`, la misma persona puede estar asignada en un parque y ser de comité en otro, que es lo que RF-13-AC-2 compara. Las 7 figuras de RF-03 quedan cubiertas con 6 roles y dos relaciones. |
| O-04 | Bajas y reemplazo completo | `PATCH` con `estado` (Ángel, Erick y borrador). No se adoptan el `DELETE` como baja lógica ni el `PUT` de reemplazo de Leonardo. | `DELETE` queda para lo que de verdad desaparece de la vista; una baja de usuario o parque conserva todo su historial (RF-29). |
| O-05 | Alta de parque | Se queda `oneOf` activo/histórico con región como enum (Ángel y Erick coinciden; el borrador ya lo tenía). | RF-02-AC-1 y AC-3 piden desarrollador, generación y región de lista cerrada; RF-31-AC-2, alta de histórico. |
| O-06 | Rutas del catálogo | Se quedan `POST /versiones-catalogo` y `GET /versiones-catalogo/{versionId}/archivo`. Pedimos cambiar el texto del SRS (SC-01, sección 6.6). No se adopta el CRUD manual de catálogo de Leonardo. | Las rutas que cita el SRS (`/catalogo/versiones`, `/catalogo/exportar`) no dicen de qué versión se exporta, y con varias generaciones hay varias versiones. El CRUD manual permitiría editar una versión que RF-01-AC-5 deja en solo lectura. |
| O-07 | Evidencia suficiente | `PATCH /criterios/{criterioId}` con `evidenciaSuficiente` (borrador). | Cada criterio pertenece a una versión, así que la descripción ya queda ligada a la versión, que era el punto de Ángel. |
| O-08 | Cambio de tipo de PI | Recurso propio: `PUT /parques/{parqueId}/tipo-pi` y `GET /parques/{parqueId}/tipos-pi` (borrador, idea de Ángel). | RF-11 recalcula criterios y congela cifras; como efecto lateral de un `PATCH` de parque no se puede probar ni auditar por separado. |
| O-09 | Asignación de consultor | Colección con historial (Ángel y borrador). | RF-10-AC-2 pide conservar las asignaciones anteriores. |
| O-10 | Contacto principal | `PUT /parques/{parqueId}/contacto-principal` (Ángel y borrador). | Un recurso único hace estructural la regla de un solo contacto (RF-34-AC-2); en la base lo refuerza la FK compuesta de R-05. |
| O-11 | Fases | Fases fijas por expediente; cierre en la ruta literal del SRS (la de Erick) y avance por excepción en `POST /parques/{parqueId}/avances-fase` con motivo. | RF-32-AC-3 cita la ruta de cierre. El esquema de Leonardo no podía guardar el motivo de RF-32-AC-4 y AC-5. Erick usaba `/fases/avance-excepcion`; preferimos un sustantivo. |
| O-12 | Autoevaluación | `PUT /parques/{parqueId}/autoevaluaciones/{criterioId}` con la respuesta en el cuerpo (Ángel y borrador). SC-01 para la ruta que cita el SRS. | El `POST /autoevaluaciones` de Erick no llevaba la respuesta en el cuerpo. Con clave natural, repetir la captura no duplica. |
| O-13 | Calificar o reabrir | Se queda `PATCH /parques/{parqueId}/criterios/{criterioId}` y se agrega el historial (D-19). | El cambio de estado como `PATCH` es lo que ya estaba en el borrador y en el diseño de Erick; el historial que pedía el de Ángel lo exige RD-14. El esquema de Leonardo no tenía estado de calificación. |
| O-14 | Plan de trabajo | Renglón por criterio con responsable y fecha (borrador). | RF-09 calcula el atraso por criterio. El plan de Leonardo no tenía criterio, responsable ni fecha. |
| O-15 | Subir evidencia | `POST /parques/{parqueId}/evidencias` en multipart, una evidencia con varios vínculos y respuesta `{creadas, rechazadas}` (D-03, forma de Erick). | Con el registro de metadatos de Leonardo, el tamaño y el estado los declara el cliente (ver Q-02). |
| O-16 | Aceptar y observar | `PATCH /evidencias/{evidenciaId}/vinculos/{criterioId}` para aceptar; `POST /evidencias/{evidenciaId}/observaciones` con `criterioId` (D-03). No se adopta el `PATCH` libre de estado de Leonardo. | Con un archivo en varios criterios, la acción tiene que decir sobre qué criterio actúa. Un `PATCH` que fija `estado` directo se salta la máquina de estados de RF-27. |
| O-17 | Versión nueva | `POST /evidencias/{evidenciaId}/versiones` (Ángel y borrador). | En los diseños de Leonardo y Erick el servidor no sabe de qué evidencia es versión la carga, y RF-05-AC-4 la regresa de "observada" a "enviada". |
| O-18 | Eliminar evidencia | 204, y 409 `evidencia_aceptada` si algún vínculo está aceptado. Ángel y Erick usaban 422. | En el contrato, 409 es cuando el estado propio del recurso destino impide la operación (duplicado, transición no permitida, ya firmado, ya aceptada) y 422 cuando falla una regla de negocio que depende de otros datos (cumplimiento, Opinión, análisis de riesgos). Aquí lo que impide borrar es el estado de la propia evidencia. |
| O-19 | Acceso al archivo | `GET /evidencias/{evidenciaId}/contenido` devuelve una URL firmada (Ángel y Erick). Ningún schema expone la ubicación del objeto. | RNF-15. `Evidence.ubicacionObjeto` de Leonardo lo contradecía. |
| O-20 | Análisis de riesgos | Revisión en JSON y documento aparte, uno por parque (borrador). | RF-16 dice que el documento solo se guarda si la APPI decide subirlo. Guardarlo como evidencia (Erick) lo metería en el flujo de estados de RF-05. |
| O-21 | Emitir Opinión | `tipo` + `favorable` (Ángel, Erick y borrador). En el diagrama, D-18. | RD-09 compara "Opinión final favorable"; el `resultado` de texto libre de Leonardo no da un dato que comparar. |
| O-22 | Cerrar sesión de comité y firmar | Cierre por `PATCH /sesiones-comite/{sesionId}`; firma por `PATCH /dictamenes/{dictamenId}` con `estado: firmado` (borrador). | `DELETE` (Erick) sugiere que la sesión desaparece y RF-13 la necesita para el historial. La firma por `PATCH` mantiene un solo camino de escritura por recurso; Ángel y Erick usaban `POST /firma`. |
| O-23 | Reporte mensual | `GET /reportes/direccion-mensual` (agrupación de Erick). | Los reportes no son de una sola generación. |
| O-24 | Bitácora | `GET /bitacora` paginada (ruta de Erick, paginación de Ángel). | RF-35-AC-4 cita la ruta. "Auditoría" (Leonardo) se confunde con las auditorías del subestándar 1.4 (RF-18). |
| O-25 | Configuración | `GET` y `PATCH /configuracion` (Ángel y borrador). | C-10 también vuelve configurable la vigencia del distintivo; un recurso solo para cargas (Erick) obligaba a crear otro. |
| O-26 | Recomendaciones | Bajo `/parques/{parqueId}/criterios/{criterioId}` (Ángel), igual que la calificación (O-13). | Sin `GET` (Erick) la APPI no las ve (RF-36-AC-1). |

### 6.2 Contrato: diferencias transversales

| Aspecto | Decisión | De quién |
|---|---|---|
| Servidor y versión | `http://localhost:8000/api`, versión 2.0.0 | Curso (D-01) |
| Esquema de seguridad | `BearerAuth` + sesión en servidor | Nombre de Leonardo; sesión de Ángel |
| Formato de error | `application/json`, `Error {codigo, mensaje, detalles}` | Venía de la v1 de Ángel y Erick usa el mismo. No adoptamos `problem+json` de la v2 de Ángel: todos los handlers del backend y las pruebas ya usan este formato. |
| 409 y 422 | 409 = el estado propio del recurso destino impide la operación; 422 = un dato viola el esquema o falla una regla de negocio que depende de otros datos. En la base, la unicidad sale como 409 y los CHECK y FK como 422 (C-05 de `revision_sql.md`). | Regla del borrador, cercana a la de Leonardo |
| 500 documentado | En todas las operaciones | Ángel y Leonardo |
| Paginación | `pagina`, `tamanoPagina` (máx. 100), `orden` → `{pagina, tamanoPagina, total, items}` | Borrador |
| Nombres | camelCase en parámetros y JSON; enums en snake_case minúsculas; schemas y `operationId` en español | camelCase de Leonardo y Erick; español de Ángel |
| Roles por operación | No se agrega `x-roles` (Ángel) al contrato. El mapa de permisos vive en `backend/app/permisos.py`, la API no arranca si una ruta protegida falta en él, y cada descripción del contrato dice quién puede usar la operación. | Ninguno |
| Idempotencia | `Idempotency-Key` opcional solo en las dos cargas de archivos (`POST /parques/{parqueId}/evidencias` y `POST /evidencias/{evidenciaId}/versiones`), donde un reintento por red lenta duplicaría archivos. No se agrega a todos los POST (Leonardo). | Ángel |
| Procesos programados | `info.x-procesos-programados` con sus criterios (D-23) | Erick |

### 6.3 Clases y arquitectura: conflictos

| ID | Tema | Decisión | Razón |
|---|---|---|---|
| K-01 | Roles | Rol como dato, uno por usuario, 6 valores (ver O-03). No se adopta la herencia de Leonardo. | Con subclases un usuario no cambia de rol y el propio contrato de Leonardo aceptaba `roles[]`: el rol quedaba modelado dos veces. |
| K-02 | Evidencia y criterio | Evidencia con vínculos que llevan el estado (Erick, ya en D-03). | Ya está en el esquema y en el contrato; el modelo de Ángel (una evidencia por criterio con archivo compartido) también cumple, pero obligaba a duplicar evidencias y a coordinar sus versiones. |
| K-03 | Versionado de evidencia | `VersionEvidencia` (Ángel). | Con la autoasociación de Erick cada versión es otra evidencia con sus propios vínculos y habría que copiar los estados. |
| K-04 | Observación | Cuelga del vínculo y guarda la versión observada. | Así sabe criterio y versión, lo que pedían por separado Ángel y Erick. |
| K-05 | Fases | `CatalogoFase` + nueve `FaseExpediente` por expediente. | C-15 pide la secuencia como datos; Leonardo la tenía en un enum y sin motivo de excepción. |
| K-06 | Expediente | Composición `Parque` *-- `Expediente` (Ángel). | Un parque que repite programa no debe mezclar generaciones (RF-31, RF-01-AC-5). Leonardo no tenía expediente. |
| K-07 | Estado del criterio | Fila para todos los criterios de la versión, marca derivada, más el historial de D-19. | RF-11-AC-4 y AC-6: un cambio de tipo no borra nada. |
| K-08 | Plan de trabajo | Renglón por criterio. | Ver O-14. |
| K-09 | Bitácora | Nombre "bitácora". `accion` queda como texto en la base, no como enum. | Cada RF nuevo agrega eventos; con un enum en PostgreSQL cada uno sería una migración del tipo. El filtro de RF-35 funciona igual sobre texto. |
| K-10 | Opinión | Una clase con `tipo` y `favorable [0..1]` (D-18). | Ángel ya había rechazado la herencia en su S04 y Erick coincidía. La tabla y el schema del borrador ya eran una sola; el diagrama era lo único con herencia. |
| K-11 | Dictamen | Del expediente, no de la sesión (D-17). | El borrador no podía guardar el caso de RF-14-AC-8. |
| K-12 | Catálogo | Cuatro niveles con marca por tipo. | Sin marca por tipo (Leonardo) no se filtra la autoevaluación (RF-04-AC-1) ni se calcula cumplimiento (RF-08). |
| K-13 | Usuarios APPI y contacto principal | Asociación directa `Parque` --> contacto principal (Ángel). | Ver O-10. |
| K-14 | Tipo de PI | Historial `ClasificacionTipoPI` (Ángel). | RF-11-AC-1, AC-2 y AC-5. |
| K-15 | Asignación de consultor | Por expediente. | RF-10-AC-1 asigna por parque y generación. |
| K-16 | Enumeraciones | Minúsculas snake, una sola lista por enum. | Son datos guardados en la base y aparecen en las pruebas. |
| Q-01 | Procesos en segundo plano | Worker aparte con outbox en PostgreSQL (Ángel). | RNF-12 y la revisión diaria necesitan un proceso que corra sin solicitudes; un broker sería un servicio más que operar. |
| Q-02 | Carga de archivos | Vía API en multipart (Ángel y Erick), con el criterio de reversión a URL prefirmada de ADR-002. | Con carga directa, RF-06 se valida sobre lo que declara el cliente y quedan objetos huérfanos. |
| Q-03 | Autenticación | Sesión en servidor (Ángel; implementada en S05-S06-A2). | RF-26-AC-5 y AC-6 no se cumplen con JWT sin estado. |
| Q-04 | Despliegue | PostgreSQL gestionado en producción; en el Compose solo en desarrollo. | Quién cumple RNF-13 (respaldo diario, 30 días). |
| Q-05 | Frontend | Estáticos servidos por Caddy (Ángel y Erick). | Un contenedor menos. |
| Q-06 | Módulos | Los de Ángel, con la outbox y los reportes de vuelta en el nivel 3 (el borrador los había perdido); la outbox como `servicios/notificaciones`, con la frontera del módulo de Leonardo. Evidencias sigue dentro de expediente. | RF-17 y RF-27 cambian evidencia y criterio en una sola transacción. |
| Q-07 | Nivel C4 | Nivel 2 y nivel 3 por separado. | El diagrama de Leonardo mezclaba los dos. |
| Q-08 | Tamaño del equipo | Tres personas (D-14). | Somos tres; los ADR de Leonardo y Erick suponían un equipo pequeño o una sola persona. |
| Q-09 | CI y desarrollo | Aceptado, pendiente para el Sprint 2: GitHub Actions con `ruff` y pruebas, y MinIO en el Compose. | No lo dejamos en el repositorio sin haberlo visto correr. |

### 6.4 Cambios que salieron de la comparación

**D-17. El dictamen pertenece al expediente (K-11).** Es el único error de fondo que encontramos en el borrador. Teníamos `SesionComite *-- Dictamen` y, en la base, `dictamen.sesion_comite_id NOT NULL`. RF-14-AC-8 pide aceptar un "no otorgar" de un parque con 60 % de obligatorios, sin autoevaluación revisada ni Opinión final favorable, y RF-15 impide abrir la sesión de comité justo en ese caso. Con el borrador, ese dictamen no se podía guardar. Ángel lo había resuelto en su v2 (decisión 3 de su `decision_arquitectonica.md`) y Erick también colgaba el dictamen del expediente.

- Base: `dictamen.expediente_id NOT NULL`, `sesion_comite_id` opcional, `UNIQUE (expediente_id)`, FK compuesta `(sesion_comite_id, expediente_id)` para que la sesión sea del mismo expediente. Ningún tipo de dictamen exige sesión, porque el SRS no lo pide; si exigiera sesión para "otorgar", el caso de RF-14-AC-5 respondería que falta la sesión en lugar del mensaje literal sobre la Opinión. Tomamos 0..1 por expediente (Erick) y no 0..* (Ángel): un borrador se corrige con `PATCH` y un dictamen firmado cierra la generación.
- Contrato: `Dictamen.sesionComiteId` nulo; `POST /parques/{parqueId}/dictamenes` ya no responde 409 `sin_sesion_comite_abierta`. Si hay sesión abierta, la captura o la edición liga el dictamen a ella; sin sesión, solo Coordinación AMPIP captura.
- Backend: el historial del parque lee el dictamen por expediente; antes lo buscaba a través de la sesión.
- Prueba: `test_D_17_RF_14_AC_8_historial_con_no_otorgar_sin_sesion` y tres casos en `pruebas/pruebas_restricciones.sql`.

**D-18. Opinión en una sola clase (K-10).** Solo cambió el diagrama: la tabla y el schema ya eran uno con `tipo`.

**D-19. Historial de calificaciones (O-13, gap 26, RD-14).** `CriterioParque` guardaba solo el último cambio, y RD-14 pide conservar quién hizo cada calificación, cuándo y con qué motivo. Ahora:

- Base: tabla `calificacion_criterio` de solo append (la misma función de trigger que la bitácora), con CHECK de que el estado cambie, de que el origen "consultor" lleve consultor y de que una reapertura del consultor lleve motivo (RF-27-AC-8).
- Contrato: `GET /parques/{parqueId}/criterios/{criterioId}/calificaciones` y schema `CalificacionCriterio`.
- Backend: cuando un criterio que conservaba su calificación mientras fue NA (RF-11-AC-6) vuelve a aplicar y regresa a "pendiente" (RF-11-AC-4), el cambio queda registrado. Si ya estaba en "pendiente" no hay cambio que registrar. La calificación por el consultor se implementa en el sprint de evidencias, y la descripción del `PATCH` ya dice que cada cambio va al historial.
- Prueba: `test_D_19_criterio_que_vuelve_a_aplicar_deja_historial` y tres casos en `pruebas/pruebas_restricciones.sql`.

**D-20. Token de recuperación en el cuerpo (O-02).** `PATCH /recuperaciones-contrasena/{token}` pasa a `POST /restablecimientos-contrasena {token, nuevaContrasena}`. La solicitud del enlace sigue en `POST /recuperaciones-contrasena`. El backend todavía no implementa recuperación, así que no hubo que cambiar código.

**D-21. Dos consultas que faltaban (gaps 14 y 30).** `GET /versiones-catalogo/{versionId}/criterios`, para que Coordinación vea los criterios de una versión al capturar la evidencia suficiente (RF-24-AC-1), y `GET /evidencias/{evidenciaId}/observaciones`, para listar las observaciones de todas las versiones (RF-05-AC-6); antes solo se podía consultar una por id.

**D-22. Rutas literales del SRS (O-06, O-12).** El SRS cita 8 rutas en el texto de sus criterios. Erick respetó las 8, Ángel 2 y el contrato de equipo 4. De las cuatro que no seguimos, `GET /reporte-asociados` es de un RF "Posterior" y no está en el contrato; las otras tres van en SC-01 (sección 6.6). Los criterios verifican comportamiento y la ruta no lo cambia, pero el SRS y el contrato no deberían decir cosas distintas.

**D-23. Procesos programados en el contrato (gap 50).** De Erick: `info.x-procesos-programados` declara la revisión diaria de plazos (RF-09-AC-2 y AC-3, RF-30-AC-2 y AC-3) y el envío de correos de la outbox (RNF-12). No son rutas, pero así el contrato dice dónde se cumplen esos criterios.

### 6.5 Gaps que no adoptamos

| Gap | Quién | Por qué no |
|---|---|---|
| 7. Roles como subrecurso | Leonardo | Un rol por usuario (O-03). |
| 8. `PUT` de usuario y parque | Leonardo | Sin RF; un reemplazo completo permitiría cambiar campos que tienen su propio recurso (tipo de PI, contacto principal). |
| 9. CRUD de desarrolladores | Ángel | El desarrollador se captura con el parque. Se revisa cuando entre la vista del gerente corporativo (RF-23, 2027). |
| 16. Edición manual del catálogo | Leonardo | Choca con RF-01-AC-5; el catálogo entra por CSV. |
| 32. `PATCH` libre de evidencia | Leonardo | Se salta la máquina de estados (O-16). |
| 36. Evaluación de Desempeño por id y su archivo | Ángel | RF-33 es 2027; se agrega con el almacenamiento de objetos. |
| 37. "Evaluaciones" genéricas con `tipo` | Leonardo | Sin RF; RF-33 pide la Evaluación de Desempeño con folio, que ya tiene recurso propio. |
| 46 a 49. Reporte para asociados, auditorías 1.4, visita de validación, distintivo y renovación | Erick | RF "Posterior" (RF-18, RF-22, RF-37, RF-38), fuera del alcance del contrato. Sus rutas quedan como referencia para el backlog. |

### 6.6 Solicitud de cambio al SRS

**SC-01**, para `SRS_equipo.md` v2.1. Cambiar en el texto de los criterios las rutas que el contrato resolvió de otra forma:

| Criterio | Dice | Debe decir |
|---|---|---|
| RF-01-AC-2 | `POST /catalogo/versiones` | `POST /versiones-catalogo` |
| RF-04-AC-2 | `POST /autoevaluaciones` | `PUT /parques/{parqueId}/autoevaluaciones/{criterioId}` |
| RF-25-AC-2 | `GET /catalogo/exportar` | `GET /versiones-catalogo/{versionId}/archivo` |

No cambia el comportamiento que piden los criterios. Lo aprueba el equipo antes de editar el SRS.
