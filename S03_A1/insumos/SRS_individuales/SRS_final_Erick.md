# Especificación de Requisitos de Software (SRS)

# 1. Introducción

## 1.1 Propósito del documento

Este documento especifica los requisitos de software de SGPIS (Sistema de Gestión del Programa Parque Industrial Seguro) y sirve como referencia para AMPIP, las APPI, consultores y el equipo de desarrollo durante el diseño, implementación, pruebas y validación del sistema.

Los requerimientos se expresan de forma verificable y se organizan en requerimientos funcionales, no funcionales y de dominio. Los puntos todavía no confirmados con AMPIP se identifican explícitamente como pendientes de validación y no se consideran requisitos definitivos.

## 1.2 Alcance del sistema

SGPIS será una plataforma web para administrar el Programa Parque Industrial Seguro de AMPIP mediante un expediente digital centralizado por parque industrial.

La primera versión cubrirá el proceso desde el registro del parque hasta el dictamen y seguimiento del distintivo. Incluirá: registro e incorporación, gestión de etapas, generación del checklist aplicable, autoevaluación, carga y versionado de evidencias, revisión y observaciones, visitas de validación, cambios de tipo de parque, dictamen, vigencia del distintivo, alertas, supervisión de expedientes y trazabilidad de acciones.

Quedan fuera de la primera versión los pagos y cuotas del programa, aplicación móvil nativa, funcionamiento sin conexión, firma electrónica avanzada, integraciones con sistemas externos, analítica avanzada, almacenamiento directo de video, portal público y renovación completamente automatizada.

## 1.3 Definiciones y acrónimos

| Término | Definición |
|---|---|
| AMPIP | Asociación Mexicana de Parques Industriales Privados; organización responsable del Programa Parque Industrial Seguro. |
| APPI | Administración del Parque Industrial; representa al parque dentro del programa y es responsable de integrar su expediente. |
| PI | Parque Industrial. Los tipos considerados son: en construcción abierto, en construcción cerrado, en operación abierto y en operación cerrado. |
| SGPIS | Sistema de Gestión del Programa Parque Industrial Seguro. |
| Checklist | Conjunto de criterios de seguridad aplicables a un parque según su tipo de PI. La referencia del proyecto es el checklist AMPIP "Criterios Mínimos de Seguridad para Parques Industriales", versión 2023. |
| O | Obligatorio. Clasificación de un criterio que debe cumplirse para el tipo de PI correspondiente. |
| R | Recomendado. Clasificación de un criterio cuya aplicabilidad se distingue de los criterios obligatorios. |
| NA | No aplica. Clasificación del catálogo que indica que un criterio no corresponde al tipo de PI. Si la APPI solicita tratar como no aplicable un criterio clasificado O o R, deberá justificarlo y la decisión requerirá validación de AMPIP; este mecanismo debe confirmarse con el stakeholder real. |
| Evidencia | Documento, imagen, registro u otro archivo que respalda el cumplimiento de uno o más criterios. |
| Observación | Solicitud formal de corrección o aclaración emitida por AMPIP durante la revisión de una evidencia. |
| Hallazgo | Incumplimiento, diferencia o condición detectada durante una revisión o visita de validación que requiere seguimiento. |
| Dictamen | Resultado formal del proceso de evaluación previo a la emisión del distintivo. |
| Distintivo | Reconocimiento "Parque Industrial Seguro" emitido por AMPIP y sujeto a vigencia y renovación. |

# 2. Descripción general

## 2.1 Perspectiva del producto

Actualmente, el Programa Parque Industrial Seguro se apoya en correos, hojas de cálculo, carpetas y archivos separados. Esto dificulta identificar el estado real de cada parque, controlar versiones de evidencias, relacionar observaciones con criterios y conocer qué expedientes están detenidos, próximos a vencer o listos para dictamen.

SGPIS centralizará esa información en un expediente único por parque. El expediente contendrá el tipo de PI, etapa del programa, checklist aplicable, autoevaluación, evidencias, observaciones, visitas, hallazgos, dictamen, distintivo y trazabilidad de las acciones realizadas.

## 2.2 Funciones del producto

SGPIS deberá proporcionar, como mínimo, las siguientes capacidades:

- Registrar parques e iniciar expedientes.
- Permitir a AMPIP aceptar o rechazar solicitudes de incorporación.
- Gestionar las etapas del programa y su estado.
- Generar el checklist aplicable según el tipo de PI.
- Permitir a la APPI registrar su autoevaluación.
- Gestionar evidencias y conservar su historial de versiones.
- Permitir a AMPIP revisar evidencias y registrar observaciones.
- Permitir a la APPI responder observaciones y presentar correcciones.
- Asignar evaluadores y consultores a expedientes.
- Registrar visitas de validación, hallazgos y acciones correctivas.
- Gestionar solicitudes de cambio de tipo de parque y recalcular el checklist cuando AMPIP autorice el cambio.
- Registrar dictamen, distintivo, vigencia y estado del distintivo.
- Generar alertas de vencimiento.
- Mostrar a AMPIP el estado de su cartera de expedientes.
- Mantener una bitácora de acciones realizadas sobre las evidencias.
- Permitir al consultor registrar recomendaciones internas sin convertirlas en decisiones formales.
- Permitir al consultor emitir el visto bueno o dictamen requerido como parte del expediente previo a la emisión del distintivo.
- Gestionar varios usuarios de una APPI y un contacto principal.
- Permitir iniciar y dar seguimiento a una solicitud de renovación sin renovar automáticamente el distintivo.
- Consultar el historial de los parques que han participado en el programa.
- Registrar y consultar la fecha anual de término o actualización del programa para apoyar la detección de atrasos.

## 2.3 Características del usuario

| Usuario | Responsabilidades e interacción |
|---|---|
| Representante de la APPI | Registra y mantiene la información del parque, realiza la autoevaluación, carga evidencias, responde observaciones, solicita cambios de tipo de parque y consulta el avance de su expediente. |
| Consultor | Apoya a la APPI en la preparación y seguimiento de evidencias de los parques asignados, puede registrar recomendaciones internas y emite el visto bueno o dictamen del consultor requerido como parte del expediente previo a la emisión del distintivo. |
| Evaluador de AMPIP | Revisa solicitudes y evidencias de los expedientes asignados, registra observaciones, valida correcciones y participa en visitas de validación. |
| Responsable del programa en AMPIP | Supervisa la cartera completa, asigna evaluadores, autoriza cierres y cambios relevantes, consulta vencimientos y coordina los casos que pueden pasar a dictamen. |

## 2.4 Restricciones

### Técnicas y de seguridad

- SGPIS será una plataforma web.
- Todo acceso requerirá autenticación.
- La autorización dependerá del rol del usuario y del parque o expediente asignado.
- La APPI solo podrá acceder a su propio parque.
- El consultor solo podrá acceder a los parques a los que esté formalmente asignado.
- El evaluador de AMPIP solo podrá acceder a los expedientes asignados, salvo perfiles de supervisión autorizados.
- Los documentos y evidencias no deberán ser accesibles mediante enlaces públicos.
- La primera versión deberá admitir PDF, JPG, PNG, XLSX y DOCX.
- El tamaño inicial máximo por archivo será de 50 MB, sujeto a validación con datos reales de operación.
- El volumen inicial esperado es de 100 a 200 parques activos o en proceso, con aproximadamente 2 a 6 usuarios APPI por parque y menos de 30 usuarios internos de AMPIP.
- Un expediente podrá contener más de cien evidencias en los casos de mayor carga.

### Negocio y alcance

- El checklist de referencia del proyecto es la versión 2023 de "Criterios Mínimos de Seguridad para Parques Industriales".
- La aplicabilidad de los criterios dependerá del tipo de PI.
- Los textos completos del checklist solo podrán cargarse con autorización de AMPIP.
- Para pruebas podrá utilizarse un subconjunto del checklist.
- De acuerdo con la entrevista con el stakeholder real, la primera versión deberá priorizar la autoevaluación y la consulta del historial de parques participantes.
- Quedan fuera de la primera versión los pagos y cuotas, la aplicación móvil nativa, la firma electrónica avanzada, las integraciones con sistemas de terceros, el almacenamiento directo de video y los flujos complejos de comité o votación.

### Pendientes de validación

Los siguientes puntos deberán confirmarse con el stakeholder real antes de convertirse en requisitos definitivos:

- Vigencia exacta del distintivo.
- Plazo obligatorio para iniciar la renovación.
- Alcance de revisión durante la renovación.
- Etapa límite para permitir un cambio de tipo de parque.
- Participación directa de terceros o validadores externos.
- Instancia final que autoriza formalmente el distintivo.
- Periodo obligatorio de conservación de expedientes y evidencias.
- Límite máximo definitivo por archivo.
- Aceptación de DWG u otros formatos adicionales.
- **Secuencia exacta de fases del programa:** `proyecto_base.md` describe diagnóstico, plan de trabajo, política de seguridad, análisis de riesgos, implementación de estándares, Opiniones de Cumplimiento y Evaluación de Desempeño; la entrevista simulada describió un flujo diferente. La secuencia definitiva debe validarse antes de fijarla en el diseño.
- **Tratamiento de NA:** debe confirmarse si una APPI puede solicitar que un criterio O/R sea tratado como no aplicable o si NA depende exclusivamente de la clasificación del catálogo por tipo de PI.
- **Disponibilidad requerida del sistema:** la entrevista no definió un SLA ni ventanas máximas de indisponibilidad.
- **Retención de evidencias y bitácoras:** se confirmó que no deben desaparecer al vencer el distintivo, pero no se definió el periodo mínimo de conservación.

# 3. Requerimientos específicos

## 3.1 Requerimientos funcionales

### RF-01: Registrar parque e iniciar expediente

**Descripción:** El sistema deberá permitir registrar un parque industrial con sus datos generales, ubicación, razón social y contacto responsable, y crear un expediente asociado.

**RF-01-AC-1**

**Dado que** el representante de una APPI proporciona los datos de un parque,  
**cuando** completa el registro con razón social, ubicación y contacto responsable,  
**entonces** el sistema registra el parque y crea un expediente asociado.

**RF-01-AC-2**

**Dado que** el registro de un parque no contiene razón social, ubicación o contacto responsable,  
**cuando** el usuario intenta completar el registro,  
**entonces** el sistema no completa el registro ni crea el expediente asociado.

**RF-01-AC-3**

**Dado que** se ha registrado un parque y se ha creado su expediente,  
**cuando** se consulta el expediente,  
**entonces** el sistema muestra una referencia única al parque registrado.

### RF-02: Evaluar solicitud de incorporación

**Descripción:** El sistema deberá permitir a AMPIP aceptar o rechazar la incorporación de un parque después de revisar la información y documentación de su solicitud.

**RF-02-AC-1**

**Dado que** existe una solicitud con información y documentación disponibles para revisión,  
**cuando** un usuario autorizado de AMPIP registra una decisión,  
**entonces** el sistema permite seleccionar aceptación o rechazo y asocia la decisión a la solicitud.

**RF-02-AC-2**

**Dado que** una decisión de incorporación fue registrada,  
**cuando** se consulta la solicitud,  
**entonces** el sistema muestra la decisión, el usuario que la tomó y la fecha de registro.

**RF-02-AC-3**

**Dado que** una solicitud fue rechazada,  
**cuando** se intenta avanzar su expediente a una etapa posterior del programa,  
**entonces** el sistema impide el avance.

### RF-03: Gestionar etapas del expediente

**Descripción:** El sistema deberá gestionar el estado y avance de las fases del Programa Parque Industrial Seguro que AMPIP configure como vigentes para el proceso.

> **Pendiente crítico de validación:** las fuentes disponibles describen secuencias de fases diferentes. El sistema debe permitir representar la secuencia validada por AMPIP sin asumir como definitiva la propuesta de la entrevista simulada.

**RF-03-AC-1**

**Dado que** AMPIP ha definido la secuencia vigente de fases del programa,  
**cuando** se consulta el seguimiento de un expediente,  
**entonces** el sistema muestra todas las fases configuradas, su estado y cuál es la fase actual.

**RF-03-AC-2**

**Dado que** una APPI ha entregado información correspondiente a una fase,  
**cuando** la validación formal todavía no ha sido registrada,  
**entonces** el sistema diferencia la información entregada de una fase validada.

**RF-03-AC-3**

**Dado que** una fase está pendiente de cierre,  
**cuando** un usuario sin permiso para autorizar cierres intenta cerrarla,  
**entonces** el sistema rechaza la operación y conserva el estado anterior.


### RF-04: Generar checklist y registrar autoevaluación

**Descripción:** El sistema deberá generar el checklist aplicable según el tipo de PI y permitir a la APPI registrar su autoevaluación por criterio.

