# Análisis de estilos arquitectónicos para SGPIS

**Insumos:** `S03_A1/SRS_equipo.md` (v2.0: 39 RF, 18 RNF, 16 RD) y `S03_A2/tareas_tecnicas.md` + `S03_A2/sprint1_planning.md` (Sprint 1 en curso).
**Diagrama de dominio que acompaña este análisis:** `diagrama_clases_agente.puml`.

## 0. Lo que ya está decidido y no se discute aquí

El Sprint 1 ya fijó el stack, así que cualquier estilo se evalúa contra él y no en abstracto:

- Backend: Python con FastAPI, pydantic-settings, SQLAlchemy 2.0 y Alembic; sesión de base por solicitud (T-02, T-03).
- Base de datos: PostgreSQL 16 en Docker Compose (T-01). Archivos de evidencia fuera de PostgreSQL, en almacenamiento de objetos (SRS 2.4).
- Sesiones guardadas en servidor, no JWT sin estado (T-10, para cumplir RF-26-AC-5 y AC-6).
- Bitácora de solo append en la misma base, con un usuario de base sin UPDATE ni DELETE (T-04).
- Autorización por rol con una dependencia reutilizable `requiere_rol` (T-12).
- Pruebas con pytest, httpx y reloj simulado; CI en GitHub Actions; `main` protegida (T-05, T-06, T-13).
- Frontend en React, que empieza en las semanas 7 y 8 del curso (HU-23).
- Todavía no hay servidor de despliegue ("No hay servidor donde desplegar", `tareas_tecnicas.md`).

Capacidad real: 3 personas × 8.5 h × 12 semanas = 306 h brutas. Con los descuentos de eventos del Sprint 1 quedan unas 42.75 h netas por sprint de dos semanas, **unas 256 h netas en todo el proyecto**. El esqueleto y la autenticación ya se llevaron 39. Para lo que queda hay 22 RF de prioridad "MVP feb-2027", y el estilo elegido no debe consumir horas en infraestructura que ningún RNF pida.

## 1. RNF que de verdad condicionan la arquitectura

Para cada uno: qué exige, por qué pesa y qué decisión obliga a tomar.

### 1.1 Control de acceso y confidencialidad (los que más pesan)

| RNF | Qué exige | Por qué pesa en la arquitectura | Decisión que obliga |
|---|---|---|---|
| **RNF-01** Aislamiento entre parques | 0 accesos cruzados en ≥ 20 combinaciones usuario/parque no autorizado. | No basta con el rol. Cada consulta del expediente tiene que filtrarse por el alcance del usuario: su parque si es APPI, sus parques asignados en la generación si es consultor (RF-10), los parques de su desarrollador si es gerente corporativo (RF-23), un acceso temporal si es consultor de comité (RF-13-AC-3). Si una sola ruta olvida el filtro, el RNF se rompe. | Una sola política de autorización centralizada con dos niveles, **rol + alcance**, aplicada en un único punto que todas las rutas usan. Es el argumento más fuerte contra repartir la lógica en servicios independientes. |
| **RNF-02** Evidencias de seguridad solo para APPI y consultor asignado | 0 aperturas de análisis de riesgos, plan de contingencia o ubicación de cámaras por Coordinación AMPIP o por el Administrador técnico. | Agrega un tercer eje de autorización: **la clasificación del contenido**. Coordinación sí abre la carta de inscripción (RF-07-AC-2) y no el plan de contingencia (RF-07-AC-3). El Administrador técnico, que opera la infraestructura, tampoco puede abrir archivos desde la aplicación. | Cada archivo necesita una clasificación (administrativa, seguridad o datos personales) que la política consulte. El bucket no puede ser público y el administrador técnico no debe tener un camino en la aplicación hacia el contenido. |
| **RNF-04** Datos personales del estándar 7 | Contenido del estándar 7 solo para APPI y consultor asignado; tratamiento legal pendiente. | Hoy es una regla de acceso. Si el abogado de AMPIP pide cifrado adicional o una retención distinta, puede hacer falta cifrar a nivel de aplicación un subconjunto de archivos. | La clasificación del contenido tiene que poder distinguir "datos personales" desde el principio, aunque hoy se trate igual que "seguridad". |
| **RNF-03** Bitácora de solo append | 100 % de subir, consultar, modificar o descargar evidencia queda registrado; nadie, ni el Administrador técnico, modifica ni borra registros. | Es transversal: lo tocan todos los módulos y todas las operaciones de RF-35. Si la operación y su registro viven en bases o procesos distintos, garantizar el 100 % exige una transacción distribuida o un patrón outbox. Con una sola base, la operación y su registro se escriben en la misma transacción. El intento denegado (RF-35-AC-2) es el caso contrario: la solicitud termina en error y su registro tiene que confirmarse aparte, para que no se pierda con el rollback. | Bitácora en la misma base que el dominio (ya hecho en T-04), escrita en la transacción de la operación, y los "denegado" en una transacción propia. Favorece fuertemente una sola base. |
| **RNF-15** Cifrado y acceso a archivos | TLS ≥ 1.2, cifrado en reposo, ningún archivo con URL pública, acceso solo con URL firmada de ≤ 5 min emitida después de validar el permiso. | Define el flujo de descarga: el navegador nunca recibe el archivo a través de una URL permanente. La API valida la política (RNF-01/02/04), registra en bitácora (RNF-03) y firma una URL corta. | Un adaptador de almacenamiento que firme URLs. Un bucket privado con cifrado en reposo. La API es la única que firma. |

