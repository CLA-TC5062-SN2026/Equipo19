# Análisis de diferencias de diseño (agente) · S05-S06-A1

Salida del agente, sin editar. Compara los tres diseños individuales de S04 para SGPIS. No resuelve conflictos: cada conflicto trae, cuando aplica, una línea marcada **Recomendación**, que el equipo puede tomar o descartar.

**Insumos leídos** (todos bajo `S05_S06_A1/insumos/`):

| Integrante | OpenAPI | Clases | Arquitectura |
|---|---|---|---|
| Ángel (v2) | `Angel_S04_A2_v2/openapi.yaml` (+ `decisiones_y_trazabilidad.md`) | `Angel_S04_A1_v2/diagrama_clases.puml` | `Angel_S04_A1_v2/diagrama_componentes.puml`, `diagrama_despliegue.puml`, `decision_arquitectonica.md` |
| Leonardo | `Leonardo_S04_A2/openapi.yaml` (+ `decisiones_y_trazabilidad.md`) | `Leonardo_S04_A1/diagrama_clases.puml` | `Leonardo_S04_A1/diagrama_componentes.puml`, `diagrama_despliegue.puml`, `decision_arquitectonica.md` |
| Erick | `Erick_S04_A2/openapi.yaml` (+ `decisiones_y_trazabilidad.md`) | `Erick_S04_A1/diagrama_clases_agente.puml` (+ `documentacion/explicacion_clases_agente.md`) | `Erick_S04_A1/diagrama_componentes_agente.puml`, `diagrama_despliegue_agente.puml`, `decision_arquitectonica.md` |

Referencia: `S03_A1/SRS_equipo.md` v2.0 (39 RF, 150 AC). La columna "¿en el borrador?" se llenó contra `S05_S06_A1/openapi_equipo.yaml` v2.0.0 y `S05_S06_A1/diagrama_clases_equipo.puml`; el borrador no se trata como cuarto diseño. Las versiones `Angel_*_v1` no se usaron.

Abreviaturas: **A** = Ángel, **L** = Leonardo, **E** = Erick. Los parámetros de ruta se citan como los escribe cada uno (`{parque_id}` en A y L, `{parqueId}` en E y en el borrador).

---

## 1. OpenAPI

### 1.a Consenso: propósitos que cubren los tres

19 propósitos. Solo seis operaciones tienen la misma ruta y el mismo método en los tres (salvo el caso del parámetro): `POST /usuarios`, `POST /parques`, `GET /parques`, `GET /parques/{id}`, `GET /evidencias/{id}` y `DELETE /evidencias/{id}`. En el resto coincide el propósito y difiere el diseño; la última columna remite al conflicto.

| # | Propósito | A | L | E | ¿En el borrador? | Conflicto |
|---|---|---|---|---|---|---|
| 1 | Iniciar sesión | `POST /sesiones` | `POST /auth/login` | `POST /auth/sesiones` | Sí: `POST /auth/login` | O-01 |
| 2 | Alta de usuario | `POST /usuarios` | `POST /usuarios` | `POST /usuarios` | Sí | O-03 |
| 3 | Modificar o dar de baja un usuario | `PATCH /usuarios/{usuario_id}` | `PATCH`, `PUT` y `DELETE /usuarios/{usuario_id}` | `PATCH /usuarios/{usuarioId}` | Sí: `PATCH /usuarios/{usuarioId}` | O-04 |
| 4 | Alta de parque | `POST /parques` | `POST /parques` | `POST /parques` | Sí | O-05 |
| 5 | Listar parques | `GET /parques` | `GET /parques` | `GET /parques` | Sí | Transversal (paginación) |
| 6 | Consultar parque | `GET /parques/{parque_id}` | `GET /parques/{parque_id}` | `GET /parques/{parqueId}` | Sí | — |
| 7 | Modificar o dar de baja un parque | `PATCH /parques/{parque_id}` | `PATCH`, `PUT` y `DELETE /parques/{parque_id}` | `PATCH /parques/{parqueId}` | Sí: `PATCH` | O-04 |
| 8 | Consultar fases | `GET /parques/{parque_id}/fases` | `GET /planes/{plan_id}/fases` | `GET /parques/{parqueId}/expediente` (campo `fases`) | Sí: `GET /parques/{parqueId}/fases` | O-11 |
| 9 | Cerrar fase y avanzar por excepción | `PATCH /parques/{parque_id}/fases/{fase}` | `PATCH /fases/{fase_id}` (+ `POST /planes/{plan_id}/fases`) | `POST /parques/{parqueId}/fases/{faseId}/cierre`, `POST /parques/{parqueId}/fases/avance-excepcion` | Sí: `POST /parques/{parqueId}/fases/{fase}/cierre`, `POST /parques/{parqueId}/avances-fase` | O-11 |
| 10 | Calificar o reabrir un criterio | `POST /parques/{parque_id}/criterios/{criterio_id}/calificaciones` | `POST /parques/{parque_id}/respuestas-criterios`, `PATCH /respuestas-criterios/{respuesta_id}` | `PATCH /evaluaciones-criterio/{evaluacionId}` | Sí: `PATCH /parques/{parqueId}/criterios/{criterioId}` | O-13 |
| 11 | Plan de trabajo | `GET /parques/{parque_id}/compromisos`, `GET`/`PUT`/`DELETE /parques/{parque_id}/compromisos/{criterio_id}` | `GET`/`POST /parques/{parque_id}/planes`, `GET`/`PATCH /planes/{plan_id}` | `POST /parques/{parqueId}/planes-trabajo` | Sí: `/parques/{parqueId}/plan-trabajo` y `/{renglonId}` | O-14 |
| 12 | Subir evidencia | `POST /parques/{parque_id}/evidencias` (multipart) | `POST /parques/{parque_id}/evidencias` (JSON de metadatos) | `POST /evidencias` (multipart) | Sí: `POST /parques/{parqueId}/evidencias` | O-15 |
| 13 | Consultar una evidencia | `GET /evidencias/{evidencia_id}` | `GET /evidencias/{evidencia_id}` | `GET /evidencias/{evidenciaId}` | Sí | K-02 (forma del schema) |
| 14 | Eliminar evidencia (baja lógica) | `DELETE /evidencias/{evidencia_id}` | `DELETE /evidencias/{evidencia_id}` | `DELETE /evidencias/{evidenciaId}` | Sí | O-18 |
| 15 | Aceptar evidencia | `PATCH /evidencias/{evidencia_id}` | `POST /evidencias/{evidencia_id}/revisiones` | `PUT /evidencias/{evidenciaId}/aceptacion` | Sí: `PATCH /evidencias/{evidenciaId}/vinculos/{criterioId}` | O-16 |
| 16 | Observar evidencia | `POST /evidencias/{evidencia_id}/observaciones` | `POST /evidencias/{evidencia_id}/revisiones` | `POST /evidencias/{evidenciaId}/observaciones` | Sí: `POST /evidencias/{evidenciaId}/observaciones` | O-16 |
| 17 | Subir versión nueva de una evidencia | `POST /evidencias/{evidencia_id}/versiones` | `POST /parques/{parque_id}/evidencias` con `numeroVersion` mayor | `POST /evidencias` (cita RF-05-AC-4) | Sí: `POST /evidencias/{evidenciaId}/versiones` | O-17 |
| 18 | Emitir Opinión de Cumplimiento | `POST /parques/{parque_id}/opiniones` | `POST /parques/{parque_id}/opiniones` | `POST /parques/{parqueId}/opiniones-cumplimiento` | Sí: `POST /parques/{parqueId}/opiniones-cumplimiento` | O-21 |
| 19 | Consultar bitácora | `GET /eventos-bitacora` | `GET /auditoria` | `GET /bitacora` | Sí: `GET /bitacora` | O-24 |

### 1.b Gaps: propósitos que cubren uno o dos

50 filas: 49 propósitos con ruta y uno sin ruta (procesos en segundo plano de E). Prioridad tomada del SRS: MVP = "MVP feb-2027", 2027, Posterior.

