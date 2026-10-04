# Issues para crear a mano en GitHub

Para cada issue: copia el título, pega el cuerpo (el bloque gris completo) y selecciona las tres etiquetas.

## HU-01

**Título:**

```text
HU-01 Como usuario del programa (APPI, consultor o personal de AMPIP), quiero iniciar sesión con mi correo y contraseña y recuperar la contraseña si la olvido, para entrar solo a las pantallas y parques que mi rol permite
```

**Etiquetas:** `epica:E1`, `prioridad:alta`, `sp:5`

**Cuerpo:**

````markdown
**Épica:** E1 Acceso y administración del programa
**Story points:** 5
**Prioridad:** Alta
**Requerimientos:** RF-26 (`SRS_equipo.md`)

## Criterios de aceptación

- [ ] Con correo y contraseña correctos recibo una sesión que expira tras 60 minutos sin actividad (RF-26-AC-1, RF-26-AC-6).
- [ ] Con contraseña incorrecta veo "Correo o contraseña incorrectos"; después de 5 intentos fallidos la cuenta queda bloqueada 15 minutos aunque la sexta contraseña sea correcta (RF-26-AC-2, RF-26-AC-3).
- [ ] El enlace de recuperación funciona una sola vez y deja de servir a los 30 minutos (RF-26-AC-4).
- [ ] Al cerrar sesión, cualquier solicitud con ese token recibe 401 (RF-26-AC-5).

## Justificación

Estimación: Cuatro mecanismos distintos: contraseña con hash, bloqueo temporal por intentos, enlace de recuperación de un solo uso con envío de correo e invalidación del token. Sin pantallas complejas.

Prioridad: Todos los demás RF suponen una sesión iniciada; RF-01-AC-1 empieza con "Coordinación AMPIP inició sesión".

## Definición de terminado

Ver la sección "Definición de terminado" de `S03_A1/backlog_completo.md`.
````

## HU-02

**Título:**

```text
HU-02 Como Coordinación AMPIP, quiero crear la generación 2027 y dar de alta en ella cada parque con su tipo de PI y su región, para que el sistema sepa desde el arranque qué criterios le aplican a cada parque
```

**Etiquetas:** `epica:E1`, `prioridad:alta`, `sp:5`

**Cuerpo:**

````markdown
**Épica:** E1 Acceso y administración del programa
**Story points:** 5
**Prioridad:** Alta
**Requerimientos:** RF-28, RF-02 (`SRS_equipo.md`)

## Criterios de aceptación

- [ ] Una generación se crea con nombre, fecha de inicio y versión del catálogo (RF-28-AC-1); APPI y consultor reciben 403 si lo intentan (RF-28-AC-2).
- [ ] Un parque con tipo de PI y región válidos queda "activo" con fecha de alta (RF-02-AC-1).
- [ ] Un parque sin generación, sin tipo de PI válido o sin región válida se rechaza con su mensaje y no se crea (RF-28-AC-3, RF-02-AC-2, RF-02-AC-3).

## Justificación

Estimación: Dos entidades (generación y parque) con validación de listas cerradas y relación con la versión del catálogo, y dos formularios.

Prioridad: El tipo de PI del parque decide qué criterios le aplican; sin parques en una generación el catálogo no se aplica a nadie.

## Definición de terminado

Ver la sección "Definición de terminado" de `S03_A1/backlog_completo.md`.
````

## HU-03

**Título:**

```text
HU-03 Como Coordinación AMPIP, quiero cargar desde un CSV el catálogo de 286 criterios con su marca O/R/NA por tipo de PI, para que la autoevaluación y el cálculo de cumplimiento usen la misma fuente que el checklist 2023
```

**Etiquetas:** `epica:E1`, `prioridad:alta`, `sp:5`

**Cuerpo:**

````markdown
**Épica:** E1 Acceso y administración del programa
**Story points:** 5
**Prioridad:** Alta
**Requerimientos:** RF-01, RF-25 (`SRS_equipo.md`)

## Criterios de aceptación

