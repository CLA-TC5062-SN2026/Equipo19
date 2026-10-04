# Especificación de Requisitos de Software (SRS)

## Sistema de Gestión del Programa Parque Industrial Seguro (SGPIS)

**Versión:** 1.1
**Fecha:** Septiembre de 2026
**Referencia:** IEEE 830 — estructura simplificada

---

# 1. Introducción

## 1.1 Propósito

El presente documento especifica los requisitos del **Sistema de Gestión del Programa Parque Industrial Seguro (SGPIS)**, una solución destinada a digitalizar, centralizar y controlar el proceso de evaluación de los parques industriales participantes en el programa **“Parque Industrial Seguro”** de la Asociación Mexicana de Parques Industriales Privados (AMPIP).

El sistema permitirá gestionar el proceso completo de evaluación, desde el diagnóstico y la autoevaluación de los criterios de seguridad hasta la revisión de evidencias, cálculo del cumplimiento, emisión de las Opiniones de Cumplimiento y Evaluación de Desempeño, así como el seguimiento de la vigencia y renovación del distintivo.

Esta especificación servirá como referencia para el análisis, diseño, desarrollo, pruebas y validación del sistema.

## 1.2 Alcance

El SGPIS permitirá a AMPIP, a las Administraciones de los Parques Industriales (APPI) y a los consultores externos gestionar de manera centralizada la información asociada al proceso de evaluación.

El sistema contemplará:

* Registro y administración de parques industriales.
* Administración de usuarios y roles.
* Asignación de consultores externos a parques.
* Gestión de las fases del proceso de evaluación.
* Autoevaluación de criterios de seguridad por parte de las APPI.
* Carga, versionado y gestión de evidencias.
* Revisión y observación de evidencias.
* Gestión del ciclo de corrección y reenvío.
* Administración versionada del catálogo de criterios y estándares.
* Determinación de aplicabilidad según el tipo de parque.
* Cálculo de porcentajes de cumplimiento.
* Gestión de Opiniones de Cumplimiento y Evaluaciones de Desempeño.
* Dashboard consolidado para AMPIP.
* Alertas de renovación del distintivo.
* Control de accesos y aislamiento de información.
* Bitácora de auditoría y trazabilidad de operaciones.
* Conservación del historial de evaluaciones, evidencias, observaciones y catálogos.

## 1.3 Definiciones, acrónimos y abreviaturas

| Término                     | Definición                                                                                                     |
| --------------------------- | -------------------------------------------------------------------------------------------------------------- |
| **SGPIS**                   | Sistema de Gestión del Programa Parque Industrial Seguro.                                                      |
| **AMPIP**                   | Asociación Mexicana de Parques Industriales Privados.                                                          |
| **APPI**                    | Administración del Parque Industrial.                                                                          |
| **RF**                      | Requerimiento Funcional.                                                                                       |
| **RNF**                     | Requerimiento No Funcional.                                                                                    |
| **RD**                      | Requerimiento de Dominio.                                                                                      |
| **O**                       | Obligatorio.                                                                                                   |
| **R**                       | Recomendado.                                                                                                   |
| **NA**                      | No Aplica.                                                                                                     |
| **Criterio**                | Elemento individual utilizado para evaluar el cumplimiento de una condición de seguridad.                      |
| **Estándar**                | Conjunto de criterios de seguridad agrupados para efectos de evaluación.                                       |
| **Evidencia**               | Documento, imagen, video u otro archivo utilizado para demostrar el cumplimiento de un criterio.               |
| **Distintivo**              | Reconocimiento denominado “Parque Industrial Seguro”.                                                          |
| **Aplicabilidad**           | Determinación de si un criterio debe ser evaluado para un parque de acuerdo con su tipo.                       |
| **Resultado de evaluación** | Resultado registrado para un criterio durante la evaluación, conforme a los valores definidos por AMPIP.       |
| **Multitenancy**            | Modelo de aislamiento lógico que impide que un parque pueda acceder a información perteneciente a otro parque. |
| **Versión de catálogo**     | Identificador de una versión específica de los criterios y estándares utilizada durante una evaluación.        |

---

# 2. Descripción general

## 2.1 Perspectiva del producto

El SGPIS será un sistema centralizado para la administración del proceso de evaluación del Programa Parque Industrial Seguro.

El sistema gestionará información perteneciente a diferentes parques industriales y deberá garantizar el aislamiento lógico de la información entre ellos.

La información estructurada se almacenará en una base de datos relacional PostgreSQL. Los archivos físicos correspondientes a las evidencias se almacenarán en un repositorio externo de almacenamiento de objetos.

El sistema implementará Control de Acceso Basado en Roles (RBAC) para los perfiles AMPIP, APPI y Consultor Externo.

## 2.2 Funciones principales del producto

Las funciones principales serán:

1. Administrar parques industriales.
2. Administrar usuarios y roles.
3. Asignar consultores a parques.
4. Gestionar las fases del proceso de evaluación.
5. Administrar versiones del catálogo de criterios y estándares.
6. Determinar la aplicabilidad de los criterios.
7. Permitir la autoevaluación de los criterios aplicables.
8. Cargar y versionar evidencias.
9. Revisar y observar evidencias.
10. Corregir y reenviar evidencias.
11. Aceptar evidencias.
12. Calcular porcentajes de cumplimiento por estándar y globalmente.
13. Emitir y registrar Opiniones de Cumplimiento.
14. Registrar Evaluaciones de Desempeño.
15. Proporcionar indicadores consolidados a AMPIP.
16. Generar alertas de renovación.
17. Mantener bitácoras de auditoría e historial.

