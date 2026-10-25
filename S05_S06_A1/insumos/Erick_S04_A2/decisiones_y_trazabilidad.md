## Sección A — Trazabilidad entre especificación y criterios de aceptación

| ID | Descripción breve | Endpoint | Método | Estado de cobertura |
|---|---|---|---|---|
| RF-01-AC-1 | Carga CSV y activa catálogo | `/catalogo/versiones` | POST | Cubierto |
| RF-01-AC-2 | Restringe carga de catálogo por rol | `/catalogo/versiones` | POST | Cubierto |
| RF-01-AC-3 | Muestra versión de catálogo del expediente | `/parques/{parqueId}` | GET | Cubierto |
| RF-01-AC-4 | Rechaza CSV inválido con fila y columna | `/catalogo/versiones` | POST | Cubierto |
| RF-01-AC-5 | Conserva versión anterior para generaciones previas | `/catalogo/versiones` | POST | Parcial (documentación adicional: no define explícitamente inmutabilidad por generación) |
| RF-02-AC-1 | Alta de parque activo | `/parques` | POST | Cubierto |
| RF-02-AC-2 | Valida tipo de PI | `/parques` | POST | Cubierto |
| RF-02-AC-3 | Valida región | `/parques` | POST | Cubierto |
| RF-03-AC-1 | Alta APPI pendiente e invitación | `/usuarios` | POST | Parcial (proceso interno: envío de invitación no está especificado) |
| RF-03-AC-2 | Impide roles incompatibles en un parque | `/usuarios` | POST | Cubierto |
| RF-03-AC-3 | Alta de administrador técnico sin acceso de negocio | `/usuarios` | POST | Parcial (documentación adicional: restricciones concretas del rol no se detallan) |
| RF-04-AC-1 | Lista criterios O y R aplicables | `/parques/{parqueId}/autoevaluaciones` | GET | Cubierto |
| RF-04-AC-2 | Rechaza autoevaluación de criterio NA | `/autoevaluaciones` | POST | Cubierto |
| RF-05-AC-1 | Crea evidencia enviada y cambia criterio a revisión | `/evidencias` | POST | Parcial (proceso interno: transición automática del criterio no se documenta) |
| RF-05-AC-2 | Observa evidencia y notifica a APPI | `/evidencias/{evidenciaId}/observaciones` | POST | Parcial (proceso interno: notificación no está especificada) |
| RF-05-AC-3 | Restringe observación a consultor asignado | `/evidencias/{evidenciaId}/observaciones` | POST | Cubierto |
| RF-05-AC-4 | Nueva versión regresa evidencia observada a enviada | `/evidencias` | POST | Parcial (documentación adicional: relación de nueva versión no se define en la solicitud) |
| RF-05-AC-5 | Guarda metadatos y referencia de evidencia | `/evidencias` | POST | Parcial (documentación adicional: referencia al almacenamiento de objetos no se expone) |
| RF-05-AC-6 | Consulta historial y versión vigente | `/evidencias/{evidenciaId}` | GET | Cubierto |
| RF-05-AC-7 | Vincula un archivo a varios criterios | `/evidencias` | POST | Cubierto |
| RF-05-AC-8 | Acepta carga parcial de archivos | `/evidencias` | POST | Cubierto |
| RF-05-AC-9 | Elimina lógicamente evidencia enviada y audita | `/evidencias/{evidenciaId}` | DELETE | Parcial (documentación adicional: evento de bitácora de eliminación no se especifica) |
| RF-05-AC-10 | Impide eliminar evidencia aceptada | `/evidencias/{evidenciaId}` | DELETE | Cubierto |
| RF-06-AC-1 | Rechaza archivo superior al límite | `/evidencias` | POST | Cubierto |
| RF-06-AC-2 | Acepta archivo dentro del límite | `/evidencias` | POST | Cubierto |
| RF-06-AC-3 | Acepta archivo igual al límite | `/evidencias` | POST | Cubierto |
| RF-06-AC-4 | Rechaza video | `/evidencias` | POST | Cubierto |
| RF-06-AC-5 | Rechaza formato no permitido | `/evidencias` | POST | Cubierto |
| RF-06-AC-6 | Aplica límite configurado | `/configuracion/cargas`, `/evidencias` | PATCH, POST | Cubierto |
| RF-06-AC-7 | Rechaza límite mayor a 100 MB | `/configuracion/cargas` | PATCH | Cubierto |
| RF-07-AC-1 | Muestra estados sin abrir evidencia restringida | `/parques/{parqueId}/expediente` | GET | Cubierto |
| RF-07-AC-2 | Permite abrir evidencia administrativa autorizada | `/evidencias/{evidenciaId}/contenido` | GET | Cubierto |
| RF-07-AC-3 | Niega acceso AMPIP a evidencia de seguridad | `/evidencias/{evidenciaId}/contenido` | GET | Cubierto |
| RF-08-AC-1 | Calcula cumplimiento de obligatorios | `/parques/{parqueId}/expediente` | GET | Parcial (documentación adicional: fórmula de cálculo no se define en OpenAPI) |
| RF-08-AC-2 | Calcula avance general | `/parques/{parqueId}/expediente` | GET | Parcial (documentación adicional: fórmula de cálculo no se define en OpenAPI) |
| RF-08-AC-3 | Devuelve no aplicable sin obligatorios | `/parques/{parqueId}/expediente` | GET | Parcial (documentación adicional: representación de “No aplica” no se define) |
| RF-08-AC-4 | Calcula cumplimiento de recomendados | `/parques/{parqueId}/expediente` | GET | Parcial (documentación adicional: fórmula de cálculo no se define en OpenAPI) |
| RF-08-AC-5 | Calcula global sin promedio simple | `/parques/{parqueId}/expediente` | GET | Parcial (documentación adicional: regla de agregación no se define) |
| RF-09-AC-1 | Crea plan de trabajo por criterio | `/parques/{parqueId}/planes-trabajo` | POST | Cubierto |
| RF-09-AC-2 | Marca atraso diario tras vencimiento | `x-background-processes` | Interno | Cubierto |
| RF-09-AC-3 | No marca atraso antes del vencimiento | `x-background-processes` | Interno | Cubierto |
| RF-09-AC-4 | Valida responsable APPI del parque | `/parques/{parqueId}/planes-trabajo` | POST | Cubierto |
| RF-10-AC-1 | Asigna consultor vigente | `/parques/{parqueId}/asignacion-consultor` | PUT | Cubierto |
| RF-10-AC-2 | Reasigna y conserva historial | `/parques/{parqueId}/asignacion-consultor` | PUT | Cubierto |
| RF-10-AC-3 | Impide asignación por APPI | `/parques/{parqueId}/asignacion-consultor` | PUT | Cubierto |
| RF-11-AC-1 | Cambia tipo, conserva historial y recalcula | `/parques/{parqueId}` | PATCH | Parcial (documentación adicional: recálculo y cierre de historial no se detallan) |
| RF-11-AC-2 | Conserva cumplimiento anterior separado | `/parques/{parqueId}` | PATCH | Parcial (documentación adicional: cálculo histórico no se define) |
| RF-11-AC-3 | Rechaza tipo de PI inválido | `/parques/{parqueId}` | PATCH | Parcial (documentación adicional: regla de validación de cambio no se describe) |
| RF-11-AC-4 | Convierte NA a pendiente al cambiar tipo | `/parques/{parqueId}` | PATCH | Parcial (proceso interno: transición automática no se especifica) |
| RF-11-AC-5 | Exige motivo y audita cambio de tipo | `/parques/{parqueId}` | PATCH | Parcial (documentación adicional: auditoría del cambio no se define) |
| RF-11-AC-6 | Conserva evidencias al pasar criterio a NA | `/parques/{parqueId}` | PATCH | Parcial (proceso interno: conservación y exclusión del cálculo no se especifican) |
| RF-12-AC-1 | Emite opinión intermedia con precondiciones | `/parques/{parqueId}/opiniones-cumplimiento` | POST | Parcial (documentación adicional: precondiciones y transición de fase no se detallan) |
| RF-12-AC-2 | Restringe opinión al consultor asignado | `/parques/{parqueId}/opiniones-cumplimiento` | POST | Parcial (documentación adicional: autorización por asignación no se detalla) |
| RF-12-AC-3 | Impide segunda opinión final | `/parques/{parqueId}/opiniones-cumplimiento` | POST | Parcial (documentación adicional: unicidad por generación no se define) |
| RF-12-AC-4 | Exige política cumplida | `/parques/{parqueId}/opiniones-cumplimiento` | POST | Parcial (documentación adicional: precondición no se define) |
| RF-12-AC-5 | Exige análisis de riesgos vigente | `/parques/{parqueId}/opiniones-cumplimiento` | POST | Parcial (documentación adicional: precondición no se define) |
| RF-12-AC-6 | Exige resultado favorable o no favorable | `/parques/{parqueId}/opiniones-cumplimiento` | POST | Parcial (documentación adicional: obligatoriedad condicional no se define) |
| RF-13-AC-1 | Abre comité con acceso temporal de solo lectura | `/parques/{parqueId}/sesiones-comite` | POST | Parcial (documentación adicional: alcance de lectura y exclusión de riesgos no se detallan) |
| RF-13-AC-2 | Impide conflicto de interés del consultor | `/parques/{parqueId}/sesiones-comite` | POST | Parcial (documentación adicional: validación contra asignación vigente no se define) |
| RF-13-AC-3 | Retira acceso al cerrar sesión de comité | `/sesiones-comite/{sesionId}` | DELETE | Cubierto |
| RF-14-AC-1 | Firma dictamen y activa vigencia | `/dictamenes/{dictamenId}/firma` | POST | Parcial (documentación adicional: creación o actualización del distintivo no se define) |
| RF-14-AC-2 | Restringe captura de dictamen | `/parques/{parqueId}/dictamenes` | POST | Parcial (documentación adicional: roles autorizados no se detallan) |
| RF-14-AC-3 | Rechaza otorgar sin 100 % obligatorio | `/parques/{parqueId}/dictamenes` | POST | Parcial (documentación adicional: precondición de cálculo no se define) |
| RF-14-AC-4 | Rechaza otorgar con evaluación sin revisar | `/parques/{parqueId}/dictamenes` | POST | Parcial (documentación adicional: precondición no se define) |
| RF-14-AC-5 | Rechaza otorgar sin opinión final favorable | `/parques/{parqueId}/dictamenes` | POST | Parcial (documentación adicional: precondición no se define) |
| RF-14-AC-6 | Conserva dictamen como borrador | `/parques/{parqueId}/dictamenes` | POST | Parcial (documentación adicional: visibilidad del comité no se define) |
| RF-14-AC-7 | Restringe firma al Director General | `/dictamenes/{dictamenId}/firma` | POST | Parcial (documentación adicional: autorización específica no se detalla) |
| RF-14-AC-8 | Permite no otorgar sin precondiciones | `/parques/{parqueId}/dictamenes` | POST | Parcial (documentación adicional: reglas condicionales no se definen) |
| RF-15-AC-1 | Abre comité con expediente válido | `/parques/{parqueId}/sesiones-comite` | POST | Parcial (documentación adicional: validación de expediente no se define) |
| RF-15-AC-2 | Rechaza comité con criterios en revisión | `/parques/{parqueId}/sesiones-comite` | POST | Parcial (documentación adicional: regla de autoevaluación revisada no se define) |
| RF-15-AC-3 | Rechaza comité sin opinión final favorable | `/parques/{parqueId}/sesiones-comite` | POST | Parcial (documentación adicional: precondición no se define) |
| RF-16-AC-1 | Registra revisión vigente de análisis de riesgos | `/parques/{parqueId}/analisis-riesgos` | POST | Cubierto |
| RF-16-AC-2 | Permite documento opcional restringido | `/parques/{parqueId}/analisis-riesgos`, `/evidencias/{evidenciaId}/contenido` | POST, GET | Cubierto |
| RF-16-AC-3 | Niega apertura AMPIP y registra intento | `/evidencias/{evidenciaId}/contenido` | GET | Parcial (documentación adicional: bitácora de acceso denegado no se especifica) |
| RF-16-AC-4 | Invalida revisión al iniciar renovación | `/parques/{parqueId}/analisis-riesgos` | POST | Parcial (proceso interno: vigencia por ciclo de renovación no se define) |
| RF-17-AC-1 | Bloquea cumplimiento sin análisis vigente | `/evaluaciones-criterio/{evaluacionId}` | PATCH | Parcial (documentación adicional: precondición por estándar no se define) |
| RF-17-AC-2 | Permite cumplimiento con análisis vigente | `/evaluaciones-criterio/{evaluacionId}` | PATCH | Parcial (documentación adicional: validación de vigencia no se define) |
| RF-17-AC-3 | No bloquea carga de evidencia de estándar 6 | `/evidencias` | POST | Parcial (documentación adicional: excepción por estándar no se define) |
| RF-18-AC-1 | Registra auditoría interna | `/auditorias` | POST | Cubierto |
| RF-18-AC-2 | Exige notificación corporativa en auditoría externa | `/auditorias` | POST | Parcial (documentación adicional: obligatoriedad condicional no se define) |
| RF-19-AC-1 | Envía aviso seis meses antes | `x-background-processes` | Interno | Parcial (proceso interno: destinatarios y cálculo de seis meses no se detallan) |
| RF-19-AC-2 | Envía aviso tres meses antes | `x-background-processes` | Interno | Parcial (proceso interno: destinatarios y cálculo de tres meses no se detallan) |
| RF-19-AC-3 | Omite aviso tras renovación | `x-background-processes` | Interno | Parcial (proceso interno: relación entre renovación y avisos no se define) |
| RF-19-AC-4 | Configura plazos de aviso | Sin endpoint | N/A | No cubierto — Fuera del alcance actual (funcionalidad futura: la configuración de plazos de aviso se implementará en una versión posterior al semestre) |
| RF-19-AC-5 | Evita duplicar aviso del mismo plazo | `x-background-processes` | Interno | Parcial (proceso interno: deduplicación no se documenta) |
| RF-20-AC-1 | Avisa auditoría interna pendiente | `x-background-processes` | Interno | Parcial (proceso interno: cálculo y envío del aviso no se detallan) |
| RF-20-AC-2 | Omite aviso si ya hay auditoría registrada | `x-background-processes` | Interno | Parcial (proceso interno: supresión del aviso no se define) |
| RF-21-AC-1 | Genera reporte mensual por generación | `/reportes/mensual` | GET | Cubierto |
| RF-21-AC-2 | Restringe reporte mensual a AMPIP | `/reportes/mensual` | GET | Cubierto |
| RF-22-AC-1 | Genera reporte agregado por región | `/reporte-asociados` | GET | Cubierto |
| RF-22-AC-2 | Omite porcentaje y ranking individual | `/reporte-asociados` | GET | Cubierto |
| RF-23-AC-1 | Lista parques visibles del gerente corporativo | `/parques` | GET | Cubierto |
| RF-23-AC-2 | Impide acciones de gerente corporativo | `/evidencias`, `/evidencias/{evidenciaId}/observaciones` | POST, POST | Cubierto |
| RF-24-AC-1 | Define y consulta evidencia suficiente | `/catalogo/criterios/{criterioId}` | PATCH, GET | Cubierto |
| RF-24-AC-2 | Restringe edición de evidencia suficiente | `/catalogo/criterios/{criterioId}` | PATCH | Cubierto |
| RF-25-AC-1 | Consulta criterio aplicable individual | `/catalogo/criterios/{criterioId}` | GET | Cubierto |
| RF-25-AC-2 | Restringe exportación a APPI | `/catalogo/exportar` | GET | Cubierto |
| RF-25-AC-3 | Exporta catálogo maestro a AMPIP | `/catalogo/exportar` | GET | Cubierto |
| RF-25-AC-4 | Restringe exportación a consultor | `/catalogo/exportar` | GET | Cubierto |
| RF-26-AC-1 | Inicia sesión con expiración por inactividad | `/auth/sesiones` | POST | Parcial (documentación adicional: aplicación de expiración por inactividad no se define) |
| RF-26-AC-2 | Rechaza credenciales incorrectas | `/auth/sesiones` | POST | Cubierto |
| RF-26-AC-3 | Bloquea tras cinco intentos fallidos | `/auth/sesiones` | POST | Parcial (proceso interno: conteo y bloqueo temporal no se especifican) |
| RF-26-AC-4 | Recupera contraseña con token de un uso | `/auth/recuperaciones-contrasena`, `/auth/recuperaciones-contrasena/{token}` | POST, POST | Parcial (documentación adicional: vigencia de 30 minutos no se define) |
| RF-26-AC-5 | Invalida token al cerrar sesión | `/auth/sesiones/actual` | DELETE | Cubierto |
| RF-26-AC-6 | Rechaza token tras inactividad | Seguridad global | N/A | Cubierto |
| RF-27-AC-1 | Acepta evidencia enviada | `/evidencias/{evidenciaId}/aceptacion` | PUT | Parcial (documentación adicional: validación del consultor asignado no se detalla) |
| RF-27-AC-2 | Califica criterio cumplido | `/evaluaciones-criterio/{evaluacionId}` | PATCH | Parcial (documentación adicional: exigencia de evidencia aceptada no se define) |
| RF-27-AC-3 | Bloquea criterio 3 sin análisis vigente | `/evaluaciones-criterio/{evaluacionId}` | PATCH | Parcial (documentación adicional: precondición por estándar no se define) |
| RF-27-AC-4 | Cambia pendiente a revisión al subir evidencia | `/evidencias` | POST | Parcial (proceso interno: transición automática no se especifica) |
| RF-27-AC-5 | Restringe calificación a consultor asignado | `/evidencias/{evidenciaId}/aceptacion`, `/evaluaciones-criterio/{evaluacionId}` | PUT, PATCH | Parcial (documentación adicional: autorización por asignación no se detalla) |
| RF-27-AC-6 | Califica criterio no cumplido | `/evaluaciones-criterio/{evaluacionId}` | PATCH | Parcial (documentación adicional: efecto en cálculo no se define) |
| RF-27-AC-7 | Reabre cumplido al subir nueva evidencia | `/evidencias` | POST | Parcial (proceso interno: transición automática no se especifica) |
| RF-27-AC-8 | Reabre no cumplido con motivo | `/evaluaciones-criterio/{evaluacionId}` | PATCH | Parcial (documentación adicional: motivo obligatorio no se define) |
| RF-28-AC-1 | Crea generación con catálogo | `/generaciones` | POST | Cubierto |
| RF-28-AC-2 | Restringe creación de generación | `/generaciones` | POST | Cubierto |
| RF-28-AC-3 | Exige generación al crear parque | `/parques` | POST | Cubierto |
| RF-29-AC-1 | Desactiva usuario y retira accesos | `/usuarios/{usuarioId}` | PATCH | Parcial (proceso interno: revocación de accesos no se especifica) |
| RF-29-AC-2 | Restringe baja de usuarios | `/usuarios/{usuarioId}` | PATCH | Cubierto |
| RF-29-AC-3 | Desactiva parque y retira accesos | `/parques/{parqueId}` | PATCH | Parcial (proceso interno: revocación y exclusión de vista no se especifican) |
| RF-30-AC-1 | Registra fechas del programa | `/parques/{parqueId}` | PATCH | Cubierto |
| RF-30-AC-2 | Marca atraso por actualización vencida | `x-background-processes` | Interno | Cubierto |
| RF-30-AC-3 | Recalcula próxima actualización anual | `x-background-processes` | Interno | Cubierto |
| RF-31-AC-1 | Consulta historial de parque | `/parques/{parqueId}` | GET | Cubierto |
| RF-31-AC-2 | Da alta mínima de parque histórico | `/parques` | POST | Cubierto |
| RF-31-AC-3 | Restringe historial de otros parques | `/parques/{parqueId}` | GET | Cubierto |
| RF-32-AC-1 | Muestra fases y fase actual | `/parques/{parqueId}/expediente` | GET | Cubierto |
| RF-32-AC-2 | Distingue evidencia entregada de fase completada | `/parques/{parqueId}/expediente` | GET | Cubierto |
| RF-32-AC-3 | Restringe cierre de fase | `/parques/{parqueId}/fases/{faseId}/cierre` | POST | Cubierto |
| RF-32-AC-4 | Exige motivo para avance excepcional | `/parques/{parqueId}/fases/avance-excepcion` | POST | Cubierto |
| RF-32-AC-5 | Avanza fase por excepción y registra motivo | `/parques/{parqueId}/fases/avance-excepcion` | POST | Cubierto |
| RF-33-AC-1 | Registra evaluación con folio y completa fase | `/parques/{parqueId}/evaluaciones-desempeno` | POST | Parcial (documentación adicional: folio consecutivo y transición de fase no se definen) |
| RF-33-AC-2 | Exige opinión final para evaluación | `/parques/{parqueId}/evaluaciones-desempeno` | POST | Parcial (documentación adicional: precondición no se define) |
| RF-33-AC-3 | Restringe evaluación al consultor asignado | `/parques/{parqueId}/evaluaciones-desempeno` | POST | Cubierto |
| RF-34-AC-1 | Lista APPI y contacto principal | `/parques/{parqueId}/usuarios-appi` | GET | Cubierto |
| RF-34-AC-2 | Mantiene un único contacto principal | `/parques/{parqueId}/usuarios-appi/{usuarioId}` | PATCH | Cubierto |
| RF-34-AC-3 | Notifica a APPI activos sin contacto principal | `x-background-processes` | Interno | Parcial (proceso interno: selección de destinatarios no se especifica) |
| RF-35-AC-1 | Audita descarga de evidencia | `/evidencias/{evidenciaId}/contenido` | GET | Cubierto |
| RF-35-AC-2 | Audita acceso denegado | Seguridad global | N/A | Cubierto |
| RF-35-AC-3 | Filtra bitácora sin contenido de evidencias | `/bitacora` | GET | Cubierto |
| RF-35-AC-4 | Restringe consulta de bitácora | `/bitacora` | GET | Cubierto |
| RF-36-AC-1 | Registra recomendación visible para APPI | `/evaluaciones-criterio/{evaluacionId}/recomendaciones` | POST | Cubierto |
| RF-36-AC-2 | No altera estados ni observaciones | `/evaluaciones-criterio/{evaluacionId}/recomendaciones` | POST | Cubierto |
| RF-37-AC-1 | Registra visita y hallazgos | `/visitas-validacion` | POST | Cubierto |
| RF-37-AC-2 | Conserva acción, cambio, usuario y fecha del hallazgo | `/visitas-validacion` | POST | Parcial (documentación adicional: historial de cambios de hallazgo no se define) |
| RF-37-AC-3 | Asocia fotos y aplica validación de archivos | `/visitas-validacion` | POST | Parcial (documentación adicional: asociación y validaciones de RF-06 no se definen) |
| RF-38-AC-1 | Inicia renovación sin extender vigencia | `/distintivos/{distintivoId}/renovaciones` | POST | Cubierto |
| RF-38-AC-2 | Marca distintivo vencido diariamente | `x-background-processes` | Interno | Parcial (proceso interno: transición a vencido no se detalla) |
| RF-38-AC-3 | Valida y registra prórroga | `/distintivos/{distintivoId}/renovaciones` | POST | Parcial (documentación adicional: campos obligatorios condicionales no se definen) |
| RF-39-AC-1 | Avisa 60, 30 y 0 días antes de vencimiento | `x-background-processes` | Interno | Parcial (proceso interno: calendario y destinatarios no se detallan) |
| RF-39-AC-2 | Omite aviso de versión sustituida | `x-background-processes` | Interno | Parcial (proceso interno: sustitución de evidencia y supresión no se definen) |

