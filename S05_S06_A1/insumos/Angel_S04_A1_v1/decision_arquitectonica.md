# ADR-001: Selección del estilo arquitectónico

**Fecha:** 2026-10-10
**Estado:** Aceptado
**Autor:** Ángel Sebastián Kociankowski Montelongo (A01379225)
**Proyecto:** SGPIS, Sistema de Gestión del Programa Parque Industrial Seguro (AMPIP)
**Insumos:** `SRS_final.md` v1.4, `stack_decision.md` (S01_A2), análisis del agente en `evidencia_agente/estilo_agente.md`

## Contexto

SGPIS sustituye el Excel, el correo y las carpetas compartidas con que AMPIP lleva hoy el expediente de cada parque industrial. Son unos 41 parques, con 70 a 80 previstos, y cerca de 150 usuarios en siete roles. Lo construye una sola persona en 12 semanas, con un stack que ya está fijo desde S01_A2: FastAPI, PostgreSQL 16, React con Vite y Docker compose.

Los requerimientos no funcionales no pesan igual. Ordenados por cuánto condicionan la arquitectura:

1. **Control de acceso y trazabilidad (RNF-01 a RNF-04).** Cero accesos cruzados entre parques; Coordinación AMPIP y el Administrador técnico no abren evidencias de seguridad; bitácora de solo append para toda operación sobre evidencias. Además, los permisos cambian con datos vivos: reasignación del consultor con retiro inmediato (RF-10-AC-2), acceso temporal del consultor de comité (RF-13), bajas (RF-29). Es el riesgo principal del sistema, y se controla mejor si la autorización se decide en un solo lugar.
2. **Reglas de dominio que cruzan entidades (RD-02, RD-04, RD-09).** Para calificar el criterio 3.1 tiene que existir un análisis de riesgos vigente (RF-17). Para capturar "otorgar" hay que revisar el estado de todos los criterios y la Opinión final (RF-14, RF-15). Son validaciones que deben rechazar en la misma solicitud, y se resuelven con una transacción si todo vive en la misma base.
3. **La restricción del equipo (2.4, RD-12).** Un desarrollador y cero presupuesto para licencias por usuario. Cualquier pieza de infraestructura adicional la opera la misma persona que escribe el código.
4. **Procesos fuera de la solicitud (RNF-11, RNF-12, RNF-13).** Revisión diaria de plazos a las 00:00 de Ciudad de México, correo con reintentos y respaldos diarios. Piden un proceso que corra solo; no piden una arquitectura de eventos.
5. **Escala y rendimiento (RNF-06, RNF-07, RNF-08, RNF-10).** 80 parques por 1,500 evidencias son 120,000 registros, y 99 % de disponibilidad mensual tolera unas 7 horas de caída. Un solo servidor con PostgreSQL los cumple. El propio SRS aclara que estas cifras las propuso el equipo y no el cliente, así que no justifican distribuir el sistema.

## Decisión

Arquitectura **cliente-servidor**: una SPA en React consume una API REST, y el backend es un **monolito modular en capas** con un proceso worker aparte.

- **Cliente.** La SPA presenta formularios, tablas y gráficas. No decide permisos ni reglas: lo que oculta, la API lo vuelve a negar.
- **API.** Un solo despliegue de FastAPI que implementa el contrato `openapi.yaml` (S04_A2). Se divide en cinco módulos de dominio (catálogo, organización, expediente, dictamen, reportes) más la bitácora transversal. Dentro de la API hay cuatro capas: routers, autorización, servicios de dominio y repositorios. La autorización por parque es una sola dependencia de FastAPI que usan todas las rutas. Un módulo llama a los servicios de otro y nunca lee sus tablas.
- **Worker.** El mismo código y la misma imagen, levantado como otro contenedor. Corre la revisión diaria de plazos, despacha una outbox de correo guardada en PostgreSQL y hace el respaldo y la depuración. No uso Redis ni RabbitMQ.
- **Datos.** PostgreSQL para todo el dominio, las sesiones y la outbox. Los archivos de evidencia van a un bucket privado compatible con S3, y solo se descargan a través de la API, para que cada apertura quede en la bitácora.
- **Autenticación.** JWT con `sub` y `sid`, validado en cada solicitud contra una tabla de sesiones. Un JWT stateless no invalida el token al cerrar sesión ni expira por inactividad (RF-26-AC-5 y AC-6); es la misma conclusión del Sprint 1 (S03_A2) y quedó escrita en el contrato de S04_A2.

El detalle está en `diagrama_componentes.puml` (C4 niveles 2 y 3) y `diagrama_despliegue.puml`.

## Alternativas consideradas