### 1.2 Archivos y rendimiento de carga

| RNF | Qué exige | Por qué pesa | Decisión que obliga |
|---|---|---|---|
| **RNF-07** Confirmación de carga en ≤ 1 s con 30 cargas simultáneas | Mide desde "archivo recibido completo" hasta la confirmación, sin contar la transferencia. | Con archivos de hasta 100 MB (RF-06), 30 cargas concurrentes que atraviesen la API son unos 3 GB en tránsito, procesos ocupados durante la transferencia desde conexiones de parque lentas y presión de memoria. Es el único RNF de rendimiento que sí cambia el diseño. | **Carga directa al almacenamiento de objetos con URL prefirmada** (POST con política de tamaño máximo igual al límite configurado), seguida de una llamada corta de confirmación a la API, que verifica el objeto (tamaño, tipo) y crea el registro. Esa confirmación es exactamente lo que mide RNF-07. |
| **RNF-18** Carga sin bloquear la pantalla, varios archivos y progreso por archivo | El usuario sigue navegando mientras suben cinco archivos de 20 MB. | Es requisito de cliente: lo resuelve una SPA con cargas en paralelo y estado global, y es difícil de lograr con páginas renderizadas en servidor que recargan. Encaja con la carga directa de RNF-07, porque el navegador conoce el progreso de cada PUT o POST. | Frontend SPA (React, ya decidido) que se comunica con una API. |
| **RNF-05** Almacenamiento con región fija en México o EE. UU. | Un solo proveedor con región fija. | Obliga a elegir un proveedor de almacenamiento S3 compatible con región conocida y a no depender de servicios sin región configurable. | Interfaz de almacenamiento con una implementación S3 compatible (MinIO en desarrollo, el proveedor elegido en producción). |
| **RNF-06, RNF-16, RNF-17, RNF-10** Respuesta y escala | Lista de 1,500 evidencias en ≤ 2 s; consultas en ≤ 3 s; vista de cartera de 80 parques en ≤ 5 s; de 41 a 80 parques sin cambios de esquema y sin degradarse más del 20 %; prueba de humo con 200. | Pesan **por lo que permiten descartar**. 80 parques × 1,500 evidencias son 120,000 filas de evidencia, unos 150 usuarios registrados y 30 concurrentes. Un PostgreSQL con índices por parque y expediente lo resuelve sin réplicas, caché distribuida ni partición. Ningún RNF justifica escalar horizontalmente por servicio. El riesgo real es de consulta, no de topología: calcular RF-08 para 80 parques en la vista de cartera con N+1 consultas. | Una instancia de API y una base. Cálculo de cumplimiento con agregaciones SQL (o una tabla de resumen que se recalcula al calificar), índices definidos desde la migración y prueba de carga con datos sintéticos. |

### 1.3 Procesos en segundo plano y tiempo