- [ ] Un CSV con las columnas definidas crea una versión activa del catálogo (RF-01-AC-1).
- [ ] Un CSV con una columna faltante o una marca distinta de O, R o NA se rechaza completo, con la fila y la columna del error (RF-01-AC-4).
- [ ] APPI y consultor reciben 403 al cargar catálogo (RF-01-AC-2) y al descargar el archivo maestro; solo Coordinación AMPIP lo descarga (RF-25-AC-2 a RF-25-AC-4).
- [ ] Una versión nueva para otra generación deja la anterior en solo lectura sin cambiar evaluaciones previas (RF-01-AC-5).

## Justificación

Estimación: Parser de CSV con validación por fila y columna, versionado del catálogo y control de descarga del archivo maestro.

Prioridad: Sin catálogo no hay autoevaluación, evidencias ni cálculo; el checklist 2023 es la referencia de todo el programa.

## Definición de terminado

Ver la sección "Definición de terminado" de `S03_A1/backlog_completo.md`.
````

## HU-04

**Título:**

```text
HU-04 Como Coordinación AMPIP, quiero dar de alta usuarios con su rol, marcar al contacto principal de cada APPI y dar de baja cuentas, para que cada persona tenga solo el acceso que le corresponde y los avisos lleguen a quien deben
```

**Etiquetas:** `epica:E1`, `prioridad:alta`, `sp:8`

**Cuerpo:**

````markdown
**Épica:** E1 Acceso y administración del programa
**Story points:** 8
**Prioridad:** Alta
**Requerimientos:** RF-03, RF-34, RF-29 (`SRS_equipo.md`)

## Criterios de aceptación

- [ ] Un alta deja la cuenta en "pendiente de activación" y envía la invitación al correo (RF-03-AC-1).
- [ ] No se puede asignar a la misma persona como APPI y consultor del mismo parque (RF-03-AC-2).
- [ ] Cada parque tiene un único contacto principal activo; marcar uno nuevo le quita la marca al anterior (RF-34-AC-1, RF-34-AC-2).
- [ ] Dar de baja un usuario o un parque retira el acceso de inmediato (RF-29-AC-1, RF-29-AC-3); un usuario APPI que lo intenta recibe 403 (RF-29-AC-2).

## Justificación

Estimación: Alta con invitación por correo, regla de roles incompatibles, contacto principal único y bajas que retiran el acceso en todas las asignaciones. Define el modelo de permisos que usan las demás historias.

Prioridad: Sin usuarios APPI y consultores no se puede probar el flujo de evidencias.

## Definición de terminado

Ver la sección "Definición de terminado" de `S03_A1/backlog_completo.md`.
````

## HU-05

**Título:**

```text
HU-05 Como Coordinación AMPIP, quiero asignar y reasignar el consultor de cada parque en la generación, para que solo el consultor responsable vea y revise el expediente
```

**Etiquetas:** `epica:E1`, `prioridad:alta`, `sp:3`

**Cuerpo:**

````markdown
**Épica:** E1 Acceso y administración del programa
**Story points:** 3
**Prioridad:** Alta
**Requerimientos:** RF-10, RNF-01 (`SRS_equipo.md`)

## Criterios de aceptación

- [ ] La asignación registra consultor, parque y generación y da acceso al expediente (RF-10-AC-1).
- [ ] Al reasignar, el consultor anterior queda en el historial y pierde el acceso en ese momento (RF-10-AC-2).
- [ ] Un consultor sin el parque asignado recibe 403 al pedir su expediente, en la prueba de 20 combinaciones de RNF-01; un usuario APPI que intenta asignar recibe 403 (RF-10-AC-3).

## Justificación

Estimación: Una relación consultor-parque-generación con historial. El costo está en retirar el acceso al reasignar y en la prueba de aislamiento de RNF-01. Es la historia de referencia de 3 puntos.

Prioridad: Bloquea toda la épica E2: sin consultor asignado nadie revisa evidencias.

## Definición de terminado

Ver la sección "Definición de terminado" de `S03_A1/backlog_completo.md`.
````

## HU-06

**Título:**

```text
HU-06 Como APPI, quiero ver y autoevaluar solo los criterios obligatorios y recomendados de mi tipo de PI, para dejar de filtrar el checklist a mano y saber qué me falta
```