| # | Propósito | Quién | Ruta | RF/AC que lo justifica | Prioridad | ¿En el borrador? |
|---|---|---|---|---|---|---|
| 1 | Cerrar sesión | A, E | A `DELETE /sesiones/actual`; E `DELETE /auth/sesiones/actual` | RF-26-AC-5 (E también cita AC-6) | MVP | Sí: `POST /auth/logout` |
| 2 | Usuario y sesión actuales | A | `GET /sesiones/actual` | RF-26-AC-6 | MVP | Sí: `GET /auth/me` |
| 3 | Recuperar contraseña (solicitar y fijar) | A, E | A `POST /solicitudes-recuperacion`, `POST /restablecimientos-contrasena`; E `POST /auth/recuperaciones-contrasena`, `POST /auth/recuperaciones-contrasena/{token}` | RF-26-AC-4 | MVP | Sí: `POST /recuperaciones-contrasena`, `PATCH /recuperaciones-contrasena/{token}` |
| 4 | Activar cuenta invitada | A | `POST /activaciones` | Sin RF (A: `x-sin-criterio`, consecuencia de RF-03-AC-1) | (RF-03: MVP) | Sí: `POST /auth/register` con token de invitación |
| 5 | Salud del servicio | A | `GET /health` | Sin RF (HT-01, RNF-08) | — | Sí: `GET /salud` |
| 6 | Listar y consultar usuarios | A, L | `GET /usuarios`, `GET /usuarios/{usuario_id}` (los dos) | Sin RF (A `x-sin-criterio`; L `x-acceptance-criteria: []`) | — | Sí |
| 7 | Roles de un usuario como subrecurso | L | `GET`/`PUT /usuarios/{usuario_id}/roles` | RF-03-AC-2 | MVP | No (rol en el body de `PATCH /usuarios/{usuarioId}`) |
| 8 | Reemplazo completo (PUT) de usuario y de parque | L | `PUT /usuarios/{usuario_id}`, `PUT /parques/{parque_id}` | Sin RF | — | No |
| 9 | Desarrolladores | A | `GET`/`POST /desarrolladores`, `GET /desarrolladores/{desarrollador_id}` | Sin RF (A: apoyo a RF-02-AC-1 y RF-23-AC-1) | — | No (`Parque.desarrollador` es texto) |
| 10 | Crear generación | A, E | `POST /generaciones` (los dos) | RF-28-AC-1, AC-2 | MVP | Sí |
| 11 | Listar y consultar generaciones | A | `GET /generaciones`, `GET /generaciones/{generacion_id}` | RF-28-AC-1 (la lista, sin RF) | MVP | Sí |
| 12 | Cargar versión del catálogo desde CSV | A, E | A `POST /versiones-catalogo`; E `POST /catalogo/versiones` | RF-01-AC-1, 2, 4, 5 | MVP | Sí: `POST /versiones-catalogo` |
| 13 | Listar y consultar versiones del catálogo | A | `GET /versiones-catalogo`, `GET /versiones-catalogo/{version_id}` | RF-01-AC-5 | MVP | Sí |
| 14 | Listar criterios del catálogo | A, L | A `GET /versiones-catalogo/{version_id}/criterios`; L `GET /estandares`, `GET /estandares/{estandar_id}/criterios` | A RF-24-AC-1; L sin RF | 2027 | No |
| 15 | Consultar un criterio del catálogo | L, E | L `GET /criterios/{criterio_id}`; E `GET /catalogo/criterios/{criterioId}` | E RF-24-AC-1, RF-25-AC-1; L sin RF | 2027 / MVP | Sí: `GET /criterios/{criterioId}` |
| 16 | Edición manual del catálogo | L | `POST /estandares`, `POST /estandares/{estandar_id}/criterios`, `PUT`/`PATCH`/`DELETE /criterios/{criterio_id}` | Sin RF; choca con RF-01-AC-5 (versión anterior en solo lectura) | — | No |
| 17 | Definir evidencia suficiente | A, E | A `PUT /versiones-catalogo/{version_id}/criterios/{criterio_id}/evidencia-suficiente`; E `PATCH /catalogo/criterios/{criterioId}` | RF-24-AC-1, AC-2 | 2027 | Sí: `PATCH /criterios/{criterioId}` |
| 18 | Descargar archivo maestro del catálogo | A, E | A `GET /versiones-catalogo/{version_id}/archivo-maestro`; E `GET /catalogo/exportar` | RF-25-AC-2 a AC-4 | MVP | Sí: `GET /versiones-catalogo/{versionId}/archivo` |
| 19 | Cambiar tipo de PI con historial | A, E | A `GET`/`POST /parques/{parque_id}/cambios-tipo-pi`; E `PATCH /parques/{parqueId}` (`tipoPI`, `motivoCambioTipo`) | RF-11-AC-1 a AC-6 | 2027 | Sí: `PUT /parques/{parqueId}/tipo-pi`, `GET /parques/{parqueId}/tipos-pi` |
| 20 | Historial del parque en el programa | A, E | A `GET /parques/{parque_id}/historial`; E campo `historial` de `GET /parques/{parqueId}` | RF-31-AC-1, AC-3 | MVP | Sí |
| 21 | Actualización anual del programa | A, E | A `GET`/`POST /parques/{parque_id}/actualizaciones-anuales`; E `fechaActualizacion` en `PATCH /parques/{parqueId}` | RF-30-AC-1, AC-3 | MVP | Sí: `POST` y `GET /{actualizacionId}` |
| 22 | Usuarios APPI y contacto principal | A, E | A `GET /parques/{parque_id}/usuarios`, `PUT /parques/{parque_id}/contacto-principal`; E `GET /parques/{parqueId}/usuarios-appi`, `PATCH /parques/{parqueId}/usuarios-appi/{usuarioId}` | RF-34-AC-1 a AC-3 | MVP | Sí: `GET /parques/{parqueId}/usuarios`, `PUT /parques/{parqueId}/contacto-principal` |
| 23 | Asignar o reasignar consultor | A, E | A `GET`/`POST /parques/{parque_id}/asignaciones-consultor`; E `PUT /parques/{parqueId}/asignacion-consultor` | RF-10-AC-1 a AC-3 | MVP | Sí: `GET`/`POST` y `GET /{asignacionId}` |
| 24 | Criterios aplicables del parque con su estado | A, E | A `GET /parques/{parque_id}/criterios`, `GET /parques/{parque_id}/criterios/{criterio_id}`; E `GET /parques/{parqueId}/autoevaluaciones`, `GET /parques/{parqueId}/expediente` | RF-04-AC-1, RF-07-AC-1 | MVP | Sí |
| 25 | Registrar autoevaluación de un criterio | A, E | A `GET /parques/{parque_id}/autoevaluaciones`, `GET`/`PUT /parques/{parque_id}/autoevaluaciones/{criterio_id}`; E `POST /autoevaluaciones` | RF-04-AC-2 | MVP | Sí: `PUT /parques/{parqueId}/autoevaluaciones/{criterioId}` |
| 26 | Historial de calificaciones de un criterio | A | `GET /parques/{parque_id}/criterios/{criterio_id}/calificaciones` | RF-27-AC-2, AC-8 | MVP | No |
| 27 | Cifras de cumplimiento | A, E | A `GET /parques/{parque_id}/cumplimiento`; E campo `cumplimiento` de `GET /parques/{parqueId}/expediente` | RF-08-AC-1 a AC-5 | MVP | Sí |
| 28 | Recomendaciones del consultor | A, E | A `GET`/`POST /parques/{parque_id}/criterios/{criterio_id}/recomendaciones`; E `POST /evaluaciones-criterio/{evaluacionId}/recomendaciones` | RF-36-AC-1, AC-2 | 2027 | Sí (ruta de A) |
| 29 | Listar evidencias del parque | A, L | `GET /parques/{parque_id}/evidencias` (los dos) | A RF-05-AC-7; L RF-05-AC-1 a AC-4 | MVP | Sí |
| 30 | Listar observaciones o revisiones de una evidencia | A, L | A `GET /evidencias/{evidencia_id}/observaciones`; L `GET /evidencias/{evidencia_id}/revisiones` | A RF-05-AC-6, RF-36-AC-2; L RF-05-AC-2 | MVP | No (solo `GET /evidencias/{evidenciaId}/observaciones/{observacionId}`) |
| 31 | URL firmada del contenido de una evidencia | A, E | `GET /evidencias/{id}/contenido` (los dos) | RF-07-AC-2, AC-3, RF-35-AC-1 | MVP | Sí |
| 32 | Modificar metadatos o estado de una evidencia | L | `PATCH /evidencias/{evidencia_id}` | Sin RF | — | No |
| 33 | Registrar revisión del análisis de riesgos | A, E | A `GET`/`POST /parques/{parque_id}/revisiones-analisis-riesgos`, `GET /revisiones-analisis-riesgos/{revision_id}`; E `POST /parques/{parqueId}/analisis-riesgos` | RF-16-AC-1 (E también AC-4) | MVP | Sí |
| 34 | Documento del análisis de riesgos | A, E | A `GET`/`PUT`/`DELETE /revisiones-analisis-riesgos/{revision_id}/documento`; E campo `documento` del `POST` + `GET /evidencias/{evidenciaId}/contenido` | RF-16-AC-2, AC-3 | MVP | Sí: `GET`/`PUT`/`DELETE /parques/{parqueId}/documento-analisis-riesgos` |
| 35 | Listar y consultar Opiniones | A, L | A `GET /parques/{parque_id}/opiniones`, `GET /opiniones/{opinion_id}`; L `GET /parques/{parque_id}/opiniones` | RF-12-AC-6 | 2027 | Sí |
| 36 | Evaluación de Desempeño | A, E | A `GET`/`POST /parques/{parque_id}/evaluaciones-desempeno`, `GET /evaluaciones-desempeno/{evaluacion_id}`, `GET /evaluaciones-desempeno/{evaluacion_id}/archivo`; E `POST /parques/{parqueId}/evaluaciones-desempeno` | RF-33-AC-1 a AC-3 | 2027 | Sí: `GET`/`POST` (sin consulta por id ni archivo) |
| 37 | "Evaluaciones" genéricas del parque (con `tipo`) | L | `GET`/`POST /parques/{parque_id}/evaluaciones` | Sin RF (L deja RF-33 como gap en `x-traceability`) | — | No |
| 38 | Abrir sesión de comité | A, E | `POST /parques/{parque_id}/sesiones-comite` (los dos) | RF-13-AC-1, AC-2, RF-15-AC-1 a AC-3 | 2027 | Sí |
| 39 | Cerrar sesión de comité | A, E | A `PATCH /sesiones-comite/{sesion_id}`; E `DELETE /sesiones-comite/{sesionId}` | RF-13-AC-3 | 2027 | Sí: `PATCH` |
| 40 | Listar y consultar sesiones de comité | A | `GET /parques/{parque_id}/sesiones-comite`, `GET /sesiones-comite/{sesion_id}` | RF-13-AC-1 | 2027 | Sí |
| 41 | Capturar y firmar dictamen | A, E | `POST /parques/{parque_id}/dictamenes`, `POST /dictamenes/{dictamen_id}/firma` (los dos) | RF-14-AC-1 a AC-8 | 2027 | Sí: `POST` y firma por `PATCH /dictamenes/{dictamenId}` |
| 42 | Listar y consultar dictámenes | A | `GET /parques/{parque_id}/dictamenes`, `GET /dictamenes/{dictamen_id}` | RF-14-AC-6 | 2027 | Sí |
| 43 | Reporte mensual para Dirección | A, E | A `GET /generaciones/{generacion_id}/reportes-mensuales/{periodo}`; E `GET /reportes/mensual` | RF-21-AC-1, AC-2 | 2027 | Sí: `GET /reportes/direccion-mensual` |
| 44 | Vista consolidada del gerente corporativo | A, E | A `GET /parques` (cita RF-23-AC-1); E `GET /parques?desarrolladorId=` | RF-23-AC-1 | 2027 | Sí, con ruta propia: `GET /reportes/portafolio-corporativo` |
| 45 | Configurar límite de tamaño de archivo | A, E | A `GET`/`PATCH /configuracion`; E `PATCH /configuracion/cargas` | RF-06-AC-6, AC-7 | MVP | Sí: `GET`/`PATCH /configuracion` |
| 46 | Reporte para asociados | E | `GET /reporte-asociados` | RF-22-AC-1, AC-2 | Posterior | No |
| 47 | Auditorías del subestándar 1.4 | E | `POST /auditorias` | RF-18-AC-1, AC-2 | Posterior | No |
| 48 | Visita de validación | E | `POST /visitas-validacion` | RF-37-AC-1 a AC-3 | Posterior | No |
| 49 | Distintivo y renovación | E | `GET /distintivos/{distintivoId}`, `POST /distintivos/{distintivoId}/renovaciones` | RF-38-AC-1, AC-3 (el `GET` sin RF) | Posterior | No |
| 50 | Procesos diarios declarados en el contrato | E | `x-background-processes` (no son rutas) | RF-09-AC-2, 3; RF-30-AC-2, 3; RF-19; RF-20; RF-38-AC-2; RF-39 | MVP y Posterior | No |