## 2.3 Características de los usuarios

| Usuario               | Descripción                                                               | Principales operaciones                                                                                               |
| --------------------- | ------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------- |
| **AMPIP**             | Usuario encargado de la administración y supervisión global del programa. | Administrar parques, usuarios, catálogos, asignaciones, consulta global, seguimiento y configuración de renovaciones. |
| **APPI**              | Administración responsable de un parque industrial.                       | Autoevaluación, carga de evidencias, consulta de observaciones, corrección y reenvío de evidencias.                   |
| **Consultor externo** | Usuario responsable de revisar y evaluar los parques asignados.           | Revisión de evidencias, observaciones, aceptación de evidencias, Opiniones de Cumplimiento y Evaluación de Desempeño. |

## 2.4 Restricciones generales

* El catálogo inicial del programa corresponde a la versión 2023 y está compuesto por 286 criterios y 10 estándares.
* Las versiones posteriores del catálogo podrán modificar la cantidad de criterios o estándares.
* Cada criterio deberá tener una clasificación de aplicabilidad de O, R o NA para cada tipo de parque.
* La aplicabilidad dependerá del tipo de parque.
* Los criterios NA deberán excluirse de los cálculos de cumplimiento.
* Los archivos de evidencia no deberán almacenarse directamente en PostgreSQL.
* La información deberá mantenerse aislada entre parques.
* Los cambios de tipo de parque no deberán eliminar información histórica.
* El acceso de los consultores estará limitado a los parques que tengan asignados.
* El distintivo tendrá una vigencia definida y controlada por el sistema.
* Cada evaluación deberá conservar la versión del catálogo utilizada para realizarla.

---

# 3. Requisitos específicos

## 3.1 Requisitos funcionales

### 3.1.1 Gestión general del proceso

**RF-01. Gestión del proceso de evaluación**

El sistema deberá permitir gestionar el proceso de evaluación de un parque desde la fase de diagnóstico hasta el cierre de la evaluación y, cuando se cumplan las condiciones establecidas por AMPIP, registrar el otorgamiento del distintivo.

**RF-02. Gestión de fases**

El sistema deberá gestionar las siguientes fases:

1. Diagnóstico.
2. Plan de trabajo.
3. Política de seguridad.
4. Análisis de riesgos.
5. Implementación de estándares.
6. Opiniones de Cumplimiento.
7. Evaluación de Desempeño.

Cada fase deberá tener, como mínimo, los estados:

* Pendiente.
* En proceso.
* Completada.

El sistema deberá impedir el avance a una fase posterior mientras no se hayan cumplido las condiciones de finalización definidas para la fase actual, salvo que el rol AMPIP realice una acción de excepción autorizada.

---

### 3.1.2 Autoevaluación

**RF-03. Autoevaluación**

El sistema deberá permitir a la APPI registrar el resultado de evaluación de cada criterio aplicable.

Los resultados permitidos deberán ser definidos por AMPIP y, como mínimo, contemplarán:

* Cumple.
* No cumple.
* Pendiente.

Los resultados deberán quedar asociados al parque, criterio, versión del catálogo y usuario que realizó el registro.

---

### 3.1.3 Gestión de evidencias

**RF-04. Carga de evidencias**

El sistema deberá permitir a la APPI cargar evidencias digitales y almacenarlas físicamente en Object Storage.

Los formatos y límites permitidos deberán estar parametrizados por AMPIP. Como mínimo, el sistema deberá permitir documentos PDF, imágenes y videos.

Cada evidencia deberá estar asociada a:

* Parque.
* Criterio.
* Evaluación.
* Versión de la evidencia.

**RF-05. Metadatos**

El sistema deberá almacenar como mínimo:

* Nombre del archivo.
* Fecha y hora de carga.
* Fecha de emisión o creación, cuando aplique.
* Número de versión.
* Tipo de archivo.
* Tamaño.
* Estado de revisión.
* Usuario que realizó la carga.
* Referencia al objeto almacenado.

**RF-06. Estados de evidencia**

Las evidencias deberán manejar los siguientes estados:

* Pendiente.
* Enviada.
* Observada.
* Aceptada.

Las transiciones válidas serán:

* Pendiente → Enviada.
* Enviada → Observada.
* Enviada → Aceptada.
* Observada → Enviada.

Una evidencia Aceptada no podrá regresar a un estado anterior sin una acción explícita y autorizada de AMPIP o conforme a una regla definida por el programa.

**RF-07. Observaciones**

El sistema deberá permitir al consultor registrar una o varias observaciones asociadas a una evidencia.

Cada observación deberá registrar:

* Comentario.
* Fecha y hora.
* Consultor que la generó.
* Versión de evidencia a la que corresponde.
* Estado de la observación.

**RF-08. Corrección y reenvío**

Cuando una evidencia se encuentre Observada, la APPI deberá poder cargar una nueva versión de la evidencia o complementar la información requerida.

La nueva versión deberá conservar la relación con la evidencia original y mantener disponibles las versiones anteriores para consulta histórica.

Al reenviar la evidencia, su estado deberá cambiar a Enviada.

