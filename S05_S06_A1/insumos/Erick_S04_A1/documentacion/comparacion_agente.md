# Comparación de estilos arquitectónicos para SGPIS

## Base del análisis

SGPIS es una aplicación web sin integraciones externas en el entregable, con React + Vite como cliente, FastAPI como API y PostgreSQL como base transaccional. El SRS delimita una escala inicial de hasta 80 parques y 1,500 evidencias por parque (RNF-10), con 30 cargas simultáneas como concurrencia de diseño (RNF-07). El análisis considera que una sola persona desarrollará y operará la solución.

## Requerimientos no funcionales que condicionan la arquitectura

| RNF | Implicación arquitectónica |
|---|---|
| RNF-01, RNF-02 y RNF-04 | La autorización debe aplicarse en la API a nivel de rol, parque, asignación y tipo de evidencia. No basta con ocultar opciones en React; las consultas y descargas deben validarse centralmente. |
| RNF-03 | Se necesita una bitácora transversal, completa y de solo append. Su inmutabilidad debe reforzarse en la base de datos, no depender solo de la interfaz. |
| RNF-05 y RNF-15 | Los archivos no pertenecen a PostgreSQL: requieren almacenamiento de objetos regionalizado, cifrado, sin acceso público y URL firmadas de máximo cinco minutos emitidas después de autorizar al usuario. |
| RNF-06, RNF-07, RNF-10, RNF-16 y RNF-17 | La API y PostgreSQL requieren consultas paginadas e indexadas, pruebas de carga y manejo eficiente de cargas. Los límites definidos no exigen distribución por servicios independientes. |
| RNF-08 | Requiere monitoreo externo, comprobación de salud y despliegues controlados en fechas críticas; no implica por sí mismo alta disponibilidad distribuida. |
| RNF-09 y RNF-18 | React debe soportar carga múltiple con progreso y navegación no bloqueante en navegadores móviles, mientras FastAPI confirma cada archivo sin bloquear otras solicitudes. |
| RNF-11 | Fechas, procesos diarios y reglas de vencimiento deben usar consistentemente `America/Mexico_City`. |
| RNF-12, RNF-13 y RNF-14 | Se requieren trabajos diferidos para reintentos de correo, respaldos y depuración con retención; deben ser idempotentes, auditables y recuperables. |

## Alternativa 1: Monolito modular por capas

Una única API de FastAPI organizada por módulos de dominio, por ejemplo: identidad y autorización, catálogo y evaluación, parques y expediente, evidencias, dictámenes, bitácora y notificaciones. Cada módulo separa API, casos de uso/reglas de negocio, persistencia e infraestructura. React + Vite permanece como cliente separado; PostgreSQL conserva datos estructurados y el almacenamiento de objetos conserva archivos.

**Ventajas**

- Centraliza las validaciones de acceso exigidas por RNF-01, RNF-02 y RNF-04, reduciendo el riesgo de que un endpoint permita acceso cruzado.
- Permite mantener una transacción coherente para operaciones relacionadas, como actualizar el estado de una evidencia y registrar el evento de bitácora de RNF-03.
- Un solo despliegue, repositorio, modelo de datos, monitoreo y flujo de pruebas reduce el trabajo operativo para una persona.
- Puede cumplir los límites de 80 parques, 1,500 evidencias por expediente y 30 cargas concurrentes mediante índices, paginación, consultas acotadas y almacenamiento de objetos, sin coordinación distribuida.
- Los trabajos de plazos, correos, retención y respaldos pueden ejecutarse como procesos en segundo plano del mismo sistema, conservando trazabilidad común.

**Desventajas y trade-offs**

- Escala la API completa aunque la carga se concentre en evidencias o notificaciones; no permite escalar un dominio de forma aislada desde el inicio.
- La mantenibilidad depende de respetar límites entre módulos. Sin esa disciplina, las reglas de negocio podrían acoplarse indebidamente.
- Los trabajos en segundo plano comparten operación y recursos con la API; deben diseñarse idempotentes y con registro de fallos.
- La complejidad es baja a media: exige una estructura interna clara, pero evita comunicación entre servicios, consistencia distribuida y observabilidad distribuida.

