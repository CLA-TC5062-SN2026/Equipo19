# SRS: SGPIS, Sistema de Gestión del Programa Parque Industrial Seguro

**Proyecto:** SGPIS, Sistema de Gestión del Programa Parque Industrial Seguro (AMPIP)
**Versión:** 1.4
**Autor:** Ángel Kociankowski, A01379225
**Fecha:** 24 de septiembre de 2026

Este documento reemplaza al borrador previo como versión de referencia del curso. Ese borrador se conserva sin modificar en `evidencia_agente/SRS_borrador.md`, como evidencia del punto de partida de esta revisión (ver `revision_SRS.md`, Partes 4 y 5).

## Control de cambios

| Versión | Fecha | Cambios principales |
|---|---|---|
| 1.0 | 24-sep-2026 | Primera versión completa después de la revisión del borrador (`evidencia_agente/SRS_borrador.md`): 25 RF, 10 RNF, 12 RD, 68 AC. |
| 1.1 | 24-sep-2026 | Corrige los 4 hallazgos bloqueantes y los 16 restantes de la validación del agente revisor (`revision_SRS.md`, Parte 6; 20 hallazgos en total, V-01 a V-20). Agrega RF-26 (Autenticación), RF-27 (Calificar criterio, separa la máquina de estado de la evidencia de la del criterio), RF-28 (Crear generación) y RF-29 (Dar de baja usuario o parque). Agrega región al alta de parque (RF-02). Agrega a RF-14 el umbral de 100 % para "otorgar" y la exigencia de una condición por obligatorio no cumplido, y separa la captura del dictamen (borrador) de su firma. Agrega RNF-11 (zona horaria), RNF-12 (canal de notificación) y RNF-13 (respaldos); agrega la cláusula de bitácora de solo append a RNF-03. Ajusta RD-08 (fecha de anclaje de la vigencia) y RD-09 (el umbral de "otorgar" deja de estar "sin norma escrita"). Ajusta el glosario, RF-01, RF-05, RF-07, RF-09, RF-11, RF-12, RF-17, RF-20 y la matriz de trazabilidad para que queden consistentes. Total: 29 RF, 13 RNF, 12 RD, 95 AC. |
| 1.2 | 24-sep-2026 | Pasada de sincronización final: agrego que "cumplido" y "no cumplido" no son estados terminales del criterio (vuelven a "en revisión" con evidencia nueva o reapertura del consultor, RF-27-AC-7/AC-8) y que un criterio que deja de ser NA por cambio de tipo de PI entra a "pendiente" (RF-11-AC-4). Agrego a RF-12 la precondición real de la coordinadora (P1, Parte A): ninguna Opinión se emite sin política de seguridad firmada (criterio 1.2 cumplido) ni sin análisis de riesgos vigente (RF-12-AC-4, AC-5). Corrijo RF-14/RD-09 para que el umbral del dictamen se valide una sola vez, al capturarlo, no al firmarlo. Corrijo RF-22: la lista pública de parques con distintivo sí lleva nombre; solo se prohíben porcentaje y ranking individuales. Agrego a RF-06 la lista cerrada de formatos permitidos (PDF, JPG, PNG, HEIC, XLSX, DOCX) con su AC de rechazo, y corrijo el estado "entregado" a "enviada" en RF-06-AC-2. Alineo RF-20-AC-1 con la regla de cálculo de la fecha esperada. Agrego RNF-14 (retención de evidencias, 6 años desde la firma del dictamen). Elimino la sección 2.5 y reparto su contenido entre 2.1 (interfaces) y 2.4 (idioma); agrego autenticación, generaciones y bajas a las funciones principales de 2.2. Sincronizo `requerimientos.md` con `SRS_final.md` en el sentido de todos los RF, RNF y RD, no solo en el texto literal. Muevo `clasificacion_agente_v0.md`, `SRS_borrador.md` y los archivos de hallazgos a `evidencia_agente/`. Total: 29 RF, 14 RNF, 12 RD, 101 AC. |
| 1.3 | 24-sep-2026 | Revisión de redacción con la skill Humanizer; sin cambios de contenido. |
| 1.4 | 24-sep-2026 | Integración de la entrevista con el cliente real (Parte C, `transcript_entrevista.md`). El dictamen deja de tener tres valores y queda en dos: otorgar o no otorgar; se elimina "otorgar con condiciones" porque el cliente real fue explícito en que AMPIP nunca entrega el distintivo con la autoevaluación sin terminar (P2, Parte C). Reescribo RD-09 y RF-14 con la nueva regla (autoevaluación revisada, Opinión de Cumplimiento final favorable y 100 % de los O cumplidos como las tres condiciones de "otorgar"); RF-15 cambia de contenido, ahora impide abrir la sesión de comité (RF-13) sin esas dos primeras condiciones. Agrego RD-13 y RF-30 (fecha de término y de actualización anual del programa por parque, con atraso automático si pasa la fecha sin actualización registrada, P1 Parte C) y RF-31 (consulta del historial de todos los parques del programa y alta de un parque histórico con datos mínimos, sin migrar su expediente, P3 Parte C). Ajusto la exclusión de "migración de expedientes históricos" para que no incluya el registro histórico mínimo de RF-31. Dejo nota en RD-08 y en "Supuestos y pendientes" de que la vigencia de tres años del distintivo viene solo de la Parte A (personaje simulado); el cliente real no la confirmó. Anoto RF-04 como confirmado por el cliente real. Ajusto 1.2, 2.2, el glosario, RNF-11, RNF-14 y la matriz de trazabilidad para que queden consistentes. Agrego RF-12-AC-6: la Opinión final exige la marca favorable o no favorable. Total: 31 RF, 14 RNF, 13 RD, 110 AC. |

## 1. Introducción

### 1.1 Propósito del documento

Este documento especifica los requerimientos de SGPIS, la plataforma web que administra el Programa Parque Industrial Seguro de AMPIP. Sustituye el manejo actual por Excel, correo y carpetas compartidas para dar seguimiento al expediente de cada parque industrial (PI), calcular su cumplimiento contra el checklist "Criterios Mínimos de Seguridad para Parques Industriales" y sostener el proceso de dictamen y renovación del distintivo. Está dirigido al equipo que construye el sistema en el semestre y a quien lo revise después: Coordinación AMPIP, los consultores del programa y el desarrollador del proyecto.

### 1.2 Alcance del sistema

SGPIS cubre, para la generación que arranca en febrero de 2027: el catálogo de criterios, el alta de parques y usuarios, la autoevaluación de diagnóstico, la carga de evidencias con revisión del consultor, el plan de trabajo y la detección de atraso, el registro de las fechas de término y de actualización anual del programa por parque con su propia detección de atraso (RD-13, RF-30), la consulta del historial de todos los parques que han estado en el programa con alta de parque histórico mínimo (RF-31), y la vista de avance para AMPIP. Durante 2027 se agrega el resto del recorrido: recálculo por cambio de tipo de PI, Opiniones de Cumplimiento, el comité de dictamen y sus reportes derivados. Quedan fuera del entregable de 12 semanas las renovaciones, el seguimiento de auditorías del subestándar 1.4, el reporte para la reunión de asociados, la migración de expedientes históricos desde 2021 (distinta del alta mínima de un parque histórico de RF-31, que sí entra en el MVP) y la operación sin señal desde el celular. Están fuera del alcance del semestre completo, por decisión ya tomada en la evaluación de viabilidad del proyecto: pagos y cuotas del programa, aplicación móvil nativa, firma electrónica avanzada e integración con sistemas de terceros. La carga directa de evidencia en video tampoco entra en este alcance (ver RF-06); la evidencia de CCTV se sube como fotografía o captura de pantalla con fecha visible.

### 1.3 Definiciones y acrónimos

- **AMPIP:** Asociación Mexicana de Parques Industriales Privados, dueña del programa.
- **APPI:** Administración del Parque Industrial. Rol y sujeto evaluado; en la práctica es el gerente de seguridad u operaciones del parque y uno o dos asistentes.
- **PI:** Parque Industrial.
- **Tipo de PI:** clasificación del parque en una de cuatro categorías: construcción abierto, construcción cerrado, operación abierto, operación cerrado. Determina qué criterios son O, R o NA.
- **O / R / NA:** marca de un criterio para un tipo de PI. O = Obligatorio (cuenta para el dictamen). R = Recomendado (no cuenta en contra, se reporta como avance general). NA = No aplica (fuera del cálculo).
- **RI:** Reglamento Interno del parque.
- **Catálogo:** conjunto vigente de 10 estándares, sus subestándares y sus criterios, con la marca O/R/NA por tipo de PI. Tiene una versión.
- **Estándar / Subestándar / Criterio:** niveles de la estructura del catálogo (por ejemplo, estándar 2 "Seguridad física", subestándar 2.8 "Sistema de alarma y CCTV", con varios criterios dentro).
- **Fase:** etapa del recorrido del parque por el programa (diagnóstico, plan de trabajo, política de seguridad, análisis de riesgos, implementación de estándares, Opinión intermedia, Opinión final, Evaluación de Desempeño, dictamen).
- **Plan de trabajo:** lista de criterios pendientes de un parque, cada uno con un responsable y una fecha comprometida.
- **Evidencia:** documento, foto, plano o registro que sustenta el cumplimiento de un criterio. Cada evidencia subida tiene su propio estado: **enviada** (recién subida por la APPI), **observada** (el consultor asignado la marca así cuando no es suficiente; vuelve a "enviada" en cuanto la APPI sube una versión nueva) o **aceptada** (el consultor asignado la marca así cuando es suficiente, ver RF-27). Un criterio puede tener más de una evidencia a la vez, en distintos estados.
- **Estado de calificación del criterio:** valor único por criterio y parque, distinto del estado de la evidencia. Va de **pendiente** (sin ninguna evidencia) a **en revisión** (en cuanto existe al menos una evidencia "enviada" para ese criterio) a **cumplido** o **no cumplido** (los decide el consultor asignado, RF-27; "cumplido" exige al menos una evidencia "aceptada" y, para los estándares 2, 3 y 7, un registro vigente de revisión del análisis de riesgos). Ninguno de los dos es un estado terminal: si la APPI sube una evidencia nueva sobre un criterio "cumplido" o "no cumplido", o el consultor asignado lo reabre con un motivo, el criterio vuelve a "en revisión" (RF-27). Un criterio marcado NA no tiene estado de calificación; si deja de ser NA por un cambio de tipo de PI (RF-11), entra directamente a "pendiente".
- **Observación:** comentario del consultor sobre una evidencia que no es suficiente; cambia el estado de esa evidencia a "observada".
- **Análisis de riesgos vigente:** un registro de revisión del análisis de riesgos (RF-16) para un parque que no ha sido reemplazado por uno más reciente del mismo ciclo (la generación en curso o el periodo de renovación vigente). Deja de estar vigente al registrarse una revisión más nueva del mismo ciclo, o al iniciar un nuevo ciclo de renovación sin revisión registrada todavía.
- **Opinión de Cumplimiento:** dictamen técnico que emite el consultor asignado sobre el estado de un parque; hay una intermedia y una final por parque, en cada generación.
- **Comité:** grupo de tres personas (Director General AMPIP, Coordinación AMPIP y un consultor de comité) que revisa el expediente y la Opinión final antes del dictamen.
- **Dictamen:** decisión del comité sobre un parque: otorgar o no otorgar el distintivo. Lo firma el Director General AMPIP. El dictamen no admite una tercera opción con condiciones (ver RD-09).
- **Distintivo:** reconocimiento "Parque Industrial Seguro" que otorga AMPIP; tiene una vigencia de tres años y se renueva.
- **Generación:** grupo de parques que entra al programa en la misma convocatoria (por ejemplo, la generación de febrero de 2027).
- **Consultor asignado:** consultor externo que acompaña a uno o varios parques durante toda la generación.
- **Consultor de comité:** consultor que participa en el comité de dictamen de un parque que no tiene asignado, con acceso temporal a su expediente.
- **Administrador técnico del sistema:** cuenta operativa para mantenimiento de la infraestructura (despliegues, respaldos). No es un rol de negocio del programa; no tiene acceso al contenido de evidencias de seguridad ni a documentos administrativos.
- **REPSE:** Registro de Prestadoras de Servicios Especializados u Obras Especializadas, exigido a la empresa de seguridad privada del parque.
- **CCTV:** circuito cerrado de televisión (cámaras de videovigilancia).

