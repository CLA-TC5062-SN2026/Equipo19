# Estilo arquitectónico para SGPIS

Respuesta del agente al prompt de S04_A1. Fuentes: `SRS_final.md` v1.4 (31 RF, 14 RNF, 13 RD) y `stack_decision.md`.

## 1. Requerimientos no funcionales que pesan en la decisión

Los 14 RNF no pesan igual. Los ordeno por cuánto condicionan la forma del sistema, no por su categoría.

**Peso alto: control de acceso y trazabilidad (RNF-01, RNF-02, RNF-03, RNF-04).** Aquí está el riesgo principal del sistema. RNF-01 exige 0 accesos cruzados entre parques; RNF-02 y RNF-04 exigen que Coordinación AMPIP y el Administrador técnico no abran evidencias de seguridad ni del estándar 7; RNF-03 exige que el 100 % de las operaciones sobre evidencia quede en una bitácora de solo append. Además, la autorización depende de datos que cambian: reasignación de consultor con retiro inmediato (RF-10-AC-2), acceso temporal del consultor de comité (RF-13-AC-3), bajas (RF-29). Consecuencia: la autorización tiene que evaluarse en un solo lugar y leer el estado de asignaciones de la misma fuente transaccional. Cada unidad de despliegue adicional es un punto más donde RNF-01 puede fallar.

**Peso alto: restricción de equipo (sección 2.4, RD-12).** Un desarrollador, 12 semanas, sin licencias ni auditorías pagadas. No es un RNF formal, pero en la práctica pesa más que cualquier métrica de rendimiento. Cada broker, servicio o pipeline adicional lo opera la misma persona que escribe el código.

**Peso alto: consistencia de reglas de dominio que cruzan entidades (RD-02, RD-04, RD-09).** Calificar el criterio 3.1 depende de que exista un análisis de riesgos vigente (RF-17); capturar "otorgar" depende del estado de todos los criterios O y R y de la Opinión final (RF-14, RF-15); la calificación cambia sola cuando llega evidencia nueva (RF-27-AC-7). Son validaciones síncronas que leen catálogo, evidencias, criterios y opiniones en una misma operación y responden con un mensaje de rechazo inmediato. Con una sola base de datos se resuelven en una transacción; con bases separadas se vuelven un problema de consistencia distribuida.

**Peso medio: procesos programados y notificación (RNF-11, RNF-12).** La revisión diaria de plazos (RF-09-AC-2, RF-30-AC-2) corta a las 00:00 de Ciudad de México y todo aviso sale por correo con 3 reintentos y registro de falla. Esto exige un componente que corra fuera del ciclo petición-respuesta. No exige una arquitectura orientada a eventos; exige un worker y un programador de tareas.

**Peso medio: manejo de archivos (RF-06, RNF-05, RNF-07, RNF-13, RNF-14).** Archivos de hasta 100 MB, región fija, respaldo diario con retención de 30 días, conservación de 6 años. Los binarios van a almacenamiento de objetos, no a PostgreSQL. Las descargas deben pasar por el backend, o por URLs firmadas que se emitan y registren una por una; si el cliente descarga directo del bucket sin pasar por el servidor, esa apertura queda fuera de la bitácora de RNF-03.

**Peso bajo: escalabilidad, rendimiento y disponibilidad (RNF-06, RNF-07, RNF-08, RNF-10).** 80 parques con 1,500 evidencias cada uno son 120,000 registros; 150 usuarios; 30 cargas concurrentes. Un PostgreSQL 16 con índices por parque y criterio maneja ese volumen sin esfuerzo. RNF-08 (99 % mensual) admite unas 7 horas de caída al mes, compatible con un solo servidor. Y el propio SRS aclara, en "Supuestos y pendientes", que estas cifras las propuso el equipo y no el cliente. No sirven para justificar distribución horizontal.

**RNF-09** (carga desde navegador móvil) afecta al frontend, no al estilo del backend.

Conclusión: la arquitectura la deciden la seguridad por parque, la consistencia de las reglas del dictamen y la capacidad de una sola persona. La escala no.

