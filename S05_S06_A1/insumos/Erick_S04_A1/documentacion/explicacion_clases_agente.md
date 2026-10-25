# Explicacion del modelo de clases de SGPIS

## Alcance del modelo

El diagrama representa las entidades persistentes centrales del dominio descrito en `SRS_equipo.md`. Es compatible con el monolito modular por capas del ADR: son clases de dominio, no microservicios ni tablas definitivas. Se omiten reportes, pantallas, notificaciones y procesos diarios porque son consultas, salidas o comportamientos sobre las entidades modeladas, no entidades del negocio por si mismos.

Las funciones posteriores que requieren datos adicionales, como auditorias, visitas de validacion, hallazgos, solicitudes de renovacion y prorrogas, no se incluyen para conservar el diagrama centrado en el recorrido principal y el alcance priorizado. Su incorporacion debe derivarse de sus RF cuando entren al backlog. Se mantienen los estados del distintivo y la fecha de vencimiento de evidencia porque el SRS los define, pero no se modelan sus flujos posteriores completos.

## Entidades principales

- `Usuario` y `Rol` representan cuentas y los siete roles definidos en RF-03. No se usa herencia: los roles determinan permisos, no tipos distintos de persona.
- `Parque`, `Desarrollador` y `Generacion` representan el parque industrial, la empresa desarrolladora y cada convocatoria. `Expediente` vincula un parque con una generacion y concentra su evaluacion, fases y resultados.
- `VersionCatalogo`, `Estandar`, `Subestandar`, `Criterio` y `MarcaCriterioTipo` modelan el catalogo versionado y las marcas O/R/NA para los cuatro tipos de PI (RF-01 y RF-04).
- `EvaluacionCriterio` materializa el criterio aplicable dentro de un expediente. Guarda la marca aplicable y su estado de calificacion, por lo que soporta las transiciones de RF-27 sin alterar el catalogo historico.
- `Evidencia` contiene metadatos y la referencia al objeto externo; `EvidenciaCriterio` representa el vinculo entre archivo y criterio. `Observacion` pertenece a ese vinculo.
- `RevisionAnalisisRiesgos`, `PlanTrabajo`, `DefinicionFase` y `FaseExpediente` cubren las reglas de riesgo, atraso y avance de fases de RF-09, RF-16, RF-17 y RF-32.
- `OpinionCumplimiento`, `EvaluacionDesempeno`, `SesionComite`, `AccesoComite`, `Dictamen` y `Distintivo` modelan el cierre del recorrido de cumplimiento y la vigencia posterior.
- `EventoBitacora` representa el registro inmutable exigido por RF-35 y RNF-03.

## Relaciones y multiplicidades relevantes

- Un `Parque` puede tener cero o muchos `Expediente`; cada expediente pertenece a exactamente un parque y una generación. La restriccion de unicidad `(parque, generacion)` es una propuesta tecnica derivada de que RF-28 crea parques dentro de una generacion y RF-31 conserva su historial. Debe validarse al diseñar las reglas de alta historica.
- Una `VersionCatalogo` compone estandares, subestandares y criterios. Cada `Criterio` compone exactamente cuatro `MarcaCriterioTipo`, una por cada `TipoPI`, como exige el CSV de RF-01.
- Un `Expediente` compone una o mas `EvaluacionCriterio`; cada una refiere a un criterio de catalogo. Esto mantiene separado el catalogo versionado de los estados particulares de cada parque.
- Un `Evidencia` puede estar vinculada a uno o varios criterios mediante `EvidenciaCriterio`. Esta clase de asociacion es necesaria porque RF-05-AC-7 permite aceptar un mismo archivo para un criterio y observarlo para otro. Su nombre y separacion respecto de `Evidencia` son una propuesta de modelado que requiere validacion, aunque la independencia de estados si esta definida por el SRS.
- La autorrelacion `versionAnterior` conserva la sucesion de versiones de una evidencia requerida por RF-05. Cada version puede tener a lo sumo una predecesora y una sucesora; si se necesitara una agrupacion independiente para el documento logico, el SRS no la especifica y se tendria que validar.
- Un expediente conserva cero o muchas `AsignacionConsultor` para el historial de reasignaciones. Solo una puede estar vigente por expediente; es una restriccion directamente alineada con RF-10-AC-2.
- `VinculoAPPI` permite varios usuarios APPI por parque y guarda la marca de contacto principal. Hay como maximo un contacto principal activo, pero puede no existir tras una baja, exactamente como define RF-34.
- Un `PlanTrabajo` se asocia a una sola `EvaluacionCriterio` y a un responsable usuario APPI del mismo parque. La multiplicidad maxima de un plan por criterio representa el plan vigente; si se requiere historial de cambios, el SRS no lo define y habria que confirmarlo.
- Un expediente tiene hasta dos `OpinionCumplimiento` (intermedia y final), con a lo sumo una final. La regla de unicidad de la opinion final se establece en RF-12-AC-3.
- Cada expediente compone las nueve `FaseExpediente` de la secuencia definida en RF-32; `DefinicionFase` mantiene esa secuencia como datos configurables y no como logica fija.
- Un expediente tiene a lo sumo una `EvaluacionDesempeno` y una `SesionComite`. Ambas cardinalidades son propuestas simplificadoras: el SRS describe una evaluacion y una apertura/cierre de sesion, pero no precisa si alguno de esos registros podria repetirse o reabrirse.
- Una `SesionComite` puede tener cero o un `AccesoComite`. RF-13 exige que el acceso temporal se otorgue al confirmar la asignacion del consultor de comite, pero no exige que la entidad de sesion nazca ya con ese acceso. La composicion se conserva porque el acceso no tiene sentido fuera de la sesion; la multiplicidad cambia de `1` a `0..1` para permitir la sesion antes de habilitarlo.
- La restriccion `MismoExpediente` sobre `EvidenciaCriterio` exige que todos los vinculos de una misma evidencia apunten a `EvaluacionCriterio` del mismo expediente. Conserva la vinculacion a varios criterios que RF-05-AC-7 requiere, sin permitir reutilizar un archivo entre parques o generaciones distintas.
- Un expediente tiene hasta un `Dictamen`. La relacion `Dictamen`--`Distintivo` es una asociacion, no una composicion: un dictamen `otorgar` firmado origina como maximo un distintivo (RF-14 y RD-08), pero el distintivo mantiene vigencia, estados, solicitudes de renovacion y prorrogas propias (RF-38 y RD-16). Por ello sus ciclos de vida no deben quedar acoplados por composicion.
- `EventoBitacora` tiene asociaciones opcionales con usuario y parque porque algunos eventos, como ciertos intentos de autenticacion, pueden no contar con ambos datos. Sus registros no se actualizan ni eliminan.