**RF-04-AC-1**

**Dado que** un parque tiene registrado uno de los tipos de PI definidos,  
**cuando** se genera su checklist,  
**entonces** el sistema incluye los criterios aplicables a ese tipo y muestra para cada uno su clasificación O, R o NA.

**RF-04-AC-2**

**Dado que** la APPI consulta el checklist aplicable de su parque,  
**cuando** registra una valoración para un criterio aplicable,  
**entonces** el sistema conserva la autoevaluación asociada a ese criterio y parque.

**RF-04-AC-3**

**Dado que** un criterio está clasificado como O o R para el tipo de PI y la APPI solicita tratarlo excepcionalmente como no aplicable,  
**cuando** intenta registrar la solicitud sin una justificación,  
**entonces** el sistema no registra la solicitud de excepción.

> **Pendiente de validación:** debe confirmarse con AMPIP si este tipo de excepción sobre criterios O/R está permitido.

### RF-05: Gestionar evidencias

**Descripción:** El sistema deberá permitir cargar, consultar, sustituir y vincular evidencias a uno o varios criterios, manteniendo la versión vigente y el historial de versiones anteriores.

**RF-05-AC-1**

**Dado que** una APPI o un usuario autorizado carga una evidencia,  
**cuando** la vincula con uno o varios criterios de su parque,  
**entonces** el sistema conserva las asociaciones de la misma evidencia con todos los criterios seleccionados.

**RF-05-AC-2**

**Dado que** existe una evidencia vinculada a un criterio,  
**cuando** se sustituye por una nueva versión,  
**entonces** el sistema identifica la nueva versión como vigente y conserva la versión anterior en el historial.

**RF-05-AC-3**

**Dado que** una evidencia se elimina lógicamente,  
**cuando** se consulta su historial,  
**entonces** la evidencia eliminada permanece registrada en el historial.

**RF-05-AC-4**

**Dado que** un usuario está autorizado para consultar un criterio,  
**cuando** consulta sus evidencias asociadas,  
**entonces** el sistema muestra las evidencias vinculadas y su versión vigente.

### RF-06: Revisar evidencias por criterio

**Descripción:** El sistema deberá permitir al evaluador de AMPIP registrar para cada evidencia un resultado de aprobación, rechazo u observación y añadir comentarios de revisión.

**RF-06-AC-1**

**Dado que** un evaluador de AMPIP tiene acceso a una evidencia de un expediente asignado,  
**cuando** registra su revisión,  
**entonces** el sistema permite seleccionar exactamente uno de los resultados aprobado, rechazado u observado.

**RF-06-AC-2**

**Dado que** el evaluador registra el resultado de una revisión,  
**cuando** guarda la revisión con su comentario,  
**entonces** el sistema la asocia con la evidencia y el criterio revisados y registra evaluador y fecha.

**RF-06-AC-3**

**Dado que** AMPIP registró una revisión de una evidencia de un parque,  
**cuando** la APPI consulta el resultado de esa evidencia,  
**entonces** el sistema muestra el resultado y el comentario de revisión.

### RF-07: Atender observaciones

**Descripción:** El sistema deberá permitir a la APPI responder observaciones, adjuntar evidencia corregida y consultar su estado hasta el cierre.

**RF-07-AC-1**

**Dado que** AMPIP emitió una observación para un parque,  
**cuando** se consulta la observación,  
**entonces** el sistema muestra su responsable, fecha, respuesta y estado.

**RF-07-AC-2**

**Dado que** una observación permanece abierta,  
**cuando** la APPI registra una respuesta y adjunta una nueva evidencia o una versión corregida,  
**entonces** el sistema asocia la respuesta y la evidencia con la observación.

**RF-07-AC-3**

**Dado que** una observación tiene una corrección presentada,  
**cuando** AMPIP valida la corrección y marca la observación como cerrada,  
**entonces** el sistema conserva la observación, su respuesta y su historial de cierre.

### RF-08: Asignar evaluadores y consultores

**Descripción:** El sistema deberá permitir registrar, modificar y retirar asignaciones de evaluadores y consultores sobre un expediente.

**RF-08-AC-1**

**Dado que** existe un expediente,  
**cuando** un usuario autorizado de AMPIP asigna un evaluador,  
**entonces** el sistema asocia al evaluador con el expediente y permite identificarlo al consultar el expediente.