Notas sobre gaps:
- L cita RF-34-AC-1 y AC-2 en `POST /usuarios`, pero ningún schema de L tiene un campo de contacto principal. Su `decisiones_y_trazabilidad.md` asigna esos mismos AC a `GET /usuarios` y `PATCH /usuarios`, distinto de lo que dice el YAML.
- L cita RF-06-AC-6 y AC-7 (límite configurable y rechazo de un límite mayor que 100 MB) en `POST /parques/{parque_id}/evidencias`; no tiene operación de configuración.
- E responde la fila 24 con `CriterionEvaluationList`; L no lista criterios aplicables: `GET /parques/{parque_id}/respuestas-criterios` lista respuestas capturadas.

### 1.c Conflictos

| ID | Propósito | A | L | E | Por qué importa | Recomendación |
|---|---|---|---|---|---|---|
| O-01 | Inicio, cierre y consulta de sesión | `POST /sesiones` → **201** `SesionCreada{token, tipo_token, expira_por_inactividad_min, usuario}`; 401, **423** (bloqueo), 422; `GET`/`DELETE /sesiones/actual` | `POST /auth/login` → **200** `TokenResponse{accessToken, tokenType, expiresIn, usuario}`; 400, 401, 422, sin código de bloqueo; sin logout ni "me" | `POST /auth/sesiones` → **200** `Token{accessToken, tokenType, expiraPorInactividadMinutos}`; 401, 422; `DELETE /auth/sesiones/actual` | Tres rutas y dos códigos para la misma operación. RF-26-AC-3 (bloqueo) tiene código propio solo en A (423). Sin logout (L) no hay forma de cumplir RF-26-AC-5. | **Recomendación:** fijar un espacio `/auth` con `login` 200, `logout` y `me`, como ya tiene el borrador (D-01), y decidir un código único para el bloqueo (A usa 423, el borrador 429). |
| O-02 | Recuperación de contraseña y activación de cuenta | `POST /solicitudes-recuperacion` + `POST /restablecimientos-contrasena` (token en el body); `POST /activaciones {token, contrasena}` | No tiene | `POST /auth/recuperaciones-contrasena` + `POST /auth/recuperaciones-contrasena/{token}` (token en la ruta); sin activación | El token en la ruta queda en los registros de acceso del proxy; en el body no. Sin activación, la cuenta creada por RF-03-AC-1 nunca entra. | **Recomendación:** token en el body; una sola ruta para fijar contraseña con token de invitación o de recuperación. |
| O-03 | Alta de usuario y modelo de rol en el contrato | `UsuarioCrear{nombre, correo, roles: [RolAsignado{rol, parque_id, desarrollador_id}]}`; enum `Rol` de **6** valores (un solo `consultor`; "asignado" y "de comité" son relaciones); 409 por correo duplicado | `UserCreate{nombre, correo, activo, roles: [TipoRol], parquesAsignados: [uuid]}`; enum `TipoRol` de **7** valores en MAYÚSCULAS (`CONSULTOR_ASIGNADO`, `CONSULTOR_COMITE`); `Idempotency-Key`; además `GET`/`PUT /usuarios/{usuario_id}/roles` | `UserCreate{correo, rol, parqueId, desarrolladorId}`: **un solo rol**, sin `nombre`; enum `Role` de **7** valores en minúsculas; sin 409 | Define la tabla de usuarios y la dependencia de autorización. Con un solo rol (E) la misma persona no puede ser consultor asignado en un parque y de comité en otro (RF-13-AC-1 y AC-2 lo suponen). RF-03 lista 7 roles; A los reduce a 6. | **Recomendación:** decidirlo junto con K-01. El argumento de A (RF-13-AC-2 compara a la misma persona) es verificable contra el SRS. |
| O-04 | Baja lógica de usuario y parque; reemplazo completo | Baja por `PATCH` con `estado: inactivo` | `DELETE` como baja lógica, responde **200** `Message`; además `PUT` de reemplazo y `PATCH` con `application/merge-patch+json` | Baja por `PATCH` con `estado` | Cambia la semántica de `DELETE` en todo el contrato y el content type de los PATCH. | **Recomendación:** `PATCH` con estado (2 de 3 y el borrador); conservar `DELETE` solo para lo que sí se borra. |
| O-05 | Alta de parque | `oneOf` `ParqueCrearActivo{tipo_registro, nombre, desarrollador_id, tipo_pi, region (enum de 32 estados), generacion_id}` / `ParqueCrearHistorico{…, fecha_ultimo_dictamen, fecha_termino_programa}` | `ParkCreate{nombre, ubicacion (texto libre), tipo (EN_CONSTRUCCION_ABIERTO…), estado}`: sin región, desarrollador, generación ni alta de histórico | `oneOf` `ActiveParkCreate{nombre, desarrolladorId, tipoPI, region (texto), generacionId, historico}` / `HistoricalParkCreate{…}` | RF-02-AC-1 pide desarrollador, región y generación, y RF-02-AC-3 una región de lista cerrada; L cita los tres AC sin esos campos. RF-31-AC-2 pide alta de histórico. | **Recomendación:** `oneOf` activo/histórico (A y E coinciden) con región como enum (A). |
| O-06 | Carga del catálogo y descarga del archivo maestro | `POST /versiones-catalogo` (CSV) y `GET /versiones-catalogo/{version_id}/archivo-maestro` | Sin carga CSV: CRUD manual de `/estandares` y `/criterios` | `POST /catalogo/versiones` y `GET /catalogo/exportar` (sin versión) | El SRS cita literalmente `POST /catalogo/versiones` (RF-01-AC-2) y `GET /catalogo/exportar` (RF-25-AC-2). El CRUD de L permite editar criterios de una versión que RF-01-AC-5 deja en solo lectura. | **Recomendación:** carga CSV por versión; decidir si se siguen las rutas que cita el SRS o se corrige el SRS. |
| O-07 | Definir evidencia suficiente | `PUT /versiones-catalogo/{version_id}/criterios/{criterio_id}/evidencia-suficiente {descripcion}` | `PATCH /criterios/{criterio_id}` sin campo de evidencia suficiente | `PATCH /catalogo/criterios/{criterioId} {evidenciaSuficiente}` | A liga la descripción a una versión del catálogo; E al criterio sin versión. | **Recomendación:** la descripción vive en el criterio de una versión (RF-01-AC-5); la ruta es secundaria. |
| O-08 | Cambio de tipo de PI | Recurso propio: `POST /parques/{parque_id}/cambios-tipo-pi {tipo_pi, motivo, fecha_desde}` → 201 y `GET` del historial | Campo `tipo` en `PATCH /parques/{parque_id}`, sin motivo ni historial (sin AC) | Campo `tipoPI` + `motivoCambioTipo` en `PATCH /parques/{parqueId}`; historial en `Park.historialTipos` | RF-11 recalcula criterios y congela cifras (AC-2, AC-6); como efecto lateral de un PATCH genérico no queda un recurso que auditar ni probar por separado. | **Recomendación:** recurso propio (A; el borrador también lo separa). |
| O-09 | Asignación de consultor | `POST /parques/{parque_id}/asignaciones-consultor {consultor_id, generacion_id}` → 201 + historial | No tiene (solo `parquesAsignados` en el usuario) | `PUT /parques/{parqueId}/asignacion-consultor {consultorId}` → 200 | RF-10-AC-2 pide conservar el historial de asignaciones; el `PUT` sobre un singleton lo oculta. | **Recomendación:** colección con historial (A). |
| O-10 | Contacto principal | `PUT /parques/{parque_id}/contacto-principal {usuario_id}` | No tiene | `PATCH /parques/{parqueId}/usuarios-appi/{usuarioId} {esContactoPrincipal}` | Con el booleano por vínculo (E) el servidor tiene que apagar el anterior; con el `PUT` (A) la unicidad es estructural (RF-34-AC-2). | **Recomendación:** `PUT` de recurso único (A). |
| O-11 | Fases | Secuencia leída de la base; `PATCH /parques/{parque_id}/fases/{fase} {estado: completada \| avanzada_por_excepcion, motivo}`; 422 sin motivo | Fases que crea el cliente (`POST /planes/{plan_id}/fases`) colgando de un plan; `PATCH /fases/{fase_id}` con `PhasePatch{nombre, estado, fechas}`: **sin `motivo` y sin estado de excepción** | `POST /parques/{parqueId}/fases/{faseId}/cierre` (sin body) y `POST /parques/{parqueId}/fases/avance-excepcion {faseDestinoId, motivo}`; listado dentro de `/expediente` | RF-32-AC-3 cita `POST /parques/{id}/fases/{fase}/cierre` (la ruta de E). L cita RF-32-AC-4 y AC-5 pero su schema no puede expresar el motivo. | **Recomendación:** fases fijas por parque y generación; acciones de cierre y de excepción separadas (E, borrador). |
| O-12 | Autoevaluación | `PUT /parques/{parque_id}/autoevaluaciones/{criterio_id} {respuesta: cumple \| cumple_parcialmente \| no_cumple, comentario}` | No tiene (las respuestas de L son la calificación, O-13) | `POST /autoevaluaciones {parqueId, criterioId}`: **el body no lleva la respuesta** | El schema de E no permite capturar la respuesta de diagnóstico. RF-04-AC-2 cita `POST /autoevaluaciones`. | **Recomendación:** `PUT` con clave natural parque+criterio (A, borrador); si se conserva la ruta del SRS, agregar `respuesta` al body. |
| O-13 | Calificar o reabrir un criterio | `POST …/criterios/{criterio_id}/calificaciones`, `oneOf` cierre `{estado, motivo?}` / reapertura `{estado: en_revision, motivo*}` → 201 `Calificacion` (cada calificación es un registro) | `POST /parques/{parque_id}/respuestas-criterios {evaluacionId, criterioId, categoria: O\|R\|NA, observaciones}` y `PATCH /respuestas-criterios/{respuesta_id}`: **no hay campo de estado de calificación** | `PATCH /evaluaciones-criterio/{evaluacionId} {estado, motivoReapertura}` → 200 | Es la máquina de estados central (RF-27, RF-17). L cita RF-27-AC-1 a AC-8 con un schema que no puede expresar cumplido/no cumplido. A conserva historial (RD-14); E y el borrador sobrescriben. | **Recomendación:** identificar por parque+criterio y decidir si cada calificación queda como registro (POST, A) o como cambio de estado (PATCH, E y borrador) con historial aparte. |
| O-14 | Plan de trabajo | Compromiso por criterio con clave natural: `PUT /parques/{parque_id}/compromisos/{criterio_id} {responsable_id, fecha_comprometida}`; `DELETE` | Plan como documento: `POST /parques/{parque_id}/planes {descripcion, estado}`; sin criterio, responsable ni fecha | `POST /parques/{parqueId}/planes-trabajo {evaluacionCriterioId, responsableId, fechaComprometida}`; sin `GET` | RF-09 pide responsable y fecha por criterio, y el atraso se calcula por criterio; el schema de L no los tiene. | **Recomendación:** renglón por criterio (A o E). |
| O-15 | Subir evidencia | `multipart` `{archivos[], criterio_ids[], fase, es_administrativa}` en `/parques/{parque_id}/evidencias` → 201 `{creadas, rechazadas}`; 422 si no pasa ninguno. Se crea **una evidencia por archivo × criterio** con `documento_id` compartido | JSON `EvidenceCreate{respuestaId, nombreArchivo, tipoContenido, tamanoBytes, ubicacionObjeto, numeroVersion, estado}`: el archivo ya está en el bucket, el cliente declara tamaño y **estado**; una evidencia por respuesta | `multipart` `{parqueId, criterioIds[], faseId, fechaVencimiento, archivos[]}` en `POST /evidencias` → 201 `{creadas, rechazadas}`; **una evidencia con `vinculos[]`** | Decide el modelo evidencia–criterio (K-02), dónde se valida RF-06 (Q-02) y si RF-05-AC-8 es una sola respuesta. Con el diseño de L el tamaño y el estado los declara el cliente. | **Recomendación:** decidir primero K-02 y Q-02; la ruta (anidada en parque o plana) es secundaria. |
| O-16 | Aceptar y observar evidencia | Aceptar: `PATCH /evidencias/{evidencia_id} {estado: aceptada}` (la evidencia ya es el vínculo); observar: `POST …/observaciones {texto}` | Un solo recurso: `POST /evidencias/{evidencia_id}/revisiones {resultado: ACEPTADA \| OBSERVADA, comentarios}`; y `PATCH /evidencias/{evidencia_id}` permite fijar `estado` directamente | Aceptar: `PUT /evidencias/{evidenciaId}/aceptacion {criterioId}`; observar: `POST …/observaciones {criterioId, motivo}` | Con un archivo vinculado a varios criterios (RF-05-AC-7) la acción tiene que decir sobre qué criterio actúa: E lo pide en el body, A lo resuelve con una evidencia por criterio, L no puede. El `PATCH` de L deja saltarse la máquina de estados. | **Recomendación:** depende de K-02; el `PATCH` libre de estado de L no debería quedar. |
| O-17 | Versión nueva de una evidencia | Subrecurso `POST /evidencias/{evidencia_id}/versiones {archivo}` → 201 | Nuevo `POST /parques/{parque_id}/evidencias` con `numeroVersion` incrementado por el cliente (409 si repite) | `POST /evidencias` (cita RF-05-AC-4); `EvidenceUpload` no tiene campo para indicar la evidencia anterior (`versionAnteriorId` solo sale en la respuesta) | En L y E el servidor no puede saber de qué evidencia es versión la carga, y RF-05-AC-4 exige regresarla de "observada" a "enviada". | **Recomendación:** subrecurso de versiones (A, borrador). |
| O-18 | Eliminar evidencia | 204; idempotente; **422** si está aceptada | **200** `Message` ("archivar"); sin regla de evidencia aceptada; sin AC | 204; **422** si está aceptada | RF-05-AC-10 exige el rechazo; L no lo modela. El borrador usa 409 para el mismo caso. | **Recomendación:** 204 y un solo código para "aceptada"; alinearlo con la regla 409/422 que se fije en transversales. |
| O-19 | Acceso al archivo | `GET /evidencias/{evidencia_id}/contenido` → `EnlaceDescarga{url, expira_en}` | Sin operación; **`Evidence` expone `ubicacionObjeto`** en la respuesta | `GET /evidencias/{evidenciaId}/contenido` → `SignedUrl{url, expiraEn}` | RNF-15 prohíbe URL públicas y pide URL firmada después de validar el permiso; exponer la ubicación del objeto lo contradice. | **Recomendación:** URL firmada (A y E coinciden salvo el caso de los nombres). |
| O-20 | Análisis de riesgos | Revisión en JSON `POST /parques/{parque_id}/revisiones-analisis-riesgos`; documento aparte con `PUT /revisiones-analisis-riesgos/{revision_id}/documento` | No tiene | `multipart` `POST /parques/{parqueId}/analisis-riesgos` con `documento` opcional; se descarga como evidencia (`documentoEvidenciaId`) | La descripción de RF-16 dice que el documento solo se guarda si la APPI decide subirlo. Guardarlo como evidencia (E) lo mete en el flujo de estados de RF-05. | **Recomendación:** documento separado de la evidencia (A); el borrador lo pone por parque, no por revisión. |
| O-21 | Emitir Opinión | `oneOf` `{tipo: intermedia, comentario}` / `{tipo: final, favorable*, comentario}`; 409 por segunda final | `OpinionCreate{numero: 1\|2, resultado (texto ≤100), observaciones, version}`; 409 | `OpinionCreate{tipo, favorable}`; 422, sin 409 | RD-09 y RF-14 necesitan saber si la Opinión final es favorable; con `resultado` de texto libre (L) no hay un dato que comparar. | **Recomendación:** `tipo` + `favorable` (A y E coinciden en el contenido). |
| O-22 | Cerrar sesión de comité y firmar dictamen | Cierre `PATCH /sesiones-comite/{sesion_id} {estado}` → 200; firma `POST /dictamenes/{dictamen_id}/firma` → **201** | No tiene | Cierre `DELETE /sesiones-comite/{sesionId}` → 204; firma `POST /dictamenes/{dictamenId}/firma` → **200** | `DELETE` sugiere que la sesión desaparece, pero RF-13 la necesita después para el historial. | **Recomendación:** cerrar por `PATCH` de estado (A, borrador). |
| O-23 | Reporte mensual para Dirección | `GET /generaciones/{generacion_id}/reportes-mensuales/{periodo}` | No tiene | `GET /reportes/mensual?generacionId=&mes=` | Solo ubicación del recurso. | **Recomendación:** agrupar reportes bajo `/reportes` (E, borrador). |
| O-24 | Consultar bitácora | `GET /eventos-bitacora`, paginada, filtros `parque_id`, `usuario_id`, `accion` (enum), `desde`, `hasta` | `GET /auditoria`, parámetros `page`/`page_size` pero **responde un arreglo sin sobre**; filtros `entidad`, `entidad_id`, `desde`, `hasta` | `GET /bitacora`, arreglo sin paginar; filtros `parqueId`, `usuarioId`, `accion`, `desde`, `hasta` | RF-35-AC-4 cita `GET /bitacora`. "Auditoría" (L) choca con `POST /auditorias` de E, que es RF-18 (auditorías del subestándar 1.4). | **Recomendación:** `GET /bitacora` paginada. |
| O-25 | Configuración del programa | `GET`/`PATCH /configuracion {limite_tamano_archivo_mb, vigencia_distintivo_anios}` | No tiene | `PATCH /configuracion/cargas {maximoMB}`; sin `GET` | C-10 vuelve parametrizable también la vigencia del distintivo (RD-08); un recurso solo para cargas obliga a otro después. | **Recomendación:** un recurso `/configuracion` con `GET` (A, borrador). |
| O-26 | Recomendaciones | `GET`/`POST /parques/{parque_id}/criterios/{criterio_id}/recomendaciones {texto}` | No tiene | `POST /evaluaciones-criterio/{evaluacionId}/recomendaciones {texto}`; sin `GET` | Igual que O-13: E identifica el criterio por el id de su evaluación, A por parque+criterio. Sin `GET` la APPI no ve las recomendaciones (RF-36-AC-1). | **Recomendación:** misma forma de identificar el criterio que se elija en O-13. |