| RNF | Qué exige | Por qué pesa | Decisión que obliga |
|---|---|---|---|
| **RNF-12** Avisos por correo con 3 reintentos y registro del fallo | Todo aviso sale por correo, con hasta 3 reintentos ante una falla y registro en bitácora si falla definitivamente. | El envío no puede ir dentro de la solicitud HTTP: un proveedor caído haría fallar la operación de negocio (por ejemplo, RF-05-AC-2: registrar la observación y notificar). Hace falta una cola persistente con reintentos. | **Outbox en PostgreSQL**: la operación escribe el aviso en la misma transacción y un proceso trabajador lo envía y reintenta. No hace falta Redis, Celery ni un broker. |
| **RNF-11** Zona horaria America/Mexico_City, corte a las 00:00 | Todas las comparaciones de fechas en hora de México. | Junto con la "revisión diaria de plazos" de RF-09-AC-2 y RF-30-AC-2 (y después RF-19, RF-20, RF-38 y RF-39) obliga a tener **un proceso programado** con un reloj inyectable. RF-19-AC-5 exige además idempotencia: ejecutar la revisión dos veces el mismo día no duplica avisos. | Un proceso trabajador del mismo código con un reloj inyectable (ya usado en las pruebas de T-09 y T-10) e idempotencia por restricción única (por ejemplo, distintivo + plazo). La revisión procesa "todo lo vencido hasta hoy y aún no procesado", para no perder un día si el proceso estuvo caído a medianoche. |

### 1.4 Operación

| RNF | Qué exige | Por qué pesa | Decisión que obliga |
|---|---|---|---|
| **RNF-08** Disponibilidad ≥ 99 % mensual y 0 mantenimientos en fechas críticas | Monitoreo cada 5 minutos con un health check (ya existe, T-02). | 99 % mensual permite unas 7.2 h de caída al mes: lo cumple una sola instancia bien operada y no exige alta disponibilidad multi-nodo. El calendario de fechas críticas obliga a que desplegar sea un acto simple y controlado, no a tener redundancia. | Un solo artefacto desplegable (una imagen para API y trabajador), despliegues manuales o por etiqueta, y un calendario de congelamiento. Cuantas más piezas desplegables haya, más difícil es cumplir "0 ventanas". |
| **RNF-13 / RNF-14** Respaldos diarios con 30 días de retención; retención de evidencias de 6 años; bitácora y dictámenes nunca se borran | Respaldo de base y de archivos; depuración controlada. | Base y archivos se respaldan por separado y tienen que ser consistentes entre sí: un registro de evidencia sin objeto, o al revés, es un expediente roto. La depuración de RNF-14 es otra tarea programada. | Base gestionada con respaldos automáticos, versionado o réplica del bucket, y depuración como una tarea más del trabajador. |

### 1.5 Restricciones que actúan como RNF

- **SRS 2.4 y RD-12:** Python + PostgreSQL, tres personas, 12 semanas, sin licencias por usuario ni auditorías externas pagadas. Todo lo que exija operar varias bases, un broker o un orquestador de contenedores sale del presupuesto de horas y de dinero.
- **RF-32 (fases como datos), RF-06, RF-19 y RD-08 (valores parametrizables), RF-01-AC-5 (catálogo versionado):** la variabilidad del dominio se resuelve con datos y configuración, no con despliegues ni con servicios separados.

### 1.6 RNF que no cambian el estilo

- **RNF-09** (Chrome y Safari móviles): decisión de frontend responsivo, la misma con cualquier estilo de backend.
- **RNF-11**, aunque obliga a tener un reloj inyectable, se resuelve dentro de cualquier estilo.
- **RNF-13** es en gran parte responsabilidad del proveedor de base y almacenamiento.

**Conclusión de la sección:** los RNF de seguridad (01, 02, 03, 04, 15) piden **centralizar** la autorización y la bitácora en una sola base transaccional. Los de rendimiento (06, 10, 16, 17) **no piden distribuir nada**. Los únicos que piden algo fuera del ciclo solicitud-respuesta son RNF-07 (carga directa al almacenamiento) y RNF-12 + RNF-11 (un proceso trabajador con cola persistente y tareas diarias).

## 2. Estilos alternativos