**Etiquetas:** `epica:E2`, `prioridad:alta`, `sp:5`

**Cuerpo:**

````markdown
**Épica:** E2 Autoevaluación y evidencias
**Story points:** 5
**Prioridad:** Alta
**Requerimientos:** RF-04, RF-25 (`SRS_equipo.md`)

## Criterios de aceptación

- [ ] Un parque "construcción cerrado" ve el criterio 2.3 y no ve el criterio de cámara en caseta, que es NA para su tipo (RF-04-AC-1).
- [ ] Autoevaluar por API un criterio NA devuelve 422 con "Este criterio no aplica al tipo de PI del parque" (RF-04-AC-2).
- [ ] La APPI consulta los criterios uno por uno y recibe 403 si intenta descargar el archivo maestro del catálogo (RF-25-AC-1, RF-25-AC-2).

## Justificación

Estimación: Filtrado por tipo de PI en la consulta y en la API (error 422), y una pantalla de lista con captura por criterio.

Prioridad: El cliente real la nombró entre lo indispensable desde el primer mes (P3, Parte C).

## Definición de terminado

Ver la sección "Definición de terminado" de `S03_A1/backlog_completo.md`.
````

## HU-07

**Título:**

```text
HU-07 Como APPI, quiero subir evidencias de un criterio desde la computadora o el celular, una o varias a la vez, para que mi consultor las revise en el expediente sin intercambiar correos
```

**Etiquetas:** `epica:E2`, `prioridad:alta`, `sp:8`

**Cuerpo:**

````markdown
**Épica:** E2 Autoevaluación y evidencias
**Story points:** 8
**Prioridad:** Alta
**Requerimientos:** RF-05, RF-06, RNF-09, RNF-18 (`SRS_equipo.md`)

## Criterios de aceptación

- [ ] Un PDF de 5 MB queda en "enviada" con fecha, autor y criterio, y el criterio pasa de "pendiente" a "en revisión" (RF-05-AC-1, RF-27-AC-4).
- [ ] Un archivo mayor al límite, un video o un .zip se rechazan con su mensaje y no se crea el registro (RF-06-AC-1, RF-06-AC-4, RF-06-AC-5).
- [ ] Si subo cuatro archivos y uno no pasa la validación, se crean los otros tres y veo el nombre del rechazado (RF-05-AC-8).
- [ ] La carga funciona en Chrome y Safari de Android e iOS con una foto tomada con la cámara (RNF-09) y muestra el progreso sin bloquear la pantalla (RNF-18).

## Justificación

Estimación: Almacenamiento de objetos fuera de PostgreSQL, validación configurable de tamaño y formato, carga múltiple con rechazo individual, HEIC desde iPhone y progreso en pantalla. Es el componente de frontend más nuevo para el equipo. Historia de referencia de 8 puntos.

Prioridad: Sustituye el intercambio de evidencias por correo y carpetas, el problema central de `proyecto_base.md`.

## Definición de terminado

Ver la sección "Definición de terminado" de `S03_A1/backlog_completo.md`.
````

## HU-08

**Título:**

```text
HU-08 Como consultor asignado, quiero revisar las evidencias enviadas y registrar una observación cuando no son suficientes, para que la APPI sepa qué corregir en el mismo expediente
```

**Etiquetas:** `epica:E2`, `prioridad:alta`, `sp:5`

**Cuerpo:**

````markdown
**Épica:** E2 Autoevaluación y evidencias
**Story points:** 5
**Prioridad:** Alta
**Requerimientos:** RF-05 (`SRS_equipo.md`)

## Criterios de aceptación

- [ ] Registrar una observación cambia la evidencia a "observada", avisa a la APPI y deja el criterio en "en revisión" (RF-05-AC-2).
- [ ] Cuando la APPI sube una versión nueva, la evidencia vuelve a "enviada" y el historial muestra las dos versiones con sus observaciones (RF-05-AC-4, RF-05-AC-6).
- [ ] Un archivo vinculado a dos criterios se revisa por separado en cada uno (RF-05-AC-7).
- [ ] Un consultor sin el parque asignado recibe 403 al observar (RF-05-AC-3).