### 1.d Diferencias transversales

| Aspecto | A | L | E | Borrador |
|---|---|---|---|---|
| Servidor y versión | `http://localhost:8000/api/v1`; `info.version` 1.0.0 | `https://api.sgpis.example.com/v1`; 1.0.0 | `https://api.sgpis.example.com/api/v1`; 1.0.0 | `http://localhost:8000/api`; 2.0.0 |
| Esquema de seguridad | `bearerAuth`, JWT HS256 con claims `sub`, `sid`, `exp` (12 h); **sesión en servidor** validada en cada solicitud (revocación y 60 min sin uso) | `BearerAuth`, JWT; sin sesión (RF-26-AC-5 y AC-6 quedan como gap en `x-traceability`) | `bearerAuth`, JWT, sin descripción; la respuesta 401 dice "revocado o expirado" pero el contrato no define cómo; su C4 menciona sesiones en PostgreSQL | `BearerAuth` + sesión en servidor |
| Formato de error | `application/problem+json` (RFC 9457), `Problema{type, title, status, detail, instance, errores[]}` | `application/json`, `Error{code, message, requestId, details}` y `ValidationError{code, message, errors[]}` | `application/json`, `Error{codigo, mensaje, detalles[]}` | `application/json`, `Error{codigo, mensaje, detalles[DetalleError]}` |
| Semántica 409/422 | 422 = regla de negocio; 409 = duplicado (7 operaciones); 423 = bloqueo | 409 también para conflictos de estado de negocio (21 operaciones); 422 = validación | Sin 409 en ninguna operación; 422 | 409 en 19 operaciones, 422 en 46 |
| 500 documentado | 86/86 operaciones | 46/46 | 1/47 (`POST /evidencias`) | 88/88 |
| Paginación | `pagina`, `por_pagina` (máx. 200) → `{datos, paginacion{pagina, por_pagina, total}}` en usuarios, parques, evidencias y bitácora; listas acotadas → `{datos}` | `page`, `page_size` (máx. 100, por omisión 20) → `{items, page, pageSize, total}` en usuarios y parques; `/auditoria` declara los parámetros y responde arreglo | Sin paginación; colecciones como arreglo | `pagina`, `tamanoPagina` (máx. 100), `orden` → `{pagina, tamanoPagina, total, items}` |
| Convención de nombres | **snake_case** en parámetros de ruta, query y campos JSON; valores de enum en minúsculas snake; nombres de schema en español | Parámetros de ruta y query **snake_case**, campos JSON **camelCase**; enums en MAYÚSCULAS; schemas en inglés (`Park`, `User`, `Evidence`) | **camelCase** en parámetros y campos; enums en minúsculas snake; schemas en inglés | camelCase; schemas en español |
| `operationId` | 86/86, español (`listarParques`) | 46/46, inglés (`listParks`) | 0/47 | 88/88, español |
| Roles por operación | `x-roles` en 86/86 | No | No | — |
| Idempotencia | Descrita en `info` (PUT solo con clave natural) | Cabecera `Idempotency-Key` en los POST; PATCH con `application/merge-patch+json` | `x-idempotency` en 5 operaciones | — |
| Cobertura de `x-acceptance-criteria` (por operación, AC distintos, script en anexo) | **131/150** (los 131 AC que no son Posterior; ningún Posterior); 32 de 39 RF; 10 operaciones sin AC, todas con `x-sin-criterio` | **51/150**; 12 de 39 RF; 23 operaciones sin AC | **136/150** (127 de los 131 no Posterior + 9 Posterior); 36 de 39 RF; 1 operación sin AC. Con `x-background-processes` (14 AC más) llega a 150/150 | 131/150 |
| AC citados que no existen en el SRS | 0 | 0 | 0 | 0 |
| Rutas literales del SRS respetadas (8 rutas citadas en el texto de los AC) | 2 (`POST /evidencias/{id}/observaciones`, `GET /evidencias/{id}/contenido`) | 0 | 8 (las 8) | 4 |

