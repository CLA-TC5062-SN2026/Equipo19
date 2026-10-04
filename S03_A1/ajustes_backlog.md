# Ajustes al backlog generado por el agente

**Entrada:** `evidencia_agente/backlog_agente_v0.md` (4 épicas, 17 historias, 81 story points)
**Salida:** `backlog_completo.md` (5 épicas, 22 historias, 111 story points)

El agente recibió `SRS_equipo.md` y el prompt de `evidencia_agente/prompts_agentes.md`. Cumplió el formato que se le pidió: historias en la forma "Como, quiero, para", dos criterios por historia como mínimo, puntos en Fibonacci y prioridad. Revisé cada historia contra el SRS y contra lo que sé del programa. Encontré seis problemas que se repetían en varias historias y los corregí antes de tocar historias individuales.

## 1. Problemas generales

### Criterios de aceptación que no se pueden probar

"El estado de la evidencia se actualiza correctamente" o "el sistema rechaza archivos con errores" no dicen qué estado, qué error ni qué mensaje. El SRS de equipo ya tiene 150 AC con valores concretos, así que reescribí cada criterio para que cite el AC del SRS que lo respalda (por ejemplo, RF-06-AC-4 para el rechazo de video). Con eso la prueba de la historia y la prueba del requerimiento son la misma, y el diseño de pruebas de semanas posteriores sale de ahí.

### Historias escritas desde el sistema

HU-10 ("Como sistema, quiero calcular el porcentaje") y HU-17 ("Como sistema, quiero registrar en bitácora") no tienen a una persona que reciba el valor. El cálculo le sirve a la APPI, que hoy no sabe qué obligatorios le faltan, y la bitácora le sirve a Coordinación AMPIP cuando necesita saber quién abrió o descargó información de un parque. Las reescribí con esos usuarios (HU-12 y HU-16 del backlog final).

### Una épica hecha de requerimientos no funcionales

La épica E4 "Seguridad y cumplimiento normativo" convertía el aislamiento entre parques y el cifrado en una historia de 8 puntos (HU-16 del v0). Eso no se entrega en un sprint y se olvida: cada endpoint que escribamos tiene que devolver 403 al usuario de otro parque desde el primer día. Quité la épica y pasé esos requerimientos (RNF-01, RNF-03, RNF-11, RNF-15) a la definición de terminado de `backlog_completo.md`, que aplica a todas las historias.

### Roles genéricos

"Como usuario" y "Como AMPIP" no existen en el SRS. Usé los roles del SRS: APPI, consultor asignado, Coordinación AMPIP, Director General de AMPIP y gerente corporativo. El cambio importa en el dictamen: el v0 ponía a Coordinación AMPIP a registrarlo, pero en RF-14 Coordinación solo captura el borrador y quien firma es el Director General. La historia final (HU-19) está escrita desde el Director, porque la firma es lo que vuelve oficial el otorgamiento.

### Prioridades que no siguen al cliente real

El agente priorizó por el orden de los módulos del SRS y por lo que suena urgente. El historial de parques quedó en Baja y los avisos de vencimiento en Alta. El miembro del comité de AMPIP dijo lo contrario: lo indispensable desde el primer mes es "tener el historial de todos los parques con programa" y la autoevaluación (P3, Parte C), y se enteran de los atrasos por las fechas de término y actualización (P1, Parte C). Subí el historial a Alta, agregué la historia de fechas del programa con prioridad Alta y bajé los avisos de vencimiento a Baja. Ningún parque de la generación 2027 va a tener un distintivo por vencer durante el semestre, y el SRS ya marcaba RF-19 como "Posterior".

### Huecos de cobertura

El v0 no tenía historias para cinco RF que el SRS marca como MVP o 2027 y de los que dependen otras historias: análisis de riesgos (RF-16), plan de trabajo (RF-09), fechas del programa (RF-30), fases (RF-32) y comité (RF-13, RF-15). El caso más claro es el análisis de riesgos. Sin un registro vigente, RF-17 bloquea la calificación de los estándares 2, 3 y 7, así que la historia de calificar criterios del v0 no podía cerrar 3 de los 10 estándares.

## 2. Cambios por historia