## 2. Recomendación: cliente-servidor con backend monolítico modular en capas

**Cliente.** SPA en React + Vite que consume una API REST por HTTPS. Presenta formularios, tablas y gráficas (2.4) y valida formato de entrada. Ninguna regla de autorización ni de negocio vive en el cliente; lo que el cliente oculta, el servidor lo vuelve a negar.

**Servidor.** Un solo despliegue de FastAPI, dividido en módulos por área de dominio y en capas dentro de cada módulo.

Módulos:

| Módulo | RF que cubre |
|---|---|
| `autenticacion` | RF-26 |
| `catalogo` | RF-01, RF-24, RF-25 |
| `organizacion` (generaciones, parques, usuarios, asignaciones) | RF-02, RF-03, RF-10, RF-28, RF-29, RF-31 |
| `expediente` (autoevaluación, evidencias, calificación, plan, análisis de riesgos) | RF-04 a RF-09, RF-11, RF-16, RF-17, RF-27 |
| `dictamen` (Opiniones, comité, dictamen) | RF-12 a RF-15 |
| `reportes` | RF-07, RF-08, RF-21, RF-23 |
| `plazos` y `notificaciones` | RF-09-AC-2, RF-19, RF-20, RF-30 |
| `bitacora` (transversal) | RNF-03 |

Capas, de afuera hacia adentro:

1. **API:** routers de FastAPI y esquemas Pydantic. Solo traduce HTTP.
2. **Autorización:** una dependencia de FastAPI que resuelve usuario, rol, parque y categoría de documento, y que usan todos los routers. Es el único punto donde se decide RNF-01, RNF-02 y RNF-04, y por eso se puede probar de forma exhaustiva (las 20 combinaciones de RNF-01 como prueba parametrizada).
3. **Servicios de dominio:** las dos máquinas de estado de RF-27 como tablas de transición explícitas, la regla de las tres condiciones de RD-09, las fórmulas de RD-02. Python puro, probable sin HTTP ni base de datos.
4. **Repositorios y adaptadores:** SQLAlchemy 2.0 para PostgreSQL, un adaptador de almacenamiento de objetos y uno de correo.

Regla de módulos: un módulo llama a los servicios de otro, no lee sus tablas directamente. Se puede verificar en CI con `import-linter`.

**Worker.** Un segundo proceso del mismo código y la misma base, levantado como otro servicio en docker compose. Corre la revisión diaria de plazos con zona horaria America/Mexico_City (RNF-11) y despacha correos desde una tabla de salida (outbox) en PostgreSQL con contador de reintentos (RNF-12). No hace falta Redis ni RabbitMQ.

Decisiones que amarran RNF específicos:

- **RNF-03:** la tabla de bitácora se escribe en la misma transacción que la operación, y el usuario de base de datos de la aplicación no tiene `UPDATE` ni `DELETE` sobre ella (`REVOKE`). El solo append lo impone PostgreSQL, no la ausencia de un endpoint.
- **RNF-02 y RF-16:** cada evidencia lleva una categoría (seguridad, administrativa, estándar 7); el contenido solo se sirve por un endpoint del backend que consulta la capa de autorización.
- **RNF-13 y RNF-14:** `pg_dump` diario y sincronización del bucket, como tarea del worker o cron del host; la depuración por antigüedad excluye por diseño bitácora y dictámenes.

Por qué esta opción: un repositorio, un despliegue, una transacción para RF-14 y RF-17, un punto de autorización. Las capas dan mantenibilidad; los módulos dan fronteras que permiten extraer una parte más adelante si algún día hace falta.

Sobre la etiqueta "MVC": describe una interfaz renderizada en servidor. Con SPA más API, la vista está en React y el backend no tiene vistas; llamarlo MVC confunde. "Capas" describe mejor el backend. La variante MVC real aparece abajo como alternativa C.

## 3. Alternativas y trade-offs

