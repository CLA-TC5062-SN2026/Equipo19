# Decisiones de diseño y trazabilidad de la API

**Proyecto:** SGPIS (AMPIP), Equipo 19, TC5062
**Actividad:** S04-A2, Diseño de API RESTful (OpenAPI)
**Contrato:** `openapi.yaml` v1.0.0 (OpenAPI 3.0.3), validado con Redocly CLI y swagger-cli sin errores
**Fuente de los criterios:** `S03_A1/SRS_equipo.md` v2.0 (39 RF, 150 criterios Given-When-Then)
**Arquitectura y modelo de dominio:** `S04_A1/decision_arquitectonica.md` (monolito modular, ADR-001 a ADR-003), `S04_A1/diagrama_clases.puml` y `S04_A1/diagrama_componentes.puml`

## Sección A. Trazabilidad spec ↔ criterios de aceptación

La tabla no se llenó a mano. Un script recorre `openapi.yaml`, junta las extensiones `x-acceptance-criteria` de cada operación y las cruza con los 150 IDs del SRS. Si un criterio en alcance se queda sin endpoint, o si el YAML cita un ID que no existe en el SRS, el script falla. Así la tabla no puede decir algo distinto de lo que dice el contrato.

Cuando un criterio aparece en varias operaciones, la tabla las lista todas. Las de escritura van primero porque son las que el criterio pone a prueba; los GET que aparecen después son los que permiten verificar el resultado.

| Estado | Criterios |
|---|---|
| ✅ Cubierto por un endpoint | 126 |
| ⚠️ Parcial | 5 |
| ❌ Fuera de alcance de v1 (RF con prioridad Posterior) | 19 |
| **Total** | **150** |