Cruce de cobertura (por operación): 49 AC los cubren los tres; 2 solo A; 0 solo L; 9 solo E (todos Posterior); 10 ninguno de los tres en una operación (RF-19-AC-1 a 5, RF-20-AC-1 y 2, RF-38-AC-2, RF-39-AC-1 y 2), que E declara en `x-background-processes`. La unión de los tres cubre 140 AC.

Rutas literales del SRS: `POST /catalogo/versiones` (RF-01-AC-2), `POST /autoevaluaciones` (RF-04-AC-2), `POST /evidencias/{id}/observaciones` (RF-05-AC-3), `GET /evidencias/{id}/contenido` (RF-07-AC-3), `GET /reporte-asociados` (RF-22-AC-2), `GET /catalogo/exportar` (RF-25-AC-2), `POST /parques/{id}/fases/{fase}/cierre` (RF-32-AC-3), `GET /bitacora` (RF-35-AC-4).

---

## 2. Diagrama de clases

### 2.a Consenso: conceptos que modelan los tres

13 conceptos.

| # | Concepto | A | L | E | ¿En el borrador? | Conflicto |
|---|---|---|---|---|---|---|
| 1 | Usuario | `Usuario` | `Usuario` (abstracta) | `Usuario` | Sí | K-01 |
| 2 | Rol | enum `Rol` dentro de `RolAsignado` | clase `Rol` + 7 subclases de `Usuario` | clase `Rol` | Sí: enum `Rol`, atributo de `Usuario` | K-01 |
| 3 | Parque | `Parque` | `ParqueIndustrial` | `Parque` | Sí | K-14 |
| 4 | Asignación de consultor | `AsignacionConsultor` | `AsignacionConsultor` | `AsignacionConsultor` | Sí | K-15 |
| 5 | Estándar y criterio | `Estandar`, `Subestandar`, `Criterio` | `EstandarSeguridad`, `CriterioSeguridad` | `Estandar`, `Subestandar`, `Criterio` | Sí | K-12 |
| 6 | Estado de un criterio en un parque | `CriterioExpediente` | `RespuestaCriterio` | `EvaluacionCriterio` | Sí: `CriterioParque` | K-07 |
| 7 | Evidencia | `Evidencia` | `Evidencia` | `Evidencia` | Sí | K-02, K-03 |
| 8 | Revisión u observación de evidencia | `Observacion` | `RevisionEvidencia` | `Observacion` | Sí: `Observacion` | K-04 |
| 9 | Fase | `DefinicionFase` + `FaseExpediente` | `FaseProceso` | `DefinicionFase` + `FaseExpediente` | Sí: `CatalogoFase` + `FaseExpediente` | K-05 |
| 10 | Plan de trabajo | `Compromiso` | `PlanTrabajo` | `PlanTrabajo` | Sí: `RenglonPlanTrabajo` | K-08 |
| 11 | Opinión de Cumplimiento | `OpinionCumplimiento` | `Opinion` | `OpinionCumplimiento` | Sí: abstracta + `OpinionIntermedia`, `OpinionFinal` | K-10 |
| 12 | Evaluación posterior a la Opinión final | `EvaluacionDesempeno` | `EvaluacionFinal` | `EvaluacionDesempeno` | Sí: `EvaluacionDesempeno` | K-10 |
| 13 | Bitácora | `EventoBitacora` | `RegistroAuditoria` | `EventoBitacora` | Sí: `RegistroBitacora` | K-09 |

### 2.b Gaps: conceptos que modelan uno o dos