## 2. Descripción general

### 2.1 Perspectiva del producto

SGPIS es un sistema nuevo, independiente. No sustituye ni se conecta con ningún sistema de los parques, de AMPIP o de proveedores de seguridad; esa integración queda fuera de alcance. Reemplaza tres herramientas informales: el Excel de autoevaluación, el correo como constancia de cierre de fase y las carpetas compartidas de evidencias.

El producto se usa desde navegador web, de escritorio y móvil (Chrome, Safari), sin aplicación nativa (RNF-09); las pantallas se limitan a formularios, tablas y gráficas simples (2.4). No requiere hardware específico: corre en cualquier dispositivo con navegador y, para evidencia fotográfica, cámara. El backend es Python con base de datos PostgreSQL, sin integración con sistemas externos en este entregable (1.2), y la comunicación es por HTTPS; no se definen protocolos adicionales para las 12 semanas del curso.

### 2.2 Funciones del producto

- Autenticación de usuarios, con bloqueo por intentos fallidos y recuperación de contraseña.
- Administración del catálogo de criterios y su marca O/R/NA por tipo de PI.
- Creación de generaciones y alta y administración de parques, usuarios y roles, incluyendo su baja.
- Autoevaluación de diagnóstico filtrada por tipo de PI.
- Carga de evidencias por criterio y fase, con revisión y calificación del consultor.
- Cálculo de cumplimiento de obligatorios y de avance general.
- Plan de trabajo con fechas comprometidas y detección de atraso.
- Registro de la revisión del análisis de riesgos sin almacenar el documento, salvo que la APPI decida subirlo.
- Emisión de Opiniones de Cumplimiento, validación del expediente antes de abrir el comité y registro del dictamen (otorgar o no otorgar).
- Registro de las fechas de término y de actualización anual del programa por parque, con detección de atraso.
- Consulta del historial de todos los parques del programa, incluida el alta de un parque histórico con datos mínimos.
- Reportes de avance para AMPIP.

### 2.3 Características del usuario

- Coordinación AMPIP: dos o tres personas, uso diario, administra el catálogo, da de alta parques y usuarios, asigna consultores y consulta el avance. No necesita ver el contenido de evidencias de seguridad.
- Director General AMPIP: uso esporádico, concentrado en las sesiones de comité; su única acción crítica en el sistema es firmar el dictamen.
- APPI (gerente y asistentes del parque): dos o tres personas por parque, uso concentrado en las semanas previas a cada Opinión de Cumplimiento; suben evidencias, muchas veces desde el celular durante una inspección.
- Consultor asignado: entre tres y seis parques por generación; revisa evidencias, registra observaciones, da seguimiento al plan de trabajo y emite las Opiniones de Cumplimiento.
- Consultor de comité: mismo perfil que un consultor asignado, pero con acceso temporal y de solo lectura a un parque que no lleva, únicamente durante la sesión de dictamen.
- Gerente corporativo del desarrollador: uso ocasional, de solo lectura, para ver el avance consolidado de todos los parques de su desarrollador.
- Administrador técnico del sistema: perfil técnico, no de negocio; entra al sistema para tareas de mantenimiento de la plataforma, sin acceso a evidencias de seguridad ni a documentos administrativos (RNF-02).

### 2.4 Restricciones

- Un solo desarrollador construye el sistema en 12 semanas: backend en Python, base de datos PostgreSQL, frontend web con formularios, tablas y gráficas simples. Fuente: `proyecto_base.md`, Evaluación de viabilidad.
- El sistema se financia con cuotas de una asociación civil: no puede requerir licencia por usuario de cada parque ni el pago de auditorías de seguridad informática o certificaciones externas. Fuente: RD-12.
- El texto completo del catálogo 2023 solo puede usarse en el sistema y en los datos de prueba con autorización de AMPIP. Fuente: `guion_entrevista.md`, restricciones técnicas o de negocio.
- El tratamiento de los datos personales del estándar 7 está pendiente de validación legal con el abogado de AMPIP; no se implementa como regla cerrada hasta esa revisión. Fuente: RNF-04.
- Fuera de alcance del semestre: pagos y cuotas del programa, aplicación móvil nativa, firma electrónica avanzada, integración con sistemas de terceros. Fuente: `proyecto_base.md`, Evaluación de viabilidad.
- La interfaz y los mensajes del sistema están en español (México); no se requiere internacionalización en este entregable.

## 3. Requerimientos específicos

### 3.1 Requerimientos funcionales

---

**RF-01: Cargar catálogo con versión**
Descripción: el sistema debe permitir a Coordinación AMPIP cargar el catálogo vigente de 10 estándares y sus criterios, con marca O/R/NA por tipo de PI, y registrar contra qué versión fue evaluado cada parque. Una sola versión activa por generación; el manejo de varias versiones simultáneas y su comparación histórica queda fuera de las 12 semanas.
Prioridad: MVP feb-2027. Fuente: P7, Parte A; P3/P7, Parte B.

**RF-01-AC-1**
**Dado que** Coordinación AMPIP inició sesión con ese rol y tiene un archivo CSV con las columnas `estandar, subestandar, criterio, metodo_verificacion, marca_construccion_abierto, marca_construccion_cerrado, marca_operacion_abierto, marca_operacion_cerrado` para los 286 criterios, cada marca con valor O, R o NA,
**cuando** lo sube desde la pantalla "Administración de catálogo" y confirma la carga,
**entonces** el sistema valida las columnas, crea una versión activa del catálogo (por ejemplo "catalogo-2023-v1") y la marca como vigente para las evaluaciones nuevas.

**RF-01-AC-2**
**Dado que** un usuario con rol APPI o Consultor asignado intenta cargar una nueva versión del catálogo (POST /catalogo/versiones),
**cuando** envía la solicitud,
**entonces** el sistema la rechaza con error de permiso (403) y no crea ninguna versión nueva.

**RF-01-AC-3**
**Dado que** un parque fue autoevaluado contra "catalogo-2023-v1",
**cuando** Coordinación AMPIP consulta el expediente del parque,
**entonces** el sistema muestra ese identificador de versión como dato del expediente, sin permitir editarlo desde esa pantalla.

**RF-01-AC-4**
**Dado que** Coordinación AMPIP sube un archivo con una columna faltante o con una marca distinta de O, R o NA,
**cuando** confirma la carga,
**entonces** el sistema rechaza el archivo completo con un mensaje que indica la fila y la columna del error, y no crea ninguna versión.

---

**RF-02: Dar de alta parque**
Descripción: el sistema debe dar de alta un parque industrial registrando su tipo de PI, su región (estado de la República, de una lista cerrada) y la generación a la que pertenece (RF-28).
Prioridad: MVP feb-2027. Fuente: P1/P7, Parte A; V-05, validación independiente del SRS (Parte 6).

**RF-02-AC-1**
**Dado que** Coordinación AMPIP llena el formulario de alta con nombre, desarrollador, tipo de PI "operación cerrado", región "Nuevo León" y la generación "2027",
**cuando** confirma el alta,
**entonces** el sistema crea el parque en estado "activo" con la fecha de alta igual a la fecha de la operación.

**RF-02-AC-2**
**Dado que** Coordinación AMPIP no selecciona uno de los cuatro tipos de PI válidos,
**cuando** confirma el formulario,
**entonces** el sistema rechaza la operación con el mensaje "Debe seleccionar un tipo de PI válido" y no crea el registro.

**RF-02-AC-3**
**Dado que** Coordinación AMPIP no selecciona una región válida de la lista de estados de la República,
**cuando** confirma el formulario,
**entonces** el sistema rechaza la operación con el mensaje "Debe seleccionar una región válida" y no crea el registro.

---

**RF-03: Dar de alta usuarios y roles**
Descripción: el sistema debe dar de alta usuarios y asignarles uno de los roles del programa (Coordinación AMPIP, Director General AMPIP, APPI, Consultor asignado, Consultor de comité, Gerente corporativo, Administrador técnico del sistema) antes de que la generación empiece a trabajar. El rol Administrador técnico es una cuenta de mantenimiento de infraestructura, sin acceso a evidencias de seguridad ni a documentos administrativos (RNF-02). Que un usuario no pueda tener a la vez el rol de APPI y de Consultor del mismo parque es un supuesto de diseño, pendiente de confirmar con AMPIP (ver "Supuestos y pendientes con el cliente").
Prioridad: MVP feb-2027. Fuente: P7, Parte A.

**RF-03-AC-1**
**Dado que** Coordinación AMPIP da de alta al correo "gerente@parquex.mx" con rol APPI del "Parque X",
**cuando** confirma el alta,
**entonces** el sistema crea la cuenta en estado "pendiente de activación" y envía una invitación a ese correo.

**RF-03-AC-2**
**Dado que** Coordinación AMPIP intenta asignar a un mismo usuario los roles "APPI" y "Consultor asignado" del mismo parque al mismo tiempo,
**cuando** confirma el alta,
**entonces** el sistema la rechaza con el mensaje "Un usuario no puede ser APPI y Consultor del mismo parque" y no guarda el cambio.

**RF-03-AC-3**
**Dado que** Coordinación AMPIP da de alta una cuenta con rol "Administrador técnico del sistema",
**cuando** confirma el alta,
**entonces** el sistema la crea sin asignarle acceso a ningún parque ni a ninguna evidencia, solo a las herramientas técnicas de administración de la plataforma.

---

**RF-04: Autoevaluación filtrada por tipo de PI**
Descripción: el sistema debe mostrar a la APPI, para su autoevaluación de diagnóstico, únicamente los criterios O o R de su tipo de PI.
Prioridad: MVP feb-2027. Fuente: P1/P7, Parte A; P3, Parte B; P3, Parte C (el cliente real confirma la autoevaluación como indispensable desde el arranque).

**RF-04-AC-1**
**Dado que** la APPI del "Parque X", tipo "construcción cerrado", abre la autoevaluación de diagnóstico,
**cuando** el sistema carga la lista de criterios,
**entonces** muestra el criterio 2.3 (barreras perimetrales, O en construcción cerrado) y omite el criterio "al menos una cámara en cada caseta de acceso" (NA en construcción cerrado, según el subestándar 2.8).

**RF-04-AC-2**
**Dado que** la APPI intenta autoevaluar directamente por API un criterio marcado NA para su tipo de PI (POST /autoevaluaciones),
**cuando** el sistema recibe la solicitud,
**entonces** la rechaza con error 422 y el mensaje "Este criterio no aplica al tipo de PI del parque" y no crea el registro.

---