## Justificación

Estimación: Transición de estados de la evidencia, versiones con historial, aviso por correo y estado por vínculo evidencia-criterio (resolución C-19).

Prioridad: Sin observaciones en el sistema, el consultor sigue trabajando por correo.

## Definición de terminado

Ver la sección "Definición de terminado" de `S03_A1/backlog_completo.md`.
````

## HU-09

**Título:**

```text
HU-09 Como consultor asignado, quiero aceptar evidencias y calificar cada criterio como cumplido o no cumplido, para que el cumplimiento del parque refleje mi revisión
```

**Etiquetas:** `epica:E2`, `prioridad:alta`, `sp:5`

**Cuerpo:**

````markdown
**Épica:** E2 Autoevaluación y evidencias
**Story points:** 5
**Prioridad:** Alta
**Requerimientos:** RF-27, RF-17 (`SRS_equipo.md`)

## Criterios de aceptación

- [ ] Aceptar una evidencia y calificar el criterio como "cumplido" registra fecha y consultor (RF-27-AC-1, RF-27-AC-2).
- [ ] Un criterio de los estándares 2, 3 o 7 no pasa a "cumplido" sin análisis de riesgos vigente (RF-27-AC-3, RF-17-AC-1).
- [ ] Una evidencia nueva sobre un criterio "cumplido" lo regresa a "en revisión"; un "no cumplido" se reabre con motivo (RF-27-AC-7, RF-27-AC-8).
- [ ] Un usuario APPI que intenta aceptar o calificar recibe 403 (RF-27-AC-5).

## Justificación

Estimación: Máquina de estados del criterio con transiciones automáticas y reapertura, más el bloqueo de RF-17. Historia de referencia de 5 puntos.

Prioridad: Sin calificación el cumplimiento queda en 0 % y no hay dictamen posible.

## Definición de terminado

Ver la sección "Definición de terminado" de `S03_A1/backlog_completo.md`.
````

## HU-10

**Título:**

```text
HU-10 Como consultor asignado, quiero registrar la revisión del análisis de riesgos del parque sin que el documento se guarde por defecto, para poder calificar los estándares 2, 3 y 7 sin exponer el análisis
```

**Etiquetas:** `epica:E2`, `prioridad:alta`, `sp:3`

**Cuerpo:**

````markdown
**Épica:** E2 Autoevaluación y evidencias
**Story points:** 3
**Prioridad:** Alta
**Requerimientos:** RF-16, RF-17 (`SRS_equipo.md`)

## Criterios de aceptación

- [ ] El registro guarda fecha, versión, firmante y resumen, queda vigente y solo lo ven la APPI y su consultor (RF-16-AC-1).
- [ ] Si la APPI decide subir el documento, solo lo abren la APPI y su consultor; Coordinación AMPIP recibe 403 y el intento queda en bitácora (RF-16-AC-2, RF-16-AC-3).
- [ ] Sin análisis vigente, las evidencias de estándares distintos de 2, 3 y 7 se cargan sin bloqueo (RF-17-AC-3).

## Justificación

Estimación: Un registro con vigencia por ciclo y permisos de lectura restringidos; el documento es opcional.

Prioridad: Sin un registro vigente no se califican los estándares 2, 3 y 7, tres de los diez.

## Definición de terminado

Ver la sección "Definición de terminado" de `S03_A1/backlog_completo.md`.
````

## HU-11

**Título:**

```text
HU-11 Como consultor asignado, quiero registrar para cada criterio pendiente un responsable de la APPI y una fecha comprometida, para que el sistema marque como atrasados solo los criterios que de verdad lo están
```

**Etiquetas:** `epica:E2`, `prioridad:media`, `sp:5`

**Cuerpo:**

````markdown
**Épica:** E2 Autoevaluación y evidencias
**Story points:** 5
**Prioridad:** Media
**Requerimientos:** RF-09 (`SRS_equipo.md`)

## Criterios de aceptación