| # | Concepto | Quién | Clase | RF/AC | Prioridad | ¿En el borrador? |
|---|---|---|---|---|---|---|
| 1 | Expediente (parque × generación) | A, E | `Expediente` | RF-28, RF-31, RF-32, RF-01-AC-5 | MVP | Sí (K-06) |
| 2 | Generación | A, E | `Generacion` | RF-28 | MVP | Sí |
| 3 | Versión del catálogo como clase | A, E (L: atributo `versionChecklist: String`) | `VersionCatalogo` | RF-01-AC-3, AC-5 | MVP | Sí |
| 4 | Subestándar | A, E | `Subestandar` | RF-01-AC-1 | MVP | Sí |
| 5 | Marca O/R/NA por tipo de PI | A, E | `MarcaCriterio` / `MarcaCriterioTipo` | RF-01-AC-1, RF-04-AC-1 | MVP | Sí: `MarcaPorTipo` |
| 6 | Desarrollador | A, E | `Desarrollador` | RF-02-AC-1, RF-23 | MVP / 2027 | Sí |
| 7 | Vínculo evidencia–criterio como clase | E | `EvidenciaCriterio` (A: la propia `Evidencia` es el vínculo) | RF-05-AC-7 | MVP | Sí: `VinculoEvidencia` (K-02) |
| 8 | Versión de evidencia como clase | A | `VersionEvidencia` | RF-05-AC-4, AC-6 | MVP | Sí (K-03) |
| 9 | Archivo almacenado compartido | A | `ArchivoAlmacenado` | RF-05-AC-5, AC-7 | MVP | No (`rutaObjeto` en `VersionEvidencia`) |
| 10 | Sesión en servidor y token de un solo uso | A | `Sesion`, `TokenUnUso` | RF-26-AC-4 a AC-6, RF-03-AC-1 | MVP | Sí: `Sesion`, `EnlaceUnSoloUso` (+ `IntentoLogin`) |
| 11 | Usuarios APPI y contacto principal | A, E | A asociación `Parque → Usuario : contacto principal` + alcance de `RolAsignado`; E `VinculoAPPI` | RF-34 | MVP | Sí, como asociaciones (K-13) |
| 12 | Historial de tipo de PI | A | `PeriodoTipoPI` | RF-11-AC-1, AC-2, AC-5 | 2027 | Sí: `ClasificacionTipoPI` (K-14) |
| 13 | Actualización anual | A | `ActualizacionAnual` | RF-30-AC-3 | MVP | Sí |
| 14 | Historial de calificaciones | A | `Calificacion` | RF-27-AC-2, AC-8 (RD-14) | MVP | No (`CriterioParque` guarda solo el último cambio) |
| 15 | Autoevaluación | A | `Autoevaluacion` | RF-04 | MVP | Sí |
| 16 | Recomendación | A | `Recomendacion` | RF-36 | 2027 | Sí (E la tiene en su OpenAPI sin clase) |
| 17 | Revisión del análisis de riesgos | A, E | `RevisionAnalisisRiesgos` | RF-16, RF-17 | MVP | Sí (+ `DocumentoAnalisisRiesgos`) |
| 18 | Sesión de comité | A, E (+ `AccesoComite` en E) | `SesionComite` | RF-13, RF-15 | 2027 | Sí |
| 19 | Dictamen | A, E | `Dictamen` | RF-14 | 2027 | Sí (K-11) |
| 20 | Configuración del programa | A | `Configuracion` | RF-06-AC-6, AC-7, RD-08 | MVP | Sí |
| 21 | Distintivo | E | `Distintivo` | RF-38, RF-19 | Posterior | No |
| 22 | Subclases de rol | L | `CoordinacionAMPIP`, `DirectorGeneralAMPIP`, `APPI`, `ConsultorAsignado`, `ConsultorComite`, `GerenteCorporativo`, `AdministradorTecnico` | RF-03 | MVP | No (K-01) |
| 23 | Evaluación del parque como contenedor de respuestas | L | `EvaluacionParque` | Sin RF directo | — | No (K-06) |

### 2.c Conflictos

| ID | Concepto | A | L | E | Por qué importa | Recomendación |
|---|---|---|---|---|---|---|
| K-01 | **Roles** | Atributo: `Usuario "1" *-- "1..*" RolAsignado {rol: Rol}`, con alcance `RolAsignado --> Parque` (APPI) y `--> Desarrollador` (gerente). Enum de 6 valores (un solo `CONSULTOR`) | **Herencia**: `abstract Usuario` con 7 subclases vacías, y **además** `Usuario "0..*" -- "1..*" Rol`. El rol está modelado dos veces | Clase `Rol {nombre: NombreRol}` con `Usuario "0..*" --> "1" Rol`: **un solo rol por usuario**, sin alcance de parque en la relación | Con herencia un objeto no cambia de clase ni tiene dos roles, pero el API de L acepta `roles[]`. Con un solo rol (E y borrador) el consultor asignado de un parque no puede ser consultor de comité de otro (RF-13-AC-1, AC-2). Decide la tabla de usuarios y `requiere_rol`. | **Recomendación:** rol como dato, no herencia (2 de 3); decidir uno o varios roles por usuario y si "asignado"/"de comité" son roles o relaciones con el parque. |
| K-02 | **Relación evidencia–criterio** | `CriterioExpediente "1" *-- "0..*" Evidencia {estado}`: cada evidencia es el vínculo con un criterio; el archivo se comparte por agregación (`VersionEvidencia "0..*" o-- "1" ArchivoAlmacenado`) | `RespuestaCriterio "1" *-- "0..*" Evidencia {estado}`: una evidencia pertenece a una sola respuesta; no hay forma de ligar un archivo a dos criterios | `Evidencia "1" -- "1..*" EvidenciaCriterio {estado, vigente}` → `EvaluacionCriterio`; clase de asociación con restricción "mismo expediente" | RF-05-AC-7 pide un archivo y un estado por criterio. A y E lo cumplen de forma distinta (A duplica la evidencia y comparte el archivo; E comparte la evidencia y separa el estado); L no lo cumple. El borrador siguió a E. Arrastra O-15, O-16, O-17, O-18 y el esquema de BD. | **Recomendación:** elegir entre "evidencia por criterio + archivo compartido" (A) y "evidencia + vínculo con estado" (E, borrador) antes de tocar endpoints. |
| K-03 | Versionado de evidencia | `Evidencia "1" *-- "1..*" VersionEvidencia {numero, vigente}` | Atributo `numeroVersion` en `Evidencia` | Autoasociación `Evidencia "0..1" --> "0..1" Evidencia : versionAnterior` + `numeroVersion`: cada versión es otra evidencia | Con E, una versión nueva crea otra fila con sus propios vínculos; hay que copiar o mover los estados por criterio. RF-05-AC-6 pide ver las versiones con sus observaciones. | **Recomendación:** clase de versión (A, borrador). |
| K-04 | Dónde cuelga la observación | `VersionEvidencia "1" *-- "0..*" Observacion` | `Evidencia "1" *-- "0..*" RevisionEvidencia {resultado: ACEPTADA \| OBSERVADA}`: aceptación y observación en una clase | `EvidenciaCriterio "1" *-- "0..*" Observacion` | Con A la observación sabe la versión pero no el criterio (resuelto porque su evidencia ya es por criterio); con E sabe el criterio pero no la versión. El borrador cuelga del vínculo y guarda `version` como atributo. | **Recomendación:** que la observación identifique criterio y versión, sea cual sea el dueño. |
| K-05 | **Fases** | `DefinicionFase {clave, nombre, orden}` (secuencia como datos) + `Expediente "1" *-- "1..*" FaseExpediente {estado, motivoExcepcion, cerradaEn}`; `EstadoFase` con `AVANZADA_POR_EXCEPCION` | `FaseProceso {nombre: NombreFase, estado, fechas}`: secuencia en un **enum**; compuesta en `ParqueIndustrial` y asociada además a `PlanTrabajo`; `EstadoFase` **sin** excepción y sin motivo | Igual que A, con `Expediente "1" *-- "9" FaseExpediente` | C-15 pide la secuencia como datos; RF-32-AC-4 y AC-5 piden motivo de excepción. L tiene dos dueños para la misma fase y no guarda el motivo. | **Recomendación:** catálogo de fases + fase por expediente (A, E, borrador); fijar 9 o `1..*`. |
| K-06 | **Expediente por generación** | `Parque "1" *-- "0..*" Expediente`, raíz de agregado; de él cuelgan criterios, evidencias, fases, Opiniones, comité y dictamen | **No existe** `Expediente` ni `Generacion`; todo cuelga de `ParqueIndustrial`; `EvaluacionParque {versionChecklist: String}` agrupa respuestas | `Parque "1" -- "0..*" Expediente` y `Generacion "1" -- "0..*" Expediente` (asociación, no composición); nota de unicidad parque+generación | RF-31 pide el historial de varias participaciones y RF-01-AC-5 que cada generación conserve su versión. Sin expediente (L) un parque que repite programa mezcla generaciones. A compone, E asocia. | **Recomendación:** expediente por parque y generación (A, E, borrador); decidir composición o asociación. |
| K-07 | Estado del criterio en el parque | `CriterioExpediente {marca: {O, R}, estado}` solo para criterios O y R, con historial `Calificacion` | `RespuestaCriterio {categoria: O\|R\|NA, observaciones}`: la marca la captura el usuario y **no hay estado de calificación** | `EvaluacionCriterio {marcaAplicable, estado, motivoReapertura}`, sin historial | RF-11-AC-4 y AC-6: un criterio NA que vuelve a aplicar entra en "pendiente" y no se pierde lo anterior; si solo existen filas O y R (A) hay que crearlas y borrarlas al cambiar de tipo. El borrador crea fila para todos y deriva la marca. | **Recomendación:** fila por cada criterio de la versión con marca derivada (borrador) y decidir si se conserva historial (A). |
| K-08 | Plan de trabajo | `CriterioExpediente "1" *-- "0..1" Compromiso {fechaComprometida, atrasado}` + responsable | `ParqueIndustrial "1" *-- "0..*" PlanTrabajo {descripcion, estado: EstadoPlan}`, que organiza fases | `EvaluacionCriterio "1" *-- "0..1" PlanTrabajo {fechaComprometida, atrasado}` + responsable | RF-09 es por criterio con responsable y fecha. L modela otra cosa (un plan general). | **Recomendación:** renglón por criterio (A, E). |
| K-09 | Bitácora | `EventoBitacora <<solo append>> {accion: AccionBitacora (enum), recursoTipo, recursoId, usuarioId, rol, parqueId}` sin asociaciones | `RegistroAuditoria {accion: String, entidad, entidadId: UUID, detalle}` con asociaciones a `Usuario` y `ParqueIndustrial` | `EventoBitacora {rol, accion: String, recurso: String}` con asociaciones opcionales | `accion` como enum (A) permite el filtro de RF-35 sin texto libre. "Auditoría" (L) choca con RF-18. `entidadId: UUID` no admite recursos con id no UUID. | **Recomendación:** nombre "bitácora"; acción como enum. |
| K-10 | Opinión y evaluación posterior | Una clase `OpinionCumplimiento {tipo, favorable [0..1]}`, `Expediente *-- "0..2"`; `EvaluacionDesempeno {folio, fecha, resultado}` `0..1` | `Opinion {numero: Integer, resultado: String, version}` `0..*` por parque; `EvaluacionFinal {fechaEvaluacion, resultado, observaciones, version}` sin folio | Como A (`0..2`, `favorable [0..1]`); `EvaluacionDesempeno` con `folio` y `referenciaArchivo` | RD-09 necesita "Opinión final favorable" como dato; RF-33 pide folio. El borrador usa herencia (`OpinionIntermedia`/`OpinionFinal`), que A rechazó en su `decision_arquitectonica.md` §5.1, decisión 2. | **Recomendación:** una clase con `tipo` y `favorable` (A, E). |
| K-11 | Dueño y multiplicidad del dictamen | `Expediente "1" *-- "0..*" Dictamen` | No modela dictamen | `Expediente "1" *-- "0..1" Dictamen`; `Dictamen "1" -- "0..1" Distintivo` | A argumenta (§5.1, decisión 3) que RF-14-AC-8 obliga a capturar un "no otorgar" sin sesión de comité. El borrador pone `SesionComite "1" *-- "0..1" Dictamen`, el diseño que A descartó por ese caso. | **Recomendación:** colgar el dictamen del expediente (A, E); revisar el borrador contra RF-14-AC-8. |
| K-12 | Estructura del catálogo | `VersionCatalogo "1" *-- "10" Estandar *-- Subestandar *-- Criterio *-- "4" MarcaCriterio` | `EstandarSeguridad "1" *-- "1..*" CriterioSeguridad {versionChecklist: String}`; sin subestándar, sin versión como clase, **sin marca por tipo de PI** | Igual que A con `VersionCatalogo "1" *-- "1..*" Estandar` | Sin marca por tipo (L) no se puede filtrar la autoevaluación (RF-04-AC-1) ni calcular cumplimiento (RF-08). | **Recomendación:** cuatro niveles con marca por tipo (A, E, borrador). |
| K-13 | Usuarios APPI y contacto principal | `RolAsignado "0..*" --> "0..1" Parque : alcance APPI`; `Parque "0..1" --> "0..1" Usuario : contacto principal` | Sin modelo | `VinculoAPPI {activo, esContactoPrincipal}` entre `Parque` y `Usuario`, con restricción de un principal | Con la asociación directa (A) la unicidad es estructural; con el booleano (E) se impone con una regla. | **Recomendación:** asociación directa (A, borrador). |
| K-14 | Tipo de PI del parque | Derivado de `Parque "1" *-- "0..*" PeriodoTipoPI {tipoPI, fechaDesde, fechaHasta, motivo, cumplimientoObligatoriosAlCierre}` | Atributo `tipo` en `ParqueIndustrial`, sin historial | Atributo `tipoActual` en `Parque` + `tipoPIEvaluado` en `Expediente`; sin historial (aunque su OpenAPI sí tiene `ParkTypeHistoryEntry`) | RF-11-AC-1, AC-2 y AC-5 piden historial con motivo y la cifra congelada al cierre. | **Recomendación:** clase de historial (A, borrador). |
| K-15 | Dueño de `AsignacionConsultor` | `Expediente "1" *-- "0..*"` | `ParqueIndustrial "1" -- "0..*"` y `Usuario "1" -- "0..*"`, con `activo: Boolean` | `Expediente "1" -- "0..*"` (asociación) | RF-10-AC-1 asigna por parque y generación: el expediente es ese par. | **Recomendación:** por expediente (A, E, borrador). |
| K-16 | Enumeraciones | MAYÚSCULAS en el diagrama, minúsculas snake en su OpenAPI; `EstadoEvidencia` incluye `ELIMINADA`; `EstadoParque` incluye `HISTORICO` | MAYÚSCULAS en diagrama y OpenAPI; `TipoParque` con prefijo `EN_` (`EN_CONSTRUCCION_ABIERTO`); `EstadoEvidencia` incluye `PENDIENTE`; `EstadoParque` sin `HISTORICO` | Minúsculas snake en ambos; `EstadoEvidencia` de 3 valores (la baja es el booleano `eliminada`) | Los valores son datos persistidos y aparecen en las pruebas. | **Recomendación:** minúsculas snake (A en su OpenAPI, E, borrador) y una sola lista de valores por enum. |

