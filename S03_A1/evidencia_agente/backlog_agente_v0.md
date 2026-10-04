# Salida del Agente 2: backlog v0 generado a partir de SRS_equipo.md

> Salida sin editar del agente generador de backlog (prompt en `prompts_agentes.md`). La revisión crítica y los cambios están en `ajustes_backlog.md`; la versión final está en `backlog_completo.md`.

## Épicas identificadas

| ID | Épica | Descripción |
|---|---|---|
| E1 | Gestión de usuarios y administración | Configuración inicial del programa: usuarios, parques, catálogo y asignaciones. |
| E2 | Autoevaluación y evidencias | Flujo central de la APPI y el consultor para demostrar el cumplimiento de criterios. |
| E3 | Seguimiento, dictamen y vigencia | Indicadores de avance, Opiniones de Cumplimiento, dictamen y control del distintivo. |
| E4 | Seguridad y cumplimiento normativo | Protección de la información sensible de los parques y trazabilidad. |

## Historias de usuario

### E1. Gestión de usuarios y administración

**HU-01.** Como usuario, quiero iniciar sesión con correo y contraseña, para acceder al sistema de forma segura.
- Criterios de aceptación:
  - El usuario puede iniciar sesión con credenciales válidas.
  - La cuenta se bloquea después de 5 intentos fallidos.
- Story points: 3 | Prioridad: Alta | RF: RF-26

**HU-02.** Como Coordinación AMPIP, quiero crear generaciones, dar de alta parques y registrar usuarios con sus roles, para preparar el arranque de la generación.
- Criterios de aceptación:
  - Se puede crear una generación con nombre y fecha de inicio.
  - Se puede dar de alta un parque con tipo de PI y región.
  - Se pueden registrar usuarios y asignarles un rol.
- Story points: 13 | Prioridad: Alta | RF: RF-28, RF-02, RF-03

**HU-03.** Como Coordinación AMPIP, quiero cargar el catálogo de criterios desde un archivo CSV, para que el sistema conozca los criterios O/R/NA de cada tipo de PI.
- Criterios de aceptación:
  - El sistema acepta un CSV con el formato definido y crea una versión del catálogo.
  - El sistema rechaza archivos con errores.
- Story points: 5 | Prioridad: Alta | RF: RF-01

**HU-04.** Como Coordinación AMPIP, quiero asignar consultores a los parques, para que cada parque tenga un responsable de revisión.
- Criterios de aceptación:
  - Se puede asignar un consultor a un parque.
  - Se puede reasignar un consultor.
- Story points: 2 | Prioridad: Media | RF: RF-10

### E2. Autoevaluación y evidencias

**HU-05.** Como APPI, quiero autoevaluar los criterios aplicables a mi tipo de PI, para conocer mi nivel de cumplimiento.
- Criterios de aceptación:
  - Solo se muestran los criterios O y R del tipo de PI del parque.
  - Los criterios NA no se pueden autoevaluar.
- Story points: 5 | Prioridad: Alta | RF: RF-04

**HU-06.** Como APPI, quiero subir evidencias para cada criterio, para demostrar el cumplimiento.
- Criterios de aceptación:
  - El sistema permite subir archivos.
  - El sistema valida el tamaño y el formato del archivo.
- Story points: 3 | Prioridad: Alta | RF: RF-05, RF-06

**HU-07.** Como consultor, quiero revisar las evidencias y registrar observaciones, para que la APPI corrija lo necesario.
- Criterios de aceptación:
  - El consultor puede marcar una evidencia como observada con un comentario.
  - La APPI ve la observación.
- Story points: 3 | Prioridad: Alta | RF: RF-05

**HU-08.** Como consultor, quiero aceptar evidencias, para avanzar en el cumplimiento del parque.
- Criterios de aceptación:
  - El consultor puede marcar una evidencia como aceptada.
  - El estado de la evidencia se actualiza correctamente.
- Story points: 2 | Prioridad: Alta | RF: RF-27

**HU-09.** Como consultor, quiero calificar los criterios como cumplido o no cumplido, para reflejar el resultado de la revisión.
- Criterios de aceptación:
  - El consultor puede calificar un criterio con al menos una evidencia aceptada.
  - La calificación se refleja en el cálculo de cumplimiento.
- Story points: 3 | Prioridad: Alta | RF: RF-27

### E3. Seguimiento, dictamen y vigencia

**HU-10.** Como sistema, quiero calcular el porcentaje de cumplimiento de obligatorios y recomendados, para mostrar el avance de cada parque.
- Criterios de aceptación:
  - El porcentaje de obligatorios excluye los criterios NA.
  - Se muestran obligatorios y recomendados por separado.
- Story points: 5 | Prioridad: Alta | RF: RF-08

**HU-11.** Como Coordinación AMPIP, quiero ver un dashboard con el avance de todos los parques, para supervisar el programa.
- Criterios de aceptación:
  - El dashboard muestra todos los parques con su porcentaje de avance.
  - El dashboard carga en menos de 5 segundos.
- Story points: 8 | Prioridad: Alta | RF: RF-07, RNF-17

**HU-12.** Como consultor, quiero emitir Opiniones de Cumplimiento, para documentar el estado del parque.
- Criterios de aceptación:
  - El consultor puede emitir una Opinión intermedia y una final.
  - No se puede emitir una segunda Opinión final en la misma generación.
- Story points: 5 | Prioridad: Media | RF: RF-12

**HU-13.** Como Coordinación AMPIP, quiero registrar el dictamen de cada parque, para formalizar el otorgamiento del distintivo.
- Criterios de aceptación:
  - El dictamen puede ser otorgar o no otorgar.
  - No se puede otorgar sin el 100 % de obligatorios cumplidos.
- Story points: 5 | Prioridad: Media | RF: RF-14

**HU-14.** Como APPI, quiero recibir avisos antes del vencimiento del distintivo, para renovar a tiempo.
- Criterios de aceptación:
  - El sistema envía avisos seis y tres meses antes del vencimiento.
  - No se envían avisos si el parque ya renovó.
- Story points: 3 | Prioridad: Alta | RF: RF-19

**HU-15.** Como Coordinación AMPIP, quiero consultar el historial de parques del programa, para conocer su trayectoria.
- Criterios de aceptación:
  - Se muestra la lista de parques que han participado en el programa.
  - Se puede consultar el detalle de cada parque.
- Story points: 3 | Prioridad: Baja | RF: RF-31

### E4. Seguridad y cumplimiento normativo

**HU-16.** Como AMPIP, quiero que la información de los parques esté cifrada y aislada, para proteger los datos sensibles.
- Criterios de aceptación:
  - Un usuario de un parque no puede acceder a la información de otro parque.
  - La información viaja cifrada con TLS.
- Story points: 8 | Prioridad: Alta | RF: RNF-01, RNF-15

**HU-17.** Como sistema, quiero registrar en bitácora todas las operaciones sobre evidencias, para mantener la trazabilidad.
- Criterios de aceptación:
  - Cada operación genera un registro en la bitácora.
  - Los registros no se pueden modificar.
- Story points: 5 | Prioridad: Media | RF: RF-35, RNF-03

## Resumen

- 4 épicas, 17 historias, 81 story points.
- Prioridad Alta: 12 historias. Media: 4. Baja: 1.