**Resumen:** Cubierto: 77. Parcial: 72. No cubierto: 1. Total: 150.


## Sección B — Decisiones de diseño

### 1. Selección de recursos, endpoints y alcance

Los recursos y endpoints de la API REST del SGPIS se seleccionaron a partir de los requerimientos funcionales y criterios de aceptación establecidos en el SRS. El objetivo fue representar las entidades y operaciones principales del sistema, manteniendo una relación clara entre las necesidades del usuario y las funcionalidades disponibles mediante la API.

Se priorizaron recursos como `parques`, `usuarios`, `evidencias`, `autoevaluaciones`, `evaluaciones-criterio`, `dictamenes` y `distintivos`, ya que representan procesos centrales del programa. También se incluyeron operaciones complementarias para autenticación, asignación de consultores, generación de reportes y consulta de bitácoras.

La selección siguió un enfoque orientado a recursos, utilizando métodos HTTP según la operación requerida: `GET` para consultas, `POST` para creación, `PATCH` para modificaciones parciales y `DELETE` para eliminación o cierre de recursos cuando corresponde.

No todos los criterios de aceptación requieren un endpoint independiente. Algunas funcionalidades, como la actualización automática de estados, los cálculos de vencimientos y determinadas notificaciones, corresponden a procesos internos del backend. Estos se identificaron mediante `x-background-processes`.