**RF-08-AC-2**

**Dado que** existe un parque o expediente,  
**cuando** un usuario autorizado de AMPIP asigna un consultor,  
**entonces** el sistema asocia al consultor con el parque o expediente correspondiente.

**RF-08-AC-3**

**Dado que** existe una asignación de evaluador o consultor,  
**cuando** un usuario autorizado de AMPIP la modifica o retira,  
**entonces** el sistema conserva en el historial el usuario que realizó el cambio y la fecha del cambio.

### RF-09: Registrar visita de validación

**Descripción:** El sistema deberá permitir registrar una visita de validación con su fecha, participantes, hallazgos, evidencias adicionales y acciones correctivas.

**RF-09-AC-1**

**Dado que** existe un expediente,  
**cuando** se registra una visita de validación con fecha y hallazgos,  
**entonces** el sistema asocia la visita a ese expediente y conserva su fecha y hallazgos.

**RF-09-AC-2**

**Dado que** existe una visita de validación registrada,  
**cuando** se agregan evidencias adicionales,  
**entonces** el sistema las asocia con la visita.

**RF-09-AC-3**

**Dado que** un hallazgo fue registrado durante una visita,  
**cuando** se registra una acción correctiva y su estado de cierre,  
**entonces** el sistema conserva ambos datos asociados al hallazgo.

**RF-09-AC-4**

**Dado que** se registra una visita de validación,  
**cuando** se registran sus participantes,  
**entonces** el sistema conserva los participantes asociados a la visita.

### RF-10: Gestionar cambio de tipo de parque

**Descripción:** El sistema deberá permitir a la APPI solicitar un cambio de tipo de PI y, después de la autorización de AMPIP, recalcular los criterios aplicables.

**RF-10-AC-1**

**Dado que** la APPI requiere modificar el tipo de PI de su parque,  
**cuando** presenta la solicitud,  
**entonces** el sistema registra el tipo solicitado y el motivo del cambio.

**RF-10-AC-2**

**Dado que** existe una solicitud de cambio de tipo pendiente de autorización,  
**cuando** la APPI o un usuario sin autorización de AMPIP intenta cambiar el tipo del parque,  
**entonces** el sistema conserva el tipo de PI actual.

**RF-10-AC-3**

**Dado que** AMPIP autoriza una solicitud de cambio de tipo de PI,  
**cuando** se registra la autorización,  
**entonces** el sistema actualiza el tipo, recalcula el checklist aplicable y conserva el tipo anterior, el tipo nuevo, la fecha, el aprobador y los criterios agregados, retirados o modificados.

**RF-10-AC-4**

**Dado que** AMPIP autorizó un cambio de tipo de PI,  
**cuando** se consulta el expediente después del recálculo,  
**entonces** las evidencias registradas antes del cambio permanecen en el expediente.

### RF-11: Registrar dictamen y distintivo

**Descripción:** El sistema deberá registrar el dictamen final, la emisión del distintivo, su vigencia y uno de los estados de seguimiento definidos. Para permitir la emisión, el expediente deberá contar con la autoevaluación terminada y con el visto bueno o dictamen favorable del consultor.

**RF-11-AC-1**

**Dado que** la autoevaluación del parque está terminada, los criterios obligatorios aplicables se encuentran cumplidos y validados, los hallazgos requeridos están cerrados y existe un visto bueno o dictamen favorable del consultor,  
**cuando** AMPIP registra el dictamen final,  
**entonces** el sistema permite asociar el dictamen al expediente y continuar con la emisión del distintivo.

**RF-11-AC-2**

**Dado que** la autoevaluación no está terminada o no existe el visto bueno requerido del consultor,  
**cuando** se intenta emitir el distintivo,  
**entonces** el sistema impide completar la emisión.

**RF-11-AC-3**

**Dado que** se registra la emisión de un distintivo,  
**cuando** se consultan sus datos,  
**entonces** el sistema muestra el expediente asociado y la fecha de emisión.

> **Pendiente de validación:** la duración exacta de la vigencia todavía no está definida, por lo que no se establece un criterio definitivo para su cálculo.

**RF-11-AC-4**

**Dado que** un distintivo tiene un estado de seguimiento registrado,  
**cuando** se consulta su seguimiento,  
**entonces** el sistema muestra uno de los estados: vigente, próximo a vencer, vencido, en renovación o con prórroga autorizada.