| ID Criterio | Descripción resumida | Endpoint | Método HTTP | ¿Cubierto? |
|---|---|---|---|---|
| RF-01-AC-1 | Coordinación carga CSV válido y crea versión vigente | `/versiones-catalogo` | POST | ✅ |
| RF-01-AC-2 | APPI o consultor intenta cargar versión: 403 | `/versiones-catalogo` | POST | ✅ |
| RF-01-AC-3 | Expediente muestra versión del catálogo sin poder editarla | `/parques/{parque_id}`<br>`/parques/{parque_id}` | PATCH<br>GET | ✅ |
| RF-01-AC-4 | CSV con columna faltante o marca inválida: rechazo con fila y columna | `/versiones-catalogo` | POST | ✅ |
| RF-01-AC-5 | Versión nueva para 2028 no altera la de 2027, que queda en solo lectura | `/generaciones`<br>`/versiones-catalogo`<br>`/versiones-catalogo/{version_id}` | POST<br>GET<br>GET | ✅ |
| RF-02-AC-1 | Alta de parque con tipo, región y generación en estado activo | `/parques` | POST | ✅ |
| RF-02-AC-2 | Alta sin tipo de PI válido: rechazo con mensaje | `/parques` | POST | ✅ |
| RF-02-AC-3 | Alta sin región válida: rechazo con mensaje | `/parques` | POST | ✅ |
| RF-03-AC-1 | Alta de usuario APPI en pendiente de activación con invitación | `/usuarios` | POST | ✅ |
| RF-03-AC-2 | Mismo usuario APPI y consultor del mismo parque: rechazo | `/parques/{parque_id}/asignaciones-consultor`<br>`/usuarios`<br>`/usuarios/{usuario_id}` | POST<br>POST<br>PATCH | ✅ |
| RF-03-AC-3 | Administrador técnico sin acceso a parques ni evidencias | `/usuarios` | POST | ✅ |
| RF-04-AC-1 | APPI ve solo criterios O o R de su tipo de PI | `/parques/{parque_id}/autoevaluaciones`<br>`/parques/{parque_id}/criterios` | GET<br>GET | ✅ |
| RF-04-AC-2 | Autoevaluar un criterio NA por API: 422 | `/parques/{parque_id}/autoevaluaciones/{criterio_id}`<br>`/parques/{parque_id}/autoevaluaciones/{criterio_id}` | PUT<br>GET | ✅ |
| RF-05-AC-1 | APPI sube evidencia: queda enviada y el criterio pasa a en revisión | `/parques/{parque_id}/evidencias` | POST | ✅ |
| RF-05-AC-2 | Consultor observa evidencia: pasa a observada y se notifica | `/evidencias/{evidencia_id}/observaciones` | POST | ✅ |
| RF-05-AC-3 | Consultor sin el parque intenta observar: 403 | `/evidencias/{evidencia_id}/observaciones` | POST | ✅ |
| RF-05-AC-4 | Versión nueva de evidencia observada la regresa a enviada | `/evidencias/{evidencia_id}/versiones` | POST | ✅ |
| RF-05-AC-5 | Se guardan metadatos y referencia; el archivo no va a PostgreSQL | `/parques/{parque_id}/evidencias` | POST | ✅ |
| RF-05-AC-6 | Historial de versiones con observaciones y versión vigente | `/evidencias/{evidencia_id}`<br>`/evidencias/{evidencia_id}/observaciones` | GET<br>GET | ✅ |
| RF-05-AC-7 | Un archivo ligado a dos criterios con estados independientes | `/parques/{parque_id}/evidencias`<br>`/evidencias/{evidencia_id}`<br>`/parques/{parque_id}/evidencias` | POST<br>PATCH<br>GET | ✅ |
| RF-05-AC-8 | Carga de 4 fotos con 1 fuera de límite: 3 creadas, 1 rechazada | `/parques/{parque_id}/evidencias` | POST | ✅ |
| RF-05-AC-9 | APPI elimina evidencia enviada: queda en historial como eliminada | `/evidencias/{evidencia_id}`<br>`/evidencias/{evidencia_id}` | DELETE<br>GET | ✅ |
| RF-05-AC-10 | Eliminar evidencia aceptada: rechazo con mensaje | `/evidencias/{evidencia_id}` | DELETE | ✅ |
| RF-06-AC-1 | Archivo de 105 MB: rechazo | `/evidencias/{evidencia_id}/versiones`<br>`/parques/{parque_id}/evidencias` | POST<br>POST | ✅ |
| RF-06-AC-2 | JPG de 90 MB: aceptado | `/parques/{parque_id}/evidencias` | POST | ✅ |
| RF-06-AC-3 | Archivo de exactamente 100 MB: aceptado | `/parques/{parque_id}/evidencias` | POST | ✅ |
| RF-06-AC-4 | Video .mp4: rechazo con mensaje | `/evidencias/{evidencia_id}/versiones`<br>`/parques/{parque_id}/evidencias` | POST<br>POST | ✅ |
| RF-06-AC-5 | Archivo .zip: rechazo con lista de formatos | `/evidencias/{evidencia_id}/versiones`<br>`/parques/{parque_id}/evidencias` | POST<br>POST | ✅ |
| RF-06-AC-6 | Límite cambiado a 50 MB: PDF de 60 MB rechazado | `/parques/{parque_id}/evidencias`<br>`/configuracion`<br>`/configuracion` | POST<br>PATCH<br>GET | ✅ |
| RF-06-AC-7 | Configurar límite de 500 MB: rechazo | `/configuracion` | PATCH | ✅ |
| RF-07-AC-1 | Coordinación ve estado de cada criterio sin enlace a evidencias | `/parques/{parque_id}/criterios` | GET | ✅ |
| RF-07-AC-2 | Coordinación abre evidencia administrativa | `/evidencias/{evidencia_id}/contenido` | GET | ✅ |
| RF-07-AC-3 | Coordinación abre evidencia de seguridad: 403 | `/evidencias/{evidencia_id}/contenido` | GET | ✅ |
| RF-08-AC-1 | Cumplimiento de obligatorios 180/200 = 90 % | `/parques/{parque_id}/cumplimiento` | GET | ✅ |
| RF-08-AC-2 | Avance general (180+30)/(200+50) = 84 % | `/parques/{parque_id}/cumplimiento` | GET | ✅ |
| RF-08-AC-3 | Estándar sin O aplicables muestra No aplica | `/parques/{parque_id}/cumplimiento` | GET | ✅ |
| RF-08-AC-4 | Cumplimiento de recomendados 30/50 = 60 % | `/parques/{parque_id}/cumplimiento` | GET | ✅ |
| RF-08-AC-5 | Global suma criterios, no promedia estándares (55 %) | `/parques/{parque_id}/cumplimiento` | GET | ✅ |
| RF-09-AC-1 | Consultor registra responsable APPI y fecha comprometida | `/parques/{parque_id}/compromisos/{criterio_id}`<br>`/parques/{parque_id}/compromisos/{criterio_id}` | PUT<br>GET | ✅ |
| RF-09-AC-2 | Fecha vencida sin cumplido: revisión diaria marca atrasado | `/parques/{parque_id}/compromisos`<br>`/parques/{parque_id}/criterios` | GET<br>GET | ⚠️ parcial (a) |
| RF-09-AC-3 | Fecha no vencida: no se marca atrasado | `/parques/{parque_id}/compromisos` | GET | ⚠️ parcial (a) |
| RF-09-AC-4 | Responsable que no es APPI del parque: rechazo | `/parques/{parque_id}/compromisos/{criterio_id}` | PUT | ✅ |
| RF-10-AC-1 | Asignar consultor a parque y generación | `/parques/{parque_id}/asignaciones-consultor` | POST | ✅ |
| RF-10-AC-2 | Reasignar: se conserva historial y se retira acceso al anterior | `/parques/{parque_id}/asignaciones-consultor`<br>`/parques/{parque_id}/asignaciones-consultor` | POST<br>GET | ✅ |
| RF-10-AC-3 | APPI intenta asignar consultor: 403 | `/parques/{parque_id}/asignaciones-consultor` | POST | ✅ |
| RF-11-AC-1 | Cambio de tipo cierra historial, abre uno nuevo y recalcula | `/parques/{parque_id}/cambios-tipo-pi`<br>`/parques/{parque_id}/cambios-tipo-pi`<br>`/parques/{parque_id}/criterios` | POST<br>GET<br>GET | ✅ |
| RF-11-AC-2 | Cumplimiento anterior se conserva aparte del nuevo | `/parques/{parque_id}/cambios-tipo-pi`<br>`/parques/{parque_id}/cumplimiento` | POST<br>GET | ✅ |
| RF-11-AC-3 | Tipo de PI fuera de los cuatro válidos: 422 | `/parques/{parque_id}/cambios-tipo-pi` | POST | ✅ |
| RF-11-AC-4 | Criterio que deja de ser NA entra en pendiente | `/parques/{parque_id}/cambios-tipo-pi`<br>`/parques/{parque_id}/criterios` | POST<br>GET | ✅ |
| RF-11-AC-5 | Cambio sin motivo: rechazo; con motivo, se guarda y va a bitácora | `/parques/{parque_id}/cambios-tipo-pi`<br>`/parques/{parque_id}/cambios-tipo-pi` | POST<br>GET | ✅ |
| RF-11-AC-6 | Criterio que pasa a NA conserva evidencias y deja de contar | `/parques/{parque_id}/cambios-tipo-pi`<br>`/parques/{parque_id}/cumplimiento` | POST<br>GET | ✅ |
| RF-12-AC-1 | Opinión intermedia con precondiciones; fase avanza | `/parques/{parque_id}/opiniones` | POST | ✅ |
| RF-12-AC-2 | Consultor sin el parque emite Opinión: 403 | `/parques/{parque_id}/opiniones` | POST | ✅ |
| RF-12-AC-3 | Segunda Opinión final en la generación: rechazo | `/parques/{parque_id}/opiniones` | POST | ✅ |
| RF-12-AC-4 | Opinión sin criterio 1.2 cumplido: rechazo | `/parques/{parque_id}/opiniones` | POST | ✅ |
| RF-12-AC-5 | Opinión sin análisis de riesgos vigente: rechazo | `/parques/{parque_id}/opiniones` | POST | ✅ |
| RF-12-AC-6 | Opinión final sin favorable/no favorable: rechazo | `/parques/{parque_id}/opiniones`<br>`/opiniones/{opinion_id}`<br>`/parques/{parque_id}/opiniones` | POST<br>GET<br>GET | ✅ |
| RF-13-AC-1 | Consultor de comité lee expediente sin análisis de riesgos | `/parques/{parque_id}/sesiones-comite`<br>`/parques/{parque_id}`<br>`/parques/{parque_id}/revisiones-analisis-riesgos`<br>`/parques/{parque_id}/sesiones-comite`<br>`/sesiones-comite/{sesion_id}` | POST<br>GET<br>GET<br>GET<br>GET | ✅ |
| RF-13-AC-2 | Consultor asignado como consultor de comité: rechazo | `/parques/{parque_id}/sesiones-comite` | POST | ✅ |
| RF-13-AC-3 | Sesión de comité cerrada: consultor de comité recibe 403 | `/sesiones-comite/{sesion_id}`<br>`/parques/{parque_id}` | PATCH<br>GET | ✅ |
| RF-14-AC-1 | Director General firma dictamen otorgar; corre vigencia | `/dictamenes/{dictamen_id}/firma` | POST | ✅ |
| RF-14-AC-2 | Consultor asignado registra dictamen: 403 | `/parques/{parque_id}/dictamenes` | POST | ✅ |
| RF-14-AC-3 | Otorgar con 85 % de obligatorios: rechazo | `/parques/{parque_id}/dictamenes` | POST | ✅ |
| RF-14-AC-4 | Otorgar sin autoevaluación revisada: rechazo | `/parques/{parque_id}/dictamenes` | POST | ✅ |
| RF-14-AC-5 | Otorgar sin Opinión final favorable: rechazo | `/parques/{parque_id}/dictamenes` | POST | ✅ |
| RF-14-AC-6 | Captura sin firma queda en borrador visible al comité | `/parques/{parque_id}/dictamenes`<br>`/dictamenes/{dictamen_id}`<br>`/parques/{parque_id}/dictamenes` | POST<br>GET<br>GET | ✅ |
| RF-14-AC-7 | Firma por alguien distinto del Director General: 403 | `/dictamenes/{dictamen_id}/firma` | POST | ✅ |
| RF-14-AC-8 | No otorgar sin condiciones: se acepta en borrador | `/parques/{parque_id}/dictamenes` | POST | ✅ |
| RF-15-AC-1 | Expediente completo: se abre la sesión de comité | `/parques/{parque_id}/sesiones-comite` | POST | ✅ |
| RF-15-AC-2 | Criterios en revisión: no se abre la sesión | `/parques/{parque_id}/sesiones-comite` | POST | ✅ |
| RF-15-AC-3 | Sin Opinión final favorable: no se abre la sesión | `/parques/{parque_id}/sesiones-comite` | POST | ✅ |
| RF-16-AC-1 | Consultor registra revisión del análisis; queda vigente | `/parques/{parque_id}/revisiones-analisis-riesgos`<br>`/parques/{parque_id}/revisiones-analisis-riesgos`<br>`/revisiones-analisis-riesgos/{revision_id}` | POST<br>GET<br>GET | ✅ |
| RF-16-AC-2 | APPI sube documento del análisis, visible solo a APPI y consultor | `/revisiones-analisis-riesgos/{revision_id}/documento`<br>`/revisiones-analisis-riesgos/{revision_id}/documento` | PUT<br>GET | ✅ |
| RF-16-AC-3 | Coordinación intenta abrir el análisis: 403 y bitácora | `/revisiones-analisis-riesgos/{revision_id}/documento` | GET | ✅ |
| RF-16-AC-4 | Revisión de 2027 no vigente en el ciclo de renovación | `/parques/{parque_id}/criterios/{criterio_id}/calificaciones` | POST | ⚠️ parcial (b) |
| RF-17-AC-1 | Calificar estándar 3 sin análisis vigente: rechazo | `/parques/{parque_id}/criterios/{criterio_id}/calificaciones` | POST | ✅ |
| RF-17-AC-2 | Con análisis vigente: se acepta la calificación | `/parques/{parque_id}/criterios/{criterio_id}/calificaciones` | POST | ✅ |
| RF-17-AC-3 | Subir evidencia del estándar 6 sin análisis: sin bloqueo | `/parques/{parque_id}/evidencias` | POST | ✅ |
| RF-18-AC-1 | Registrar auditoría interna | (sin endpoint en v1) | — | ❌ fuera de alcance |
| RF-18-AC-2 | Auditoría externa sin notificación al corporativo: rechazo | (sin endpoint en v1) | — | ❌ fuera de alcance |
| RF-19-AC-1 | Aviso de vencimiento del distintivo a 6 meses | (sin endpoint en v1) | — | ❌ fuera de alcance |
| RF-19-AC-2 | Aviso a 3 meses | (sin endpoint en v1) | — | ❌ fuera de alcance |
| RF-19-AC-3 | Sin aviso si ya renovó | (sin endpoint en v1) | — | ❌ fuera de alcance |
| RF-19-AC-4 | Plazos de aviso configurables | (sin endpoint en v1) | — | ❌ fuera de alcance |
| RF-19-AC-5 | No duplicar aviso el mismo día | (sin endpoint en v1) | — | ❌ fuera de alcance |
| RF-20-AC-1 | Aviso de auditoría interna un mes antes | (sin endpoint en v1) | — | ❌ fuera de alcance |
| RF-20-AC-2 | Sin aviso si la auditoría ya se registró | (sin endpoint en v1) | — | ❌ fuera de alcance |
| RF-21-AC-1 | Reporte mensual con fase, atraso y observaciones abiertas | `/generaciones/{generacion_id}/reportes-mensuales/{periodo}` | GET | ✅ |
| RF-21-AC-2 | APPI genera reporte mensual: 403 | `/generaciones/{generacion_id}/reportes-mensuales/{periodo}` | GET | ✅ |
| RF-22-AC-1 | Reporte agregado por región para asociados | (sin endpoint en v1) | — | ❌ fuera de alcance |
| RF-22-AC-2 | Reporte de asociados sin porcentaje ni ranking por parque | (sin endpoint en v1) | — | ❌ fuera de alcance |
| RF-23-AC-1 | Gerente corporativo ve el avance de sus parques | `/parques` | GET | ✅ |
| RF-23-AC-2 | Gerente corporativo sube evidencia u observa: 403 | `/evidencias/{evidencia_id}/observaciones`<br>`/parques/{parque_id}/evidencias` | POST<br>POST | ✅ |
| RF-24-AC-1 | Coordinación define evidencia suficiente; se muestra a consultor y APPI | `/versiones-catalogo/{version_id}/criterios/{criterio_id}/evidencia-suficiente`<br>`/parques/{parque_id}/criterios/{criterio_id}`<br>`/versiones-catalogo/{version_id}/criterios` | PUT<br>GET<br>GET | ✅ |
| RF-24-AC-2 | Consultor modifica evidencia suficiente: 403 | `/versiones-catalogo/{version_id}/criterios/{criterio_id}/evidencia-suficiente` | PUT | ✅ |
| RF-25-AC-1 | APPI ve cada criterio aplicable de forma individual | `/parques/{parque_id}/criterios`<br>`/parques/{parque_id}/criterios/{criterio_id}` | GET<br>GET | ✅ |
| RF-25-AC-2 | APPI descarga archivo maestro: 403 con mensaje | `/versiones-catalogo/{version_id}/archivo-maestro` | GET | ✅ |
| RF-25-AC-3 | Coordinación descarga archivo maestro completo | `/versiones-catalogo/{version_id}/archivo-maestro` | GET | ✅ |
| RF-25-AC-4 | Consultor descarga archivo maestro: 403; sí ve sus criterios | `/parques/{parque_id}/criterios`<br>`/versiones-catalogo/{version_id}/archivo-maestro` | GET<br>GET | ✅ |
| RF-26-AC-1 | Inicio de sesión correcto entrega token | `/sesiones` | POST | ✅ |
| RF-26-AC-2 | Contraseña incorrecta: mensaje genérico y sin token | `/sesiones` | POST | ✅ |
| RF-26-AC-3 | Sexto intento tras 5 fallos: cuenta bloqueada 15 min | `/sesiones` | POST | ✅ |
| RF-26-AC-4 | Enlace de recuperación de un solo uso y 30 min | `/restablecimientos-contrasena`<br>`/solicitudes-recuperacion` | POST<br>POST | ✅ |
| RF-26-AC-5 | Cierre de sesión invalida el token (401 después) | `/sesiones/actual` | DELETE | ✅ |
| RF-26-AC-6 | 60 min sin actividad: 401 | `/sesiones/actual` | GET | ✅ |
| RF-27-AC-1 | Consultor acepta evidencia enviada | `/evidencias/{evidencia_id}` | PATCH | ✅ |
| RF-27-AC-2 | Con evidencia aceptada, consultor califica cumplido | `/parques/{parque_id}/criterios/{criterio_id}/calificaciones`<br>`/parques/{parque_id}/criterios/{criterio_id}/calificaciones` | POST<br>GET | ✅ |
| RF-27-AC-3 | Estándar 3 sin análisis vigente: no se califica cumplido | `/parques/{parque_id}/criterios/{criterio_id}/calificaciones` | POST | ✅ |
| RF-27-AC-4 | Primera evidencia pasa el criterio de pendiente a en revisión | `/parques/{parque_id}/evidencias` | POST | ✅ |
| RF-27-AC-5 | APPI intenta aceptar, calificar o reabrir: 403 | `/parques/{parque_id}/criterios/{criterio_id}/calificaciones`<br>`/evidencias/{evidencia_id}` | POST<br>PATCH | ✅ |
| RF-27-AC-6 | Consultor califica no cumplido; cuenta en RF-08 | `/parques/{parque_id}/criterios/{criterio_id}/calificaciones`<br>`/parques/{parque_id}/cumplimiento` | POST<br>GET | ✅ |
| RF-27-AC-7 | Evidencia nueva sobre criterio cumplido lo regresa a en revisión | `/evidencias/{evidencia_id}/versiones`<br>`/parques/{parque_id}/evidencias` | POST<br>POST | ✅ |
| RF-27-AC-8 | Consultor reabre criterio no cumplido con motivo | `/parques/{parque_id}/criterios/{criterio_id}/calificaciones`<br>`/parques/{parque_id}/criterios/{criterio_id}/calificaciones` | POST<br>GET | ✅ |
| RF-28-AC-1 | Crear generación con versión del catálogo | `/generaciones`<br>`/generaciones/{generacion_id}` | POST<br>GET | ✅ |
| RF-28-AC-2 | APPI o consultor crea generación: 403 | `/generaciones` | POST | ✅ |
| RF-28-AC-3 | Alta de parque sin generación: rechazo | `/parques` | POST | ✅ |
| RF-29-AC-1 | Baja de consultor retira acceso a sus parques | `/usuarios/{usuario_id}` | PATCH | ✅ |
| RF-29-AC-2 | APPI intenta dar de baja una cuenta: 403 | `/usuarios/{usuario_id}` | PATCH | ✅ |
| RF-29-AC-3 | Baja de parque retira accesos y lo saca de la vista activa | `/parques/{parque_id}`<br>`/parques` | PATCH<br>GET | ✅ |
| RF-30-AC-1 | Registrar fecha de término y próxima actualización | `/parques/{parque_id}`<br>`/parques/{parque_id}` | PATCH<br>GET | ✅ |
| RF-30-AC-2 | Actualización anual vencida: revisión diaria marca atrasado | `/parques` | GET | ⚠️ parcial (a) |
| RF-30-AC-3 | Actualización registrada a tiempo recalcula la siguiente fecha | `/parques/{parque_id}/actualizaciones-anuales`<br>`/parques/{parque_id}/actualizaciones-anuales` | POST<br>GET | ✅ |
| RF-31-AC-1 | Historial del parque en una sola vista | `/parques/{parque_id}/historial` | GET | ✅ |
| RF-31-AC-2 | Alta de parque histórico con datos mínimos | `/parques` | POST | ✅ |
| RF-31-AC-3 | APPI consulta historial de otro parque: 403 | `/parques/{parque_id}/historial` | GET | ✅ |
| RF-32-AC-1 | Expediente muestra las nueve fases y la actual | `/parques/{parque_id}/fases` | GET | ✅ |
| RF-32-AC-2 | Entregado sin cierre sigue en proceso | `/parques/{parque_id}/fases` | GET | ✅ |
| RF-32-AC-3 | APPI o consultor intenta cerrar fase: 403 | `/parques/{parque_id}/fases/{fase}` | PATCH | ✅ |
| RF-32-AC-4 | Avance por excepción sin motivo: rechazo | `/parques/{parque_id}/fases/{fase}` | PATCH | ✅ |
| RF-32-AC-5 | Avance por excepción con motivo, usuario, fecha y bitácora | `/parques/{parque_id}/fases/{fase}` | PATCH | ✅ |
| RF-33-AC-1 | Evaluación de Desempeño con folio consecutivo; fase completada | `/parques/{parque_id}/evaluaciones-desempeno`<br>`/evaluaciones-desempeno/{evaluacion_id}`<br>`/evaluaciones-desempeno/{evaluacion_id}/archivo`<br>`/parques/{parque_id}/evaluaciones-desempeno` | POST<br>GET<br>GET<br>GET | ✅ |
| RF-33-AC-2 | Evaluación sin Opinión final: rechazo | `/parques/{parque_id}/evaluaciones-desempeno` | POST | ✅ |
| RF-33-AC-3 | Consultor sin el parque registra evaluación: 403 | `/parques/{parque_id}/evaluaciones-desempeno` | POST | ✅ |
| RF-34-AC-1 | Lista de usuarios APPI con contacto principal | `/parques/{parque_id}/usuarios` | GET | ✅ |
| RF-34-AC-2 | Cambiar contacto principal quita la marca al anterior | `/parques/{parque_id}/contacto-principal` | PUT | ✅ |
| RF-34-AC-3 | Sin contacto principal: aviso a todos los APPI y alerta a Coordinación | `/parques/{parque_id}` | GET | ⚠️ parcial (c) |
| RF-35-AC-1 | Descarga de evidencia queda en bitácora | `/evidencias/{evidencia_id}/contenido` | GET | ✅ |
| RF-35-AC-2 | Acceso denegado (403) queda en bitácora | `/parques/{parque_id}` | GET | ✅ |
| RF-35-AC-3 | Bitácora filtrada por parque y mes, más reciente primero | `/eventos-bitacora` | GET | ✅ |
| RF-35-AC-4 | APPI, consultor o administrador técnico consultan bitácora: 403 | `/eventos-bitacora` | GET | ✅ |
| RF-36-AC-1 | Consultor deja recomendación en criterio pendiente | `/parques/{parque_id}/criterios/{criterio_id}/recomendaciones`<br>`/parques/{parque_id}/criterios/{criterio_id}/recomendaciones` | POST<br>GET | ✅ |
| RF-36-AC-2 | Recomendación no cambia estados ni aparece como observación | `/parques/{parque_id}/criterios/{criterio_id}/recomendaciones`<br>`/evidencias/{evidencia_id}/observaciones`<br>`/parques/{parque_id}/criterios/{criterio_id}` | POST<br>GET<br>GET | ✅ |
| RF-37-AC-1 | Registrar visita de validación con hallazgos | (sin endpoint en v1) | — | ❌ fuera de alcance |
| RF-37-AC-2 | Cerrar hallazgo con acción correctiva | (sin endpoint en v1) | — | ❌ fuera de alcance |
| RF-37-AC-3 | Fotos de la visita con validaciones de RF-06 | (sin endpoint en v1) | — | ❌ fuera de alcance |
| RF-38-AC-1 | APPI inicia renovación; estado en renovación | (sin endpoint en v1) | — | ❌ fuera de alcance |
| RF-38-AC-2 | Vencimiento sin renovar ni prórroga: vencido | (sin endpoint en v1) | — | ❌ fuera de alcance |
| RF-38-AC-3 | Prórroga sin motivo o fecha: rechazo | (sin endpoint en v1) | — | ❌ fuera de alcance |
| RF-39-AC-1 | Avisos de vencimiento de constancia REPSE a 60, 30 y 0 días | (sin endpoint en v1) | — | ❌ fuera de alcance |
| RF-39-AC-2 | Sin aviso si se subió versión nueva vigente | (sin endpoint en v1) | — | ❌ fuera de alcance |