Asimismo, se distinguieron las funcionalidades contempladas para el semestre de aquellas previstas para versiones posteriores. Por ejemplo, la configuración de plazos de aviso (`RF-19-AC-4`) quedó fuera del alcance actual, decisión documentada en la matriz de trazabilidad.

### 2. Patrones de diseño de API

Durante el diseño se consideraron los siguientes patrones y prácticas:

- **Paginación:** se consideró para las operaciones que pueden devolver colecciones extensas, como los listados de parques, usuarios o registros de bitácora. Su finalidad es evitar respuestas demasiado grandes y facilitar la consulta de información.
- **Filtrado:** se contempló para consultar información según criterios relevantes, como parque, generación, región o estado, respetando las restricciones de acceso de cada rol.
- **Versionado:** se mantuvo OpenAPI 3.0.3 como formato de especificación. No se consideró necesario introducir múltiples versiones públicas de la API durante esta etapa, ya que todavía se encuentra en diseño. El versionado de los catálogos de criterios es independiente del versionado de la API y sí constituye una necesidad funcional del sistema.
- **Autenticación y autorización:** se adoptó JWT mediante Bearer Authentication para proteger las operaciones. Además, se contemplaron restricciones específicas según los roles y las asignaciones de los usuarios.
- **Manejo de errores:** se definieron respuestas HTTP apropiadas para distinguir operaciones exitosas, errores de validación, falta de autenticación, acceso no autorizado y recursos inexistentes.