### 2.d Correspondencia entre clases y el OpenAPI propio

| Integrante | Correspondencia general | Diferencias encontradas |
|---|---|---|
| A | Alta en nombres y contenido, con distinto caso: clases en camelCase (`fechaAlta`), schemas en snake_case (`fecha_alta`). Las clases internas no tienen schema, como corresponde (`TokenUnUso`, `ArchivoAlmacenado`, `hashContrasena`). | (1) `Usuario.intentosFallidos` y `bloqueadoHasta`: la descripción de `POST /sesiones` dice que el contador "se lleva por correo, exista o no la cuenta"; con el atributo en `Usuario` no se puede contar un correo inexistente. (2) `Evidencia.documento_id` es uno por evidencia en el schema, pero en la clase el archivo cuelga de cada `VersionEvidencia`. (3) Sin atributo en la clase: `Usuario.desactivado_en`, `Parque.tipo_registro`, `VersionCatalogo.solo_lectura` y `total_criterios`, `EventoBitacora.detalle` y `correo_usuario`. (4) Campos del schema sin asociación en la clase: `Fase.cerrada_por`, `CambioTipoPI.registrado_por`, `EvaluacionDesempeno.consultor` y `version_catalogo`, `Recomendacion.autor`, `Observacion.autor`. (5) El recurso `CambioTipoPI` se llama `PeriodoTipoPI` en la clase. |
| L | Alta en atributos (camelCase en ambos), con schemas en inglés y clases en español: `ParqueIndustrial`↔`Park`, `EstandarSeguridad`↔`Standard`, `CriterioSeguridad`↔`Criterion`, `RespuestaCriterio`↔`CriterionResponse`, `Evidencia`↔`Evidence`, `RevisionEvidencia`↔`EvidenceReview`, `PlanTrabajo`↔`WorkPlan`, `Opinion`↔`Opinion`, `RegistroAuditoria`↔`AuditEvent`. | (1) Las 7 subclases de rol no aparecen en el API: `User.roles` es una lista de `TipoRol` y existe `RoleAssignment`. (2) `User.parquesAsignados` y `fechaCreacion` no tienen atributo ni asociación en la clase. (3) `AsignacionConsultor` no tiene schema ni endpoint. (4) `Evaluation` mezcla `EvaluacionParque` con `EvaluacionFinal` (agrega `tipo`, `resultado`, `observaciones`); `EvaluacionFinal` no tiene schema. (5) `FaseProceso` cuelga del parque en la clase y del plan en el API (`Phase.planId`); `fechaCierre` no está en el schema. (6) `AuditEvent` no tiene `parqueId`, aunque la clase asocia la bitácora al parque. |
| E | Alta en atributos (camelCase en ambos), schemas en inglés: `EvaluacionCriterio`↔`CriterionEvaluation`, `EvidenciaCriterio`↔`EvidenceCriterionLink`, `VinculoAPPI`↔`AppiLink`, `Dictamen`↔`Verdict`, `Distintivo`↔`Badge`, `EventoBitacora`↔`AuditLog`; `SesionComite` + `AccesoComite` se aplanan en `CommitteeSession`. | (1) Schemas sin clase: `Recommendation`, `FileLimit` (configuración), `Audit` (RF-18), `ValidationVisit` (RF-37), `ParkTypeHistoryEntry`, `Token`, `EvidenceVersion`, `RenewalCreate`. (2) `Parque.tipoActual` en la clase, `tipoPI` en el schema; `Park.atrasadoPorActualizacion` y `ParkPatch.fechaActualizacion` sin atributo. (3) `Expediente.tipoPIEvaluado` y `fechaInicio` no están en `CaseFile`. (4) `RevisionAnalisisRiesgos.referenciaDocumento: URI` en la clase, `documentoEvidenciaId` en el schema. (5) `Evidence.faseId` sin asociación `Evidencia → fase` en la clase. (6) `Desarrollador`, `Subestandar`, `MarcaCriterioTipo` y `DefinicionFase` no tienen schema; `Criterion` no expone marcas por tipo. |

---

## 3. Arquitectura

### 3.a Consenso