### Criterios parciales: qué falta y por qué

**(a) RF-09-AC-2, RF-09-AC-3 y RF-30-AC-2. La revisión diaria de plazos no es un endpoint.** Lo que dispara la marca de atraso es un proceso programado del backend que corre una vez al día a las 00:00 de Ciudad de México (RNF-11), no una solicitud de un usuario. La API solo expone el resultado: el campo `atrasado` en `GET /parques`, `GET /parques/{parque_id}/criterios` y `GET /parques/{parque_id}/compromisos?atrasado=true`. Decidí no agregar un endpoint tipo `POST /revisiones-plazos` para disparar la revisión a mano: sería una operación administrativa que ningún requerimiento pide y que alguien podría usar para alterar fechas de atraso. Las pruebas de estos tres criterios llaman directamente a la función del proceso con reloj simulado, igual que las pruebas de RF-26 en el Sprint 1. **Veredicto: el requerimiento está en el alcance del backend y fuera del alcance de la API.**

**(b) RF-16-AC-4. Falta el concepto de "ciclo de renovación".** El endpoint de calificación ya aplica la regla de RF-17 (sin análisis vigente no hay "cumplido"). Lo que falta es saber cuándo empieza un ciclo de renovación, y eso lo define RF-38, que tiene prioridad Posterior. Con el contrato actual la vigencia de una revisión solo distingue generaciones. **Veredicto: falta un endpoint, pero llega con RF-38.** Cuando entre RF-38, agregar `POST /parques/{parque_id}/renovaciones` no rompe nada de v1.