**RF-05: Subir evidencia y registrar observación**
Descripción: el sistema debe permitir a la APPI subir evidencias por criterio y fase (quedan en estado "enviada"), y al consultor asignado marcarlas como "observada" cuando no son suficientes, registrando el motivo. Cuando la APPI sube una nueva versión de una evidencia "observada", el sistema la regresa a "enviada". Aceptar una evidencia y calificar el criterio como "cumplido" son acciones de RF-27, no de este RF.
Prioridad: MVP feb-2027. Fuente: P1/P7, Parte A; V-01/V-02, validación independiente del SRS (Parte 6).

**RF-05-AC-1**
**Dado que** la APPI sube un PDF de 5 MB como evidencia del criterio 2.8 en la fase "Implementación de estándares",
**cuando** confirma la carga,
**entonces** el sistema crea el registro de evidencia en estado "enviada", con fecha, autor y criterio asociado, y pasa el criterio de "pendiente" a "en revisión" si era la primera evidencia (RF-27).

**RF-05-AC-2**
**Dado que** el consultor asignado revisa una evidencia en estado "enviada" y la considera insuficiente,
**cuando** registra la observación "Falta el protocolo de retención del grabador",
**entonces** el sistema cambia el estado de esa evidencia a "observada" y notifica a la APPI; el criterio permanece en "en revisión".

**RF-05-AC-3**
**Dado que** un consultor sin ese parque asignado intenta registrar una observación (POST /evidencias/{id}/observaciones),
**cuando** envía la solicitud,
**entonces** el sistema la rechaza con error de permiso (403) y no crea la observación.

**RF-05-AC-4**
**Dado que** una evidencia del criterio 2.8 está en estado "observada",
**cuando** la APPI sube una nueva versión de esa evidencia,
**entonces** el sistema cambia el estado de esa evidencia de "observada" a "enviada" otra vez.

---

**RF-06: Rechazar archivo de evidencia mayor a 100 MB o de formato no permitido; video fuera de alcance**
Descripción: el sistema debe rechazar, al momento de la carga, cualquier archivo de evidencia mayor a 100 MB o que no esté en la lista cerrada de formatos permitidos: PDF, JPG, PNG, HEIC, XLSX y DOCX (cubren los documentos escaneados, fotos de inspección, hojas de Excel y procedimientos documentados que describe el transcript, P3/P5 Parte B). La carga directa de video queda fuera de alcance: la evidencia de CCTV se sube como fotografía o captura de pantalla del grabador con la fecha visible, que es lo que acepta el consultor según la Parte B de la entrevista (P3, Parte B).
Prioridad: MVP feb-2027. Fuente: P6, Parte A; P3, Parte B; defecto de cierre de sincronización (decidí agregar la lista de formatos).

**RF-06-AC-1**
**Dado que** la APPI intenta subir un documento o imagen de 105 MB,
**cuando** confirma la carga,
**entonces** el sistema la rechaza con el mensaje "El archivo supera el límite de 100 MB" y no crea el registro de evidencia.

**RF-06-AC-2**
**Dado que** la APPI sube una imagen JPG de 90 MB,
**cuando** confirma la carga,
**entonces** el sistema la acepta y crea el registro de evidencia en estado "enviada".

**RF-06-AC-3**
**Dado que** la APPI sube un archivo de exactamente 100 MB,
**cuando** confirma la carga,
**entonces** el sistema lo acepta y crea el registro de evidencia, porque el límite rechaza solo lo mayor a 100 MB.

**RF-06-AC-4**
**Dado que** la APPI intenta subir un archivo de video (por ejemplo, con extensión .mp4) como evidencia,
**cuando** confirma la carga,
**entonces** el sistema la rechaza con el mensaje "Este sistema no acepta archivos de video; suba una fotografía o captura de pantalla con fecha visible" y no crea el registro.

**RF-06-AC-5**
**Dado que** la APPI intenta subir un archivo con extensión .zip como evidencia,
**cuando** confirma la carga,
**entonces** el sistema la rechaza con el mensaje "Formato de archivo no permitido; use PDF, JPG, PNG, HEIC, XLSX o DOCX" y no crea el registro.

---

**RF-07: Vista de estado de criterio para AMPIP**
Descripción: el sistema debe mostrar a AMPIP el estado de calificación de cada criterio por parque (pendiente, en revisión, cumplido o no cumplido; NA no tiene estado, ver 1.3 y RF-27) sin abrir evidencias de seguridad, salvo las administrativas.
Prioridad: MVP feb-2027. Fuente: P5, Parte A; V-02, validación independiente del SRS (Parte 6).

**RF-07-AC-1**
**Dado que** Coordinación AMPIP abre el expediente de un parque,
**cuando** consulta la lista de criterios,
**entonces** el sistema muestra el estado de calificación de cada criterio (pendiente, en revisión, cumplido o no cumplido), la fecha del último cambio y quién lo registró, sin un enlace para abrir evidencias de seguridad.

**RF-07-AC-2**
**Dado que** Coordinación AMPIP consulta la carta de inscripción, evidencia administrativa,
**cuando** hace clic en "ver documento",
**entonces** el sistema abre el archivo.

**RF-07-AC-3**
**Dado que** Coordinación AMPIP intenta abrir el plan de contingencia de un parque, que es evidencia de seguridad (GET /evidencias/{id}/contenido),
**cuando** envía la solicitud,
**entonces** el sistema la rechaza con error de permiso (403).

---

**RF-08: Calcular dos cifras de cumplimiento**
Descripción: el sistema debe calcular, por parque y por estándar, el cumplimiento de O sin NA y el avance general que incluye los R, con las fórmulas de RD-02.
Prioridad: MVP feb-2027. Fuente: P3/P7, Parte A.

**RF-08-AC-1**
**Dado que** un parque "operación cerrado" tiene 200 criterios O aplicables y 180 cumplidos,
**cuando** el sistema calcula el cumplimiento,
**entonces** muestra "90 % de cumplimiento de obligatorios" (180 ÷ 200 × 100), la cifra que se usa para el dictamen.

**RF-08-AC-2**
**Dado que** el mismo parque tiene además 50 criterios R aplicables y 30 cumplidos,
**cuando** el sistema calcula el avance general,
**entonces** muestra "84 % de avance general (incluye recomendados)", calculado como (180 + 30) ÷ (200 + 50) × 100, según la fórmula de RD-02.

**RF-08-AC-3**
**Dado que** un estándar no tiene ningún criterio O aplicable al tipo de PI del parque,
**cuando** el sistema calcula el cumplimiento de obligatorios de ese estándar,
**entonces** muestra "No aplica" en vez de un error o de 0 %.

---

**RF-09: Plan de trabajo y detección de atraso**
Descripción: el sistema debe registrar, por criterio pendiente, un responsable (un usuario con rol APPI del mismo parque, dado de alta por RF-03) y una fecha comprometida, y marcar automáticamente el atraso cuando la fecha pasa sin que el criterio llegue a estado de calificación "cumplido" (RF-27).
Prioridad: MVP feb-2027. Fuente: P1/P7, Parte A (necesidad implícita I1); V-15, validación independiente del SRS (Parte 6).

**RF-09-AC-1**
**Dado que** el consultor asignado registra, para el criterio 2.8 pendiente, como responsable a la cuenta APPI "gerente de seguridad del parque" (dada de alta en el "Parque X" por RF-03) y la fecha comprometida 2027-04-15,
**cuando** guarda el plan,
**entonces** el sistema crea el registro de plan de trabajo asociado a ese criterio y parque.

**RF-09-AC-2**
**Dado que** la fecha comprometida (2027-04-15) ya pasó y el criterio 2.8 sigue sin llegar a estado "cumplido",
**cuando** el sistema ejecuta la revisión diaria de plazos,
**entonces** marca el criterio como "atrasado" y lo agrega al listado de atrasos del parque.

**RF-09-AC-3**
**Dado que** la fecha comprometida de un criterio aún no ha pasado,
**cuando** el sistema ejecuta la revisión diaria de plazos,
**entonces** no marca ese criterio como atrasado, aunque el criterio siga "pendiente" o "en revisión".

**RF-09-AC-4**
**Dado que** el consultor asignado intenta registrar como responsable de un criterio del "Parque X" a un usuario que no tiene rol APPI en ese parque (por ejemplo, la APPI de otro parque),
**cuando** guarda el plan,
**entonces** el sistema rechaza la operación con el mensaje "El responsable debe ser un usuario APPI de este parque" y no crea el registro.

---

**RF-10: Asignar consultor a parque**
Descripción: el sistema debe permitir a AMPIP asignar y reasignar consultores por parque y generación.
Prioridad: MVP feb-2027. Fuente: P2, Parte A.

**RF-10-AC-1**
**Dado que** Coordinación AMPIP asigna al consultor "Juan Pérez" al "Parque X" en la generación 2027,
**cuando** confirma la asignación,
**entonces** el sistema registra la relación consultor-parque-generación y le da acceso al expediente del "Parque X".

**RF-10-AC-2**
**Dado que** el "Parque X" ya tenía asignado a "Juan Pérez",
**cuando** Coordinación AMPIP asigna a "Ana Ruiz" al mismo parque en la misma generación,
**entonces** el sistema reemplaza la asignación, conserva en el historial que "Juan Pérez" fue consultor hasta esa fecha, y le retira el acceso al expediente a partir de ese momento.

**RF-10-AC-3**
**Dado que** un usuario con rol APPI intenta asignar un consultor a su propio parque,
**cuando** envía la solicitud,
**entonces** el sistema la rechaza con error de permiso (403).

---

**RF-11: Recalcular criterios al cambiar tipo de PI**
Descripción: el sistema debe recalcular los criterios O/R/NA al cambiar el tipo de PI, con historial de tipo de PI y de cumplimiento anterior.
Prioridad: 2027. Fuente: P3, Parte A; P7, Parte B.

**RF-11-AC-1**
**Dado que** un parque cambia de "construcción cerrado" a "operación cerrado" el 2027-06-01,
**cuando** Coordinación AMPIP actualiza el tipo de PI,
**entonces** el sistema cierra el historial anterior con fecha_hasta = 2027-06-01, crea uno nuevo con fecha_desde = 2027-06-01 y recalcula los criterios (por ejemplo, "al menos una cámara en cada caseta de acceso" pasa de NA a O).

**RF-11-AC-2**
**Dado que** el parque tenía 85 % de cumplimiento de obligatorios bajo "construcción cerrado",
**cuando** el sistema recalcula bajo "operación cerrado",
**entonces** conserva el 85 % anterior asociado a la clasificación previa y muestra el nuevo porcentaje por separado, sin sobrescribir el dato anterior.

**RF-11-AC-3**
**Dado que** Coordinación AMPIP intenta cambiar el tipo de PI a un valor fuera de los cuatro válidos,
**cuando** confirma el cambio,
**entonces** el sistema rechaza el cambio con error 422 y el mensaje "Tipo de PI inválido" y no crea ningún registro de historial.

**RF-11-AC-4**
**Dado que** el criterio "al menos una cámara en cada caseta de acceso" estaba marcado "NA" bajo "construcción cerrado" y pasa a "O" al recalcularse bajo "operación cerrado" (RF-11-AC-1),
**cuando** el sistema termina el recálculo,
**entonces** asigna a ese criterio el estado de calificación "pendiente" (RF-27), como si fuera la primera vez que aplica al parque.

---