Se buscó mantener una especificación suficientemente clara para orientar la implementación, evitando incorporar mecanismos adicionales que no estuvieran justificados por los requerimientos actuales.

### 3. Revisión de buenas prácticas REST y correcciones al agente

Durante la generación y revisión de `openapi.yaml`, el agente propuso algunas decisiones que requerían ajustes para mejorar la consistencia con los principios REST.

Uno de los casos fue la recuperación de contraseña, cuya confirmación inicialmente utilizaba `PUT`. Se decidió cambiar a `POST`, ya que la operación consume un token de un solo uso y representa una acción específica de confirmación, en lugar de una sustitución convencional de un recurso.

También se identificaron operaciones relacionadas con cambios de estado, como el cierre de fases, la firma de dictámenes y la aceptación de evidencias. En estos casos se precisó el comportamiento ante solicitudes repetidas para evitar transiciones o registros duplicados.

Otra observación fue la ausencia de respuestas de error suficientemente explícitas en algunos endpoints. Por ello, se incorporaron respuestas `401 Unauthorized` y `404 Not Found` donde correspondía, mejorando la claridad del contrato para los consumidores de la API.

En la carga múltiple de evidencias se revisó el uso de `201 Created` cuando algunos archivos podían ser rechazados. Se decidió conservar este código y documentar mediante `EvidenceUploadResult` cuáles archivos fueron aceptados y cuáles rechazados.

Estas observaciones se detectaron mediante una revisión específica de los principios REST, contrastando los endpoints con el SRS y verificando los métodos HTTP, las rutas, los códigos de respuesta y el comportamiento esperado. Los hallazgos y las correcciones quedaron registrados en `revision_rest.md`.

Finalmente, la revisión de trazabilidad permitió identificar operaciones que requerían mayor precisión. Por ejemplo, se incorporó una operación para cerrar sesiones de comité y retirar accesos temporales, atendiendo el criterio `RF-13-AC-3`.

### Conclusión

Las decisiones de diseño buscaron mantener un equilibrio entre la cobertura de los requerimientos, el respeto a las buenas prácticas REST y la simplicidad de implementación.

El uso del agente permitió generar una primera propuesta y acelerar las revisiones, pero fue necesario evaluar críticamente sus resultados. La comparación con el SRS, el análisis REST y la matriz de trazabilidad ayudaron a detectar inconsistencias, justificar exclusiones y mejorar el contrato.

Como resultado, se obtuvo una especificación que proporciona una base para desarrollar el backend, aunque algunas reglas de negocio y procesos internos deberán detallarse durante las siguientes etapas del proyecto.