**(c) RF-34-AC-3. El envío a todos los APPI es del servicio de notificaciones.** La API cubre la mitad visible: `GET /parques/{parque_id}` devuelve `contacto_principal: null` y Coordinación ve que el parque no tiene contacto. Que el aviso se mande a todos los APPI activos mientras no haya contacto es una regla del servicio de correo (RNF-12), sin endpoint. **Veredicto: fuera del alcance de la API.** Se prueba en el servicio de notificaciones.

### Criterios fuera de alcance

Los 19 criterios marcados ❌ son de RF-18, RF-19, RF-20, RF-22, RF-37, RF-38 y RF-39. El SRS (sección 1.2) los deja fuera del entregable de 12 semanas: auditorías del subestándar 1.4, avisos de vencimiento del distintivo, de auditoría interna y de documentos críticos, reporte para asociados, visitas de validación y renovación del distintivo. No son huecos del diseño; están fuera por decisión de alcance, y v1 no reserva rutas para ellos. RF-22-AC-2 ya nombra `GET /reporte-asociados`. Cuando se construya, la ruta va a ser `GET /reportes-asociados`, en plural como el resto, y entra como adición sin romper v1.

### Endpoints sin criterio de aceptación

Recorrí también la dirección contraria: endpoints que no satisfacen ningún criterio. Si no tienen justificación, son alcance que nadie pidió. Hay 10 operaciones con `x-acceptance-criteria: []`, y cada una lleva en el YAML una extensión `x-sin-criterio` que explica por qué existe:

| Operación | Por qué existe |
|---|---|
| `GET /health` | Habilitador técnico del Sprint 1 (T-02) y del monitoreo de RNF-08. |
| `POST /activaciones` | RF-03-AC-1 deja la cuenta "pendiente de activación"; sin este endpoint nadie podría activarla. |
| `GET /usuarios`, `GET /usuarios/{usuario_id}` | Pantallas de administración que soportan RF-03, RF-10 y RF-29. |
| `GET /desarrolladores`, `POST /desarrolladores`, `GET /desarrolladores/{desarrollador_id}` | RF-02-AC-1 pide el desarrollador del parque y RF-23 agrupa por desarrollador; hace falta que exista como entidad. |
| `GET /generaciones` | Lista para elegir generación en el alta de parque (RF-28-AC-3). |
| `DELETE /revisiones-analisis-riesgos/{revision_id}/documento` | La descripción de RF-16 dice que la APPI "puede eliminarlo", pero ningún criterio lo cubre. **Es un hueco del SRS:** propongo agregar RF-16-AC-5 en la siguiente versión. |
| `DELETE /parques/{parque_id}/compromisos/{criterio_id}` | RF-09 no dice cómo corregir un compromiso registrado por error (hallazgo R-05 de la revisión). |

### Cambios que este contrato pide en otros documentos