**RF-09. Aceptación y nueva observación**

El consultor deberá poder:

* Aceptar una evidencia cuando determine que demuestra el cumplimiento del criterio.
* Registrar una nueva observación cuando la evidencia continúe sin demostrar el cumplimiento.

Las observaciones anteriores deberán conservarse como parte del historial.

---

### 3.1.4 Aplicabilidad de criterios

**RF-10. Recálculo de aplicabilidad**

Cuando se modifique el tipo de parque, el sistema deberá recalcular automáticamente la aplicabilidad de los criterios utilizando la matriz de aplicabilidad correspondiente a la versión vigente del catálogo.

**RF-11. Clasificación de criterios**

Para cada parque y versión de catálogo, el sistema deberá determinar para cada criterio una clasificación:

* O — Obligatorio.
* R — Recomendado.
* NA — No Aplica.

La clasificación deberá derivarse de la matriz de aplicabilidad asociada al tipo de parque.

**RF-12. Nuevos criterios aplicables**

Cuando un criterio cambie de NA a O o R como consecuencia de un cambio de tipo de parque, el sistema deberá crear una nueva instancia de evaluación con estado Pendiente.

**RF-13. Conservación histórica**

Cuando un criterio deje de aplicar, el sistema deberá conservar:

* Resultado de evaluación anterior.
* Evidencias.
* Versiones de evidencias.
* Observaciones.
* Fechas.
* Usuarios responsables.
* Clasificación anterior.
* Versión del catálogo utilizada.

La información histórica no deberá modificarse como consecuencia del cambio de tipo de parque.

---

### 3.1.5 Cálculo de cumplimiento

**RF-14. Cumplimiento por estándar**

El sistema deberá calcular el porcentaje de cumplimiento de cada estándar utilizando únicamente criterios aplicables.

Para cada estándar deberá mostrar por separado:

* Porcentaje de cumplimiento de criterios O.
* Porcentaje de cumplimiento de criterios R.

La fórmula será:

**Porcentaje de cumplimiento = (criterios cumplidos / criterios aplicables evaluables) × 100**

Los criterios NA no formarán parte del denominador.

Los criterios Pendientes y No cumple formarán parte del denominador y no del numerador.

Cuando no existan criterios aplicables de una categoría, el resultado deberá mostrarse como **NA** y no como 0 %.

**RF-15. Cumplimiento global**

El sistema deberá calcular el cumplimiento global utilizando todos los criterios aplicables de los 10 estándares.

El cálculo deberá realizarse de forma independiente para O y R mediante:

**Cumplimiento global = (total de criterios cumplidos / total de criterios aplicables evaluables) × 100**

El resultado no deberá calcularse como promedio simple de los porcentajes de los estándares.

**RF-16. Exclusión de criterios NA**

Los criterios clasificados como NA no deberán formar parte del numerador ni del denominador de ningún cálculo de cumplimiento.

Cuando cambie la aplicabilidad, los cálculos deberán utilizar únicamente la clasificación vigente para la evaluación actual.

---

### 3.1.6 Dashboard y seguimiento

**RF-17. Dashboard de AMPIP**

El sistema deberá proporcionar a AMPIP un dashboard consolidado que muestre como mínimo:

* Cantidad de parques por fase.
* Porcentaje de avance por parque.
* Cumplimiento O y R.
* Parques con atraso.
* Distintivos próximos a vencer.
* Estado de los procesos de renovación.

Se considerará que un parque presenta atraso cuando la fecha actual sea posterior a la fecha objetivo definida para la fase correspondiente y esta no se encuentre completada.

**RF-18. Gestión de parques asignados**

El consultor deberá poder consultar y gestionar únicamente los parques que tenga asignados.

---

### 3.1.7 Renovación del distintivo

**RF-19. Alertas de renovación**

El sistema deberá generar automáticamente una alerta cuando la fecha de vencimiento de un distintivo se encuentre dentro del periodo de anticipación configurado por AMPIP.

El proceso de validación de vencimientos deberá ejecutarse al menos una vez cada 24 horas.

**RF-20. Información de vencimiento**

Cada alerta deberá mostrar:

* Parque.
* Fecha de vencimiento.
* Días restantes.
* Estado actual del distintivo.
* Situación del proceso de renovación, cuando exista.

**RF-21. Parametrización**

AMPIP deberá poder configurar el periodo de anticipación de las alertas en días naturales.

El sistema deberá almacenar el valor configurado y utilizarlo en las siguientes ejecuciones automáticas de validación.

Una alerta deberá identificarse de manera única por distintivo y periodo de vencimiento para evitar la generación de registros duplicados.

---

### 3.1.8 Auditoría y administración

**RF-22. Bitácora**

El sistema deberá registrar como mínimo los siguientes eventos:

* Inicio de sesión.
* Cierre de sesión.
* Intentos de acceso no autorizado.
* Alta, modificación o baja lógica de parques.
* Cambios de tipo de parque.
* Asignación o desasignación de consultores.
* Creación y modificación de evaluaciones.
* Cambios de estado de evidencias.
* Carga de nuevas versiones de evidencias.
* Observaciones.
* Aceptaciones.
* Emisión de resultados.
* Cambios en catálogos.
* Cambios en permisos o usuarios.

Cada evento deberá registrar:

* Fecha y hora.
* Usuario.
* Rol.
* Parque afectado, cuando aplique.
* Tipo de operación.
* Recurso afectado.
* Resultado de la operación.
* Identificador del registro afectado, cuando aplique.

Los registros de auditoría deberán ser inmutables para los usuarios de la aplicación.

**RF-23. Administración de parques y catálogos**

AMPIP deberá poder:

* Dar de alta parques.
* Modificar información de parques.
* Realizar baja lógica de parques.
* Asignar y desasignar consultores.
* Crear versiones de estándares.
* Crear versiones de criterios.
* Cargar catálogos.
* Validar catálogos antes de activarlos.
* Consultar versiones históricas.

Cada evaluación deberá conservar la versión del catálogo con la que fue realizada.

Una nueva versión del catálogo no deberá modificar retroactivamente evaluaciones históricas.

**RF-24. Emisión de resultados**

El consultor deberá poder emitir y registrar formalmente las dos Opiniones de Cumplimiento definidas por AMPIP y la Evaluación de Desempeño.

Cada resultado deberá contener como mínimo:

* Parque.
* Evaluación.
* Tipo de documento.
* Folio único.
* Fecha de emisión.
* Consultor responsable.
* Versión del catálogo utilizada.
* Resultado.
* Documento generado o archivo asociado, cuando aplique.

---

# 4. Requisitos no funcionales

## 4.1 Seguridad y control de acceso

**RNF-01. Control de acceso basado en roles**

El sistema deberá implementar RBAC.

Como mínimo, se definirán los siguientes permisos:

| Operación             |    AMPIP |   APPI | Consultor |
| --------------------- | -------: | -----: | --------: |
| Administrar parques   |       Sí |     No |        No |
| Administrar usuarios  |       Sí |     No |        No |
| Asignar consultores   |       Sí |     No |        No |
| Administrar catálogos |       Sí |     No |        No |
| Autoevaluación        | Consulta |     Sí |  Consulta |
| Cargar evidencias     | Consulta |     Sí |        No |
| Observar evidencias   | Consulta |     No |        Sí |
| Aceptar evidencias    | Consulta |     No |        Sí |
| Consultar parque      |    Todos | Propio | Asignados |
| Emitir resultados     | Consulta |     No |        Sí |
| Dashboard global      |       Sí |     No |        No |
| Consultar auditoría   |       Sí |     No |        No |

**RNF-02. Aislamiento de información**

El sistema deberá impedir que un usuario APPI consulte o modifique información perteneciente a otro parque.

Un consultor únicamente podrá acceder a información de los parques que tenga asignados.

Las restricciones deberán aplicarse tanto en la interfaz como en los servicios/API y consultas de datos.

**RNF-03. Cifrado y protección de información**

La información sensible deberá protegerse:

* Mediante cifrado durante la transmisión utilizando TLS.
* Mediante cifrado en reposo para la base de datos y Object Storage.
* Mediante mecanismos de control de acceso al almacenamiento de objetos.

Los archivos de evidencia no deberán ser accesibles mediante URLs públicas.

---

## 4.2 Integridad y trazabilidad

**RNF-04. Integridad del historial**

El sistema deberá conservar las versiones históricas de:

* Evaluaciones.
* Evidencias.
* Observaciones.
* Clasificaciones de criterios.
* Catálogos.
* Resultados emitidos.

Una modificación posterior no deberá sobrescribir la información histórica que haya sido utilizada para generar un resultado formal.

Los registros de auditoría deberán ser inmutables para los usuarios de la aplicación.

---

## 4.3 Gestión de almacenamiento

**RNF-05. Almacenamiento de evidencias**

Los archivos físicos deberán almacenarse en Object Storage.

PostgreSQL deberá almacenar únicamente:

* Referencia al objeto.
* Metadatos.
* Estado.
* Información de versionado.
* Relaciones con parque, criterio y evaluación.

El acceso a los objetos deberá estar autorizado por el sistema y deberá impedirse el acceso entre parques no autorizados.

---

## 4.4 Autenticación y administración de usuarios

**RNF-06. Autenticación**

El sistema deberá autenticar a todos los usuarios antes de permitir el acceso a información protegida.

Las credenciales no deberán almacenarse en texto plano.

**RNF-07. Gestión del ciclo de vida de usuarios**

AMPIP deberá poder activar, desactivar y bloquear usuarios.

Un usuario desactivado no deberá poder iniciar nuevas sesiones.

La desactivación de un usuario no deberá eliminar los registros históricos asociados a sus operaciones.

---

## 4.5 Rendimiento

**RNF-08. Tiempo de respuesta**

En condiciones normales de operación, las consultas de información estructurada deberán responder en un máximo de 3 segundos para al menos el 95 % de las solicitudes.

Las operaciones de carga de archivos deberán informar al usuario del progreso de la operación y no deberán bloquear la interfaz durante toda la transferencia.

**RNF-09. Dashboard**

El dashboard deberá cargar sus indicadores principales en un máximo de 5 segundos bajo la carga operativa definida para el sistema.

---

# 5. Requisitos de dominio

**RD-01. Catálogo de evaluación**

El catálogo inicial del programa corresponde a la versión 2023 y contiene 286 criterios y 10 estándares.

Las versiones posteriores podrán modificar la cantidad de criterios o estándares.

**RD-02. Clasificación**

Cada criterio aplicable deberá clasificarse como O o R.