Escala usada en los trade-offs: lo que cada estilo **ofrece** frente a lo que SGPIS **necesita** según la sección 1.

### E1. Monolito en capas (horizontal)

**Aplicado a SGPIS.** Una aplicación FastAPI organizada por capa técnica: `routers/` (todos los endpoints), `services/` (todas las reglas: transiciones de RF-27, candados de RF-12, RF-14, RF-15 y RF-17, cálculo de RF-08), `repositories/` y `models/` (todas las tablas). Una base PostgreSQL. Es, en la práctica, lo que hoy produce el esqueleto del Sprint 1 si nadie decide otra cosa.

| Criterio | Evaluación |
|---|---|
| Escalabilidad | Suficiente. Una instancia atiende 30 concurrentes y 80 parques; si hiciera falta, se replica la instancia completa detrás de un balanceador, porque las sesiones viven en la base. |
| Mantenibilidad | Buena al principio y se degrada con el tamaño. Con 39 RF, `services/` acaba con decenas de archivos donde las reglas de dictamen llaman directamente a los repositorios de evidencias, catálogo y parques. Nada impide que cualquier capa importe cualquier modelo, y la política de RNF-01 tiende a repetirse en cada servicio. |
| Complejidad de implementación | La más baja. Patrón conocido, documentado en FastAPI, sin decisiones de fronteras. |
| Adecuación al equipo | Alta para empezar. Media a partir de la semana 8: tres personas trabajando en paralelo en `services/` y `models/` chocan en los mismos archivos y en las mismas migraciones de Alembic. |

### E2. Monolito modular (vertical por dominio, con capas dentro de cada módulo)

**Aplicado a SGPIS.** Una sola aplicación FastAPI y una sola base, divididas en módulos de dominio con frontera explícita. Cada módulo tiene sus propias capas (router, servicio, repositorio, modelos) y expone una interfaz pública mínima (`servicio.py`). Los demás módulos solo llaman esa interfaz y nunca importan sus modelos. Módulos propuestos, con los RF que cubren:

| Módulo | RF / RNF |
|---|---|
| `identidad_acceso` | RF-03, RF-26, RF-29 (usuarios), RF-34; política rol + alcance + clasificación (RNF-01, RNF-02, RNF-04) |
| `catalogo` | RF-01, RF-24, RF-25 |
| `programa` (generaciones, parques, tipo de PI, fases, fechas, historial) | RF-02, RF-10, RF-11, RF-28, RF-29 (parques), RF-30, RF-31, RF-32 |
| `expediente` (criterios del expediente, autoevaluación, evidencias, calificación, plan de trabajo, análisis de riesgos, recomendaciones, cálculo) | RF-04 a RF-09, RF-16, RF-17, RF-27, RF-36 |
| `dictamen` (Opiniones, Evaluación de Desempeño, comité, dictamen) | RF-12 a RF-15, RF-33 |
| `reportes` (solo lectura) | RF-21, RF-23 |
| `avisos` (outbox de correo y revisión diaria) | RNF-12, RNF-11, RF-09-AC-2, RF-30-AC-2 |
| `bitacora` | RF-35, RNF-03 (ya existe por T-04) |
| `archivos` (puerto de almacenamiento y URL firmadas) | RF-06, RNF-05, RNF-07, RNF-15 |
| Posteriores, cada uno como módulo nuevo | RF-18 (auditorías), RF-19, RF-20 y RF-39 (avisos), RF-22, RF-37 (visitas), RF-38 (distintivo) |

El mismo código se despliega como dos procesos: la API y un trabajador (`python -m sgpis.worker`) que ejecuta la revisión diaria y vacía el outbox de correo.

| Criterio | Evaluación |
|---|---|
| Escalabilidad | La misma que E1, que ya basta. Además, si algún día un módulo lo justificara (por ejemplo, `avisos` o `archivos`), su frontera ya existe y se puede extraer. |
| Mantenibilidad | La mejor de las opciones viables. Cada regla vive en un solo módulo: las máquinas de estado de RF-05 y RF-27 en `expediente`, los candados de RD-09 en `dictamen`. Los RF posteriores (RF-18, RF-37, RF-38) entran como módulos nuevos sin tocar los existentes. La frontera se verifica en CI con `import-linter`. |
| Complejidad de implementación | Baja a media. Solo agrega una disciplina: decidir la interfaz pública de cada módulo y no cruzar modelos. No agrega infraestructura: una base, una transacción por solicitud (T-03), la bitácora en la misma transacción (RNF-03). |
| Adecuación al equipo | Alta. Tres personas se reparten módulos con poca colisión de archivos. Lo ya construido en el Sprint 1 se convierte en `identidad_acceso` y `bitacora` sin reescribir nada. |