**A. Microservicios.** Servicios separados para autenticación, catálogo, expediente, dictamen y notificaciones, cada uno con su base y un API gateway. Gana escalado independiente, que con 150 usuarios no se necesita. Pierde lo que más pesa: RD-09 y RF-17 se vuelven llamadas entre servicios o datos replicados, RNF-01 se valida en cada servicio y RNF-03 exige agregar bitácoras de varios orígenes. Para un desarrollador significa cinco o más despliegues, contratos entre servicios, trazas distribuidas y CI por servicio dentro de 12 semanas.

**B. Orientada a eventos.** Un bus (RabbitMQ o Redis Streams) y componentes que reaccionan a `EvidenciaEnviada`, `CriterioCalificado`, `PlazoVencido`. Encaja bien con las transiciones automáticas (RF-27-AC-4, AC-7) y con los avisos. Falla en lo central: las reglas del dictamen son validaciones síncronas que deben rechazar en la misma petición (RF-14-AC-3 a AC-5). Con consistencia eventual, el comité podría capturar "otorgar" sobre un estado de criterios todavía no actualizado. La depuración también se complica. Lo útil de este estilo ya está en la recomendación: eventos de dominio dentro del proceso y outbox para correo.

**C. Monolito MVC renderizado en servidor (FastAPI + Jinja2 + HTMX).** Es el plan alterno de `stack_decision.md`. Es la opción de menor complejidad: sin SPA separada, sin CORS, sesión por cookie, un solo lenguaje. Para formularios y tablas (2.4) y para carga desde el navegador móvil (RNF-09) alcanza. En contra: no corresponde al stack elegido (React + Vite), el curso pide scaffolding de frontend en las semanas 7-8 y las gráficas interactivas cuestan más. Conviene mantenerla como salida de emergencia; la recomendación la permite, porque los servicios de dominio no dependen de la capa API.

| Criterio | Recomendada: monolito modular en capas + SPA | A. Microservicios | B. Orientada a eventos | C. Monolito MVC con Jinja2 + HTMX |
|---|---|---|---|---|
| Escalabilidad | Suficiente para 80 parques y 150 usuarios (RNF-10); escala vertical y réplicas del mismo contenedor si se requiere | La más alta, por servicio; sin demanda que la justifique | Alta en procesamiento asíncrono; irrelevante con este volumen | Igual que la recomendada |
| Mantenibilidad | Buena si se respeta la frontera entre módulos; reglas en un solo lugar | Buena por servicio, mala en reglas que cruzan servicios (RD-09, RF-17) | Media-baja: flujo implícito, difícil de seguir y depurar | Buena para pantallas simples; plantillas mezclan algo de lógica de presentación |
| Complejidad de implementación | Media: dos procesos, una base, un bucket | Muy alta: gateway, contratos, datos distribuidos | Alta: broker, idempotencia, reintentos, orden de eventos | Baja |
| Adecuación a un solo desarrollador | Alta | Muy baja | Baja | Muy alta |
| Riesgo sobre RNF-01/02/03 | Bajo: un punto de autorización, bitácora transaccional | Alto: autorización y bitácora repartidas | Medio: la bitácora depende de que todo evento se procese | Bajo |
| Consistencia de RD-09 y RF-17 | Transaccional | Distribuida | Eventual | Transaccional |
| Ajuste al stack elegido | Completo | Completo, con infraestructura extra | Requiere broker adicional | Parcial: descarta React |

## 4. Riesgos de la recomendación

- **Erosión de módulos.** Un monolito modular se degrada a monolito sin estructura si un módulo empieza a leer tablas de otro. Mitigación: regla de imports verificada en CI.
- **Un solo servidor.** RNF-08 depende de ese host. Mitigación: health check externo cada 5 minutos y calendario de despliegues que bloquee las fechas críticas declaradas por Coordinación AMPIP.
- **Worker silencioso.** Si el worker se cae, los atrasos y avisos dejan de generarse sin error visible. Mitigación: registrar la fecha de la última corrida y alertar si pasan más de 24 horas sin ejecución.