Un criterio no aplicable deberá clasificarse como NA.

**RD-03. Tipos de parque**

El sistema deberá contemplar las siguientes combinaciones:

* Construcción abierto.
* Construcción cerrado.
* Operación abierto.
* Operación cerrado.

**RD-04. Matriz de aplicabilidad**

AMPIP deberá disponer de una matriz que determine la clasificación O, R o NA de cada criterio para cada tipo de parque y versión de catálogo.

La matriz será la fuente oficial utilizada por el sistema para determinar la aplicabilidad.

**RD-05. Cambio de tipo de parque**

Cuando un parque cambie de tipo, el sistema deberá generar una nueva configuración de aplicabilidad para la evaluación vigente sin modificar las evaluaciones históricas.

Los criterios que pasen de NA a O/R deberán quedar pendientes de evaluación.

**RD-06. Cálculo de cumplimiento**

Los criterios NA deberán excluirse del numerador y denominador de los cálculos.

Los criterios Pendientes y No cumple deberán formar parte del denominador.

**RD-07. Condición para el distintivo**

El otorgamiento del distintivo requerirá:

1. Dos Opiniones de Cumplimiento emitidas y registradas.
2. Una Evaluación de Desempeño emitida y registrada.
3. Cumplimiento de los porcentajes mínimos establecidos por AMPIP.
4. Cumplimiento de cualquier requisito adicional establecido para el programa.

El sistema no deberá registrar el distintivo como otorgado mientras no se cumplan todas las condiciones.

**RD-08. Vigencia**

El distintivo deberá registrar:

* Fecha de otorgamiento.
* Fecha de inicio de vigencia.
* Fecha de vencimiento.
* Estado.
* Información de renovación.

La duración de la vigencia deberá ser parametrizable conforme a las reglas vigentes de AMPIP.

**RD-09. Restricción de información**

La información de cada parque deberá estar restringida de acuerdo con su ámbito de acceso.

AMPIP podrá consultar información consolidada de todos los parques.

Una APPI solamente podrá consultar y gestionar la información de su parque.

Un consultor solamente podrá consultar y gestionar información de los parques que tenga asignados.

---

# 6. Reglas de negocio

| ID        | Regla de negocio                                                                                                    |
| --------- | ------------------------------------------------------------------------------------------------------------------- |
| **RN-01** | Cada evaluación deberá utilizar la matriz de aplicabilidad correspondiente al tipo de parque y versión de catálogo. |
| **RN-02** | Cada criterio deberá tener una clasificación O, R o NA.                                                             |
| **RN-03** | Los criterios NA no deberán participar en ningún cálculo de cumplimiento.                                           |
| **RN-04** | Un cambio en el tipo de parque deberá generar un nuevo cálculo de aplicabilidad.                                    |
| **RN-05** | Los criterios que pasen de NA a O/R deberán quedar pendientes de evaluación.                                        |
| **RN-06** | El cambio de aplicabilidad no deberá eliminar ni modificar el historial previo.                                     |
| **RN-07** | Las evidencias deberán respetar las transiciones de estado definidas en RF-06.                                      |
| **RN-08** | Una evidencia observada deberá generar una nueva versión cuando sea corregida o complementada.                      |
| **RN-09** | El consultor podrá aceptar una evidencia o registrar una nueva observación.                                         |
| **RN-10** | El porcentaje se calculará utilizando únicamente criterios aplicables.                                              |
| **RN-11** | Los criterios Pendientes y No cumple formarán parte del denominador y no del numerador.                             |
| **RN-12** | El cumplimiento global se calculará sobre el conjunto de criterios aplicables y no como promedio de estándares.     |
| **RN-13** | Cada evaluación deberá quedar asociada a una versión específica del catálogo.                                       |
| **RN-14** | Una nueva versión del catálogo no deberá modificar evaluaciones históricas.                                         |
| **RN-15** | Un consultor solamente podrá gestionar parques que tenga asignados.                                                 |
| **RN-16** | Una APPI solamente podrá gestionar información de su parque.                                                        |
| **RN-17** | AMPIP podrá consultar información consolidada de todos los parques.                                                 |
| **RN-18** | El otorgamiento del distintivo estará condicionado al cumplimiento de las condiciones establecidas en RD-07.        |
| **RN-19** | Las alertas de renovación deberán generarse conforme al periodo de anticipación configurado por AMPIP.              |
| **RN-20** | Los registros de auditoría no podrán ser modificados ni eliminados mediante la aplicación.                          |

---

# 7. Matriz de trazabilidad simplificada

| Funcionalidad           | Requisitos relacionados             |
| ----------------------- | ----------------------------------- |
| Gestión del proceso     | RF-01, RF-02, RD-07, RD-08          |
| Autoevaluación          | RF-03                               |
| Gestión de evidencias   | RF-04 a RF-09, RN-07, RN-08         |
| Aplicabilidad           | RF-10 a RF-13, RD-03 a RD-05        |
| Cálculo de cumplimiento | RF-14 a RF-16, RD-06, RN-10 a RN-12 |
| Dashboard               | RF-17                               |
| Parques asignados       | RF-18, RN-15 a RN-17                |
| Renovación              | RF-19 a RF-21, RD-08, RN-19         |
| Auditoría               | RF-22, RN-20, RNF-04                |
| Administración          | RF-23                               |
| Resultados              | RF-24, RD-07                        |
| Seguridad               | RNF-01 a RNF-03, RNF-06, RNF-07     |
| Historial               | RNF-04                              |
| Almacenamiento          | RNF-05                              |
| Rendimiento             | RNF-08, RNF-09                      |