El contrato manda sobre el código y las pruebas, pero aquí también corrige rutas que el SRS y el Sprint 1 habían escrito antes de diseñar la API:

| Documento | Dice | El contrato usa | Motivo |
|---|---|---|---|
| SRS, RF-01-AC-2 | `POST /catalogo/versiones` | `POST /versiones-catalogo` | Colección en plural y sin namespace singular (revisión REST, O-2). |
| SRS, RF-04-AC-2 | `POST /autoevaluaciones` | `PUT /parques/{parque_id}/autoevaluaciones/{criterio_id}` | Clave natural y PUT idempotente (O-3). |
| SRS, RF-25-AC-2 | `GET /catalogo/exportar` | `GET /versiones-catalogo/{version_id}/archivo-maestro` | Verbo en la ruta, y con varias versiones vivas "el catálogo" era ambiguo (O-2). |
| SRS, RF-32-AC-3 | `POST /parques/{id}/fases/{fase}/cierre` | `PATCH /parques/{parque_id}/fases/{fase}` | Transición de estado (O-1). |
| SRS, RF-35-AC-4 | `GET /bitacora` | `GET /eventos-bitacora` | Colección en plural (O-2). |
| Sprint 1, T-08 y T-10 | `POST /auth/login`, `POST /auth/logout` | `POST /sesiones`, `DELETE /sesiones/actual` | La sesión es un recurso que se crea y se revoca (O-1). |
| Sprint 1, T-11 | `POST /auth/recuperacion`, `POST /auth/restablecimiento` | `POST /solicitudes-recuperacion`, `POST /restablecimientos-contrasena` | Sustantivos en plural (O-2). |

T-08, T-10 y T-11 siguen abiertas en el Sprint 1 (termina el 18 de octubre), así que el cambio de ruta les cuesta minutos. Los criterios de done de esas tareas no cambian: siguen pidiendo los mismos mensajes, códigos y tiempos. `POST /evidencias/{id}/observaciones` (RF-05-AC-3) y `GET /evidencias/{id}/contenido` (RF-07-AC-3) se conservan tal como las nombra el SRS.

## Sección B. Decisiones de diseño

### 1. ¿Por qué estos recursos y endpoints? ¿Qué quedó fuera?

**Los recursos salen del dominio, no de las pantallas.** Cada sustantivo con identidad propia en el SRS es un recurso: parque, evidencia, versión del catálogo, generación, Opinión, dictamen, sesión de comité, revisión del análisis de riesgos. Lo que en el SRS es una transición de estado (aceptar una evidencia, cerrar una fase, firmar un dictamen) no se volvió ruta con verbo. Se modeló de una de dos formas: como PATCH al estado del recurso, o como creación de un registro cuando la transición tiene datos propios que el SRS obliga a conservar (calificación con motivo, cambio de tipo de PI con historial, firma del Director General). El contrato queda en 57 rutas, 86 operaciones y 19 grupos. Los recursos principales son `parques`, `evidencias`, `versiones-catalogo`, `usuarios` y `generaciones`; casi todo lo demás cuelga del parque.