| Criterio | **Elegida:** monolito modular en capas + SPA | Microservicios | Orientada a eventos | Monolito MVC con Jinja2 + HTMX |
|---|---|---|---|---|
| Escalabilidad | Suficiente para 80 parques y 150 usuarios; crece en vertical o con réplicas del mismo contenedor | La más alta, por servicio, sin demanda que la pida | Alta para procesos asíncronos; irrelevante con este volumen | Igual que la elegida |
| Mantenibilidad | Buena mientras se respeten las fronteras entre módulos; las reglas viven en un solo lugar | Buena dentro de cada servicio, mala en las reglas que cruzan servicios (RD-09, RF-17) | Media a baja: el flujo queda implícito y cuesta depurarlo | Buena para pantallas simples |
| Complejidad de implementación | Media: dos procesos, una base, un bucket | Muy alta: gateway, contratos entre servicios, datos distribuidos | Alta: broker, idempotencia, orden de eventos | Baja |
| Adecuación a un desarrollador | Alta | Muy baja | Baja | Muy alta |
| Riesgo sobre RNF-01 a RNF-03 | Bajo: un punto de autorización y bitácora en la misma transacción | Alto: autorización y bitácora repartidas | Medio: la bitácora depende de que todo evento se procese | Bajo |
| Consistencia de RD-09 y RF-17 | Transaccional | Distribuida | Eventual | Transaccional |

**Microservicios.** Lo descarté porque reparte justo lo que más pesa. La validación de "otorgar" tendría que consultar criterios, Opiniones y análisis de riesgos en servicios distintos, y RNF-01 se tendría que probar en cada uno. Para una sola persona en 12 semanas, operar cinco despliegues no es viable.

**Orientada a eventos.** Encaja con las transiciones automáticas (RF-27-AC-4 y AC-7) y con los avisos, pero no con lo central: con consistencia eventual, el comité podría capturar "otorgar" sobre un estado de criterios que todavía no se actualiza. Me quedo con las dos ideas útiles del estilo, eventos dentro del proceso y outbox para el correo, sin agregar un broker.

**Monolito MVC renderizado en servidor.** Es la opción más simple y es el plan alterno que dejé en `stack_decision.md` si el frontend se atora. No la elegí como principal porque el curso pide scaffolding de frontend en las semanas 7 y 8 y el stack ya fijó React. La arquitectura elegida no la cierra: los servicios de dominio no dependen de la capa HTTP, así que se pueden servir con plantillas si hace falta.

## Consecuencias

**A favor**
- Las reglas del dictamen y el bloqueo por análisis de riesgos se validan en una transacción, sin consistencia distribuida.
- RNF-01, RNF-02 y RNF-04 se deciden en una sola dependencia, que se prueba con una prueba parametrizada de al menos 20 combinaciones usuario-parque, como pide RNF-01.
- Un repositorio, una imagen y un `docker compose` sirven igual en mi Mac que en el servidor.
- El costo es de infraestructura y volumen de correo, nunca por usuario (RD-12).

**En contra, y cómo lo manejo**
- **Un solo servidor.** RNF-08 depende de ese host. Lo cubre el monitoreo externo de `/api/v1/salud` cada 5 minutos, y en el calendario de despliegues quedan bloqueadas las fechas críticas que declare Coordinación AMPIP.
- **Los módulos se pueden erosionar.** Un monolito modular se vuelve un monolito sin estructura en cuanto un módulo lee tablas de otro. Propongo al equipo agregar la regla a la Definition of Done y verificarla con `import-linter` cuando exista el pipeline de CI, que la DoD de S03_A2 dejó diferido.
- **El worker puede fallar sin que nadie lo note.** Si se cae, dejan de marcarse atrasos sin ningún error visible. Por eso registra su última corrida y el health check falla si pasan más de 24 horas sin ejecución.
- **Respaldos en la misma región.** RNF-05 obliga a un solo proveedor y región, así que el respaldo protege contra borrado o corrupción, no contra la caída de la región completa. Lo dejo escrito como riesgo aceptado.
- **RNF-02 a nivel infraestructura.** La aplicación impide que Coordinación o el Administrador técnico abran evidencias, pero quien tenga SSH al servidor o las credenciales del bucket podría leerlas. El acceso SSH se limita al Administrador técnico; si AMPIP quiere más, la siguiente medida sería cifrar los archivos en la aplicación.

**Pendientes con AMPIP:** proveedor cloud concreto y su región (México o Estados Unidos, RNF-05); presupuesto mensual de infraestructura.

## Evaluación de la recomendación del agente

El agente recomendó lo mismo que elegí, y de nuevo eso no lo tomo como validación: es la respuesta más común para este tipo de sistema. Lo que sí revisé fue si el análisis se sostenía en el SRS, y se sostenía: ordenó los RNF por su efecto en la arquitectura y no por categoría, y fue explícito en que las cifras de rendimiento no vienen del cliente.

Corregí tres cosas al pasar la recomendación a los diagramas (detalle en `decisiones_diagramas.md`):

1. Ponía al Administrador técnico a usar "herramientas técnicas de administración" desde la SPA. La frase viene de RF-03-AC-3, pero el SRS no dice qué son esas herramientas. Decidí que son de infraestructura (desplegar, restaurar respaldos, revisar registros) y se usan por SSH: el contrato de la API no tiene endpoints técnicos, y su cuenta en la aplicación no da acceso a parques ni evidencias. Queda por confirmar con AMPIP.
2. El monitoreo llamaba a `/api/salud`, una ruta que no está en el contrato. La agregué a `openapi.yaml` como `GET /api/v1/salud`, sin sesión y sin datos del programa.
3. Proponía verificar las fronteras entre módulos "en CI", que todavía no existe. Mientras no haya pipeline, la regla se revisa a mano como parte de la Definition of Done.