### E3. Microservicios

**Aplicado a SGPIS.** Servicios desplegados por separado, cada uno con su base: Identidad, Catálogo, Programa, Expediente/Evidencias, Dictamen, Avisos y Bitácora. Una API gateway valida sesiones. Un broker (RabbitMQ o Kafka) propaga eventos como `EvidenciaEnviada`, que Expediente consume para pasar el criterio a "en revisión", o `DictamenFirmado`, que inicia la vigencia del distintivo.

| Criterio | Evaluación |
|---|---|
| Escalabilidad | Máxima en teoría, y ningún RNF la pide. Escalar Evidencias por separado no sirve de nada con 30 usuarios concurrentes. |
| Mantenibilidad | Mala para este dominio. Las reglas cruzan datos de varios servicios: "otorgar" (RD-09) necesita el estado de todos los criterios (Expediente), la Opinión final (Dictamen) y el 100 % de O (cálculo sobre Catálogo + Expediente); "cumplido" en los estándares 2, 3 y 7 necesita el análisis de riesgos vigente (RF-17). Cada regla se vuelve una llamada remota o una réplica de datos con consistencia eventual. Además, RNF-01 tendría que aplicarse igual en siete servicios. |
| Complejidad de implementación | Muy alta. La bitácora al 100 % (RNF-03) exige outbox en cada servicio. Las pruebas de RNF-01 se vuelven pruebas de integración entre servicios. El Docker Compose de desarrollo pasa de 1 a unas 9 piezas, y el CI de T-06 tendría que levantarlas todas. |
| Adecuación al equipo | Muy baja. Con unas 256 h netas, la infraestructura (gateway, broker, siete bases, siete pipelines, observabilidad distribuida) se comería una fracción grande del proyecto antes de entregar un RF. Cumplir RNF-08 con siete despliegues y 0 ventanas en fechas críticas es más difícil, no más fácil. Contradice lo ya construido (una base, sesión por solicitud, bitácora con permisos de base). |

### E4. Cliente-servidor con MVC renderizado en servidor

**Aplicado a SGPIS.** Un servidor (Django con su patrón MVT, o FastAPI con Jinja2) que renderiza HTML: los controladores reciben formularios, los modelos son el ORM y las vistas son plantillas. Sin SPA y sin API JSON como contrato principal. Nota: cliente-servidor, como topología, también describe la opción elegida (SPA + API). Lo que se evalúa aquí es la variante MVC renderizada en servidor frente a SPA + API.

| Criterio | Evaluación |
|---|---|
| Escalabilidad | Suficiente, igual que E1. |
| Mantenibilidad | Buena si el producto fuera solo formularios y tablas, que es casi el caso (2.4). Pero mezcla la presentación con el contrato: los criterios de aceptación del SRS están escritos contra endpoints y códigos (403, 422, 401; por ejemplo RF-01-AC-2, RF-04-AC-2, RF-27-AC-5), y verificarlos contra HTML es más frágil. |
| Complejidad de implementación | Baja para pantallas CRUD. Alta justo donde SGPIS es exigente: RNF-18 (varios archivos con progreso individual mientras el usuario navega) y RNF-07 (carga directa al almacenamiento) requieren JavaScript de todos modos. Con HTMX se suaviza, pero se tendría un híbrido. Si se elige Django, es un cambio de framework a mitad del proyecto: se reescriben T-02, T-03, T-08 a T-12. |
| Adecuación al equipo | Media. Ahorra el frontend separado de las semanas 7 y 8, pero tira trabajo del Sprint 1 (o, con FastAPI + Jinja, sacrifica el contrato OpenAPI que la definición de terminado ya usa en `/docs`) y contradice HU-23. |

### E5. Event-driven / serverless