| Aspecto | A | L | E |
|---|---|---|---|
| Estilo | Monolito modular en capas, cliente-servidor (ADR-001) | Monolito modular en capas, cliente-servidor (ADR-001) | Monolito modular por capas (ADR-001) |
| Alternativa principal descartada | Microservicios (además capas horizontales, MVC en servidor y serverless) | Microservicios orientados a eventos | Microservicios |
| Frontend | SPA React 18, TypeScript, Vite | "Frontend web" (sin tecnología) | React + Vite |
| Backend | Python 3.12, FastAPI, SQLAlchemy 2.0 | "Backend Python, API REST" | FastAPI / Python |
| Base de datos | PostgreSQL 16 | PostgreSQL (sin versión) | PostgreSQL 16 |
| Archivos | Almacenamiento de objetos; PostgreSQL solo metadatos y referencia | Igual | Igual |
| Correo | Proveedor externo SMTP | Proveedor externo (SMTP o API) | Proveedor externo (SMTP o API por definir) |
| Descarga de archivos | URL firmada ≤ 5 min directo del bucket | "Carga y recuperación autorizada" (sin URL firmada explícita) | URL firmada ≤ 5 min directo del bucket |

### 3.b Conflictos

| ID | Aspecto | A | L | E | Por qué importa | Recomendación |
|---|---|---|---|---|---|---|
| Q-01 | Procesos en segundo plano | Contenedor `worker` con APScheduler, misma imagen que la API; cola de correos como tabla de PostgreSQL (patrón outbox); sin broker | Contenedor "trabajador en segundo plano" y "cola de tareas, opcional según implementación"; el módulo Notificaciones encola | "Trabajos en segundo plano" dentro del mismo contenedor del backend; sin cola definida | RNF-12 (3 reintentos) y la revisión diaria de RF-09/RF-30 necesitan un proceso que corra aunque no haya solicitudes. Un broker suma un servicio que operar. | **Recomendación:** proceso programado aparte con outbox en PostgreSQL (A); L y E no lo contradicen. |
| Q-02 | Carga de archivos | A través de la API en `multipart` (ADR-002), con criterio de reversión a URL prefirmada si falla la prueba de RNF-07 | Carga directa al almacenamiento y registro posterior de metadatos (inferido de `POST /parques/{parque_id}/evidencias`: "Registrar metadatos de una evidencia cargada al almacenamiento de objetos", campo `ubicacionObjeto`) | A través de la API en `multipart` (`POST /evidencias`) | Con carga directa, RF-06 se valida sobre lo que declara el cliente y quedan objetos huérfanos; vía API, el backend absorbe 30 cargas de 100 MB (RNF-07). | **Recomendación:** vía API (A, E) con el criterio de reversión de ADR-002. |
| Q-03 | Autenticación | JWT con claim `sid` + sesión en PostgreSQL validada en cada solicitud (ADR-003) | JWT sin estado; sin sesión en ningún diagrama | JWT Bearer en el contrato; el C4 dice que el backend aplica "sesiones" y PostgreSQL las guarda, sin clase ni mecanismo | RF-26-AC-5 (invalidar al cerrar sesión) y AC-6 (60 min sin actividad) no se cumplen con JWT sin estado. | **Recomendación:** sesión en servidor (A; el borrador ya la tiene, E la menciona). |
| Q-04 | Despliegue | Una VM con Docker Compose (Caddy, `api` con 2 workers, `worker`); PostgreSQL 16 **gestionado** con respaldo diario y 30 días; bucket gestionado; GitHub Actions + GHCR; desarrollo con Postgres y MinIO en Compose | Entorno cloud con capa de entrada HTTPS, contenedores frontend, backend y trabajador, cola opcional, PostgreSQL, almacenamiento, monitoreo y respaldos; sin decir si la base es gestionada | VM o servicio de contenedores con Docker Compose marcado como "propuesta" no validada, con **PostgreSQL dentro del Compose**; proxy "por definir"; monitoreo externo | Base gestionada o en contenedor cambia quién cumple RNF-13 (respaldo diario, 30 días). | **Recomendación:** base gestionada (A) o documentar cómo se cumple RNF-13 con la base en contenedor. |
| Q-05 | Entrega del frontend | Archivos estáticos servidos por el proxy Caddy | Contenedor frontend propio | Estáticos servidos por el proxy | Un contenedor más que construir y desplegar. | **Recomendación:** estáticos en el proxy (A, E). |
| Q-06 | Módulos del backend | 5 módulos (identidad y acceso; programa; expediente; dictaminación; reportes y bitácora) + componentes transversales (seguridad, errores, bitácora, validador de archivos, puerto de almacenamiento, outbox, reloj, motor de cumplimiento); `import-linter` en CI | 6 módulos (usuarios y permisos; parques y checklist; evidencias; opiniones y evaluaciones; auditoría y reportes; notificaciones) | 5 componentes en el texto del ADR (usuarios, expedientes, evidencias, evaluaciones, dictámenes); el diagrama no los detalla | La partición fija qué equipo toca qué carpeta y dónde viven las reglas que cruzan módulos (RD-09, RF-17). L separa evidencias del expediente; A no. | **Recomendación:** partir de los módulos de A, que tienen nivel 3, y decidir si evidencias es módulo propio. |
| Q-07 | Nivel de detalle C4 | Nivel 2 (contenedores) y nivel 3 (componentes del backend) | Un diagrama titulado "C4 Container Level" que mezcla contenedores con módulos internos | Solo nivel 2 | La actividad pide C4; mezclar niveles dificulta revisar fronteras. | **Recomendación:** nivel 2 y nivel 3 por separado. |
| Q-08 | Supuesto de tamaño del equipo | Evalúa para un desarrollador y para tres | "Equipo de desarrollo pequeño" | "Será desarrollado por una sola persona" | El equipo es de tres; cambia el peso de las fronteras de módulo. | **Recomendación:** documentar el ADR para tres personas. |
| Q-09 | Integración continua y ambiente de desarrollo | GitHub Actions (ruff + pytest con PostgreSQL de servicio), registro de imágenes, Compose de desarrollo con MinIO | No lo modela | Nota: Compose de desarrollo del Sprint 1 con PostgreSQL 16; sin CI | Las pruebas de carga de archivos necesitan un S3 local (MinIO) o un doble en memoria. | **Recomendación:** incluir CI y el Compose de desarrollo en el diagrama de despliegue. |

---

## 4. Resumen en cifras

| Contrato | Operaciones | Rutas | Schemas | AC distintos en `x-acceptance-criteria` |
|---|---|---|---|---|
| A (`Angel_S04_A2_v2/openapi.yaml`) | 86 | 57 | 99 | 131 / 150 |
| L (`Leonardo_S04_A2/openapi.yaml`) | 46 | 21 | 48 | 51 / 150 |
| E (`Erick_S04_A2/openapi.yaml`) | 47 | 43 | 73 | 136 / 150 (150 con `x-background-processes`) |
| Borrador (`openapi_equipo.yaml`) | 88 | 62 | 110 | 131 / 150 |

| Diagrama | Clases | Abstractas | Enumeraciones |
|---|---|---|---|
| A (`Angel_S04_A1_v2/diagrama_clases.puml`) | 34 | 0 | 10 dibujadas (8 más nombradas en una nota) |
| L (`Leonardo_S04_A1/diagrama_clases.puml`) | 22 (7 son subclases de rol) | 1 | 10 |
| E (`Erick_S04_A1/diagrama_clases_agente.puml`) | 28 | 0 | 12 |
| Borrador (`diagrama_clases_equipo.puml`) | 37 | 1 | 11 |

| Artefacto | Consensos | Gaps | Conflictos |
|---|---|---|---|
| OpenAPI | 19 | 50 | 26 (O-01 a O-26) + 12 aspectos transversales |
| Clases | 13 | 23 | 16 (K-01 a K-16) |
| Arquitectura | 8 aspectos | — | 9 (Q-01 a Q-09) |

---

## Anexo. Cálculo de cobertura

Script (Python 3, PyYAML 6.0.3). Lee los IDs `RF-XX-AC-Y` y la prioridad de cada RF de la sección 3.1 de `SRS_equipo.md` y los compara con la unión de `x-acceptance-criteria` de cada operación (`get`, `post`, `put`, `patch`, `delete`) de cada contrato. No cuenta menciones en texto libre: L lista los 150 AC en `x-traceability` y E en `x-scope`/`x-background-processes`, y eso no es cobertura por operación.

```python
import re, yaml
srs = open('S03_A1/SRS_equipo.md').read().split('### 3.2')[0]
rfs, cur = {}, None
for line in srs.splitlines():
    m = re.match(r'\*\*(RF-\d\d): (.*)\*\*$', line)
    if m: cur = m.group(1); rfs[cur] = {'p': '', 'ac': []}; continue
    m = re.match(r'Prioridad: ([^.]*)', line)
    if m and cur: rfs[cur]['p'] = m.group(1)
    m = re.match(r'\*\*(RF-\d\d-AC-\d+)\*\*', line)
    if m and cur: rfs[cur]['ac'].append(m.group(1))
todos = {a for v in rfs.values() for a in v['ac']}                       # 150
posterior = {a for v in rfs.values() if v['p'] == 'Posterior' for a in v['ac']}  # 19
for f in CONTRATOS:
    d = yaml.safe_load(open(f)); xs = set()
    for p, v in d['paths'].items():
        for m in ('get', 'post', 'put', 'patch', 'delete'):
            if m in v: xs |= set(v[m].get('x-acceptance-criteria') or [])
    print(f, len(xs), len(xs - posterior), sorted(xs - todos))
```

Resultado: A 131 (131 no Posterior, 0 huérfanos); L 51 (51, 0); E 136 (127, 0); borrador 131 (131, 0). RF-18, RF-19, RF-20, RF-22, RF-37, RF-38 y RF-39 son Posterior (19 AC).