**Viabilidad para una persona:** alta. Ofrece separación suficiente para los dominios del SRS sin multiplicar infraestructura ni tareas de soporte.

## Alternativa 2: Microservicios por dominio

Servicios independientes, por ejemplo, identidad/autorización, expedientes y evaluación, evidencias, notificaciones y bitácora, comunicados por HTTP o mensajería. Cada servicio podría tener su propio ciclo de despliegue y, potencialmente, su propia persistencia.

**Ventajas**

- Permite escalar de manera independiente los componentes de mayor carga, como las cargas de evidencias o el envío de correos.
- Establece límites físicos entre dominios y permite despliegues independientes si el sistema crece o incorpora integraciones futuras.
- Aísla parcialmente fallos de componentes no críticos, por ejemplo notificaciones, si se diseña con colas y tolerancia a fallos.

**Desventajas y trade-offs**

- El SRS no justifica esta distribución: la escala prevista es 80 parques y 30 cargas simultáneas, y no hay integraciones externas en el entregable.
- RNF-01 a RNF-04 se vuelven más difíciles de garantizar: cada servicio debe aplicar de forma consistente permisos por parque, rol y evidencia, además de proteger la propagación de identidad entre servicios.
- RNF-03 requiere coordinar una bitácora completa e inmutable entre servicios; aparecen problemas de eventos duplicados, orden parcial y fallos parciales.
- Las reglas que involucran expediente, evidencia, calificación y dictamen requieren consistencia entre servicios, por lo que habría que introducir transacciones distribuidas, compensaciones o consistencia eventual.
- Aumenta de forma importante la complejidad de implementación y operación: contratos entre servicios, autenticación servicio a servicio, colas, observabilidad, despliegues, pruebas de integración, respaldos y diagnóstico.

**Viabilidad para una persona:** baja. Sus beneficios potenciales no compensan la carga operativa ni el mayor riesgo de errores de seguridad y consistencia para el alcance actual.

## Tabla comparativa

| Criterio | Monolito modular por capas | Microservicios por dominio |
|---|---|---|
| Escalabilidad | Adecuada para RNF-06, RNF-07, RNF-10, RNF-16 y RNF-17 con escalamiento vertical, índices, paginación y almacenamiento de objetos. | Alta en teoría por dominio, pero innecesaria para la carga especificada y costosa de habilitar. |
| Mantenibilidad | Alta si se preservan módulos y capas; controles de acceso, bitácora y configuración se reutilizan. | Media a baja al inicio: límites físicos claros, pero contratos y cambios coordinados multiplican el mantenimiento. |
| Complejidad de implementación | Baja a media: una API, una base transaccional y procesos en segundo plano. | Alta: comunicación distribuida, seguridad entre servicios, consistencia, colas y observabilidad. |
| Seguridad y privacidad | Más fácil de aplicar uniformemente para RNF-01 a RNF-05 y RNF-15 desde una capa de autorización común. | Más superficies y puntos de fallo; cada servicio debe implementar y probar las mismas restricciones. |
| Operación y disponibilidad | Un despliegue y monitoreo simplifican cumplir RNF-08, respaldos y restauración. | Mayor aislamiento potencial, a cambio de más servicios que monitorear, respaldar y recuperar. |
| Viabilidad para una persona | Alta. | Baja. |

## Recomendación para evaluación

La alternativa más adecuada para evaluar es el **monolito modular por capas**. Se alinea con la prioridad de simplicidad y mantenibilidad, el desarrollo individual y la ausencia de integraciones externas en el alcance. También responde directamente a los riesgos centrales del SRS: control de acceso granular sobre evidencias sensibles (RNF-01, RNF-02 y RNF-04), bitácora inmutable (RNF-03), almacenamiento de objetos protegido (RNF-05 y RNF-15) y rendimiento acotado para la escala prevista (RNF-06, RNF-07, RNF-10, RNF-16 y RNF-17).

Microservicios solo sería razonable si mediciones posteriores mostraran que un dominio concreto excede esos límites, o si se incorporaran integraciones y equipos que justificaran ciclos de despliegue independientes. Esta es una recomendación comparativa; no constituye una decisión arquitectónica definitiva ni un ADR.