- [ ] El plan guarda criterio, responsable y fecha comprometida (RF-09-AC-1).
- [ ] La revisión diaria marca "atrasado" un criterio con fecha vencida que no llegó a "cumplido" y no marca los que siguen en plazo (RF-09-AC-2, RF-09-AC-3).
- [ ] El responsable tiene que ser un usuario APPI del mismo parque (RF-09-AC-4).

## Justificación

Estimación: Plan por criterio (hasta 286 por parque) con validación del responsable y listado de atrasos por parque, sobre el proceso diario que introduce HU-14.

Prioridad: El atraso que AMPIP usa hoy es el de las fechas del programa (HU-14); el atraso por criterio es una mejora sobre eso.

## Definición de terminado

Ver la sección "Definición de terminado" de `S03_A1/backlog_completo.md`.
````

## HU-12

**Título:**

```text
HU-12 Como APPI, quiero ver el cumplimiento de obligatorios separado del de recomendados y del avance general, por estándar y del parque, para saber qué obligatorios me faltan antes del dictamen
```

**Etiquetas:** `epica:E3`, `prioridad:alta`, `sp:5`

**Cuerpo:**

````markdown
**Épica:** E3 Seguimiento y cumplimiento
**Story points:** 5
**Prioridad:** Alta
**Requerimientos:** RF-08 (`SRS_equipo.md`)

## Criterios de aceptación

- [ ] Con 200 O aplicables y 180 cumplidos veo "90 % de cumplimiento de obligatorios" (RF-08-AC-1).
- [ ] Con 50 R aplicables y 30 cumplidos veo "60 % de cumplimiento de recomendados" y "84 % de avance general" (RF-08-AC-2, RF-08-AC-4).
- [ ] Un estándar sin O aplicables muestra "No aplica" y no 0 % (RF-08-AC-3).
- [ ] El global se calcula sobre la suma de criterios: 55 % y no el promedio de 75 % del ejemplo de RF-08-AC-5.

## Justificación

Estimación: Tres fórmulas por estándar y globales, con NA fuera del denominador, "No aplica" en lugar de 0 % y suma en lugar de promedio. Pocas pantallas, muchas combinaciones que probar.

Prioridad: Es la cifra que decide el dictamen (RD-02) y lo que la APPI hoy no sabe calcular.

## Definición de terminado

Ver la sección "Definición de terminado" de `S03_A1/backlog_completo.md`.
````

## HU-13

**Título:**

```text
HU-13 Como Coordinación AMPIP, quiero ver todos los parques de la generación con su fase, su cumplimiento de obligatorios y sus atrasos, para detectar a tiempo qué parque necesita seguimiento
```

**Etiquetas:** `epica:E3`, `prioridad:alta`, `sp:8`

**Cuerpo:**

````markdown
**Épica:** E3 Seguimiento y cumplimiento
**Story points:** 8
**Prioridad:** Alta
**Requerimientos:** RF-07, RF-32, RNF-17 (`SRS_equipo.md`)

## Criterios de aceptación

- [ ] El expediente muestra las nueve fases con su estado y la fase actual (RF-32-AC-1); lo entregado y lo validado se distinguen (RF-32-AC-2).
- [ ] El estado de cada criterio se ve sin enlace para abrir evidencias de seguridad; abrirlas por API devuelve 403 (RF-07-AC-1, RF-07-AC-3).
- [ ] Solo Coordinación AMPIP cierra fases y solo avanza sin cerrar con un motivo que queda en bitácora (RF-32-AC-3 a RF-32-AC-5).
- [ ] La vista carga en 5 segundos o menos con 80 parques (RNF-17).

## Justificación

Estimación: Vista agregada de todos los parques con fases, cumplimiento y atrasos; gestión de fases con excepción; restricción de evidencias de seguridad, y meta de 5 segundos con 80 parques.

Prioridad: Es la pantalla diaria de Coordinación AMPIP, que hoy reconstruye el avance con Excel y correo.

## Definición de terminado

Ver la sección "Definición de terminado" de `S03_A1/backlog_completo.md`.
````

## HU-14

**Título:**