**Aplicado a SGPIS.** Funciones (AWS Lambda o Cloud Functions) por grupo de endpoints detrás de un API Gateway; carga directa a S3 con un evento `ObjectCreated` que dispara una función para validar el archivo y crear la evidencia; EventBridge programa la revisión diaria; SQS con cola de mensajes fallidos para los correos y sus reintentos; PostgreSQL gestionado (RDS) con un proxy de conexiones.

| Criterio | Evaluación |
|---|---|
| Escalabilidad | Automática y con costo casi cero en reposo. Encaja de forma natural con RNF-07 (evento de objeto creado), RNF-12 (cola con reintentos) y la revisión diaria (programador gestionado). |
| Mantenibilidad | Media a baja. La lógica queda repartida entre funciones, reglas de eventos y permisos IAM; la política de RNF-01 y RNF-02 tiene que vivir en una biblioteca compartida que se despliega con cada función. Las sesiones en servidor (T-10) y la ventana de inactividad deslizante funcionan, pero cada invocación consulta la base. |
| Complejidad de implementación | Alta. Las pruebas locales dejan de ser `docker compose up` + `pytest` (la definición de terminado del Sprint 1) y pasan a necesitar emuladores. Aparecen arranques en frío frente a RNF-16, la gestión de conexiones de Lambda contra PostgreSQL (el proxy tiene costo) y la consistencia entre "objeto creado" y "registro de evidencia y bitácora" (RNF-03) con eventos que pueden llegar duplicados. |
| Adecuación al equipo | Baja. Ninguno de los tres ha trabajado con este stack (el planning ya reconoce que el esqueleto es nuevo para todos). Ata el proyecto a un proveedor antes de saber cuál paga AMPIP (RD-12, RNF-05). Rehace la infraestructura del Sprint 1. |

### 2.1 Tabla comparativa

| Criterio (RNF que lo motiva) | E1 Capas | E2 Modular | E3 Microservicios | E4 MVC en servidor | E5 Event-driven/serverless |
|---|---|---|---|---|---|
| Escalabilidad suficiente para 80 parques y 30 concurrentes (RNF-06, 10, 16, 17) | Sí | Sí | Sí, sobrada | Sí | Sí, sobrada |
| Autorización centralizada rol + alcance + clasificación (RNF-01, 02, 04) | Fácil, tiende a repetirse | Fácil, un solo módulo | Difícil, en N servicios | Fácil | Media, biblioteca compartida |
| Bitácora 100 % en la misma transacción (RNF-03) | Sí | Sí | No, requiere outbox por servicio | Sí | No, eventos duplicables |
| Carga directa y URL firmadas (RNF-07, 15, 18) | Sí, con adaptador | Sí, módulo `archivos` | Sí | Requiere JS aparte | Nativo |
| Trabajos diarios y correo con reintentos (RNF-11, 12) | Trabajador + outbox | Trabajador + outbox | Servicio + broker | Trabajador + outbox | Nativo (programador + cola) |
| Operación y 0 ventanas en fechas críticas (RNF-08) | 1 artefacto | 1 artefacto, 2 procesos | ~9 piezas | 1 artefacto | Muchas piezas gestionadas |
| Mantenibilidad con 39 RF y RF posteriores | Media, se degrada | Alta | Baja, reglas cruzadas | Media | Media-baja |
| Complejidad de implementación | Baja | Baja-media | Muy alta | Baja (CRUD), alta (cargas) | Alta |
| Encaje con el Sprint 1 ya construido | Total | Total | Rehace todo | Parcial o reescritura | Rehace infraestructura |
| Trabajo en paralelo de 3 personas | Medio, colisiones | Alto | Alto en teoría, inviable en horas | Medio | Medio |
| Costo de operación (RD-12) | Bajo | Bajo | Alto | Bajo | Muy bajo en reposo, con riesgo de dependencia del proveedor |
| Adecuación global al equipo (256 h netas) | Alta | **Alta** | Muy baja | Media | Baja |

### 2.2 Recomendación

**Monolito modular (E2), en topología cliente-servidor SPA + API REST, con un proceso trabajador del mismo código y almacenamiento de objetos externo.**

Por qué:

1. **Los RNF que más pesan piden centralizar, no distribuir.** RNF-01, 02 y 04 se cumplen con una sola política de autorización en `identidad_acceso`; RNF-03 se cumple escribiendo la bitácora en la misma transacción. Las dos cosas son triviales con una base y difíciles en E3 y E5.
2. **Los RNF de rendimiento no justifican ninguna distribución.** 120,000 evidencias y 30 concurrentes caben en una instancia; el riesgo de RNF-17 se resuelve con SQL, no con topología.
3. **Las dos necesidades fuera de la solicitud HTTP se cubren sin infraestructura nueva:** RNF-07 y RNF-15 con URL prefirmadas directas al almacenamiento; RNF-12 y RNF-11 con un outbox en PostgreSQL y un trabajador. Sin Redis, broker ni orquestador.
4. **Frente a E1 gana en lo que importa a mitad del proyecto:** con 39 RF, máquinas de estado (RF-05, RF-27, RF-32, RF-14) y candados que cruzan dominios (RD-09, RF-17), las fronteras de módulo evitan que todo dependa de todo y permiten que tres personas trabajen sin pisarse. El costo extra frente a E1 es disciplina, no horas de infraestructura.
5. **Conserva todo el Sprint 1:** T-03 (sesión por solicitud) es la unidad de trabajo compartida, T-04 es el módulo `bitacora` y T-12 se extiende a `requiere_acceso_parque`.

Decisiones concretas que se derivan:

- **Autorización en dos pasos** dentro de `identidad_acceso`: `requiere_rol` (ya existe) + `requiere_alcance(parque | expediente)` + verificación de clasificación del archivo antes de firmar una URL. La prueba de RNF-01 (20 combinaciones) entra al CI en cuanto exista el primer endpoint de expediente.
- **Fronteras verificadas en CI** con `import-linter`: ningún módulo importa `modelos` o `repositorio` de otro.
- **Archivos:** `POST /evidencias/carga` valida extensión, tamaño declarado y permiso, y devuelve un POST prefirmado con `content-length-range` ≤ límite configurado (RF-06); el navegador sube directo; `POST /evidencias/confirmacion` verifica el objeto con HEAD y crea la evidencia, el cambio de estado del criterio (RF-27-AC-4) y la bitácora en una sola transacción. La descarga emite una URL de 5 minutos y deja registro en bitácora. En desarrollo, MinIO en el mismo Docker Compose.
- **Trabajador:** misma imagen, comando distinto. Revisión diaria a las 00:05 hora de México. Procesa "todo lo vencido no procesado". Idempotencia por restricción única. Outbox de correo con 3 reintentos y registro en bitácora del fallo definitivo.
- **Despliegue objetivo:** contenedor de API + contenedor de trabajador + PostgreSQL gestionado + bucket privado cifrado en región fija (RNF-05), detrás de TLS. Sin balanceador mientras RNF-08 lo permita.

Riesgos del estilo recomendado y su control:

| Riesgo | Control |
|---|---|
| Las fronteras se erosionan con la presión del calendario | `import-linter` en CI; revisión de PR con la regla "solo se llama `servicio.py` de otro módulo". |
| Punto único de falla (una instancia) | RNF-08 tolera unas 7.2 h al mes; health check externo; despliegues fuera de fechas críticas. |
| El trabajador se cae y no corre la revisión diaria | Revisión de recuperación: "todo lo vencido no procesado" en lugar de "lo de hoy"; alerta si la última ejecución tiene más de 26 h. |
| La confirmación de carga nunca llega (el usuario cierra la pestaña) | Objetos sin registro que se depuran tras 24 h con una regla de ciclo de vida del bucket; nunca se crean registros sin objeto. |

## 3. Preguntas y riesgos que no se resuelven con el SRS

