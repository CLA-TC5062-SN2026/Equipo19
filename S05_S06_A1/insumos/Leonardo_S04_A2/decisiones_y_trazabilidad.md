# Sección A — Trazabilidad spec ↔ criterios de aceptación

| ID Criterio | Descripción resumida                                                                                   | Endpoint                                    | Método HTTP | ¿Cubierto? |
| ----------- | ------------------------------------------------------------------------------------------------------ | ------------------------------------------- | ----------- | ---------- |
| RF-01-AC-1  | Validar columnas del CSV y crear una versión activa del catálogo.                                      | —                                           | —           | No         |
| RF-01-AC-2  | Rechazar la carga de catálogo por un usuario sin permisos.                                             | —                                           | —           | No         |
| RF-01-AC-3  | Mostrar la versión del catálogo asociada al expediente sin permitir editarla.                          | —                                           | —           | No         |
| RF-01-AC-4  | Rechazar un CSV inválido e indicar fila y columna del error.                                           | —                                           | —           | No         |
| RF-01-AC-5  | Conservar las versiones anteriores del catálogo y su asociación con las generaciones.                  | —                                           | —           | No         |
| RF-02-AC-1  | Crear un parque con datos válidos y estado activo.                                                     | `/parques`                                  | POST        | Sí         |
| RF-02-AC-2  | Rechazar el alta si no se selecciona un tipo de parque válido.                                         | `/parques`                                  | POST        | Sí         |
| RF-02-AC-3  | Rechazar el alta si la región no es válida.                                                            | `/parques`                                  | POST        | Sí         |
| RF-03-AC-1  | Crear una cuenta APPI y enviar una invitación de activación.                                           | `/usuarios`                                 | POST        | Sí         |
| RF-03-AC-2  | Impedir asignar simultáneamente roles APPI y consultor al mismo parque.                                | `/usuarios/{usuario_id}/roles`              | PUT         | Sí         |
| RF-03-AC-3  | Crear una cuenta de administrador técnico sin acceso a parques ni evidencias.                          | `/usuarios`                                 | POST        | Sí         |
| RF-04-AC-1  | Mostrar únicamente los criterios aplicables al tipo de parque.                                         | —                                           | —           | No         |
| RF-04-AC-2  | Rechazar una respuesta de autoevaluación para un criterio marcado NA.                                  | —                                           | —           | No         |
| RF-05-AC-1  | Registrar una evidencia y actualizar el estado del criterio.                                           | `/parques/{parque_id}/evidencias`           | POST        | Sí         |
| RF-05-AC-2  | Registrar la revisión de una evidencia insuficiente, cambiar su estado y notificar a la APPI.          | `/evidencias/{evidencia_id}/revisiones`     | POST        | Sí         |
| RF-05-AC-3  | Rechazar una revisión u observación realizada por un consultor no asignado al parque.                  | `/evidencias/{evidencia_id}/revisiones`     | POST        | Sí         |
| RF-05-AC-4  | Permitir reenviar una evidencia observada y actualizar su estado.                                      | `/evidencias/{evidencia_id}/revisiones`     | POST        | Sí         |
| RF-05-AC-5  | Guardar los metadatos de la evidencia y su referencia al archivo.                                      | —                                           | —           | No         |
| RF-05-AC-6  | Consultar las versiones de una evidencia y distinguir la vigente.                                      | —                                           | —           | No         |
| RF-05-AC-7  | Asociar un único archivo a varios criterios mediante vínculos individuales.                            | —                                           | —           | No         |
| RF-05-AC-8  | Aceptar archivos válidos de una carga múltiple y rechazar individualmente los inválidos.               | —                                           | —           | No         |
| RF-05-AC-9  | Dar de baja una evidencia enviada conservándola en el historial.                                       | —                                           | —           | No         |
| RF-05-AC-10 | Impedir eliminar una evidencia aceptada.                                                               | —                                           | —           | No         |
| RF-06-AC-1  | Rechazar archivos que excedan el límite de tamaño permitido.                                           | `/parques/{parque_id}/evidencias`           | POST        | Sí         |
| RF-06-AC-2  | Aceptar una imagen válida dentro del límite de tamaño.                                                 | `/parques/{parque_id}/evidencias`           | POST        | Sí         |
| RF-06-AC-3  | Aceptar un archivo cuyo tamaño sea exactamente el límite permitido.                                    | `/parques/{parque_id}/evidencias`           | POST        | Sí         |
| RF-06-AC-4  | Rechazar archivos de video como evidencia.                                                             | `/parques/{parque_id}/evidencias`           | POST        | Sí         |
| RF-06-AC-5  | Rechazar formatos de archivo no permitidos.                                                            | `/parques/{parque_id}/evidencias`           | POST        | Sí         |
| RF-06-AC-6  | Aplicar el límite de tamaño configurado al validar una carga.                                          | `/parques/{parque_id}/evidencias`           | POST        | Sí         |
| RF-06-AC-7  | Rechazar una configuración que exceda el límite máximo permitido.                                      | `/parques/{parque_id}/evidencias`           | POST        | Sí         |
| RF-07-AC-1  | Mostrar estado de calificación, fecha del cambio y usuario responsable.                                | —                                           | —           | No         |
| RF-07-AC-2  | Abrir o consultar un documento administrativo del expediente.                                          | —                                           | —           | No         |
| RF-07-AC-3  | Impedir que un usuario sin permisos acceda al contenido de una evidencia.                              | —                                           | —           | No         |
| RF-08-AC-1  | Calcular el porcentaje de cumplimiento de criterios obligatorios.                                      | —                                           | —           | No         |
| RF-08-AC-2  | Calcular el porcentaje de avance general incluyendo criterios recomendados.                            | —                                           | —           | No         |
| RF-08-AC-3  | Mostrar “No aplica” cuando no existan criterios obligatorios aplicables.                               | —                                           | —           | No         |
| RF-08-AC-4  | Calcular por separado el porcentaje de cumplimiento de criterios recomendados.                         | —                                           | —           | No         |
| RF-08-AC-5  | Calcular el cumplimiento global ponderado por el total de criterios obligatorios aplicables.           | —                                           | —           | No         |
| RF-09-AC-1  | Crear un registro del plan de trabajo asociado al parque y criterio.                                   | `/parques/{parque_id}/planes`               | POST        | Sí         |
| RF-09-AC-2  | Identificar como atrasados los criterios cuya fecha comprometida ya pasó.                              | `/parques/{parque_id}/planes`               | POST        | Sí         |
| RF-09-AC-3  | No marcar como atrasado un criterio cuya fecha comprometida aún no ha pasado.                          | `/planes/{plan_id}`                         | PATCH       | Sí         |
| RF-09-AC-4  | Rechazar un responsable que no sea usuario APPI del parque correspondiente.                            | —                                           | —           | No         |
| RF-10-AC-1  | Asignar un consultor a un parque y generación y conceder acceso al expediente.                         | —                                           | —           | No         |
| RF-10-AC-2  | Sustituir al consultor asignado y conservar el historial de la asignación.                             | —                                           | —           | No         |
| RF-10-AC-3  | Impedir que un usuario APPI asigne un consultor a su propio parque.                                    | —                                           | —           | No         |
| RF-11-AC-1  | Registrar el cambio de tipo de parque y conservar el historial de clasificación.                       | —                                           | —           | No         |
| RF-11-AC-2  | Conservar el porcentaje de cumplimiento histórico y calcular el nuevo por separado.                    | —                                           | —           | No         |
| RF-11-AC-3  | Rechazar un tipo de parque inválido.                                                                   | —                                           | —           | No         |
| RF-11-AC-4  | Restablecer a pendiente un criterio que comienza a aplicar por el cambio de clasificación.             | —                                           | —           | No         |
| RF-11-AC-5  | Exigir el motivo y registrar los datos del cambio de tipo de parque.                                   | —                                           | —           | No         |
| RF-11-AC-6  | Conservar evidencias e historial cuando un criterio deja de aplicar.                                   | —                                           | —           | No         |
| RF-12-AC-1  | Registrar una Opinión intermedia con fecha y porcentajes vigentes.                                     | `/parques/{parque_id}/opiniones`            | POST        | Sí         |
| RF-12-AC-2  | Rechazar la emisión de una Opinión por un usuario sin permisos.                                        | `/parques/{parque_id}/opiniones`            | POST        | Sí         |
| RF-12-AC-3  | Impedir registrar una segunda Opinión final para la misma generación.                                  | `/parques/{parque_id}/opiniones`            | POST        | Sí         |
| RF-12-AC-4  | Impedir emitir una Opinión sin la política de seguridad firmada.                                       | `/parques/{parque_id}/opiniones`            | POST        | Sí         |
| RF-12-AC-5  | Impedir emitir una Opinión sin análisis de riesgos vigente.                                            | `/parques/{parque_id}/opiniones`            | POST        | Sí         |
| RF-12-AC-6  | Exigir el resultado favorable o no favorable de la Opinión final.                                      | `/parques/{parque_id}/opiniones`            | POST        | Sí         |
| RF-13-AC-1  | Conceder acceso de solo lectura al expediente conforme a las reglas de asignación.                     | —                                           | —           | No         |
| RF-13-AC-2  | Impedir asignar como consultor de comité al consultor asignado al mismo parque.                        | —                                           | —           | No         |
| RF-13-AC-3  | Denegar acceso al expediente a usuarios sin autorización.                                              | —                                           | —           | No         |
| RF-14-AC-1  | Registrar el dictamen de otorgamiento, su firmante y la fecha correspondiente.                         | —                                           | —           | No         |
| RF-14-AC-2  | Rechazar la emisión del dictamen por un usuario sin permisos.                                          | —                                           | —           | No         |
| RF-14-AC-3  | Impedir otorgar el distintivo si no se cumple el porcentaje obligatorio requerido.                     | —                                           | —           | No         |
| RF-15-AC-1  | —                                                                                                      | —                                           | —           | No         |
| RF-15-AC-2  | —                                                                                                      | —                                           | —           | No         |
| RF-15-AC-3  | —                                                                                                      | —                                           | —           | No         |
| RF-16-AC-1  | —                                                                                                      | —                                           | —           | No         |
| RF-16-AC-2  | —                                                                                                      | —                                           | —           | No         |
| RF-16-AC-3  | —                                                                                                      | —                                           | —           | No         |
| RF-17-AC-1  | —                                                                                                      | —                                           | —           | No         |
| RF-17-AC-2  | —                                                                                                      | —                                           | —           | No         |
| RF-18-AC-1  | —                                                                                                      | —                                           | —           | No         |
| RF-18-AC-2  | —                                                                                                      | —                                           | —           | No         |
| RF-18-AC-3  | —                                                                                                      | —                                           | —           | No         |
| RF-19-AC-1  | Enviar aviso de vencimiento a los destinatarios correspondientes.                                      | —                                           | —           | No         |
| RF-19-AC-2  | Enviar el segundo aviso conforme al plazo configurado.                                                 | —                                           | —           | No         |
| RF-19-AC-3  | No enviar avisos si el distintivo ya no está próximo a vencer.                                         | —                                           | —           | No         |
| RF-19-AC-4  | Aplicar los plazos de aviso actualizados a los distintivos vigentes.                                   | —                                           | —           | No         |
| RF-19-AC-5  | Evitar duplicar avisos para el mismo distintivo y plazo.                                               | —                                           | —           | No         |
| RF-20-AC-1  | Enviar el aviso correspondiente a la APPI del parque.                                                  | —                                           | —           | No         |
| RF-20-AC-2  | No enviar el aviso cuando no se cumplan las condiciones definidas.                                     | —                                           | —           | No         |
| RF-21-AC-1  | Generar un reporte con parques, fase, atraso y observaciones abiertas.                                 | —                                           | —           | No         |
| RF-21-AC-2  | Rechazar la consulta del reporte por usuarios sin permisos.                                            | —                                           | —           | No         |
| RF-22-AC-1  | Generar estadísticas por región y listado público de parques con distintivo vigente.                   | —                                           | —           | No         |
| RF-22-AC-2  | Excluir porcentajes de avance y rankings de la información pública.                                    | —                                           | —           | No         |
| RF-23-AC-1  | Mostrar el avance de varios parques en una vista de solo lectura.                                      | —                                           | —           | No         |
| RF-23-AC-2  | Rechazar el acceso a la vista comparativa por usuarios sin permisos.                                   | —                                           | —           | No         |
| RF-24-AC-1  | Asociar una observación al criterio y mostrarla a los usuarios autorizados.                            | —                                           | —           | No         |
| RF-24-AC-2  | Rechazar la operación de observación por un usuario sin permisos.                                      | —                                           | —           | No         |
| RF-25-AC-1  | Permitir consultar individualmente los criterios aplicables.                                           | —                                           | —           | No         |
| RF-25-AC-2  | Restringir la descarga del catálogo maestro a Coordinación AMPIP.                                      | —                                           | —           | No         |
| RF-25-AC-3  | Generar el archivo maestro con los criterios y sus marcas O/R/NA.                                      | —                                           | —           | No         |
| RF-25-AC-4  | Impedir que un consultor descargue el catálogo maestro completo.                                       | —                                           | —           | No         |
| RF-26-AC-1  | Iniciar sesión y entregar un token que expire tras 60 minutos de inactividad.                          | `/auth/login`                               | POST        | Sí         |
| RF-26-AC-2  | Rechazar credenciales incorrectas sin entregar un token.                                               | `/auth/login`                               | POST        | Sí         |
| RF-26-AC-3  | Bloquear temporalmente el inicio de sesión tras intentos fallidos consecutivos.                        | `/auth/login`                               | POST        | Sí         |
| RF-26-AC-4  | Generar un enlace de recuperación de contraseña de un solo uso y con expiración.                       | —                                           | —           | No         |
| RF-26-AC-5  | Invalidar el token al cerrar sesión.                                                                   | —                                           | —           | No         |
| RF-26-AC-6  | Rechazar solicitudes realizadas después de la expiración por inactividad.                              | —                                           | —           | No         |
| RF-27-AC-1  | Aceptar una evidencia revisada por el consultor asignado.                                              | `/parques/{parque_id}/respuestas-criterios` | POST        | Sí         |
| RF-27-AC-2  | Marcar como cumplido un criterio con evidencia aceptada y registrar fecha y consultor.                 | `/respuestas-criterios/{respuesta_id}`      | PATCH       | Sí         |
| RF-27-AC-3  | Impedir calificar un criterio sin análisis de riesgos vigente.                                         | `/respuestas-criterios/{respuesta_id}`      | PATCH       | Sí         |
| RF-27-AC-4  | Cambiar automáticamente el criterio a “en revisión” al recibir evidencia.                              | `/parques/{parque_id}/respuestas-criterios` | POST        | Sí         |
| RF-27-AC-5  | Restringir la calificación y reapertura al consultor asignado.                                         | `/respuestas-criterios/{respuesta_id}`      | PATCH       | Sí         |
| RF-27-AC-6  | Registrar el estado “no cumplido” y reflejarlo en los cálculos de cumplimiento.                        | `/respuestas-criterios/{respuesta_id}`      | PATCH       | Sí         |
| RF-27-AC-7  | Volver a “en revisión” cuando se agrega evidencia a un criterio cumplido.                              | `/parques/{parque_id}/respuestas-criterios` | POST        | Sí         |
| RF-27-AC-8  | Reabrir un criterio no cumplido y cambiarlo a “en revisión”.                                           | `/respuestas-criterios/{respuesta_id}`      | PATCH       | Sí         |
| RF-28-AC-1  | Crear una generación asociada a una versión del catálogo.                                              | —                                           | —           | No         |
| RF-28-AC-2  | Rechazar la creación de una generación por un usuario sin permisos.                                    | —                                           | —           | No         |
| RF-28-AC-3  | Impedir dar de alta un parque sin indicar su generación.                                               | —                                           | —           | No         |
| RF-29-AC-1  | Desactivar un usuario y retirar su acceso a los parques asignados.                                     | `/usuarios/{usuario_id}`                    | DELETE      | Sí         |
| RF-29-AC-2  | Impedir que un usuario APPI desactive cuentas de usuario.                                              | `/usuarios/{usuario_id}`                    | DELETE      | Sí         |
| RF-29-AC-3  | Desactivar un parque y retirar los accesos asociados.                                                  | `/parques/{parque_id}`                      | DELETE      | Sí         |
| RF-30-AC-1  | Registrar fechas de término del programa y próxima actualización anual.                                | —                                           | —           | No         |
| RF-30-AC-2  | Marcar como atrasado un parque cuya actualización anual venció.                                        | —                                           | —           | No         |
| RF-30-AC-3  | Evitar marcar como atrasado un parque con actualización registrada oportunamente.                      | —                                           | —           | No         |
| RF-31-AC-1  | Consultar el historial de generaciones, fechas, autoevaluaciones, opiniones y dictámenes de un parque. | —                                           | —           | No         |
| RF-31-AC-2  | Dar de alta un parque histórico sin exigir documentos de expediente.                                   | —                                           | —           | No         |
| RF-31-AC-3  | Impedir que una APPI consulte el historial de otro parque.                                             | —                                           | —           | No         |
| RF-32-AC-1  | Mostrar las nueve fases del expediente, su estado y la fase actual.                                    | `/planes/{plan_id}/fases`                   | GET         | Sí         |
| RF-32-AC-2  | Distinguir entre una fase con documentos entregados y una fase validada.                               | `/fases/{fase_id}`                          | PATCH       | Sí         |
| RF-32-AC-3  | Impedir que una APPI o un consultor cierre una fase sin autorización.                                  | `/fases/{fase_id}`                          | PATCH       | Sí         |
| RF-32-AC-4  | Exigir el motivo de excepción al avanzar sin cerrar la fase actual.                                    | `/fases/{fase_id}`                          | PATCH       | Sí         |
| RF-32-AC-5  | Registrar el avance por excepción con motivo, usuario y estado.                                        | `/fases/{fase_id}`                          | PATCH       | Sí         |
| RF-33-AC-1  | Registrar la Evaluación de Desempeño cuando existe la Opinión final.                                   | —                                           | —           | No         |
| RF-33-AC-2  | Impedir registrar la Evaluación de Desempeño sin Opinión final.                                        | —                                           | —           | No         |
| RF-33-AC-3  | Rechazar el registro por un consultor no asignado al parque.                                           | —                                           | —           | No         |
| RF-34-AC-1  | Mostrar los usuarios APPI del parque e identificar al contacto principal.                              | `/usuarios`                                 | GET         | Sí         |
| RF-34-AC-2  | Cambiar el contacto principal y asegurar que solo haya uno activo.                                     | `/usuarios`                                 | PATCH       | Sí         |
| RF-34-AC-3  | Avisar a las cuentas APPI si el contacto principal se da de baja.                                      | —                                           | —           | No         |
| RF-35-AC-1  | Registrar en bitácora la descarga de una evidencia con usuario, fecha y recurso.                       | `/auditoria`                                | GET         | Sí         |
| RF-35-AC-2  | Registrar intentos de acceso denegados en la bitácora.                                                 | `/auditoria`                                | GET         | Sí         |
| RF-35-AC-3  | Filtrar la bitácora por parque y periodo y ordenar los resultados.                                     | `/auditoria`                                | GET         | Sí         |
| RF-35-AC-4  | Restringir la consulta de bitácora a los roles autorizados.                                            | `/auditoria`                                | GET         | Sí         |
| RF-36-AC-1  | Registrar y mostrar una recomendación del consultor asociada a un criterio.                            | —                                           | —           | No         |
| RF-36-AC-2  | Mantener sin cambios los estados del criterio y sus evidencias al registrar una recomendación.         | —                                           | —           | No         |
| RF-37-AC-1  | Registrar una visita con fecha, participantes y hallazgos.                                             | —                                           | —           | No         |
| RF-37-AC-2  | Registrar acciones correctivas y conservar su historial de cambios.                                    | —                                           | —           | No         |
| RF-37-AC-3  | Asociar fotografías a una visita y aplicar validaciones de archivo.                                    | —                                           | —           | No         |
| RF-38-AC-1  | Iniciar la renovación y cambiar el distintivo al estado “en renovación”.                               | —                                           | —           | No         |
| RF-38-AC-2  | Marcar como vencido un distintivo sin renovación ni prórroga vigente.                                  | —                                           | —           | No         |
| RF-38-AC-3  | Validar que una prórroga incluya motivo, responsable y nueva fecha límite.                             | —                                           | —           | No         |
| RF-39-AC-1  | Enviar avisos de vencimiento de documentos críticos en los plazos establecidos.                        | —                                           | —           | No         |
| RF-39-AC-2  | Evitar avisos cuando ya existe una versión vigente que no está próxima a vencer.                       | —                                           | —           | No         |