```text
HU-14 Como Coordinación AMPIP, quiero registrar la fecha de término y la de actualización anual del programa de cada parque, para que el sistema marque qué parque se atrasó, que es como hoy me entero de los atrasos
```

**Etiquetas:** `epica:E3`, `prioridad:alta`, `sp:3`

**Cuerpo:**

````markdown
**Épica:** E3 Seguimiento y cumplimiento
**Story points:** 3
**Prioridad:** Alta
**Requerimientos:** RF-30 (`SRS_equipo.md`)

## Criterios de aceptación

- [ ] Las dos fechas quedan como dato del expediente (RF-30-AC-1).
- [ ] Si pasa la fecha de actualización sin actualización registrada, el parque aparece "atrasado" en la vista de avance (RF-30-AC-2).
- [ ] Si la actualización se registra antes, el parque no se marca y la siguiente fecha se calcula un año después (RF-30-AC-3).

## Justificación

Estimación: Dos fechas y una regla de atraso. Introduce el proceso diario de revisión de plazos, pero con una sola comparación.

Prioridad: El cliente real dijo que se enteran de los atrasos por las fechas de término o actualización (P1, Parte C).

## Definición de terminado

Ver la sección "Definición de terminado" de `S03_A1/backlog_completo.md`.
````

## HU-15

**Título:**

```text
HU-15 Como Coordinación AMPIP, quiero consultar el historial de todos los parques que han pasado por el programa y dar de alta parques históricos con datos mínimos, para tener en un solo lugar lo que hoy está repartido en carpetas desde 2021
```

**Etiquetas:** `epica:E3`, `prioridad:alta`, `sp:5`

**Cuerpo:**

````markdown
**Épica:** E3 Seguimiento y cumplimiento
**Story points:** 5
**Prioridad:** Alta
**Requerimientos:** RF-31 (`SRS_equipo.md`)

## Criterios de aceptación

- [ ] El historial de un parque muestra en una vista sus generaciones, fechas, autoevaluaciones, Opiniones y dictámenes (RF-31-AC-1).
- [ ] Un parque histórico se da de alta con nombre, región, fecha del último dictamen y fecha de término, sin exigir evidencias (RF-31-AC-2).
- [ ] Un usuario APPI que consulta el historial de otro parque recibe 403 (RF-31-AC-3).

## Justificación

Estimación: Consulta que junta generaciones, autoevaluaciones, Opiniones y dictámenes de un parque, más el formulario de alta histórica.

Prioridad: El cliente real lo pidió desde el primer mes (P3, Parte C) y casi no depende de las demás historias.

## Definición de terminado

Ver la sección "Definición de terminado" de `S03_A1/backlog_completo.md`.
````

## HU-16

**Título:**

```text
HU-16 Como Coordinación AMPIP, quiero consultar la bitácora filtrando por parque, usuario, acción y fechas, para saber quién vio, descargó o cambió información sensible de un parque
```

**Etiquetas:** `epica:E3`, `prioridad:media`, `sp:5`

**Cuerpo:**

````markdown
**Épica:** E3 Seguimiento y cumplimiento
**Story points:** 5
**Prioridad:** Media
**Requerimientos:** RF-35, RNF-03 (`SRS_equipo.md`)

## Criterios de aceptación

- [ ] Una descarga de evidencia deja un registro con usuario, rol, parque, acción, recurso y resultado (RF-35-AC-1); un 403 queda como "denegado" (RF-35-AC-2).
- [ ] El filtro por parque y mes lista solo esos registros, del más reciente al más antiguo, sin enlace al contenido de evidencias (RF-35-AC-3).
- [ ] APPI, consultor y Administrador técnico reciben 403 al consultarla (RF-35-AC-4) y nadie puede editar ni borrar un registro (RNF-03).

## Justificación

Estimación: Filtros por cuatro dimensiones sobre una tabla que crece con cada operación, con paginación y permisos. El registro ya existe por la definición de terminado.

Prioridad: El riesgo lo cubre el registro desde el primer sprint; la pantalla de consulta sirve cuando ya hay meses de operación.

## Definición de terminado