1. **¿Dónde se despliega y quién paga?** El Sprint 1 reconoce que no hay servidor. RNF-05 (región), RNF-08 (99 % con monitoreo externo), RNF-13 (respaldos) y RD-12 (sin costos de licencia) dependen de un proveedor y un presupuesto que el SRS no fija. Sin esa respuesta, RNF-08 y RNF-13 no se pueden verificar dentro de las 12 semanas.
2. **¿Qué proveedor de almacenamiento de objetos y cuál de correo?** RNF-05 restringe la región; RNF-12 exige reintentos, pero el proveedor de correo quedó diferido (T-11 escribe en consola). La elección afecta el adaptador de URL firmadas y los costos.
3. **¿Cuál es la regla exacta para clasificar un archivo como "de seguridad" o "administrativo"?** RNF-02 da tres ejemplos (análisis de riesgos, plan de contingencia, ubicación de cámaras) y RF-07-AC-2 uno administrativo (carta de inscripción). No dice si la clasificación es por criterio, por estándar, por tipo de documento o la decide la APPI al subir. Es la base de la política de RNF-02 y se tiene que confirmar. El diagrama asume que se hereda del criterio y se guarda en el archivo.
4. **Tratamiento legal del estándar 7 (RNF-04).** Si el abogado pide cifrado a nivel de aplicación o una retención distinta de RNF-14, cambia el adaptador de archivos y la depuración.
5. **"Descargar" en la bitácora con URL firmada (RNF-03 + RNF-15).** La aplicación puede registrar la emisión de la URL, no la descarga efectiva, que ocurre en el almacenamiento. ¿Basta con registrar la emisión, o hay que activar y conciliar los registros de acceso del bucket?
6. **Validación del contenido de los archivos.** El SRS valida extensión y tamaño (RF-06), pero no pide revisar malware ni verificar que el contenido coincida con la extensión. Tampoco dice cómo verá Coordinación AMPIP o el consultor una foto HEIC desde un navegador de escritorio que no la muestra (RF-07-AC-2: "el sistema abre el archivo"). ¿Se convierte a JPG al recibirla?
7. **Cifras de rendimiento y disponibilidad sin validar.** RNF-06, 07, 08, 10, 16 y 17 son propuestas del equipo; la concurrencia de 30 es un supuesto. Si AMPIP las cambia mucho (por ejemplo, 99.9 %), la recomendación de una sola instancia se tiene que revisar.
8. **El "ciclo" de renovación no está modelado.** RF-16 y RF-16-AC-4 hablan de "mismo ciclo" y de un ciclo de renovación en 2030, y RD-06 de evaluar la renovación con el catálogo vigente, pero RF-38 está fuera del entregable y no hay una entidad "ciclo". El diagrama usa el expediente (parque × generación) como ciclo; falta confirmar si una renovación es otra "generación" o un ciclo distinto.
9. **Fechas críticas de RNF-08.** ¿Quién las declara y dónde? Si el sistema debe impedir desplegar en esas fechas, son un dato del dominio (calendario de la generación), no solo un acuerdo de operación.
10. **Comité.** No está confirmado si el consultor de comité puede capturar el borrador del dictamen (RF-14, pendiente explícito), ni si una sesión de comité puede repetirse para el mismo parque y generación después de un "no otorgar".
11. **Desarrollador y gerente corporativo.** RF-02 captura "desarrollador" como dato y RF-23 da una vista por desarrollador, pero el SRS no define el desarrollador como entidad ni qué cifras ve el gerente (¿los tres porcentajes de RF-08?). El diagrama lo modela como entidad.
12. **Contenido de la autoevaluación (RF-04).** El SRS dice qué criterios se muestran, pero no qué registra la APPI por criterio (¿sí/no, porcentaje, comentario?) ni cómo se relaciona con el estado de calificación. El diagrama asume una autodeclaración sí/no con comentario.
13. **Parque histórico y bajas.** No está definido si un parque histórico (RF-31) puede reactivarse en una generación futura ni si un parque dado de baja (RF-29) sigue en el historial y los reportes. Esto decide si "histórico" es un subtipo fijo o un estado.
14. **Riesgo de alcance frente a capacidad, independiente del estilo.** Quedan 22 RF "MVP feb-2027" para unas 217 h netas después del Sprint 1, más el frontend completo desde la semana 7. Ningún estilo lo resuelve; lo que sí puede hacer el estilo es no sumar horas de infraestructura, y por eso se descartan E3 y E5.
15. **Nota documental:** el SRS identifica al equipo como "Gpo 10" y los documentos del Sprint 1 como "Equipo 19". No afecta la arquitectura, pero conviene unificarlo antes de la entrega.