## ¿Falta un endpoint o el requerimiento está fuera del alcance de la API?


| ID Criterio(s)           | Decisión                                                    | Justificación                                                                                                                                                                                                                                                                                                                 |
| ------------------------ | ----------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| RF-01-AC-1 a RF-01-AC-5  | Falta un endpoint                                           | La carga versionada del catálogo, su validación, la asignación por generación y la consulta de la versión no están cubiertas explícitamente.                                                |
| RF-04-AC-1 a RF-04-AC-2  | Falta un endpoint                   | Se requiere consultar los criterios aplicables según el tipo de parque y validar que los criterios NA no puedan responderse.                                                                |
| RF-05-AC-5 a RF-05-AC-10 | Falta un endpoint                                           | Faltan operaciones explícitas para consultar metadatos e historial, vincular evidencias a criterios, gestionar cargas múltiples y aplicar bajas lógicas.                                    | Añadir endpoints para consultar versiones, asociar evidencias, procesar cargas múltiples y dar de baja evidencias conforme a las reglas del SRS.    |
| RF-07-AC-1 a RF-07-AC-3  | Falta un endpoint                                           | La consulta del estado de los criterios y los datos de trazabilidad para AMPIP no están definidos explícitamente.                                                                           | Definir un endpoint de consulta del estado de criterios y documentar autorización y acceso a documentos administrativos.                            |
| RF-08-AC-1 a RF-08-AC-5  | Falta un endpoint                                           | No existe una operación asociada al cálculo de cumplimiento obligatorio, recomendado y global.                                                                                                                   |
| RF-09-AC-4               | Falta un endpoint                   | No se documenta explícitamente la validación de que el responsable sea un usuario APPI del mismo parque.                                                                                    
| RF-10-AC-1 a RF-10-AC-3  | Falta un endpoint                                           | La asignación, sustitución y consulta de consultores por parque y generación no están vinculadas explícitamente a una operación.                                                            |
| RF-11-AC-1 a RF-11-AC-6  | Falta un endpoint                                           | El cambio de tipo de parque y sus efectos sobre criterios, historial y cálculos no tienen cobertura explícita.                                                                              |
| RF-13-AC-1 a RF-13-AC-3  | Falta un endpoint                                           | No se especifica el acceso temporal de un consultor de comité ni la prevención de conflictos de interés.                                                                                    |
| RF-14-AC-1 a RF-14-AC-8  | Falta un endpoint                                           | El registro del dictamen y sus validaciones previas no están vinculados explícitamente a una operación.                                                                                     |
| RF-15-AC-1 a RF-15-AC-3  | Falta un endpoint                                           | La validación del expediente antes de abrir la sesión de comité requiere una operación explícita.                                                                                           |
| RF-16-AC-1 a RF-16-AC-4  | Falta un endpoint                                           | No está cubierta explícitamente la revisión del análisis de riesgos, su resultado ni su vigencia.                                                                                           |
| RF-17-AC-1 a RF-17-AC-3  | Falta ampliar la lógica de negocio de endpoints existentes  | El bloqueo de la calificación de los estándares 2, 3 y 7 depende de un análisis de riesgos vigente. No necesariamente requiere un endpoint independiente, pero sí una validación explícita.    |
| RF-18-AC-1 a RF-18-AC-2  | Fuera del alcance del entregable de 12 semanas              | El SRS identifica el seguimiento de auditorías del subestándar 1.4 como fuera del entregable.                                                                                               |
| RF-19-AC-1 a RF-19-AC-5  | Fuera del alcance del entregable de 12 semanas              | Los avisos de vencimiento del distintivo forman parte del seguimiento de vigencia, cuya implementación queda fuera del entregable inicial.                                                  |
| RF-20-AC-1 a RF-20-AC-2  | Requiere confirmar alcance; probablemente falta un endpoint | La notificación de auditoría interna pendiente no aparece entre las funciones MVP descritas. Su relación con el seguimiento de auditorías fuera de alcance debe confirmarse.                |
| RF-21-AC-1 a RF-21-AC-2  | Falta un endpoint                      | El reporte mensual para Dirección no está asociado a una operación en OpenAPI. El SRS contempla reportes derivados durante una fase posterior.                                              |
| RF-22-AC-1 a RF-22-AC-2  | Fuera del alcance del entregable de 12 semanas              | El reporte agregado para asociados se identifica expresamente como fuera del entregable inicial.                                                                                            |
| RF-23-AC-1 a RF-23-AC-2  | Falta un endpoint                      | La vista consolidada para gerente corporativo no está asociada a una operación.                                                                                                             |
| RF-24-AC-1 a RF-24-AC-2  | Falta un endpoint                                           | No está definida explícitamente la gestión de las reglas sobre qué evidencia se considera suficiente para un criterio.                                                                     |
| RF-25-AC-1 a RF-25-AC-4  | Falta un endpoint                                           | No se documenta la descarga del catálogo maestro ni las restricciones específicas de acceso.                                                                                                |
| RF-26-AC-4 a RF-26-AC-6  | Falta un endpoint                                           | La recuperación de contraseña, el cierre de sesión y la expiración por inactividad no están cubiertos explícitamente por las operaciones actuales.                                          |
| RF-28-AC-1 a RF-28-AC-3  | Falta un endpoint                                           | No se define la creación de generaciones ni su relación con el catálogo y los parques.                                                                                                      |
| RF-30-AC-1 a RF-30-AC-3  | Falta un endpoint                                           | El registro de fechas del programa y la detección de atraso son parte del MVP, pero no aparecen vinculados explícitamente a operaciones.                                                    |
| RF-31-AC-1 a RF-31-AC-3  | Falta un endpoint                                           | El historial de parques y el alta de parques históricos mínimos forman parte del MVP, pero no están cubiertos explícitamente.                                                               |
| RF-33-AC-1 a RF-33-AC-3  | Falta un endpoint                     | El SRS contempla la Evaluación de Desempeño durante una fase posterior de 2027. Además, su papel como condición para otorgar el distintivo queda pendiente de confirmación con AMPIP.       |
| RF-34-AC-3               | Falta un endpoint o ampliar uno existente                   | La notificación a las cuentas APPI cuando se da de baja al contacto principal no está cubierta explícitamente.                                                                              |
| RF-36-AC-1 a RF-36-AC-2  | Falta un endpoint                      | Las recomendaciones del consultor se contemplan en la fase posterior del recorrido funcional de 2027.                                                                                       |
| RF-37-AC-1 a RF-37-AC-3  | Fuera del alcance del entregable de 12 semanas              | Las visitas de validación se identifican expresamente como fuera del MVP.                                                                                                 |                  
| RF-38-AC-1 a RF-38-AC-3  | Fuera del alcance del entregable de 12 semanas              | La renovación y el seguimiento del estado del distintivo se identifican  como fuera del MVP.                                                                                    |
| RF-39-AC-1 a RF-39-AC-2  | Fuera del alcance del entregable de 12 semanas              | Los avisos de vencimiento de documentos críticos se identifican tal cual como fuera del MVP.                                                                                            |