**El parque es la raíz del expediente.** Las colecciones que pertenecen a un parque (evidencias, criterios, compromisos, Opiniones, dictámenes, fases) se crean y se listan bajo `/parques/{parque_id}/…`. El motivo es de seguridad: RNF-01 exige 0 accesos cruzados entre parques, y con el `parque_id` en la ruta la dependencia `requiere_rol` de T-12 decide el permiso antes de tocar la base. Los elementos que ya tienen identificador global (`/evidencias/{evidencia_id}`, `/dictamenes/{dictamen_id}`, `/opiniones/{opinion_id}`) se operan en ruta corta. Es anidación superficial: rutas de un solo nivel bajo el parque, en vez de `/parques/{id}/criterios/{id}/evidencias/{id}/versiones/{n}`.

**"Consultor asignado" y "consultor de comité" no son roles.** El SRS los lista como roles en RF-03, pero RF-13-AC-1 y AC-2 suponen que la misma persona es consultora asignada de un parque y de comité en otro. Si fueran roles distintos, Ana Ruiz necesitaría dos cuentas y la regla de conflicto de interés de RF-13-AC-2 no podría compararlas. En el contrato hay un rol `consultor`, y "asignado" y "de comité" son relaciones con un parque (`asignaciones-consultor`, `sesiones-comite`).

**La sesión es JWT, pero vive en el servidor.** La actividad pide seguridad Bearer con JWT, y en el Sprint 1 ya habíamos descartado el JWT sin estado: no permite invalidar el token al cerrar sesión (RF-26-AC-5) ni expirar por inactividad (RF-26-AC-6). El contrato usa los dos: el token es un JWT firmado con un claim `sid`, y el backend además verifica en la tabla `sesiones` que esa sesión no esté revocada y que tenga uso en los últimos 60 minutos. El JWT ahorra una consulta para identificar al usuario; la tabla da el control que piden los criterios.

**Los archivos no pasan por la API para leerse.** Para subir sí pasan por ella; la razón está en ADR-002 de S04-A1. Abrir una evidencia devuelve una URL firmada de 5 minutos (RNF-15) después de validar el permiso y registrar la descarga en la bitácora (RF-35-AC-1). El backend recibe el multipart porque tiene que validar tamaño y formato (RF-06) antes de aceptar nada.

**Quedó fuera:**

- Los siete RF con prioridad Posterior (Sección A).
- Los procesos programados (revisión diaria de plazos) y el envío de correos. Son componentes del backend, no operaciones de la API.
- Las "herramientas técnicas de administración" del Administrador técnico (RF-03-AC-3). Son de infraestructura (despliegues, respaldos de RNF-13) y no se exponen en la API de negocio. En v1 el Administrador técnico no pasa `requiere_rol` en ningún endpoint, y eso es justo lo que piden RNF-02 y RF-35-AC-4.
- La solicitud de incorporación en línea, la excepción de NA pedida por la APPI y la migración de expedientes, porque el SRS ya las sacó (conflictos C-12 y C-13, sección 1.2).

### 2. Patrones de diseño de API: qué incluí y qué excluí

| Patrón | Decisión | Por qué |
|---|---|---|
| **Versionado** | Incluido, en la URL: `/api/v1`. | Es el más simple de operar con un `APIRouter(prefix="/api/v1")` de FastAPI y se ve en cada log. La regla está en `info.description`: agregar endpoints o campos opcionales no cambia la versión mayor; quitar o renombrar sí. Descarté el versionado por cabecera porque obliga a cada cliente y a cada prueba a acordarse de mandarla, y no tenemos más que un cliente. |
| **Paginación** | Incluida solo en `usuarios`, `parques`, `evidencias` y `eventos-bitacora`, con `pagina` y `por_pagina` (máximo 200) y respuesta `{datos, paginacion}` con `total`. | Son las colecciones que crecen sin tope. RNF-06 habla de expedientes con 1,500 evidencias y la bitácora crece con cada operación. Las colecciones acotadas por parque (9 fases, 2 Opiniones, menos de 300 criterios) se devuelven completas: paginarlas obliga a la pantalla a pedir varias páginas para dibujar un expediente. Elegí offset y no cursor porque la interfaz necesita el total para mostrar "página 3 de 30" y los volúmenes del SRS son chicos. **Riesgo conocido:** si la bitácora pasa de cientos de miles de registros, el offset se vuelve lento; el cambio a cursor sería un parámetro nuevo y no rompe v1. |
| **Filtrado** | Incluido, con parámetros de consulta por igualdad: `estado`, `region`, `atrasado`, `criterio_id`, rango `desde` y `hasta` en bitácora. | Cada filtro sale de un criterio: RF-35-AC-3 filtra la bitácora por parque y mes, y RF-09-AC-2 pide el listado de atrasos. Excluí un lenguaje de consulta genérico (`?filter=estado eq 'x'`) porque abre consultas que nadie pidió y complica la autorización por parque. |
| **Ordenamiento** | Excluido como parámetro; el orden es fijo y está documentado. | RF-35-AC-3 exige "del más reciente al más antiguo". Con un `orden` libre, una prueba podría pasar con un orden que el criterio no acepta. |
| **Errores estándar** | Incluido: `application/problem+json` (RFC 9457) con `type` estable por regla y `detail` con el mensaje exacto del SRS. | El SRS fija decenas de mensajes en español. Con `type` estable las pruebas de S09 comparan un identificador y no texto, y el texto se puede corregir sin romperlas. |
| **400 / 409 / 422** | 400 = JSON mal formado; 422 = validación o regla de negocio; 409 = solo duplicados (segunda Opinión final, dictamen ya firmado, correo repetido, sesión de comité ya abierta). | El revisor propuso 409 también para transiciones inválidas (aceptar algo que no está "enviada", borrar una evidencia aceptada). Lo rechacé: el SRS trata esas situaciones como reglas de negocio con mensaje propio, igual que las precondiciones de RF-12 o RF-14. Un solo código para "rompiste una regla" es más fácil de manejar en el frontend. 409 queda para lo que de verdad es un choque con un recurso existente. |
| **Location en 201** | Incluido donde el recurso creado tiene un GET propio. | Donde no lo tiene (calificaciones, observaciones, cambios de tipo de PI) el 201 devuelve el recurso en el cuerpo y no apunta a una URL que no existe. |
| **Idempotencia** | PUT solo con clave natural; DELETE idempotente (repetirlo responde 204); PATCH de transición repetido responde 200 sin cambios. | Detalle en `revision_rest.md`. |
| **HATEOAS** | Excluido. | El único cliente es nuestro frontend y lo construimos nosotros. Los enlaces en cada respuesta duplicarían en el JSON lo que ya dice el contrato. |
| **Control de concurrencia (ETag / If-Match)** | Excluido de v1. | Cada parque tiene un solo consultor asignado y las transiciones de estado se validan contra el estado actual dentro de una transacción. Si el piloto muestra ediciones simultáneas (dos APPI en la autoevaluación, por ejemplo), se agrega `If-Match` como cabecera opcional. |
| **Llaves de idempotencia en POST** | Excluido. | El riesgo real es la carga de evidencias desde el celular con mala señal (RNF-09), donde un reintento duplicaría la evidencia. Lo dejo anotado como mejora para S05-S06: una cabecera `Idempotency-Key` opcional en `POST /parques/{parque_id}/evidencias`. |