**RF-12: Emitir Opinión de Cumplimiento**
Descripción: el sistema debe permitir al consultor asignado emitir la Opinión intermedia y la final sobre sus parques, sin exigir un mínimo de cumplimiento general para la intermedia (RD-09 solo exige el 100 % para la final). Ninguna Opinión, intermedia o final, se emite sin que el criterio 1.2 (política de seguridad) esté calificado "cumplido" (RF-27) y sin un registro vigente de revisión del análisis de riesgos (RF-16); la coordinadora de AMPIP lo dijo explícitamente en P1, Parte A: "Lo que sí no dejamos pasar es una Opinión de Cumplimiento sin política firmada y sin análisis de riesgos entregado". Al emitir la Opinión final, el consultor asignado la marca como favorable o no favorable; esa marca es el "visto bueno" que exige RD-09 para poder capturar el dictamen "otorgar" (RF-14).
Prioridad: 2027. Fuente: P1/P7, Parte A; P2, Parte C (el "visto bueno" del consultor como parte del expediente para dictaminar).

**RF-12-AC-1**
**Dado que** el consultor asignado del "Parque X" tiene el criterio 1.2 calificado "cumplido" y un registro vigente de revisión del análisis de riesgos, y decide que ya revisó lo suficiente para reportar el avance a mitad del programa,
**cuando** emite la Opinión de Cumplimiento intermedia,
**entonces** el sistema la registra con fecha, tipo "intermedia" y los porcentajes de cumplimiento de obligatorios y de avance general vigentes en ese momento, sin exigir un mínimo de cumplimiento general, y cambia la fase del parque de "Implementación de estándares" a "Opinión intermedia emitida".

**RF-12-AC-2**
**Dado que** un consultor sin ese parque asignado intenta emitir una Opinión de Cumplimiento para él,
**cuando** envía la solicitud,
**entonces** el sistema la rechaza con error de permiso (403) y no crea el registro.

**RF-12-AC-3**
**Dado que** el "Parque X" ya tiene registrada una Opinión de Cumplimiento final para la generación en curso,
**cuando** el consultor asignado intenta emitir una segunda Opinión final para la misma generación,
**entonces** el sistema rechaza la operación con el mensaje "Ya existe una Opinión final para este parque en esta generación" y no crea un segundo registro.

**RF-12-AC-4**
**Dado que** el criterio 1.2 (política de seguridad) del "Parque X" no está calificado "cumplido",
**cuando** el consultor asignado intenta emitir la Opinión intermedia o la final,
**entonces** el sistema rechaza la operación con el mensaje "No se puede emitir la Opinión sin la política de seguridad firmada" y no crea el registro.

**RF-12-AC-5**
**Dado que** el "Parque X" no tiene un registro vigente de revisión del análisis de riesgos (RF-16),
**cuando** el consultor asignado intenta emitir la Opinión intermedia o la final,
**entonces** el sistema rechaza la operación con el mensaje "No se puede emitir la Opinión sin un análisis de riesgos vigente" y no crea el registro.

**RF-12-AC-6**
**Dado que** el consultor asignado del "Parque X" cumple las precondiciones de RF-12-AC-4 y RF-12-AC-5,
**cuando** emite la Opinión de Cumplimiento final sin indicar si es favorable o no favorable,
**entonces** el sistema rechaza la operación con el mensaje "Indica si la Opinión final es favorable o no favorable" y no crea el registro; si la indica, el sistema guarda el valor y lo muestra en el expediente que revisa el comité (RF-15).

---

**RF-13: Acceso temporal del consultor de comité, sin conflicto de interés**
Descripción: el sistema debe dar al consultor de comité acceso de solo lectura y temporal al expediente del parque en dictamen, sin el análisis de riesgos, y no permitir que sea el consultor asignado del mismo parque. Antes de dar ese acceso, el sistema valida el expediente del parque (RF-15); si no pasa esa validación, la sesión de comité no se abre.
Prioridad: 2027. Fuente: P5/P7, Parte A; P2, Parte A; P2, Parte C.

**RF-13-AC-1**
**Dado que** Coordinación AMPIP abre la sesión de comité del "Parque X" y asigna como consultor de comité a "Ana Ruiz", que no es su consultora asignada,
**cuando** confirma la asignación,
**entonces** el sistema le da acceso de solo lectura al expediente, sin el registro de revisión del análisis de riesgos.

**RF-13-AC-2**
**Dado que** Coordinación AMPIP intenta asignar como consultor de comité del "Parque X" al mismo "Juan Pérez" que ya lo tiene asignado,
**cuando** confirma la asignación,
**entonces** el sistema la rechaza con el mensaje "El consultor asignado a este parque no puede ser su consultor de comité" y no otorga el acceso.

**RF-13-AC-3**
**Dado que** la sesión de comité del "Parque X" se cerró el 2027-11-20,
**cuando** "Ana Ruiz" intenta consultar el expediente después de esa fecha,
**entonces** el sistema le niega el acceso (403).

---

**RF-14: Registrar dictamen**
Descripción: el sistema debe permitir a Coordinación AMPIP o al consultor de comité capturar el dictamen de un parque: otorgar o no otorgar, con su motivo. El dictamen ya no admite una tercera opción con condiciones: el cliente real fue explícito en que AMPIP nunca ha entregado el distintivo con la autoevaluación sin terminar (P2, Parte C), lo que contradice y sustituye a "otorgar con condiciones" de la Parte A. El sistema valida una sola vez, en el momento de la captura: "otorgar" solo se puede registrar si se cumplen las tres condiciones de RD-09 (autoevaluación revisada, Opinión de Cumplimiento final favorable del consultor asignado y 100 % de los criterios O cumplidos); si falta cualquiera de las tres, la captura de "otorgar" se rechaza y el único valor disponible es "no otorgar". Un dictamen que pasa esa validación queda en estado "borrador"; solo el Director General AMPIP puede pasarlo a "firmado", sin que firmar repita la validación. Un dictamen "borrador" no cambia la vigencia del distintivo; eso ocurre al quedar "firmado" (RD-08).
Prioridad: 2027. Fuente: P2, Parte C; P2/P7, Parte A; V-04/V-16, validación independiente del SRS (Parte 6).

**RF-14-AC-1**
**Dado que** el comité revisó el expediente del "Parque X" con la autoevaluación revisada, la Opinión de Cumplimiento final favorable del consultor asignado y 100 % de obligatorios cumplidos, y el dictamen quedó capturado como "otorgar" con su motivo,
**cuando** el Director General AMPIP lo confirma como "firmado",
**entonces** el sistema lo registra con fecha, tipo "otorgar" y el identificador del Director General como firmante, y a partir de esa fecha corre la vigencia del distintivo (RD-08).

**RF-14-AC-2**
**Dado que** un consultor asignado (no de comité) intenta registrar un dictamen,
**cuando** envía la solicitud,
**entonces** el sistema la rechaza con error de permiso (403) y no crea el registro.

**RF-14-AC-3**
**Dado que** el expediente del "Parque X" tiene 85 % de obligatorios cumplidos,
**cuando** el comité intenta capturar el dictamen "otorgar",
**entonces** el sistema rechaza la operación con el mensaje "No se puede otorgar sin el 100 % de los obligatorios cumplidos" y no crea el registro.

**RF-14-AC-4**
**Dado que** el "Parque X" tiene el 100 % de los criterios O cumplidos, pero 4 criterios R siguen en estado "en revisión" (la autoevaluación no está revisada),
**cuando** el comité intenta capturar el dictamen "otorgar",
**entonces** el sistema rechaza la operación con el mensaje "No se puede otorgar sin la autoevaluación revisada: hay criterios pendientes o en revisión" y no crea el registro.

**RF-14-AC-5**
**Dado que** el "Parque X" tiene la autoevaluación revisada y el 100 % de los criterios O cumplidos, pero el consultor asignado no registró una Opinión de Cumplimiento final favorable,
**cuando** el comité intenta capturar el dictamen "otorgar",
**entonces** el sistema rechaza la operación con el mensaje "No se puede otorgar sin la Opinión de Cumplimiento final favorable del consultor" y no crea el registro.

**RF-14-AC-6**
**Dado que** Coordinación AMPIP captura el tipo de dictamen y el motivo para el "Parque X",
**cuando** guarda esa captura sin que el Director General la haya confirmado,
**entonces** el sistema la conserva en estado "borrador", visible para los tres miembros del comité, sin que cuente todavía como dictamen oficial.

**RF-14-AC-7**
**Dado que** un dictamen del "Parque X" está en estado "borrador",
**cuando** un usuario que no es el Director General AMPIP intenta pasarlo a "firmado",
**entonces** el sistema rechaza la operación con error de permiso (403).

**RF-14-AC-8**
**Dado que** el expediente del "Parque X" tiene 60 % de obligatorios cumplidos, sin autoevaluación revisada ni Opinión de Cumplimiento final favorable,
**cuando** el comité captura el dictamen "no otorgar" con su motivo,
**entonces** el sistema acepta la captura y la registra en estado "borrador", porque "no otorgar" no exige ninguna de las tres condiciones de RD-09.

---

**RF-15: Validar expediente para comité**
Descripción: el sistema debe impedir abrir la sesión de comité (RF-13) de un parque que no tenga la autoevaluación revisada (ningún criterio O o R aplicable en estado "pendiente" ni "en revisión") y la Opinión de Cumplimiento final favorable del consultor asignado (RF-12). Este RF reemplaza al RF-15 anterior, "Registrar condición del dictamen": el cliente real eliminó la figura de "otorgar con condiciones" (P2, Parte C), así que ya no hay condiciones que registrar; en su lugar, la validación se mueve al momento de abrir la sesión de comité, antes de que exista un dictamen.
Prioridad: 2027. Fuente: P2, Parte C.

**RF-15-AC-1**
**Dado que** el "Parque X" tiene la autoevaluación revisada y una Opinión de Cumplimiento final favorable registrada,
**cuando** Coordinación AMPIP abre la sesión de comité del parque (RF-13),
**entonces** el sistema abre la sesión y otorga el acceso temporal al consultor de comité.

**RF-15-AC-2**
**Dado que** el "Parque X" tiene 5 criterios O o R en estado "en revisión",
**cuando** Coordinación AMPIP intenta abrir la sesión de comité del parque,
**entonces** el sistema rechaza la operación con el mensaje "No se puede abrir la sesión de comité: la autoevaluación no está revisada" y no otorga el acceso de RF-13.

**RF-15-AC-3**
**Dado que** el "Parque X" tiene la autoevaluación revisada pero no tiene una Opinión de Cumplimiento final favorable registrada,
**cuando** Coordinación AMPIP intenta abrir la sesión de comité del parque,
**entonces** el sistema rechaza la operación con el mensaje "No se puede abrir la sesión de comité sin la Opinión de Cumplimiento final favorable del consultor" y no otorga el acceso de RF-13.

---

**RF-16: Registrar revisión del análisis de riesgos**
Descripción: el sistema debe registrar la revisión del análisis de riesgos sin almacenar el documento por defecto; la APPI decide si lo sube y puede eliminarlo. Un registro de revisión está vigente para un parque mientras no exista uno más reciente del mismo ciclo (la generación en curso o el periodo de renovación vigente); deja de estar vigente al registrarse una revisión más nueva del mismo ciclo, o al iniciar un nuevo ciclo de renovación sin revisión registrada todavía.
Prioridad: MVP feb-2027. Fuente: Seguimiento P1/P2, Parte A.

**RF-16-AC-1**
**Dado que** el consultor asignado revisó el análisis de riesgos del "Parque X" el 2027-03-10, versión "1.0", firmado por "María López, gerente del parque",
**cuando** registra el resumen "12 riesgos identificados, 4 altos, con plan de tratamiento",
**entonces** el sistema crea el registro, visible solo para la APPI del parque y su consultor asignado, y lo marca como vigente para el ciclo actual del parque.