# Sección B — Decisiones de diseño
## ¿Por qué elegiste los recursos y endpoints que están en la especificación? ¿Cuáles quedaron fuera del alcance?
### Elección de recursos y endpoints

Se priorizaron los componentes esenciales definidos en el alcance del MVP del periodo de 12 semanas del proyecto. Esto incluye:
* Autenticación (/auth/login), 
* Gestión de usuarios y roles (/usuarios, /usuarios/{usuario_id}/roles), 
* Administración de parques industriales (/parques)
* Estructura de los checklists de seguridad/estándares (/estandares, /criterios)
* Planes de trabajo y sus fases (/parques/{parque_id}/planes, /fases/{fase_id}), 
* Respuestas a criterios y evidencias con su respectivo historial de revisión (/parques/{parque_id}/respuestas-criterios, /parques/{parque_id}/evidencias, /evidencias/{evidencia_id}/revisiones)
* Opiniones y evaluaciones (/parques/{parque_id}/opiniones, /parques/{parque_id}/evaluaciones)
* Consulta de eventos de auditoría (/auditoria).   

### Fuera del alcance
Quedaron excluidas las funcionalidades asociadas a fases posteriores o explícitamente fuera del MVP inicial de 12 semanas.
* El módulo de auditorías del subestándar 1.4 (RF-18).   
* Los avisos automatizados y gestión de vencimientos de distintivos (RF-19) y de documentos críticos (RF-39).   
* El reporte agregado para asociados (RF-22).   
* Las visitas de validación en campo con sus acciones correctivas (RF-37).   
* El proceso completo de renovación del distintivo (RF-38).   
* Cargas masivas avanzadas y la gestión detallada de catálogos históricos (como RF-01 y RF-31 en su totalidad).