| v0 | Final | Cambio | Razón |
|---|---|---|---|
| HU-01, 3 SP | HU-01, 5 SP | Rol específico y cuatro criterios ligados a RF-26-AC-1 a AC-6. | El v0 solo cubría inicio de sesión y bloqueo. RF-26 también pide recuperación con enlace de un solo uso, expiración por inactividad e invalidación del token al cerrar sesión; eso incluye envío de correo y manejo de tokens. |
| HU-02, 13 SP | HU-02, 5 SP y HU-04, 8 SP | Dividida en dos: generación con parques, y usuarios con contacto principal y bajas. | 13 puntos era la señal de que la historia no cabía en un sprint. Los dos pedazos se pueden entregar y probar por separado. HU-04 absorbe RF-34 (contacto principal) y RF-29 (bajas), que el v0 no tenía. |
| HU-03, 5 SP | HU-03, 5 SP | Se agregan la restricción de descarga del archivo maestro (RF-25) y la conservación de versiones (RF-01-AC-5). | El catálogo es propiedad de AMPIP (RD-05); la restricción de descarga es parte de cargarlo bien, no un extra. |
| HU-04, 2 SP, Media | HU-05, 3 SP, Alta | Sube prioridad y estimación. | Sin consultor asignado, nadie puede revisar evidencias: bloquea toda la épica E2. La estimación sube por el retiro de acceso al reasignar y por la prueba de 20 combinaciones de RNF-01. |
| HU-05, 5 SP | HU-06, 5 SP | Criterios con el ejemplo del criterio 2.3 y el error 422 de RF-04. | Sin cambio de alcance. |
| HU-06, 3 SP | HU-07, 8 SP | Se agregan carga de varios archivos, carga desde el celular, progreso sin bloqueo y metadatos fuera de PostgreSQL. | 3 puntos suponía un formulario de un archivo. RF-05, RF-06, RNF-09 y RNF-18 piden validación de tamaño configurable y formatos, HEIC desde iPhone, varios archivos con rechazo individual y almacenamiento de objetos. Es la historia con más frontend nuevo para mí. |
| HU-07, 3 SP | HU-08, 5 SP | Se agregan versiones con historial y la revisión independiente por criterio de un archivo vinculado a varios (RF-05-AC-7). | La resolución C-19 del SRS de equipo cambia el modelo de datos: el estado vive en el vínculo evidencia-criterio, no en el archivo. |
| HU-08, 2 SP y HU-09, 3 SP | HU-09, 5 SP | Fusionadas. | Aceptar una evidencia sin calificar el criterio no cambia nada que vea la APPI o AMPIP. RF-27 define las dos acciones en una sola máquina de estados, con la reapertura y el bloqueo de RF-17. |
| (no existía) | HU-10, 3 SP, Alta | Historia nueva: registrar la revisión del análisis de riesgos. | Dependencia de HU-09 para los estándares 2, 3 y 7. |
| (no existía) | HU-11, 5 SP, Media | Historia nueva: plan de trabajo con responsable, fecha y atraso. | RF-09 es MVP. Media porque el atraso por fechas del programa (HU-14) cubre la necesidad que el cliente real nombró. |
| HU-10, 5 SP | HU-12, 5 SP | De "Como sistema" a "Como APPI"; tres cifras y cálculo global por suma de criterios. | Resoluciones C-11 del SRS de equipo y RF-08-AC-4 y AC-5. |
| HU-11, 8 SP | HU-13, 8 SP | Se agregan fases (RF-32) y la restricción de no abrir evidencias de seguridad (RF-07-AC-3). | Un tablero sin fases no le dice a Coordinación en qué parte del programa va cada parque, que es lo primero que pregunta. |
| (no existía) | HU-14, 3 SP, Alta | Historia nueva: fechas de término y actualización con atraso. | P1, Parte C. |
| HU-15, 3 SP, Baja | HU-15, 5 SP, Alta | Sube prioridad y estimación; se agrega el alta de parque histórico. | P3, Parte C. La estimación sube porque la vista junta generaciones, Opiniones y dictámenes, y el alta histórica es un formulario propio. |
| HU-17, 5 SP | HU-16, 5 SP, Media | De "Como sistema" a "Como Coordinación AMPIP"; la historia es la consulta con filtros. | El registro en bitácora pasa a la definición de terminado de todas las historias; la historia queda para la pantalla de consulta, que puede esperar. |
| HU-12, 5 SP | HU-17, 5 SP | Se agregan las dos precondiciones de las Opiniones (política firmada y análisis de riesgos vigente) y la marca favorable o no favorable. | RF-12-AC-4 a AC-6. Sin la marca favorable, el candado de RF-15 no tiene con qué validar. |
| (no existía) | HU-18, 8 SP, Media | Historia nueva: abrir la sesión de comité con validación del expediente y consultor de comité temporal. | El v0 iba de la Opinión al dictamen sin pasar por el comité, que es donde se valida el expediente (RF-15) y se controla el conflicto de interés (RF-13-AC-2). |
| HU-13, 5 SP | HU-19, 5 SP | Reescrita desde el Director General; separa borrador y firma. | RF-14-AC-6 y AC-7. |
| (no existía) | HU-20, 3 SP, Media | Historia nueva: reporte mensual para Dirección. | RF-21, prioridad 2027 en el SRS. |
| (no existía) | HU-21, 2 SP, Baja | Historia nueva: vista del gerente corporativo. | RF-23. Baja porque es de solo lectura sobre datos que ya existen. |
| HU-14, 3 SP, Alta | HU-22, 5 SP, Baja | Baja prioridad, sube estimación. | Plazos configurables, sin duplicados y reintentos de correo (RF-19-AC-4 y AC-5, RNF-12). |
| HU-16, 8 SP | (eliminada) | Pasa a la definición de terminado. | Ver sección 1. |

## 3. Efecto en números

El backlog pasó de 81 a 111 story points. Las seis historias que faltaban suman 24 (HU-10, HU-11, HU-14, HU-18, HU-20 y HU-21). Las reestimaciones suman 14: la carga de evidencias pasó de 3 a 8; HU-01, HU-08, HU-15 y HU-22 subieron 2 cada una; HU-05 subió 1. Quitar la historia de seguridad resta 8 puntos del tablero, aunque no del trabajo: ese esfuerzo quedó repartido en la definición de terminado de cada historia.

Las estimaciones siguen siendo iniciales. Las vamos a recalibrar después del primer sprint con la velocidad real del equipo, en especial las historias con frontend nuevo (HU-07, HU-13 y HU-18).