## Reglas que el diagrama no sustituye

Las restricciones de autorizacion por rol, parque y asignacion; el bloqueo de calificacion en estandares 2, 3 y 7; la validacion previa al dictamen; los porcentajes de cumplimiento; y las transiciones de estado deben implementarse como reglas de dominio y pruebas. El diagrama las refleja mediante entidades y notas, pero no reemplaza los criterios de aceptacion ni las reglas RNF-01 a RNF-04.

## Revisión crítica del agente y decisiones de diseño propias

Después de revisar el diagrama de clases generado por el agente de IA, considero que su propuesta representa adecuadamente las entidades principales de SGPIS y las relaciones entre ellas. Sin embargo, identifiqué algunas decisiones de diseño que podían mejorarse para representar con mayor precisión las reglas de negocio y el comportamiento esperado del sistema.

### 1. Relación entre SesionComite y AccesoComite

Originalmente, el agente propuso una composición con multiplicidad de 1 a 1, lo que implicaba que cada sesión debía contar obligatoriamente con un registro de acceso.

Consideré que esta relación era demasiado restrictiva, ya que una sesión podría crearse antes de habilitar el acceso temporal del consultor. Por ello, decidí modificar la multiplicidad a `0..1` en el extremo de `AccesoComite`, conservando la composición porque dicho acceso depende de la sesión.

Esta modificación permite representar un proceso más flexible sin contradecir los requerimientos relacionados con la asignación de consultores (RF-13).

### 2. Restricción de evidencias por expediente

El agente propuso correctamente la clase `EvidenciaCriterio` para permitir que una evidencia se vincule con varios criterios. Sin embargo, el modelo original no expresaba explícitamente que estos criterios debían pertenecer al mismo expediente.

Consideré importante agregar la restricción `MismoExpediente`, ya que el sistema maneja información de distintos parques industriales y generaciones. Sin esta restricción, el modelo podría permitir asociaciones inconsistentes entre evidencias y evaluaciones de expedientes diferentes.

Este cambio refuerza la consistencia de los datos y complementa los controles de acceso establecidos en el SRS.

### 3. Relación entre Dictamen y Distintivo

Originalmente, el agente utilizó una composición entre `Dictamen` y `Distintivo`, indicando que el distintivo dependía completamente del ciclo de vida del dictamen.

Decidí reemplazarla por una asociación, ya que, aunque el distintivo se origina a partir de un dictamen favorable, posteriormente tiene vigencia y estados propios, además de contemplar procesos de renovación y prórroga (RF-38 y RD-16).

Considero que una asociación representa mejor esta relación, pues permite conservar el vínculo entre ambas entidades sin asumir que necesariamente comparten el mismo ciclo de vida.

### Conclusión

El agente de IA fue útil para identificar las entidades y proponer una estructura inicial coherente con el SRS. Sin embargo, la revisión permitió detectar relaciones demasiado restrictivas y reglas de negocio que no estaban representadas explícitamente.

Las modificaciones realizadas buscan mejorar la precisión del modelo, mantener la integridad de los datos y facilitar futuras ampliaciones del sistema. Esto demuestra la importancia de revisar críticamente las propuestas generadas por IA en lugar de aceptarlas sin validación.

## Cambios realizados

- `SesionComite`--`AccesoComite`: multiplicidad corregida de `1` a `0..1` en el extremo de acceso, con nota de temporalidad y referencia a RF-13.
- `EvidenciaCriterio`: se agrego la restriccion UML `MismoExpediente`, fundamentada en el vinculo de una evidencia con varios criterios de un mismo parque de RF-05-AC-7.
- `Dictamen`--`Distintivo`: se reemplazo la composicion por asociacion y se documento que solo un dictamen `otorgar` firmado puede originar el distintivo, conforme a RF-14, RD-08, RF-38 y RD-16.