Ver la sección "Definición de terminado" de `S03_A1/backlog_completo.md`.
````

## HU-17

**Título:**

```text
HU-17 Como consultor asignado, quiero emitir la Opinión de Cumplimiento intermedia y la final de mis parques, para dejar constancia del avance y del visto bueno que pide el comité
```

**Etiquetas:** `epica:E4`, `prioridad:media`, `sp:5`

**Cuerpo:**

````markdown
**Épica:** E4 Opinión, comité y dictamen
**Story points:** 5
**Prioridad:** Media
**Requerimientos:** RF-12 (`SRS_equipo.md`)

## Criterios de aceptación

- [ ] La Opinión intermedia se registra con los porcentajes vigentes y sin mínimo de cumplimiento, y el parque cambia de fase (RF-12-AC-1).
- [ ] Ninguna Opinión se emite sin el criterio 1.2 cumplido ni sin análisis de riesgos vigente (RF-12-AC-4, RF-12-AC-5).
- [ ] La Opinión final exige marcar favorable o no favorable y solo hay una por parque y generación (RF-12-AC-6, RF-12-AC-3).
- [ ] Un consultor sin el parque asignado recibe 403 (RF-12-AC-2).

## Justificación

Estimación: Dos tipos de Opinión con tres precondiciones, unicidad por generación y cambio de fase.

Prioridad: La primera Opinión intermedia ocurre a mitad del programa, no al arranque de la generación.

## Definición de terminado

Ver la sección "Definición de terminado" de `S03_A1/backlog_completo.md`.
````

## HU-18

**Título:**

```text
HU-18 Como Coordinación AMPIP, quiero abrir la sesión de comité de un parque solo con su expediente completo y dar acceso temporal de lectura al consultor de comité, para que el comité dictamine un expediente revisado y sin conflicto de interés
```

**Etiquetas:** `epica:E4`, `prioridad:media`, `sp:8`

**Cuerpo:**

````markdown
**Épica:** E4 Opinión, comité y dictamen
**Story points:** 8
**Prioridad:** Media
**Requerimientos:** RF-13, RF-15 (`SRS_equipo.md`)

## Criterios de aceptación

- [ ] La sesión no se abre si hay criterios O o R en "pendiente" o "en revisión", ni sin Opinión final favorable (RF-15-AC-2, RF-15-AC-3); con ambas condiciones se abre (RF-15-AC-1).
- [ ] El consultor de comité ve el expediente en solo lectura y sin el análisis de riesgos (RF-13-AC-1).
- [ ] El consultor asignado del parque no puede ser su consultor de comité (RF-13-AC-2).
- [ ] Al cerrar la sesión, el consultor de comité recibe 403 (RF-13-AC-3).

## Justificación

Estimación: Validación del expediente sobre todos los criterios, sesión con apertura y cierre, permisos temporales de solo lectura que expiran y regla de conflicto de interés.

Prioridad: El comité ocurre al final del programa de diez meses.

## Definición de terminado

Ver la sección "Definición de terminado" de `S03_A1/backlog_completo.md`.
````

## HU-19

**Título:**

```text
HU-19 Como Director General de AMPIP, quiero firmar el dictamen que capturó el comité, para que el otorgamiento quede registrado con fecha y firmante y empiece a correr la vigencia del distintivo
```

**Etiquetas:** `epica:E4`, `prioridad:media`, `sp:5`

**Cuerpo:**

````markdown
**Épica:** E4 Opinión, comité y dictamen
**Story points:** 5
**Prioridad:** Media
**Requerimientos:** RF-14 (`SRS_equipo.md`)

## Criterios de aceptación

- [ ] El comité captura "otorgar" o "no otorgar" con motivo y queda en "borrador" (RF-14-AC-6, RF-14-AC-8).
- [ ] "Otorgar" se rechaza al capturarlo si falta el 100 % de obligatorios, la autoevaluación revisada o la Opinión final favorable (RF-14-AC-3 a RF-14-AC-5).
- [ ] Solo el Director General pasa el dictamen a "firmado"; cualquier otro usuario recibe 403 (RF-14-AC-1, RF-14-AC-7).
- [ ] Un consultor asignado que intenta registrar un dictamen recibe 403 (RF-14-AC-2).