---

# 8. Criterios generales de aceptación

| ID             | Given                                                                                                | When                                                                | Then                                                                                                                                                                                                      |
| -------------- | ---------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **RF-01-AC-1** | Dado que existe un parque registrado en el sistema                                                   | Cuando un usuario autorizado inicia su proceso de evaluación        | Entonces el sistema debe permitir gestionar el proceso desde el diagnóstico hasta la obtención del distintivo “Parque Industrial Seguro”                                                                  |
| **RF-01-AC-2** | Dado que un parque se encuentra en una fase del proceso de evaluación                                | Cuando la fase correspondiente es completada                        | Entonces el sistema debe permitir avanzar a la siguiente fase definida del proceso                                                                                                                        |
| **RF-02-AC-1** | Dado que un parque se encuentra registrado                                                           | Cuando un usuario autorizado consulta su proceso                    | Entonces el sistema debe mostrar las fases de diagnóstico, plan de trabajo, política de seguridad, análisis de riesgos, implementación de estándares, Opiniones de Cumplimiento y Evaluación de Desempeño |
| **RF-02-AC-2** | Dado que existe una fase del proceso                                                                 | Cuando un usuario autorizado actualiza su información               | Entonces el sistema debe registrar el estado correspondiente de dicha fase                                                                                                                                |
| **RF-03-AC-1** | Dado que una APPI tiene acceso a su parque                                                           | Cuando inicia la autoevaluación                                     | Entonces el sistema debe mostrar los criterios aplicables al parque                                                                                                                                       |
| **RF-03-AC-2** | Dado que la APPI está realizando una autoevaluación                                                  | Cuando registra el resultado de un criterio                         | Entonces el sistema debe guardar la evaluación asociada al criterio y al parque                                                                                                                           |
| **RF-04-AC-1** | Dado que la APPI se encuentra evaluando un criterio                                                  | Cuando carga una evidencia válida                                   | Entonces el sistema debe asociar la evidencia con el criterio correspondiente                                                                                                                             |
| **RF-04-AC-2** | Dado que un criterio requiere múltiples evidencias                                                   | Cuando la APPI carga varios archivos                                | Entonces el sistema debe permitir asociar múltiples evidencias al mismo criterio                                                                                                                          |
| **RF-04-AC-3** | Dado que la evidencia corresponde a un documento, imagen u otro archivo permitido                    | Cuando la APPI intenta cargarla                                     | Entonces el sistema debe almacenar la referencia de la evidencia y asociarla con el criterio correspondiente                                                                                              |
| **RF-05-AC-1** | Dado que una evidencia ha sido cargada                                                               | Cuando el sistema registra la evidencia                             | Entonces debe almacenar como mínimo su nombre, fecha, versión y estado de revisión                                                                                                                        |
| **RF-05-AC-2** | Dado que una evidencia existente tiene una nueva versión                                             | Cuando la APPI carga la nueva versión                               | Entonces el sistema debe registrar la nueva versión sin perder la información histórica de la evidencia anterior                                                                                          |
| **RF-06-AC-1** | Dado que una evidencia ha sido creada                                                                | Cuando se consulta su estado                                        | Entonces el sistema debe permitir identificar si está Pendiente, Enviada, Observada o Aceptada                                                                                                            |
| **RF-06-AC-2** | Dado que una evidencia se encuentra en un estado determinado                                         | Cuando ocurre una acción válida del flujo de revisión               | Entonces el sistema debe actualizar su estado conforme al ciclo de revisión                                                                                                                               |
| **RF-07-AC-1** | Dado que un consultor revisa una evidencia                                                           | Cuando determina que está incompleta o no demuestra el cumplimiento | Entonces el sistema debe permitir registrar una observación asociada a la evidencia                                                                                                                       |
| **RF-07-AC-2** | Dado que existe una observación registrada                                                           | Cuando la APPI consulta la evidencia                                | Entonces debe poder visualizar la observación realizada por el consultor                                                                                                                                  |
| **RF-08-AC-1** | Dado que una evidencia tiene una observación                                                         | Cuando la APPI consulta el resultado de la revisión                 | Entonces el sistema debe mostrar la observación correspondiente                                                                                                                                           |
| **RF-08-AC-2** | Dado que una evidencia fue observada                                                                 | Cuando la APPI corrige o complementa la evidencia                   | Entonces el sistema debe permitir cargar la información corregida                                                                                                                                         |
| **RF-08-AC-3** | Dado que una evidencia observada ha sido corregida                                                   | Cuando la APPI la reenvía                                           | Entonces el sistema debe cambiar su estado a Enviada y ponerla nuevamente a disposición del consultor                                                                                                     |
| **RF-09-AC-1** | Dado que existe una evidencia en revisión                                                            | Cuando el consultor determina que demuestra el cumplimiento         | Entonces el sistema debe permitir marcarla como Aceptada                                                                                                                                                  |
| **RF-09-AC-2** | Dado que una evidencia fue revisada                                                                  | Cuando el consultor determina que aún no demuestra el cumplimiento  | Entonces el sistema debe permitir generar una nueva observación y mantener el ciclo de revisión                                                                                                           |
| **RF-10-AC-1** | Dado que un parque tiene un tipo registrado                                                          | Cuando un usuario autorizado modifica su tipo de parque             | Entonces el sistema debe recalcular automáticamente la aplicabilidad de los 286 criterios                                                                                                                 |
| **RF-10-AC-2** | Dado que se ha modificado el tipo de parque                                                          | Cuando finaliza el recálculo                                        | Entonces el sistema debe actualizar la aplicabilidad de los criterios conforme a la nueva configuración                                                                                                   |
| **RF-11-AC-1** | Dado que el sistema conoce el tipo de parque y la matriz de aplicabilidad correspondiente            | Cuando se determina la aplicabilidad de los criterios               | Entonces cada criterio debe quedar clasificado como O, R o NA                                                                                                                                             |
| **RF-11-AC-2** | Dado que cambia el tipo de parque                                                                    | Cuando se ejecuta el recálculo de aplicabilidad                     | Entonces el sistema debe actualizar la clasificación de los criterios afectados                                                                                                                           |
| **RF-12-AC-1** | Dado que un criterio estaba clasificado como NA                                                      | Cuando un cambio de tipo de parque provoca que pase a O o R         | Entonces el sistema debe registrar el criterio como pendiente de evaluación                                                                                                                               |
| **RF-12-AC-2** | Dado que existen criterios que cambiaron de NA a O/R                                                 | Cuando la APPI consulta su evaluación                               | Entonces dichos criterios deben aparecer como pendientes                                                                                                                                                  |
| **RF-13-AC-1** | Dado que un criterio tiene evaluaciones y evidencias históricas                                      | Cuando el criterio cambia de aplicable a NA                         | Entonces el sistema debe conservar las evaluaciones y evidencias previamente registradas                                                                                                                  |
| **RF-13-AC-2** | Dado que un criterio dejó de aplicar                                                                 | Cuando un usuario consulta el historial del parque                  | Entonces debe poder consultar la información histórica asociada al criterio                                                                                                                               |
| **RF-14-AC-1** | Dado que un parque tiene criterios evaluados pertenecientes a un estándar                            | Cuando el sistema calcula el cumplimiento                           | Entonces debe mostrar el porcentaje de cumplimiento correspondiente a dicho estándar                                                                                                                      |
| **RF-14-AC-2** | Dado que un estándar contiene criterios O y R                                                        | Cuando se calcula su cumplimiento                                   | Entonces el sistema debe mostrar los porcentajes diferenciados para criterios obligatorios y recomendados                                                                                                 |
| **RF-14-AC-3** | Dado que existen criterios NA dentro de un estándar                                                  | Cuando se calcula el porcentaje de cumplimiento                     | Entonces dichos criterios no deben formar parte del denominador del cálculo                                                                                                                               |
| **RF-15-AC-1** | Dado que un parque tiene evaluaciones registradas                                                    | Cuando se consulta su cumplimiento global                           | Entonces el sistema debe calcular y mostrar el porcentaje global de cumplimiento                                                                                                                          |
| **RF-15-AC-2** | Dado que existen criterios O y R evaluados                                                           | Cuando se calcula el cumplimiento global                            | Entonces el sistema debe mostrar los resultados diferenciados entre O y R                                                                                                                                 |
| **RF-16-AC-1** | Dado que un parque tiene criterios clasificados como NA                                              | Cuando se calcula cualquier porcentaje de cumplimiento              | Entonces los criterios NA deben excluirse del denominador                                                                                                                                                 |
| **RF-16-AC-2** | Dado que cambia la clasificación de aplicabilidad de los criterios                                   | Cuando el sistema recalcula los porcentajes                         | Entonces los criterios que actualmente estén clasificados como NA no deben afectar el porcentaje de cumplimiento                                                                                          |
| **RF-17-AC-1** | Dado que existen parques registrados en diferentes fases                                             | Cuando un usuario AMPIP consulta el dashboard                       | Entonces el sistema debe mostrar la cantidad de parques correspondiente a cada fase                                                                                                                       |
| **RF-17-AC-2** | Dado que existen diferentes niveles de avance entre los parques                                      | Cuando AMPIP consulta el dashboard                                  | Entonces el sistema debe mostrar los porcentajes de avance separados para O y R                                                                                                                           |
| **RF-17-AC-3** | Dado que existen parques con atraso                                                                  | Cuando AMPIP consulta el dashboard                                  | Entonces el sistema debe identificar y mostrar los parques que presentan atrasos                                                                                                                          |
| **RF-17-AC-4** | Dado que existen distintivos próximos a vencer                                                       | Cuando AMPIP consulta el dashboard                                  | Entonces el sistema debe mostrar indicadores relacionados con los vencimientos próximos                                                                                                                   |
| **RF-18-AC-1** | Dado que un consultor tiene parques asignados                                                        | Cuando accede al módulo de gestión                                  | Entonces el sistema debe mostrar únicamente los parques que tiene asignados                                                                                                                               |
| **RF-18-AC-2** | Dado que un consultor intenta consultar un parque que no tiene asignado                              | Cuando solicita acceso a dicho parque                               | Entonces el sistema no debe permitirle consultar ni gestionar su información                                                                                                                              |
| **RF-19-AC-1** | Dado que un distintivo tiene una fecha de vencimiento dentro del periodo de anticipación configurado | Cuando el sistema ejecuta la validación de vencimientos             | Entonces debe generar una alerta de renovación para AMPIP                                                                                                                                                 |
| **RF-19-AC-2** | Dado que un distintivo no se encuentra dentro del periodo configurado para alertas                   | Cuando el sistema ejecuta la validación de vencimientos             | Entonces no debe generar una alerta de renovación                                                                                                                                                         |
| **RF-20-AC-1** | Dado que existe una alerta de renovación                                                             | Cuando AMPIP consulta la alerta                                     | Entonces debe mostrar el parque, fecha de vencimiento, días restantes y estado actual                                                                                                                     |
| **RF-20-AC-2** | Dado que existe información sobre un proceso de renovación                                           | Cuando AMPIP consulta la alerta correspondiente                     | Entonces la alerta debe mostrar también la situación del proceso de renovación                                                                                                                            |
| **RF-21-AC-1** | Dado que un usuario AMPIP tiene permisos de configuración                                            | Cuando modifica el periodo de anticipación de las alertas           | Entonces el sistema debe guardar el nuevo periodo de configuración                                                                                                                                        |
| **RF-21-AC-2** | Dado que existe un periodo de anticipación configurado                                               | Cuando el sistema evalúa los vencimientos                           | Entonces debe utilizar dicho periodo para determinar qué distintivos generan alertas                                                                                                                      |
| **RF-22-AC-1** | Dado que un usuario realiza una operación relevante en el sistema                                    | Cuando la operación es ejecutada                                    | Entonces el sistema debe registrar la operación en la bitácora                                                                                                                                            |
| **RF-22-AC-2** | Dado que existen operaciones registradas                                                             | Cuando un usuario autorizado consulta la bitácora                   | Entonces el sistema debe permitir consultar el historial de operaciones realizadas                                                                                                                        |
| **RF-23-AC-1** | Dado que un usuario tiene rol AMPIP                                                                  | Cuando registra un nuevo parque                                     | Entonces el sistema debe crear el registro del parque y permitir gestionar su información                                                                                                                 |
| **RF-23-AC-2** | Dado que existe un parque registrado                                                                 | Cuando un usuario AMPIP asigna un consultor externo                 | Entonces el sistema debe asociar el consultor con el parque                                                                                                                                               |
| **RF-23-AC-3** | Dado que un usuario AMPIP administra el catálogo                                                     | Cuando carga una nueva versión de los estándares y criterios        | Entonces el sistema debe registrar la nueva versión del catálogo                                                                                                                                          |
| **RF-23-AC-4** | Dado que existen versiones anteriores del catálogo                                                   | Cuando se incorpora una nueva versión                               | Entonces el sistema debe conservar las versiones históricas para mantener la trazabilidad                                                                                                                 |
| **RF-24-AC-1** | Dado que el consultor ha finalizado la revisión de un parque                                         | Cuando emite una Opinión de Cumplimiento                            | Entonces el sistema debe permitir registrar formalmente dicha opinión asociándola al parque y al proceso de evaluación                                                                                    |
| **RF-24-AC-2** | Dado que el consultor ha finalizado la evaluación correspondiente                                    | Cuando registra la Evaluación de Desempeño                          | Entonces el sistema debe almacenar formalmente la evaluación asociada al parque                                                                                                                           |
| **RF-24-AC-3** | Dado que una Opinión de Cumplimiento o Evaluación de Desempeño ha sido registrada                    | Cuando un usuario autorizado consulta el resultado                  | Entonces el sistema debe mostrar el documento o registro correspondiente                                                                                                                                  |