**RF-16-AC-2**
**Dado que** la APPI decide subir el documento completo del análisis de riesgos,
**cuando** lo sube,
**entonces** el sistema lo guarda visible únicamente para la APPI y su consultor asignado, sin opción de apertura para Coordinación AMPIP ni para el Administrador técnico del sistema.

**RF-16-AC-3**
**Dado que** Coordinación AMPIP intenta abrir el documento del análisis de riesgos de un parque,
**cuando** hace la solicitud,
**entonces** el sistema le niega el acceso (403) y registra el intento en la bitácora.

**RF-16-AC-4**
**Dado que** el "Parque X" tiene una revisión registrada durante la generación 2027 y en 2030 inicia su ciclo de renovación sin una revisión nueva para ese ciclo,
**cuando** el consultor asignado intenta calificar un criterio del estándar 3,
**entonces** el sistema trata la revisión de 2027 como no vigente para el ciclo de renovación y aplica el bloqueo de RF-17.

---

**RF-17: Bloquear calificación de estándares 2, 3 y 7 sin análisis de riesgos vigente**
Descripción: el sistema debe impedir que la calificación de criterio (RF-27) transicione a "cumplido" cualquier criterio de los estándares 2, 3 o 7 sin un registro vigente de revisión del análisis de riesgos (ver definición en 1.3), sin bloquear otras fases.
Prioridad: MVP feb-2027. Fuente: P1, Parte A y B; P7, Parte B.

**RF-17-AC-1**
**Dado que** el "Parque X" no tiene un registro vigente de revisión del análisis de riesgos,
**cuando** el consultor asignado intenta calificar como "cumplido" el criterio 3.1 (personal de seguridad, estándar 3),
**entonces** el sistema rechaza la operación con el mensaje "No se puede calificar este criterio sin un análisis de riesgos vigente" y el criterio conserva su estado anterior.

**RF-17-AC-2**
**Dado que** el "Parque X" sí tiene ese registro vigente,
**cuando** el consultor asignado califica como "cumplido" el criterio 3.1,
**entonces** el sistema acepta el cambio de estado.

**RF-17-AC-3**
**Dado que** el "Parque X" no tiene análisis de riesgos vigente,
**cuando** la APPI sube evidencia de un criterio del estándar 6 (seguridad de vehículos de carga, que no depende del análisis de riesgos),
**entonces** el sistema acepta la carga sin bloqueo.

---

**RF-18: Registrar auditorías del subestándar 1.4**
Descripción: el sistema debe permitir registrar cada auditoría con fecha, tipo, participantes, acciones y, en la externa, tercero acreditado y notificación al corporativo.
Prioridad: Posterior. Fuente: P4, Parte A; P4, Parte B.

**RF-18-AC-1**
**Dado que** la APPI del "Parque X" registra una auditoría interna del 2027-05-02 con los participantes "gerente de seguridad" y "asistente de operaciones" y la acción correctiva "reforzar el rondín nocturno",
**cuando** confirma el registro,
**entonces** el sistema lo guarda con tipo "interna", sin exigir informe completo.

**RF-18-AC-2**
**Dado que** la APPI registra una auditoría externa hecha por "Auditorías ABC S.C.",
**cuando** confirma el registro sin indicar si se notificó al corporativo del parque,
**entonces** el sistema rechaza el guardado con el mensaje "Debe indicar si se notificó al corporativo del PI".

---

**RF-19: Avisar vencimiento del distintivo**
Descripción: el sistema debe avisar a la APPI, con copia al desarrollador y a AMPIP, seis y tres meses antes del vencimiento, y no reenviar el aviso si el parque ya renovó.
Prioridad: Posterior. Fuente: P4/P7, Parte A.

**RF-19-AC-1**
**Dado que** el distintivo del "Parque X" vence el 2027-09-01,
**cuando** faltan exactamente seis meses (2027-03-01),
**entonces** el sistema envía un aviso a la APPI, con copia al desarrollador y a Coordinación AMPIP.

**RF-19-AC-2**
**Dado que** el mismo distintivo,
**cuando** faltan exactamente tres meses (2027-06-01),
**entonces** el sistema envía un segundo aviso a los mismos destinatarios.

**RF-19-AC-3**
**Dado que** el distintivo del "Parque X" ya fue renovado antes de la fecha en que tocaría enviar el segundo aviso,
**cuando** llega esa fecha,
**entonces** el sistema no envía el aviso, porque el distintivo ya no está por vencer.

---

**RF-20: Avisar auditoría interna pendiente**
Descripción: el sistema debe avisar a la APPI un mes antes de la fecha esperada de la próxima auditoría interna. La fecha esperada se calcula como la fecha de la última auditoría interna registrada (RF-18) más seis meses; si no hay auditoría previa registrada, se calcula como la fecha de alta del parque más seis meses.
Prioridad: Posterior. Fuente: P4, Parte A; V-10, validación independiente del SRS (Parte 6).

**RF-20-AC-1**
**Dado que** la fecha esperada de la próxima auditoría interna del "Parque X", calculada como su última auditoría interna registrada (2027-02-15) más seis meses, es 2027-08-15,
**cuando** falta exactamente un mes (2027-07-15),
**entonces** el sistema envía un aviso a la APPI del parque.

**RF-20-AC-2**
**Dado que** la APPI ya registró la auditoría interna antes de esa fecha,
**cuando** llega el día en que se hubiera enviado el aviso,
**entonces** el sistema no lo envía.

---

**RF-21: Reporte mensual para Dirección**
Descripción: el sistema debe generar un reporte mensual por generación con nombre de parque, fase, atraso y observaciones abiertas.
Prioridad: 2027. Fuente: P7, Parte A.

**RF-21-AC-1**
**Dado que** la generación 2027 tiene 18 parques en distintas fases,
**cuando** Coordinación AMPIP genera el reporte de mayo de 2027,
**entonces** el sistema produce un reporte con el nombre de cada uno de los 18 parques, su fase, si está atrasado (RF-09) y su número de observaciones abiertas.

**RF-21-AC-2**
**Dado que** un usuario con rol APPI intenta generar el reporte mensual de Dirección,
**cuando** envía la solicitud,
**entonces** el sistema la rechaza con error de permiso (403).

---

**RF-22: Reporte agregado para asociados**
Descripción: el sistema debe generar un reporte agregado por región para la reunión de asociados, con cifras agregadas y la lista pública de los parques con distintivo vigente (con su nombre); no debe mostrar el porcentaje de avance de un parque individual ni un orden o comparación entre parques.
Prioridad: Posterior. Fuente: P7, Parte A.

**RF-22-AC-1**
**Dado que** hay 41 parques con distintivo vigente, 14 en proceso y 9 renovados,
**cuando** Coordinación AMPIP genera el reporte para la reunión de asociados,
**entonces** el sistema produce cifras agregadas por región y la lista pública de los 41 parques con distintivo vigente, con el nombre de cada uno, sin porcentaje ni posición individual de ningún parque.

**RF-22-AC-2**
**Dado que** se solicita GET /reporte-asociados,
**cuando** se inspecciona la respuesta,
**entonces** ningún objeto de parque incluye un campo de porcentaje de avance ni de posición o ranking.

---

**RF-23: Vista consolidada para gerente corporativo**
Descripción: el sistema debe dar al gerente corporativo una vista de solo lectura de todos sus parques.
Prioridad: 2027. Fuente: P2, Parte A.

**RF-23-AC-1**
**Dado que** el desarrollador "Grupo Industrial ABC" tiene tres parques inscritos,
**cuando** su gerente corporativo inicia sesión,
**entonces** el sistema muestra el avance de los tres parques en una sola vista, de solo lectura.

**RF-23-AC-2**
**Dado que** el gerente corporativo intenta subir una evidencia o registrar una observación,
**cuando** envía la solicitud,
**entonces** el sistema la rechaza con error de permiso (403).

---

**RF-24: Definir evidencia suficiente por criterio**
Descripción: el sistema debe permitir capturar, por criterio, una descripción de la evidencia suficiente.
Prioridad: 2027. Fuente: P3/P7, Parte A.

**RF-24-AC-1**
**Dado que** Coordinación AMPIP captura, para el criterio 2.8, el texto "reproducir en el grabador la grabación de hace 30 días con foto de la pantalla con fecha visible, más el protocolo de retención",
**cuando** guarda el texto,
**entonces** el sistema lo asocia al criterio y lo muestra al consultor y a la APPI al abrirlo.

**RF-24-AC-2**
**Dado que** un consultor asignado intenta modificar esa descripción,
**cuando** envía la solicitud,
**entonces** el sistema la rechaza con error de permiso (403).

---

**RF-25: Restringir la descarga del archivo maestro del catálogo**
Descripción: el sistema debe impedir que cualquier usuario, salvo Coordinación AMPIP, descargue el archivo maestro del catálogo (los criterios completos con sus cuatro columnas O/R/NA en un solo archivo); la APPI y el consultor asignado pueden ver y descargar, criterio por criterio o en un listado filtrado, únicamente los criterios aplicables al tipo de PI del parque que les corresponde (RD-05).
Prioridad: MVP feb-2027. Fuente: P7, Parte A.

**RF-25-AC-1**
**Dado que** la APPI del "Parque X" consulta la lista de criterios aplicables a su parque,
**cuando** la visualiza,
**entonces** el sistema le permite ver cada criterio de forma individual.

**RF-25-AC-2**
**Dado que** la APPI intenta descargar el archivo maestro del catálogo completo en un solo archivo (GET /catalogo/exportar),
**cuando** envía la solicitud,
**entonces** el sistema la rechaza con error de permiso (403) y el mensaje "La descarga del archivo maestro del catálogo está restringida a Coordinación AMPIP".

**RF-25-AC-3**
**Dado que** Coordinación AMPIP solicita el archivo maestro del catálogo completo,
**cuando** confirma la descarga,
**entonces** el sistema genera el archivo con los 286 criterios y sus cuatro columnas O/R/NA.

**RF-25-AC-4**
**Dado que** un consultor asignado intenta descargar el archivo maestro del catálogo completo,
**cuando** envía la solicitud,
**entonces** el sistema la rechaza con error de permiso (403), aunque sí puede ver los criterios aplicables a los parques que tiene asignados.

---

**RF-26: Autenticación**
Descripción: el sistema debe autenticar usuarios con correo y contraseña, bloquear la cuenta 15 minutos después de 5 intentos fallidos consecutivos, permitir recuperar la contraseña mediante un enlace de un solo uso con vigencia de 30 minutos, invalidar el token de sesión al cerrar sesión, y expirar la sesión tras 60 minutos de inactividad. Este RF no proviene del transcript ni de la Guía; es una función base de cualquier sistema con cuentas, exigida por la validación independiente del SRS (V-03, Parte 6). Es lo que implementa el caso de uso "Iniciar sesión" del diagrama.
Prioridad: MVP feb-2027. Fuente: V-03, validación independiente del SRS (Parte 6).

**RF-26-AC-1**
**Dado que** un usuario activo introduce su correo y la contraseña correcta,
**cuando** envía el formulario de inicio de sesión,
**entonces** el sistema le entrega un token de sesión que expira tras 60 minutos de inactividad.

**RF-26-AC-2**
**Dado que** un usuario introduce una contraseña incorrecta,
**cuando** envía el formulario,
**entonces** el sistema rechaza el inicio de sesión con el mensaje "Correo o contraseña incorrectos" y no entrega ningún token.

**RF-26-AC-3**
**Dado que** un usuario falla 5 intentos consecutivos de inicio de sesión,
**cuando** lo intenta una sexta vez, aunque use la contraseña correcta,
**entonces** el sistema rechaza el intento con el mensaje "Cuenta bloqueada temporalmente; intente de nuevo en 15 minutos" y no entrega ningún token.