### RF-12: Generar alertas de vencimiento

**Descripción:** El sistema deberá generar alertas relacionadas con el vencimiento del distintivo y de documentos críticos.

**RF-12-AC-1**

**Dado que** un distintivo tiene una fecha de vencimiento registrada,  
**cuando** faltan 90, 60 o 30 días para esa fecha,  
**entonces** el sistema genera el recordatorio de vencimiento correspondiente.

**RF-12-AC-2**

**Dado que** un documento crítico tiene una fecha de vencimiento registrada,  
**cuando** faltan 60 o 30 días para su vencimiento o llega su fecha de vencimiento,  
**entonces** el sistema genera la alerta correspondiente.

**RF-12-AC-3**

**Dado que** el sistema genera una alerta de vencimiento,  
**cuando** determina sus destinatarios,  
**entonces** incluye al representante principal de la APPI y al responsable del programa en AMPIP.

**Pendiente de validación:** El SRS permite que un consultor asignado reciba copia de una alerta, pero no define la condición ni la configuración que activa ese envío. Por ello no se establece un criterio de aceptación definitivo para ese comportamiento opcional.

### RF-13: Supervisar cartera de expedientes

**Descripción:** El sistema deberá proporcionar a AMPIP una vista de cartera que permita consultar el avance y situación de los expedientes.

**RF-13-AC-1**

**Dado que** un usuario de AMPIP consulta la vista de cartera,  
**cuando** la vista se muestra,  
**entonces** identifica la etapa actual de cada expediente.

**RF-13-AC-2**

**Dado que** existen expedientes con observaciones pendientes,  
**cuando** AMPIP consulta la vista de cartera,  
**entonces** el sistema permite identificarlos.

**RF-13-AC-3**

**Dado que** existen distintivos o documentos próximos a vencer,  
**cuando** AMPIP consulta la vista de cartera,  
**entonces** el sistema muestra los próximos vencimientos.

**RF-13-AC-4**

**Dado que** existen expedientes listos para dictamen,  
**cuando** AMPIP consulta la vista de cartera,  
**entonces** el sistema permite identificarlos y muestra la asignación de evaluadores de los expedientes.

### RF-14: Registrar bitácora de acciones sobre evidencias

**Descripción:** El sistema deberá registrar las acciones sensibles realizadas sobre documentos y evidencias.

**RF-14-AC-1**

**Dado que** un usuario carga, consulta, descarga, reemplaza, modifica metadatos o elimina lógicamente una evidencia,  
**cuando** la acción se realiza,  
**entonces** el sistema registra una entrada de bitácora para esa acción.

**RF-14-AC-2**

**Dado que** el sistema registra una acción en la bitácora,  
**cuando** se consulta la entrada,  
**entonces** incluye el usuario, fecha, hora, expediente, acción realizada y criterio relacionado cuando aplique.

**RF-14-AC-3**

**Dado que** existe una entrada de bitácora de una acción sobre evidencia,  
**cuando** se consulta la evidencia correspondiente,  
**entonces** la entrada permanece asociada a esa evidencia.

**RF-14-AC-4**

**Dado que** existe una entrada de bitácora,  
**cuando** un usuario APPI, consultor o evaluador intenta modificarla o eliminarla,  
**entonces** el sistema rechaza la operación y la entrada permanece sin cambios.


### RF-15: Registrar recomendaciones del consultor

**Descripción:** El sistema deberá permitir al consultor asignado registrar recomendaciones internas para la APPI relacionadas con criterios o evidencias, sin convertirlas en observaciones formales ni modificar el estado de validación de AMPIP.

**RF-15-AC-1**

**Dado que** un consultor está asignado a un parque,  
**cuando** registra una recomendación asociada a un criterio o evidencia de ese parque,  
**entonces** el sistema conserva la recomendación y la hace visible para la APPI correspondiente.

**RF-15-AC-2**

**Dado que** existe una recomendación registrada por un consultor,  
**cuando** se consulta el estado formal del criterio o evidencia,  
**entonces** la recomendación no modifica por sí misma el estado de validación ni se presenta como una observación formal de AMPIP.

### RF-16: Gestionar usuarios de la APPI y contacto principal

**Descripción:** El sistema deberá permitir asociar varios usuarios a una APPI e identificar un único contacto principal para las comunicaciones del expediente.