---

# 9. Consideraciones para diseño e implementación

La arquitectura deberá contemplar, como mínimo:

**Capa de aplicación:** responsable de implementar las reglas de negocio, autenticación, autorización, evaluación, gestión de evidencias, revisión, cálculo de indicadores, generación de alertas y auditoría.

**Base de datos relacional:** PostgreSQL, destinada a almacenar información estructurada, relaciones, metadatos, estados, referencias a archivos, versiones, historial y trazabilidad.

**Almacenamiento de objetos:** repositorio externo para almacenar físicamente las evidencias.

El diseño deberá garantizar el aislamiento por parque desde la capa de aplicación, API y persistencia de datos.

Cada registro relacionado con una evaluación deberá conservar la referencia al parque correspondiente y, cuando aplique, a la versión del catálogo utilizada.

El acceso a evidencias deberá realizarse mediante mecanismos autorizados por el sistema. Los objetos no deberán exponerse públicamente.

Antes del desarrollo deberán definirse:

* Matriz completa de aplicabilidad de los 286 criterios.
* Flujo detallado de fases.
* Matriz de permisos RBAC.
* Fórmulas definitivas de cumplimiento.
* Catálogo de resultados de evaluación.
* Catálogo de estados y transiciones.
* Formato de las Opiniones de Cumplimiento.
* Formato de la Evaluación de Desempeño.
* Reglas exactas de otorgamiento del distintivo.
* Duración de la vigencia.
* Formatos y tamaños máximos de evidencias.
* Política de retención de archivos.
* Especificación de API.
* Casos de uso.
* Modelo de datos.
* Flujos BPMN o diagramas de actividad.
* Casos de prueba derivados de los criterios de aceptación.

Esta especificación deberá utilizarse como base para la elaboración del diseño técnico y de la estrategia de pruebas.