## Justificación

Estimación: Captura en borrador, validación de las tres condiciones de RD-09 al capturar y firma restringida al Director General.

Prioridad: Depende del comité y ocurre al final del programa.

## Definición de terminado

Ver la sección "Definición de terminado" de `S03_A1/backlog_completo.md`.
````

## HU-20

**Título:**

```text
HU-20 Como Coordinación AMPIP, quiero generar cada mes un reporte por generación con la fase, el atraso y las observaciones abiertas de cada parque, para presentarlo a Dirección sin armarlo a mano en Excel
```

**Etiquetas:** `epica:E5`, `prioridad:media`, `sp:3`

**Cuerpo:**

````markdown
**Épica:** E5 Reportes y vigencia
**Story points:** 3
**Prioridad:** Media
**Requerimientos:** RF-21 (`SRS_equipo.md`)

## Criterios de aceptación

- [ ] El reporte de mayo de 2027 lista los 18 parques de la generación con fase, atraso y número de observaciones abiertas (RF-21-AC-1).
- [ ] Un usuario APPI que intenta generarlo recibe 403 (RF-21-AC-2).

## Justificación

Estimación: Consulta de datos que ya existen, presentada en un formato fijo.

Prioridad: Hoy el reporte se arma a mano; Dirección puede esperar a que haya meses de datos para tenerlo.

## Definición de terminado

Ver la sección "Definición de terminado" de `S03_A1/backlog_completo.md`.
````

## HU-21

**Título:**

```text
HU-21 Como gerente corporativo de un desarrollador, quiero ver en una sola pantalla el avance de todos los parques de mi desarrollador, para dar seguimiento sin pedirle el dato a cada APPI
```

**Etiquetas:** `epica:E5`, `prioridad:baja`, `sp:2`

**Cuerpo:**

````markdown
**Épica:** E5 Reportes y vigencia
**Story points:** 2
**Prioridad:** Baja
**Requerimientos:** RF-23 (`SRS_equipo.md`)

## Criterios de aceptación

- [ ] Con tres parques inscritos, la vista muestra el avance de los tres en solo lectura (RF-23-AC-1).
- [ ] Subir evidencia o registrar una observación desde esta cuenta devuelve 403 (RF-23-AC-2).

## Justificación

Estimación: Vista de solo lectura sobre datos existentes, filtrada por desarrollador.

Prioridad: Usuario ocasional; ninguna otra historia depende de ella.

## Definición de terminado

Ver la sección "Definición de terminado" de `S03_A1/backlog_completo.md`.
````

## HU-22

**Título:**

```text
HU-22 Como APPI, quiero recibir avisos antes de que venza el distintivo de mi parque, para iniciar la renovación a tiempo
```

**Etiquetas:** `epica:E5`, `prioridad:baja`, `sp:5`

**Cuerpo:**

````markdown
**Épica:** E5 Reportes y vigencia
**Story points:** 5
**Prioridad:** Baja
**Requerimientos:** RF-19, RNF-12 (`SRS_equipo.md`)

## Criterios de aceptación

- [ ] Se envían avisos a la APPI, con copia al desarrollador y a Coordinación AMPIP, seis y tres meses antes del vencimiento (RF-19-AC-1, RF-19-AC-2).
- [ ] No se envía el aviso si el parque ya renovó, ni se duplica si la revisión diaria corre dos veces (RF-19-AC-3, RF-19-AC-5).
- [ ] Coordinación AMPIP puede cambiar los plazos y la siguiente revisión usa los nuevos (RF-19-AC-4).
- [ ] Un fallo del correo se reintenta 3 veces y queda en bitácora si no se envía (RNF-12).

## Justificación

Estimación: Proceso diario con plazos configurables, deduplicación de avisos, reintentos de correo y registro de fallos.

Prioridad: Ningún distintivo de la generación 2027 vence durante el semestre; el SRS lo marca "Posterior".

## Definición de terminado

Ver la sección "Definición de terminado" de `S03_A1/backlog_completo.md`.
````