### 3. ¿Dónde propuso el agente algo que no seguía buenas prácticas REST? ¿Cómo lo detecté?

Trabajé con dos pasadas de agente con contextos separados. Los prompts están en `evidencia_agente/prompts_agentes.md`. La primera generó `evidencia_agente/openapi_v0.yaml`; la segunda revisó ese v0 contra los principios REST y produjo 21 hallazgos (`evidencia_agente/revision_rest_agente.md`). El detalle de cada corrección está en `revision_rest.md`. Aquí van las fallas del agente y cómo las encontré.

**El agente generador copió rutas del SRS y del Sprint 1 al pie de la letra.** El v0 tenía `POST /auth/login`, `/catalogo/exportar`, `/evidencias/{id}/aceptar`, `/criterios/{id}/reabrir`, `/dictamenes/{id}/firmar`, `/usuarios/{id}/baja` y `/parques/{id}/fases/{fase}/cierre`. Son verbos en la ruta: llamadas RPC con forma de URL. El agente las tomó como requisito porque el SRS o las tareas las nombraban, cuando esos documentos se escribieron antes de diseñar la API. **Cómo lo detecté:** revisé cada ruta del v0 con una sola pregunta: ¿el último segmento es un sustantivo? Siete no lo eran.

**El agente usó PUT donde la operación crea algo cada vez.** `PUT /parques/{id}/tipo-pi` cerraba el historial y creaba un registro nuevo en cada llamada. Si el navegador reintenta, quedan dos cambios de tipo de PI y dos eventos en la bitácora. **Cómo lo detecté:** pregunté por cada PUT y cada DELETE "¿qué pasa si esta solicitud llega dos veces?". El revisor lo encontró por el mismo camino (hallazgo R-02).

**Al revés, usó POST donde había clave natural.** `POST /autoevaluaciones` y `POST /parques/{id}/plan-trabajo` permitían dos respuestas o dos compromisos para el mismo criterio y no tenían forma de corregirlos. El SRS dice que hay una respuesta y un compromiso por criterio, así que el criterio es la llave y PUT es el verbo correcto.

**El revisor también se equivocó, y no acepté todo lo que propuso.** Tomó las rutas del SRS como intocables y en varios hallazgos recomendó conservar `POST /autoevaluaciones`, `/catalogo/exportar` y `/fases/{fase}/cierre` "porque el SRS las nombra". Es el mismo sesgo del generador: tratar el documento como más fuerte que el principio. En un enfoque spec-first el contrato de API es el que fija las rutas, y si el SRS escribió una antes, se corrige el SRS (tabla de la Sección A). También rechacé tres recomendaciones con razón técnica:

- **413 y 415 para archivos.** El límite de tamaño es configurable y el SRS fija el mensaje para cada caso. 413 suele mandarlo el proxy antes de llegar a la aplicación y sin nuestro mensaje.
- **303 en vez de JSON para la URL firmada.** Con `fetch` y cabecera `Authorization`, un redireccionamiento a otro origen pierde la cabecera o se bloquea por CORS. La SPA necesita la URL en el JSON.
- **`oneOf` por cada uno de los seis roles.** El SRS exige mensajes exactos, como "Un usuario no puede ser APPI y Consultor del mismo parque", que un error genérico de esquema no da. Esa regla la valida el negocio.

**Lo que ninguno de los dos agentes vio: errores de sintaxis.** El v0 tenía 5 errores de especificación: `nullable: true` junto a `allOf` sin `type`, que OpenAPI 3.0 no permite. El revisor no los mencionó y `swagger-cli` tampoco los marca. Los encontró `redocly lint`. Al corregir el final aparecieron otros 6, por comas dentro de descripciones en mapas YAML en línea. **Lección:** la revisión de un agente no sustituye a un validador. Los dos validadores corren sobre el archivo final sin errores.

**Limitación de fondo de los agentes.** Ninguno de los dos cuestionó la decisión de seguridad más importante del contrato. Si se pide "Bearer con JWT", el agente genera `bearerFormat: JWT` y sigue, aunque un JWT sin estado no cumpla RF-26-AC-5 ni AC-6. Ese problema lo encontramos en el Sprint 1 leyendo los criterios contra la propuesta del agente, y el contrato lo resuelve con la sesión en servidor descrita en la decisión 1.