**RF-26-AC-4**
**Dado que** un usuario solicita recuperar su contraseña,
**cuando** el sistema le envía un enlace de recuperación de un solo uso,
**entonces** ese enlace deja de funcionar 30 minutos después de generado o en cuanto se usa una vez, lo que ocurra primero.

**RF-26-AC-5**
**Dado que** un usuario con sesión activa cierra sesión,
**cuando** confirma el cierre,
**entonces** el sistema invalida el token de esa sesión y cualquier solicitud posterior con ese token se rechaza con error de autenticación (401).

**RF-26-AC-6**
**Dado que** un usuario con sesión activa no realiza ninguna acción durante 60 minutos,
**cuando** intenta hacer una nueva solicitud después de ese lapso,
**entonces** el sistema la rechaza con error de autenticación (401) y le pide iniciar sesión de nuevo.

---

**RF-27: Calificar criterio**
Descripción: el sistema debe permitir al consultor asignado marcar una evidencia como "aceptada", y calificar el criterio asociado como "cumplido" o "no cumplido". El estado de calificación de un criterio pasa de "pendiente" a "en revisión" automáticamente en cuanto existe al menos una evidencia "enviada" para ese criterio. Un criterio solo puede pasar a "cumplido" si tiene al menos una evidencia "aceptada" y, para los estándares 2, 3 y 7, un registro vigente de revisión del análisis de riesgos (RF-16, bloqueo de RF-17). "Cumplido" y "no cumplido" no son estados terminales: el sistema regresa el criterio a "en revisión" si la APPI sube una evidencia nueva sobre él, o si el consultor asignado lo reabre registrando un motivo. Un criterio marcado NA no tiene estado de calificación (ver 1.3); si deja de ser NA por un cambio de tipo de PI (RF-11), entra a "pendiente".
Prioridad: MVP feb-2027. Fuente: V-01/V-02, validación independiente del SRS (Parte 6); elicitado a partir de RF-05, RF-08, RF-09 y RF-17, que ya asumían esta acción sin definirla.

**RF-27-AC-1**
**Dado que** el consultor asignado revisa una evidencia en estado "enviada" del criterio 2.8 y la considera suficiente,
**cuando** la marca como "aceptada",
**entonces** el sistema cambia el estado de esa evidencia a "aceptada".

**RF-27-AC-2**
**Dado que** el criterio 2.8 del "Parque X" (estándar 2, sin la restricción de RF-17) tiene al menos una evidencia en estado "aceptada",
**cuando** el consultor asignado califica el criterio como "cumplido",
**entonces** el sistema cambia el estado de calificación del criterio de "en revisión" a "cumplido", registra fecha y consultor, y lo refleja en el cálculo de RF-08.

**RF-27-AC-3**
**Dado que** el criterio 3.1 del "Parque X" tiene una evidencia en estado "aceptada" pero el parque no tiene un registro vigente de revisión del análisis de riesgos,
**cuando** el consultor asignado intenta calificar el criterio como "cumplido",
**entonces** el sistema rechaza la operación con el mensaje "No se puede calificar este criterio sin un análisis de riesgos vigente" (RF-17) y el criterio permanece en "en revisión".

**RF-27-AC-4**
**Dado que** el criterio 2.6 del "Parque X" está en estado "pendiente" y no tiene ninguna evidencia,
**cuando** la APPI sube la primera evidencia para ese criterio (RF-05, queda en estado "enviada"),
**entonces** el sistema cambia automáticamente el estado de calificación del criterio de "pendiente" a "en revisión".

**RF-27-AC-5**
**Dado que** un usuario con rol APPI intenta marcar una evidencia como "aceptada", calificar un criterio como "cumplido" o "no cumplido", o reabrir un criterio ya calificado,
**cuando** envía la solicitud,
**entonces** el sistema la rechaza con error de permiso (403), porque solo el consultor asignado califica, reabre o califica evidencias y criterios.

**RF-27-AC-6**
**Dado que** el consultor asignado determina que un criterio no se va a cumplir en el ciclo actual,
**cuando** lo califica como "no cumplido",
**entonces** el sistema registra ese estado y lo refleja en el cálculo de RF-08 como criterio O no cumplido.

**RF-27-AC-7**
**Dado que** el criterio 2.8 del "Parque X" está en estado "cumplido" y la APPI sube una nueva evidencia para ese criterio,
**cuando** el sistema recibe la evidencia (RF-05, queda en estado "enviada"),
**entonces** cambia automáticamente el estado de calificación del criterio de "cumplido" a "en revisión".

**RF-27-AC-8**
**Dado que** el criterio 3.1 del "Parque X" está en estado "no cumplido" y el consultor asignado decide reabrirlo con el motivo "cambió la configuración de accesos del parque",
**cuando** confirma la reapertura,
**entonces** el sistema cambia el estado de calificación del criterio de "no cumplido" a "en revisión", sin necesidad de una evidencia nueva.

**Tabla de transiciones: estado de evidencia**

| De | A | Evento | Quién la ejecuta | RF |
|----|----|--------|-------------------|----|
| (sin evidencia) | enviada | la APPI sube un archivo para el criterio | APPI | RF-05-AC-1 |
| enviada | aceptada | el consultor asignado la considera suficiente | Consultor asignado | RF-27-AC-1 |
| enviada | observada | el consultor asignado la considera insuficiente y registra el motivo | Consultor asignado | RF-05-AC-2 |
| observada | enviada | la APPI sube una nueva versión del archivo | APPI | RF-05-AC-4 |

**Tabla de transiciones: estado de calificación del criterio**

| De | A | Evento | Quién la ejecuta | RF |
|----|----|--------|-------------------|----|
| pendiente | en revisión | existe al menos una evidencia en estado "enviada" para el criterio | El sistema, automático | RF-27-AC-4 |
| en revisión | cumplido | hay ≥1 evidencia "aceptada" y, para estándares 2/3/7, análisis de riesgos vigente registrado | Consultor asignado | RF-27-AC-2 |
| en revisión | no cumplido | el consultor asignado decide que no se cumplirá en el ciclo actual | Consultor asignado | RF-27-AC-6 |
| cumplido | en revisión | la APPI sube una evidencia nueva sobre ese criterio | El sistema, automático (evento: APPI) | RF-27-AC-7 |
| no cumplido | en revisión | el consultor asignado reabre el criterio registrando un motivo | Consultor asignado | RF-27-AC-8 |
| NA | pendiente | el criterio deja de ser NA por un cambio de tipo de PI (RF-11) | El sistema, automático | RF-11-AC-4 |

Ni "cumplido" ni "no cumplido" son estados terminales: ambos pueden volver a "en revisión". Ningún otro rol (APPI para calificar/reabrir, Coordinación AMPIP, Director General, consultor de comité, Administrador técnico) puede ejecutar una transición de evidencia o de criterio; intentarlo se rechaza con 403 (RF-27-AC-5).

---

**RF-28: Crear generación**
Descripción: el sistema debe permitir a Coordinación AMPIP crear una generación con nombre, fecha de inicio y la versión del catálogo vigente asociada (RF-01), antes de dar de alta parques dentro de ella (RF-02).
Prioridad: MVP feb-2027. Fuente: V-08, validación independiente del SRS (Parte 6); necesidad implícita de RF-01, RF-02 y RF-10, que ya suponen una generación existente.

**RF-28-AC-1**
**Dado que** Coordinación AMPIP crea la generación "2027" con fecha de inicio 2027-02-01 y la asocia a la versión "catalogo-2023-v1" del catálogo,
**cuando** confirma la creación,
**entonces** el sistema la registra y permite dar de alta parques dentro de ella.

**RF-28-AC-2**
**Dado que** un usuario con rol APPI o Consultor intenta crear una generación,
**cuando** envía la solicitud,
**entonces** el sistema la rechaza con error de permiso (403).

**RF-28-AC-3**
**Dado que** Coordinación AMPIP intenta dar de alta un parque (RF-02) sin indicar a qué generación pertenece,
**cuando** confirma el alta,
**entonces** el sistema rechaza la operación con el mensaje "Debe indicar la generación del parque" y no crea el registro.

---

**RF-29: Dar de baja usuario o parque**
Descripción: el sistema debe permitir a Coordinación AMPIP desactivar la cuenta de un usuario o el registro de un parque, retirando de inmediato el acceso de las cuentas afectadas.
Prioridad: MVP feb-2027. Fuente: V-09, validación independiente del SRS (Parte 6); P4, Parte A ("algunos consultores ya ni trabajaban con nosotros").

**RF-29-AC-1**
**Dado que** Coordinación AMPIP desactiva la cuenta del consultor "Juan Pérez",
**cuando** confirma la baja,
**entonces** el sistema le retira de inmediato el acceso a todos los parques que tenía asignados, igual que ya hace RF-10-AC-2 al reasignar un consultor.

**RF-29-AC-2**
**Dado que** un usuario con rol APPI intenta desactivar su propia cuenta o la de otro usuario,
**cuando** envía la solicitud,
**entonces** el sistema la rechaza con error de permiso (403).

**RF-29-AC-3**
**Dado que** Coordinación AMPIP desactiva un parque,
**cuando** confirma la baja,
**entonces** el sistema retira el acceso a todos los usuarios asociados a ese parque (APPI y consultor asignado) y deja de mostrarlo en la vista de avance activa.

---

**RF-30: Registrar fechas del programa y marcar atraso por falta de actualización**
Descripción: el sistema debe permitir a Coordinación AMPIP registrar, por parque, la fecha de término del programa y la fecha de la próxima actualización anual (RD-13), y marcar el parque como atrasado en la vista de avance de AMPIP (RF-07) cuando la fecha de actualización pasa sin que se registre una actualización nueva. Es el mecanismo que el cliente real describió como su principal fuente de aviso de atraso: "nos enteramos principalmente por las fechas de término o de actualización del programa" (P1, Parte C).
Prioridad: MVP feb-2027. Fuente: P1, Parte C.

**RF-30-AC-1**
**Dado que** Coordinación AMPIP registra para el "Parque X" la fecha de término del programa 2027-11-30 y la fecha de la próxima actualización anual 2028-02-01,
**cuando** confirma el registro,
**entonces** el sistema lo guarda como dato del expediente del parque.

**RF-30-AC-2**
**Dado que** la fecha de la próxima actualización anual del "Parque X" (2028-02-01) ya pasó y Coordinación AMPIP no ha registrado una actualización nueva,
**cuando** el sistema ejecuta la revisión diaria de plazos,
**entonces** marca al "Parque X" como "atrasado" en la vista de avance de AMPIP (RF-07).

**RF-30-AC-3**
**Dado que** Coordinación AMPIP registra la actualización anual del "Parque X" antes del 2028-02-01,
**cuando** llega esa fecha,
**entonces** el sistema no marca al parque como atrasado y calcula la siguiente fecha de actualización un año después de la actualización registrada.

---

**RF-31: Consultar historial de parques del programa**
Descripción: el sistema debe permitir a Coordinación AMPIP consultar el historial de todos los parques que han estado en el programa: por parque, las generaciones que cursó, sus fechas de término y de actualización (RF-30), sus autoevaluaciones, las Opiniones de Cumplimiento (RF-12) y los dictámenes (RF-14) registrados en el sistema. También debe permitir dar de alta un parque histórico con datos mínimos (nombre, región, fecha del último dictamen y fecha de término), sin migrar su expediente completo; la migración de expedientes queda fuera del alcance de las 12 semanas (ver 1.2). El cliente real lo puso entre lo indispensable desde el primer mes: "que se pueda tener el historial de todos los parques con programa" (P3, Parte C).
Prioridad: MVP feb-2027. Fuente: P3, Parte C.