**RF-16-AC-1**

**Dado que** una APPI tiene varios usuarios registrados,  
**cuando** se consulta la configuración de usuarios del parque,  
**entonces** el sistema muestra los usuarios asociados e identifica cuál es el contacto principal.

**RF-16-AC-2**

**Dado que** una APPI cambia a su contacto principal,  
**cuando** un usuario autorizado registra el cambio,  
**entonces** el sistema conserva un único contacto principal activo para esa APPI.

**RF-16-AC-3**

**Dado que** se genera una alerta dirigida a la APPI,  
**cuando** el sistema determina sus destinatarios,  
**entonces** incluye al contacto principal activo.

### RF-17: Iniciar solicitud de renovación

**Descripción:** El sistema deberá permitir a la APPI iniciar una solicitud de renovación del distintivo y asociar al expediente la información y evidencias actualizadas requeridas para su revisión.

**RF-17-AC-1**

**Dado que** un parque cuenta con un distintivo registrado,  
**cuando** la APPI inicia una solicitud de renovación,  
**entonces** el sistema crea una solicitud asociada al expediente y registra su fecha de inicio.

**RF-17-AC-2**

**Dado que** existe una solicitud de renovación,  
**cuando** la APPI actualiza información o agrega evidencias para la renovación,  
**entonces** el sistema conserva esos elementos asociados a la solicitud.

**RF-17-AC-3**

**Dado que** existe una solicitud de renovación en proceso,  
**cuando** se consulta el distintivo,  
**entonces** el sistema puede identificarlo como “en renovación” sin extender automáticamente su vigencia.

> **Pendiente de validación:** el plazo para iniciar la renovación y el alcance exacto de la reevaluación todavía no están definidos.



### RF-18: Emitir visto bueno del consultor

**Descripción:** El sistema deberá permitir al consultor asignado registrar el visto bueno o dictamen del consultor requerido para que el expediente pueda continuar hacia la emisión del distintivo.

**RF-18-AC-1**

**Dado que** un consultor está asignado a un expediente y la autoevaluación correspondiente está disponible para revisión,  
**cuando** el consultor registra su visto bueno o dictamen,  
**entonces** el sistema conserva el resultado asociado al expediente, junto con el consultor y la fecha de registro.

**RF-18-AC-2**

**Dado que** un expediente no cuenta con el visto bueno o dictamen del consultor requerido,  
**cuando** se consulta su preparación para dictamen final,  
**entonces** el sistema lo identifica como pendiente de este requisito.

### RF-19: Consultar historial de parques

**Descripción:** El sistema deberá conservar y permitir a AMPIP consultar el historial de los parques que han participado en el Programa Parque Industrial Seguro.

**RF-19-AC-1**

**Dado que** existen parques con expedientes actuales o anteriores en el programa,  
**cuando** un usuario autorizado de AMPIP consulta el historial de parques,  
**entonces** el sistema muestra los parques registrados y permite acceder a sus expedientes históricos disponibles.

**RF-19-AC-2**

**Dado que** un parque ha concluido una participación anterior en el programa,  
**cuando** inicia un nuevo proceso o renovación,  
**entonces** el sistema conserva accesible su información histórica sin sobrescribir los expedientes anteriores.

### RF-20: Gestionar actualización anual del programa

**Descripción:** El sistema deberá registrar y mostrar la fecha anual de término o actualización del programa para cada parque, de modo que AMPIP pueda identificar atrasos en el seguimiento.

**RF-20-AC-1**

**Dado que** un expediente tiene registrada una fecha anual de término o actualización,  
**cuando** AMPIP consulta el expediente o la vista de seguimiento,  
**entonces** el sistema muestra dicha fecha.

**RF-20-AC-2**

**Dado que** la fecha anual de término o actualización de un parque ha vencido sin que se registre la actualización correspondiente,  
**cuando** AMPIP consulta la vista de seguimiento,  
**entonces** el sistema identifica el expediente como atrasado.


## 3.2 Requerimientos no funcionales