## ¿Qué patrones de diseño de API (paginación, versionado, filtering) decidiste incluir o excluir?
* Paginación: Se incluyó de manera explícita en las colecciones principales de consulta masiva (como usuarios, parques y auditoría) mediante parámetros de consulta estándar en snake_case (page para el número de página empezando en 1, y page_size para limitar la cantidad de elementos por página).   
* Versionado: Se implementó a nivel global de la URL del servidor base para asegurar la compatibilidad y estabilidad del contrato de la API. Asimismo, se manejan versiones a nivel de negocio y catálogos en los esquemas.   
* Filtering: Se incluyeron parámetros de consulta específicos orientados al dominio en endpoints de listado para acotar resultados. Por ejemplo, filtrar usuarios por activo o parque_id; parques por tipo o estado; evidencias por respuesta_id o estado; y auditorías por entidad, entidad_id, desde y hasta.   
* Idempotencia y Actualización Parcial: Se incorporó el uso de la cabecera Idempotency-Key en operaciones POST críticas para prevenir duplicidades en reintentos, y se adoptó el estándar application/merge-patch+json (PATCH) junto con operaciones idempotentes en PUT y bajas lógicas en DELETE. 


## ¿En qué aspectos el agente propuso algo que no seguía buenas prácticas REST? ¿Cómo lo detectaste?

* El primer error detectado fueron en las rutas y convenciones de nomenclatura. Originalmente se proponían estructuras de rutas anidadas incorrectas o mezcla de estilos (como /checklist/estandares), las cuales no cumplían con el principio de utilizar rutas en minúsculas y colecciones en plural (/estandares).

* Tambien se detecto el manejo incorrecto de la idempotencia en métodos HTTP ya que el agente propuso comportamientos iniciales en los métodos PUT y DELETE que no garantizaban la idempotencia ante reintentos de peticiones idénticas. Se detectó mediante la validación de los efectos secundarios, como la duplicidad de registros o alteración de historiales.

* El agente dio un uso impreciso de códigos de estado HTTP. El diseño del agente agrupaba o confundía conflictos derivados de reglas de negocio con errores de validación genéricos o peticiones incorrectas. Me percate de esto tras analizar las restricciones unicas del dominio como correos duplicados, respuestas a criterios ya existentes o emisión de evaluaciones sin cumplir condiciones previas.