**RF-31-AC-1**
**Dado que** el "Parque X" cursó las generaciones 2021 y 2024, con dos dictámenes "otorgar" registrados,
**cuando** Coordinación AMPIP abre el historial del "Parque X",
**entonces** el sistema muestra, en una sola vista, sus generaciones cursadas, fechas de término y actualización, autoevaluaciones, Opiniones de Cumplimiento y dictámenes registrados.

**RF-31-AC-2**
**Dado que** Coordinación AMPIP da de alta un parque histórico con nombre "Parque Y", región "Jalisco", fecha del último dictamen 2022-03-15 y fecha de término 2022-01-10, sin ningún otro dato,
**cuando** confirma el alta,
**entonces** el sistema crea el registro histórico del parque sin exigir ningún documento ni evidencia de su expediente.

**RF-31-AC-3**
**Dado que** un usuario con rol APPI del "Parque X" intenta consultar el historial de un parque que no es el suyo,
**cuando** envía la solicitud,
**entonces** el sistema la rechaza con error de permiso (403).

### 3.2 Requerimientos no funcionales

**RNF-01: Aislamiento entre parques.** Categoría: seguridad. Métrica: 0 accesos cruzados exitosos en una muestra de al menos 20 combinaciones usuario/parque no autorizado. Verificación: prueba automatizada que, autenticada como usuario de un parque, solicita el expediente de otro parque y exige 403 en el 100 % de los casos.

**RNF-02: Evidencias de seguridad restringidas a APPI y consultor asignado.** Categoría: privacidad. Métrica: 0 aperturas exitosas de análisis de riesgos, plan de contingencia o ubicación de cámaras por cuentas de Coordinación AMPIP o de Administrador técnico del sistema. Verificación: prueba automatizada con esas cuentas contra los endpoints de esos documentos, esperando 403.

**RNF-03: Bitácora de accesos.** Categoría: seguridad. Métrica: 100 % de las operaciones de subir, consultar, modificar o descargar evidencia generan un registro de bitácora (usuario, fecha, hora, acción, evidencia); los registros son de solo append, ningún rol, incluido el Administrador técnico del sistema, puede modificarlos ni borrarlos desde la aplicación. Verificación: prueba automatizada que ejecuta cada operación y confirma el registro correspondiente, y una segunda prueba que, con una cuenta de Administrador técnico, intenta un UPDATE o DELETE sobre un registro de bitácora vía la API y confirma que la operación no existe o se rechaza.

**RNF-04: Datos personales del estándar 7.** Categoría: privacidad. Métrica: acceso al contenido de evidencias del estándar 7 limitado a APPI y consultor asignado; Coordinación AMPIP solo ve el estado del criterio, no el contenido. Verificación: prueba de control de acceso por rol sobre esos endpoints. Nota: el tratamiento exacto de estos datos está pendiente de validación legal con AMPIP.

**RNF-05: Almacenamiento por país.** Categoría: privacidad. Métrica: para el entregable de 12 semanas, los archivos se guardan en un único proveedor con región fija en México o Estados Unidos. Verificación: inspección de la configuración de almacenamiento del despliegue.

**RNF-06: Capacidad y respuesta del expediente.** Categoría: escalabilidad. Métrica: la lista de evidencias de un expediente con hasta 1,500 registros responde en 2 segundos o menos, percentil 95, medido del lado del servidor. Verificación: prueba de carga con un expediente sintético de 1,500 evidencias. Nota: cifra propuesta por el equipo de desarrollo (ver "Supuestos y pendientes con el cliente").

**RNF-07: Confirmación de carga de evidencia.** Categoría: rendimiento. Métrica: el servidor confirma la recepción de un archivo de evidencia ya subido en 1 segundo o menos, bajo una concurrencia de diseño de 30 usuarios subiendo evidencia al mismo tiempo (supuesto derivado de los cerca de 150 usuarios registrados, de los cuales no todos se conectan a la vez). Esta métrica no incluye el tiempo de transferencia del archivo por la red del usuario, que depende de la conectividad del parque y no lo controla el sistema. Verificación: prueba de carga (por ejemplo con k6) que mide el tiempo entre "archivo recibido completo" y "respuesta de confirmación", no el tiempo total de subida. Nota: cifra y concurrencia propuestas por el equipo de desarrollo (ver "Supuestos y pendientes con el cliente").

**RNF-08: Disponibilidad en fechas críticas.** Categoría: disponibilidad. Métrica: disponibilidad ≥ 99 % medida por monitoreo externo cada 5 minutos y calculada por mes calendario, sin contar las ventanas de mantenimiento programado; 0 ventanas de mantenimiento programadas durante los días de cierre de Opinión de Cumplimiento, la semana del comité y la ceremonia de marzo. Verificación: registro del monitoreo externo (health check cada 5 minutos) y revisión del calendario de despliegues contra las fechas críticas declaradas por Coordinación AMPIP. Nota: cifra propuesta por el equipo de desarrollo (ver "Supuestos y pendientes con el cliente").

**RNF-09: Carga desde navegador móvil.** Categoría: usabilidad. Métrica: la pantalla de carga de evidencias funciona en Chrome y Safari para Android e iOS sin instalación adicional. Verificación: prueba manual de aceptación en ambos navegadores, subiendo una foto tomada con la cámara del dispositivo.

**RNF-10: Escalar de 41 a 70-80 parques.** Categoría: escalabilidad. Métrica: el esquema de base de datos soporta 80 parques con hasta 1,500 evidencias cada uno sin cambios de esquema (DDL); el tiempo de respuesta de la vista de cartera (RF-07) con 80 parques no se degrada más del 20 % respecto al de 41 parques. Verificación: prueba de carga con datos sintéticos. Nota: cifra propuesta por el equipo de desarrollo (ver "Supuestos y pendientes con el cliente").

**RNF-11: Zona horaria.** Categoría: mantenibilidad. Métrica: todas las fechas del sistema (atraso de criterios, vencimiento del distintivo, fechas de término y actualización del programa, avisos) se calculan y comparan en la zona horaria America/Mexico_City; el corte de "día vencido" ocurre a las 00:00 hora de Ciudad de México. Verificación: prueba automatizada que fija la hora del servidor en UTC y confirma que las comparaciones de fecha siguen dando el resultado esperado en hora de México.

**RNF-12: Canal de notificación.** Categoría: mantenibilidad. Métrica: todo aviso del sistema (invitación de alta, notificación de observación, avisos de vencimiento y de auditoría) se envía por correo electrónico a la dirección registrada del usuario; un fallo de envío se reintenta hasta 3 veces y, si falla definitivamente, se registra en la bitácora. Verificación: prueba automatizada que simula un proveedor de correo caído y confirma los 3 reintentos y el registro de error.

**RNF-13: Respaldos.** Categoría: mantenibilidad. Métrica: la base de datos y los archivos de evidencia se respaldan con frecuencia diaria y una retención de 30 días; se documenta una prueba de restauración cada mes. Verificación: revisión del registro de respaldos y de la bitácora de la prueba de restauración del mes anterior.

**RNF-14: Retención de evidencias.** Categoría: mantenibilidad. Métrica: las evidencias de un parque se conservan mientras su distintivo esté vigente más un ciclo completo de renovación, es decir, hasta 6 años desde la fecha en que el dictamen "otorgar" quedó firmado (RF-14, RD-08); pasado ese plazo, pueden depurarse. La bitácora (RNF-03) y los dictámenes (RF-14) no se eliminan nunca, sin importar la antigüedad. Verificación: prueba automatizada que crea una evidencia con fecha de dictamen simulada hace más de 6 años y confirma que el proceso de depuración la marca elegible para borrado, y una segunda prueba que confirma que un registro de bitácora o de dictamen con la misma antigüedad permanece intacto.

### 3.3 Requerimientos de dominio

- **RD-01:** cada criterio se marca O, R o NA por tipo de PI; los NA quedan fuera del cálculo de cumplimiento.
- **RD-02:** el cumplimiento de los criterios O, sin contar los NA, es la cifra que determina si procede el dictamen: número de criterios O en estado de calificación "cumplido" (RF-27) entre número de O aplicables, por cien. El avance general se calcula sobre el total de O+R aplicables: número de O+R en estado "cumplido" entre número de O+R aplicables, por cien; un criterio R en estado "no cumplido" no cuenta en contra del cumplimiento de O.
- **RD-03:** auditorías internas al menos dos veces al año; externas, por tercero acreditado, al menos una vez cada dos años.
- **RD-04:** el estándar 1 (análisis de riesgos, política, plan de contingencia) condiciona la calificación de los estándares 2, 3 y 7.
- **RD-05:** el catálogo es propiedad de AMPIP. La APPI y el consultor asignado de un parque pueden ver, dentro del sistema, los criterios aplicables al tipo de PI de ese parque; el archivo maestro con los 286 criterios y sus cuatro columnas O/R/NA solo lo puede descargar Coordinación AMPIP, y no se comparte con terceros ajenos al programa (ver RF-25).
- **RD-06:** al renovar, la evaluación se hace contra la versión del catálogo vigente en ese momento, no contra la original.
- **RD-07:** un cambio de tipo de PI se evalúa según la situación real al momento de la Opinión final; aparecen criterios que antes eran NA.
- **RD-08:** el distintivo tiene vigencia de tres años, que inicia en la fecha en que el dictamen "otorgar" queda firmado por el Director General (RF-14); la renovación no repite el programa completo de diez meses. La cifra de tres años viene solo de la Parte A (personaje simulado); el cliente real (Parte C) no la confirmó (ver "Supuestos y pendientes con el cliente").
- **RD-09:** el dictamen tiene dos valores: otorgar o no otorgar. Se elimina "otorgar con condiciones": el cliente real fue explícito en que el expediente para dictaminar necesita la autoevaluación revisada y un dictamen del consultor con visto bueno, y en que AMPIP nunca ha entregado el distintivo con la autoevaluación sin terminar (P2, Parte C). "Otorgar" solo se puede capturar (registrar) si se cumplen tres condiciones: la autoevaluación está revisada (ningún criterio O o R aplicable sigue en "pendiente" ni en "en revisión"), el consultor asignado emitió una Opinión de Cumplimiento final favorable, y el 100 % de los criterios O están cumplidos. Si falta cualquiera de las tres, corresponde capturar "no otorgar". Esta validación ocurre una sola vez, al capturar el dictamen; firmarlo (RF-14) no la repite.
- **RD-10:** el asterisco (*) es un atributo del catálogo cuyo significado no está definido; ningún comportamiento del sistema depende de él hasta que AMPIP lo confirme.
- **RD-11:** el sistema no suspende ni retira el distintivo de forma automática; cualquier sanción requiere aprobación del Consejo.
- **RD-12:** el sistema no requiere licencia por usuario de cada parque ni pago de auditorías de seguridad informática o certificaciones externas.
- **RD-13:** cada parque en el programa tiene una fecha de término y una fecha de actualización anual; la actualización del programa es anual (P1, Parte C).

## Anexo. Matriz de trazabilidad