- RNF-01: El acceso al sistema deberá requerir autenticación y aplicar autorización según el rol y el parque o expediente asignado. | Categoría: seguridad
- RNF-02: La APPI no deberá poder consultar información de otros parques; los consultores y evaluadores solo podrán consultar los expedientes que tengan asignados. | Categoría: seguridad
- RNF-03: La consulta de la bitácora deberá limitarse a perfiles de AMPIP con permiso de supervisión o auditoría; usuarios APPI, consultores y evaluadores no podrán modificar ni eliminar sus entradas. | Categoría: integridad / seguridad
- RNF-04: La primera versión deberá aceptar como mínimo PDF, JPG, PNG, XLSX y DOCX y permitir la selección y carga de varios archivos en una misma operación. | Categoría: compatibilidad / usabilidad
- RNF-05: La solución deberá soportar inicialmente entre 100 y 200 parques activos o en proceso, aproximadamente 2 a 6 usuarios APPI por parque, menos de 30 usuarios internos de AMPIP y más de cien evidencias en los expedientes de mayor carga. | Categoría: capacidad
- RNF-06: La primera versión deberá admitir archivos individuales de hasta 50 MB. Este valor deberá revisarse cuando existan datos reales de operación. | Categoría: capacidad
- RNF-07: La vista de expediente deberá mostrar la fase actual, estado de criterios, observaciones pendientes y siguiente acción; la vista de cartera de AMPIP deberá mostrar próximos vencimientos y expedientes listos para dictamen. | Categoría: usabilidad
- RNF-08: Ningún documento o evidencia deberá ser accesible mediante un enlace público o sin una sesión autenticada con permisos sobre el expediente correspondiente. | Categoría: seguridad

> **Gap pendiente:** no se definió un requisito cuantitativo de disponibilidad, tiempo de respuesta o concurrencia. No se inventa un SLA hasta obtenerlo del stakeholder real.

## 3.3 Requerimientos de dominio

- RD-01: AMPIP será responsable de aceptar o rechazar el ingreso de un parque, supervisar el proceso, cerrar las fases que le correspondan y emitir o autorizar las decisiones finales del programa.
- RD-02: La APPI será responsable de integrar la información de su parque, registrar su autoevaluación, presentar evidencias y atender las observaciones formales que correspondan.
- RD-03: El consultor apoyará a la APPI durante la evaluación y deberá emitir el visto bueno o dictamen del consultor requerido para que el expediente pueda continuar hacia la emisión del distintivo.
- RD-04: El distintivo solo podrá emitirse cuando la autoevaluación esté terminada, exista el visto bueno o dictamen favorable del consultor y se cumplan las demás condiciones de cierre aplicables al expediente.
- RD-05: Una evidencia solo podrá sustentar el cumplimiento de un criterio cuando sea vigente, legible, corresponda al parque evaluado y demuestre lo solicitado por el criterio.
- RD-06: Los criterios clasificados como NA por el catálogo para el tipo de PI no forman parte del cumplimiento exigible. Si la APPI solicita excepcionalmente tratar como no aplicable un criterio O/R, deberá justificarlo y AMPIP deberá resolver la solicitud; la existencia de este mecanismo requiere validación con el stakeholder real.
- RD-07: Un cambio de tipo de PI requerirá solicitud de la APPI y autorización de AMPIP antes de modificar el checklist aplicable.
- RD-08: Toda decisión o validación relevante deberá conservar trazabilidad de quién la realizó, cuándo se realizó y, cuando corresponda, el motivo o comentario asociado.
- RD-09: La renovación del distintivo no será automática por el hecho de que exista una solicitud de renovación en proceso.
- RD-10: Si una renovación se retrasa por incumplimiento o falta de atención de la APPI, el distintivo podrá vencer y permanecer sin estatus vigente hasta completar el proceso.
- RD-11: Si una renovación se retrasa por causa atribuible a AMPIP o por una situación excepcional, AMPIP podrá autorizar una prórroga documentada que indique responsable, motivo y nueva fecha límite.

## 3.4 Gaps pendientes de definición

Los siguientes gaps fueron identificados durante la revisión técnica y no se convierten en requisitos definitivos hasta ser validados:

- Secuencia exacta y reglas de transición entre fases del programa.
- Regla exacta para solicitar o aprobar “No aplica” sobre criterios O/R.
- SLA de disponibilidad y tiempos de respuesta.
- Periodo mínimo de conservación de evidencias, expedientes y bitácoras.
- Condiciones exactas de renovación: ventana de inicio, criterios que se reevaluarán y duración de la vigencia.
- Participación directa de terceros o validadores externos dentro del sistema.