| RF | Caso(s) de uso (casos_de_uso.puml) | Criterios de aceptación | Fuente |
|----|--------------------------------------|--------------------------|--------|
| RF-01 | Cargar catálogo de criterios | RF-01-AC-1 a AC-4 | P7 Parte A; P3/P7 Parte B |
| RF-02 | Dar de alta parque | RF-02-AC-1 a AC-3 | P1/P7 Parte A; V-05 |
| RF-03 | Dar de alta usuario | RF-03-AC-1 a AC-3 | P7 Parte A |
| RF-04 | Autoevaluar diagnóstico | RF-04-AC-1, AC-2 | P1/P7 Parte A; P3 Parte B |
| RF-05 | Subir evidencia; Registrar observación (extend de Revisar evidencia) | RF-05-AC-1 a AC-4 | P1/P7 Parte A; V-01/V-02 |
| RF-06 | Validar archivo de evidencia (tamaño y tipo) (include de Subir evidencia) | RF-06-AC-1 a AC-5 | P6 Parte A; P3 Parte B |
| RF-07 | Consultar avance de parques | RF-07-AC-1 a AC-3 | P5 Parte A; V-02 |
| RF-08 | Calcular cumplimiento por parque (include de Consultar avance) | RF-08-AC-1 a AC-3 | P3/P7 Parte A |
| RF-09 | Registrar plan de trabajo (independiente); Detectar atraso de criterio (include de Consultar avance de parques) | RF-09-AC-1 a AC-4 | P1/P7 Parte A; V-15 |
| RF-10 | Asignar consultor a parque | RF-10-AC-1 a AC-3 | P2 Parte A |
| RF-11 | Actualizar tipo de PI del parque; Recalcular criterios aplicables (include) | RF-11-AC-1 a AC-4 | P3 Parte A; P7 Parte B |
| RF-12 | Emitir opinión de cumplimiento | RF-12-AC-1 a AC-6 | P1/P7 Parte A; P2 Parte C; V-14 |
| RF-13 | Abrir sesión de comité; Otorgar acceso temporal a consultor de comité (include); Validar expediente para comité (include, RF-15); Consultar expediente en sesión de comité | RF-13-AC-1 a AC-3 | P5/P7 Parte A; P2 Parte A; P2 Parte C |
| RF-14 | Registrar dictamen | RF-14-AC-1 a AC-8 | P2 Parte C; P2/P7 Parte A; V-04/V-16 |
| RF-15 | Validar expediente para comité (include de Abrir sesión de comité) | RF-15-AC-1 a AC-3 | P2 Parte C |
| RF-16 | Registrar revisión de análisis de riesgos | RF-16-AC-1 a AC-4 | Seguimiento P1/P2 Parte A |
| RF-17 | Bloquear calificación sin análisis de riesgos (extend de Calificar criterio) | RF-17-AC-1 a AC-3 | P1 Parte A y B; P7 Parte B |
| RF-18 | (Posterior, sin caso de uso en el diagrama actual) | RF-18-AC-1, AC-2 | P4 Parte A y B |
| RF-19 | (Posterior) | RF-19-AC-1 a AC-3 | P4/P7 Parte A |
| RF-20 | (Posterior) | RF-20-AC-1, AC-2 | P4 Parte A; V-10 |
| RF-21 | Generar reporte mensual de Dirección | RF-21-AC-1, AC-2 | P7 Parte A |
| RF-22 | (Posterior) | RF-22-AC-1, AC-2 | P7 Parte A |
| RF-23 | Consultar avance consolidado de portafolio | RF-23-AC-1, AC-2 | P2 Parte A |
| RF-24 | Definir evidencia suficiente por criterio | RF-24-AC-1, AC-2 | P3/P7 Parte A |
| RF-25 | Consultar catálogo del parque (extend desde Autoevaluar diagnóstico) | RF-25-AC-1 a AC-4 | P7 Parte A |
| RF-26 | Iniciar sesión | RF-26-AC-1 a AC-6 | V-03, validación independiente del SRS (Parte 6) |
| RF-27 | Calificar criterio (extend de Revisar evidencia) | RF-27-AC-1 a AC-8 | V-01/V-02, validación independiente del SRS (Parte 6) |
| RF-28 | Crear generación | RF-28-AC-1 a AC-3 | V-08, validación independiente del SRS (Parte 6) |
| RF-29 | Dar de baja usuario o parque | RF-29-AC-1 a AC-3 | V-09, validación independiente del SRS (Parte 6) |
| RF-30 | Registrar fechas del programa | RF-30-AC-1 a AC-3 | P1 Parte C |
| RF-31 | Consultar historial de parques | RF-31-AC-1 a AC-3 | P3 Parte C |

## Supuestos y pendientes con el cliente

- **Asterisco (*) en criterios del catálogo:** su significado no está definido en la Guía ni en el checklist 2023 (RD-10). Ningún comportamiento del sistema debe depender de él hasta que AMPIP lo confirme.
- **Tratamiento de datos personales del estándar 7:** antecedentes, estudios socioeconómicos y clínicos de guardias y personal. RNF-04 propone un acceso restringido, pero el tratamiento exacto (cifrado adicional, plazo de retención, aviso de privacidad) está pendiente de validación con el abogado de AMPIP.
- **Vigencia del registro de revisión del análisis de riesgos:** RF-16 define que un registro deja de estar vigente al aparecer uno más reciente del mismo ciclo, o al iniciar un ciclo de renovación sin revisión nueva. Es una definición de diseño para poder construir el bloqueo de RF-17; no está confirmada por AMPIP.
- **Concurrencia de diseño (RNF-07) y demás cifras de rendimiento, disponibilidad y escalabilidad (RNF-06, RNF-08, RNF-10):** ninguna de estas cifras sale del transcript ni de la Guía; son propuestas del equipo de desarrollo para poder construir pruebas de carga durante las 12 semanas, pendientes de validar con AMPIP antes de operar con parques reales.
- **Regla de roles incompatibles (RF-03-AC-2):** que un usuario no pueda ser APPI y Consultor del mismo parque a la vez es un supuesto de buena práctica, no una regla que haya pedido algún stakeholder; se mantiene hasta que se confirme o se retire con AMPIP.
- **Vigencia de tres años del distintivo (RD-08):** viene solo de la Parte A (personaje simulado del transcript). El cliente real (Parte C) no la confirmó ni la contradijo; sigue en tres años porque nadie la ha corregido, pero queda pendiente de validar con AMPIP antes de operar con parques reales. Lo mismo aplica a RF-19 (aviso de vencimiento seis y tres meses antes), que depende de esa misma cifra.
- **Video como evidencia (RF-06):** la carga directa de archivos de video queda fuera de alcance de las 12 semanas; la evidencia de CCTV se sustituye por fotografía o captura de pantalla con fecha visible, como ya acepta el consultor en la práctica (P3, Parte B). Si AMPIP considera esto insuficiente para alguna generación futura, hace falta definir un mecanismo de carga de video (compresión, servicio externo o carga por partes) que no entra en este entregable.
- **Descarga del archivo maestro del catálogo (RD-05, RF-25):** se resolvió que solo Coordinación AMPIP puede descargarlo completo, y que la APPI y el consultor asignado solo ven los criterios de su(s) parque(s). Queda pendiente confirmar con AMPIP si el consultor asignado necesita alguna vez el archivo completo (por ejemplo, para capacitación) fuera del sistema.
- **RF-26 (Autenticación) no viene del transcript:** ni la Parte A ni la Parte B mencionan cómo entran los usuarios al sistema; se dio por hecho porque toda la operación descrita (P1 a P7) ya asume una sesión iniciada. Los parámetros (5 intentos, bloqueo de 15 min, enlace de recuperación de 30 min de un solo uso, expiración por 60 min de inactividad) los decidí en esta revisión, no vienen de un stakeholder de AMPIP; quedan pendientes de validar con el área de sistemas de AMPIP antes de operar con usuarios reales.
- **Opinión intermedia sin mínimo de cumplimiento general, pero con precondición real (RF-12):** el agente revisor (V-14) propuso condicionar la Opinión intermedia a que las fases de Diagnóstico, Plan de trabajo y Política de seguridad estén en "cumplido". No adopté esa condición literal porque contradice lo que dijo la coordinadora del programa (P3, Parte A: "la Opinión intermedia no exige nada, es para medir avance y avisar a tiempo"), codificado en RD-09. En la sincronización final encontré la precondición real que sí existe en el transcript: la coordinadora fue explícita en P1, Parte A, en que ninguna Opinión (intermedia o final) se emite sin política de seguridad firmada y sin análisis de riesgos entregado. La agregué como RF-12-AC-4 y AC-5 (criterio 1.2 calificado "cumplido" y análisis de riesgos vigente), en vez del umbral que propuso el agente revisor.
- **Separación de "borrador" y "firmado" en el dictamen (RF-14, V-16):** el transcript no distingue quién captura el dictamen de quién lo hace definitivo; introduje esa separación (Coordinación AMPIP o consultor de comité capturan en "borrador", solo el Director General firma) como decisión de diseño para que la regla de las tres condiciones de "otorgar" (RD-09) tenga un momento único de verificación, que además precisé en el cierre de sincronización: la validación ocurre al capturar el dictamen, no al firmarlo. Queda pendiente confirmar con AMPIP si el consultor de comité debe poder capturar el borrador o si ese paso es exclusivo de Coordinación.
- **Generación (RF-28) y baja de usuario o parque (RF-29):** ambos casos estaban implícitos en el resto del catálogo (RF-01, RF-02, RF-10 asumían una generación existente; P4 de la Parte A mencionaba consultores que ya no colaboraban con AMPIP sin que hubiera una acción para retirarles el acceso). Se agregaron como RF nuevos; no hay confirmación explícita de AMPIP sobre el flujo exacto de creación de una generación ni sobre si dar de baja un parque debe conservar su historial visible en algún reporte histórico.
- **Comparación de calificaciones entre consultores (I6, fuera de las 12 semanas):** el transcript documenta que "cada consultor califica distinto: uno te acepta una foto de la barda como evidencia y otro te exige el plano con la memoria técnica" (P2, Parte A) y lista explícitamente esta necesidad (I6: "comparación de calificaciones entre consultores para reducir la disparidad de criterio"). No entra en el entregable de 12 semanas porque exigiría un panel de analítica entre consultores que no está en el alcance de MVP feb-2027 ni de 2027. La mitigación parcial que sí queda en el sistema es RF-24 (definir evidencia suficiente por criterio): estandariza qué cuenta como evidencia suficiente antes de que cada consultor decida, sin resolver la disparidad de criterio en la calificación final.
- **Dictamen binario, "otorgar" o "no otorgar" (RD-09, RF-14, RF-15):** la Parte A (personaje simulado) describía un dictamen de tres valores, incluido "otorgar con condiciones" con fecha límite por obligatorio pendiente. El cliente real (Parte C, P2) lo contradijo de forma directa: "si no está terminada no entregamos". Elimino la tercera opción y muevo la validación de "condiciones" a un candado más temprano, antes de abrir la sesión de comité (RF-15): autoevaluación revisada y Opinión de Cumplimiento final favorable. Queda pendiente confirmar con AMPIP qué pasa hoy, en la práctica, con los parques a los que ya se les otorgó "con condiciones" bajo la regla anterior; el transcript no lo cubre.
- **Aviso de la actualización anual del programa (RD-13, RF-30):** el cliente real no precisó con cuánta anticipación debe avisar el sistema antes de que venza la fecha de actualización, ni a quién además de Coordinación AMPIP. RF-30 solo marca el parque como atrasado cuando la fecha ya pasó; un aviso previo, si se necesita, queda pendiente de definir con AMPIP.
- **Alta de parque histórico sin expediente (RF-31):** el cliente real no dijo qué pasa si más adelante se decide migrar el expediente completo de un parque dado de alta como histórico, ni si ese parque puede reactivarse en una generación futura. RF-31 solo cubre el alta con datos mínimos y su consulta; la migración sigue fuera de alcance (1.2).
