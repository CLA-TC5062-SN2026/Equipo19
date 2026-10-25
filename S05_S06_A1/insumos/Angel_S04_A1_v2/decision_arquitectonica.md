# Arquitectura de SGPIS

**Proyecto:** SGPIS, Sistema de Gestión del Programa Parque Industrial Seguro (AMPIP). Equipo 19, TC5062
**Actividad:** S04-A1, Diseño de Arquitectura de Software (individual)
**Insumos:** `S03_A1/SRS_equipo.md` v2.0 (39 RF, 18 RNF, 16 RD), `S03_A2/tareas_tecnicas.md` y `S03_A2/sprint1_planning.md` (el Sprint 1 ya está en curso)
**Propuesta del agente, sin editar:** `evidencia_agente/analisis_estilos_agente.md` y `evidencia_agente/diagrama_clases_agente.puml` (con su imagen)

| Archivo | Contenido |
|---|---|
| `decision_arquitectonica.md` | Este documento: ADR-001 (estilo), ADR-002 y ADR-003 (decisiones derivadas), índice de diagramas y revisión crítica de la propuesta del agente |
| `diagrama_componentes.puml` | C4 nivel 2 (contenedores) y C4 nivel 3 (componentes del backend) |
| `diagrama_despliegue.puml` | Despliegue UML: piloto en la nube, CI y ambiente de desarrollo |
| `diagrama_clases.puml` | Clases del dominio y enumeraciones |
| `imagenes/` | Las cinco imágenes exportadas con PlantUML 1.2024.7 y Graphviz |

---

# ADR-001: Selección del estilo arquitectónico

**Fecha:** 2026-10-11
**Estado:** Aceptado
**Decide:** Ángel Kociankowski (A01379225). El análisis de alternativas lo preparó un agente de IA y la decisión es mía; en la sección 5 explico en qué difiere de lo que propuso.

## Contexto

SGPIS sustituye el Excel, el correo y las carpetas compartidas con que AMPIP lleva el Programa Parque Industrial Seguro. En el piloto de febrero de 2027 son unos 41 parques, que crecen a 70-80, y alrededor de 150 usuarios en seis roles. El sistema guarda información sensible de los parques: análisis de riesgos, planes de contingencia, ubicación de cámaras y datos personales de guardias.

No todos los RNF pesan igual al elegir el estilo. Los separé en tres grupos:

| Grupo | RNF | Qué le piden a la arquitectura |
|---|---|---|
| **Piden centralizar** | RNF-01 (0 accesos cruzados entre parques), RNF-02 y RNF-04 (contenido de seguridad y datos personales solo para APPI y consultor asignado), RNF-03 (bitácora del 100 % de las operaciones, de solo append), RNF-15 (sin URL públicas; URL firmadas de 5 min después de validar el permiso) | Una sola política de autorización por **rol + alcance de parque + clasificación del archivo**, aplicada en un punto que usen todas las rutas. La bitácora tiene que escribirse en la misma transacción que la operación, o el 100 % no se puede garantizar. Las dos cosas son triviales con una base y difíciles si los datos se reparten. |
| **Piden trabajo fuera de la solicitud HTTP** | RNF-12 (correo con 3 reintentos), RNF-11 junto con RF-09-AC-2 y RF-30-AC-2 (revisión diaria a las 00:00 de Ciudad de México), RNF-07 y RNF-18 (30 cargas simultáneas de archivos de hasta 100 MB) | Un proceso programado con una cola persistente, y una decisión explícita sobre cómo viajan los archivos grandes (ADR-002). |
| **Sirven para descartar** | RNF-06, RNF-10, RNF-16 y RNF-17 (80 parques × 1,500 evidencias, unas 120,000 filas; 30 usuarios concurrentes; consultas en 3 s o menos) | Ningún RNF de rendimiento justifica distribuir. Una instancia de PostgreSQL con índices por parque basta. El riesgo es de consultas (N+1 al calcular RF-08 para 80 parques), no de topología. |

Hay además tres restricciones duras:

- **Capacidad.** Somos 3 personas con 8.5 h por semana durante 12 semanas: unas 256 h netas en todo el proyecto, de las que el Sprint 1 ya usa 39, y quedan 22 RF de MVP. La actividad pide además evaluar el estilo "para un desarrollador". Con una sola persona, cualquier hora de infraestructura que no pida un RNF es una hora que no se dedica a un RF.
- **Lo ya construido.** El Sprint 1 fijó FastAPI, SQLAlchemy 2.0, Alembic, PostgreSQL 16, sesiones en servidor, la bitácora con un usuario de base sin UPDATE ni DELETE, `requiere_rol` y CI en GitHub Actions. Un estilo que obligue a rehacer eso tiene un costo hundido real.
- **Costo.** AMPIP es una asociación civil (RD-12), y el proveedor de despliegue y su presupuesto todavía no están definidos.

## Decisión

**Monolito modular en capas, con topología cliente-servidor: una SPA en React consume una API REST (FastAPI), más un proceso programado del mismo código. Hay una sola base PostgreSQL y un almacenamiento de objetos externo para los archivos.**

Lo concreto:

1. **Módulos de dominio con frontera explícita.** Son cinco: identidad y acceso, programa (catálogo, generaciones, parques, fases), expediente, dictaminación, y reportes y bitácora. Cada módulo tiene sus capas (router → servicio → repositorio) y expone solo su servicio. Ningún módulo importa modelos ni repositorios de otro, y la regla se revisa en CI con `import-linter`, una idea que tomo del agente. El detalle está en el diagrama C4 de componentes.
2. **Componentes transversales con un solo dueño.** Seguridad (`sesion_actual`, `requiere_rol` y el alcance de parque), registro de bitácora, validador de archivos, puerto de almacenamiento, cola de correos y reloj inyectable. Las reglas que cruzan módulos (RD-09, RF-17) se resuelven en el servicio dueño de la decisión, llamando al servicio del otro módulo. El cálculo de cumplimiento (RD-02) es un componente de funciones puras sin acceso a base que usan tres módulos.
3. **El mismo artefacto corre como dos procesos.** La API (uvicorn) y el proceso programado (APScheduler) comparten imagen. El proceso programado hace la revisión diaria de plazos y vacía la cola de correos.
4. **La cola de correos es una tabla de PostgreSQL (patrón outbox).** Un servicio que necesita avisar escribe el aviso en la misma transacción que el cambio. Si el proveedor de correo se cae, la operación de negocio no falla y el aviso se reintenta 3 veces (RNF-12). No hay broker, ni Redis, ni Celery.
5. **El contrato entre el frontend y el backend es `openapi.yaml`** (S04-A2), con el prefijo `/api/v1`.

## Alternativas consideradas

El agente comparó cinco estilos. Los resumo con los trade-offs que decidieron, aplicados a SGPIS y no en abstracto. La última columna evalúa para un desarrollador y para el equipo de tres.

| Alternativa | Escalabilidad | Mantenibilidad | Complejidad de implementación | Adecuación (un desarrollador / equipo de 3) |
|---|---|---|---|---|
| **A. Monolito en capas horizontales** (`routers/`, `services/`, `repositories/` para todo el sistema) | Suficiente: una instancia atiende 30 concurrentes y se puede replicar completa porque las sesiones viven en la base. | Buena al inicio y se degrada. Con 39 RF y cuatro máquinas de estado (RF-05, RF-27, RF-32, RF-14), `services/` acaba con reglas de dictamen que leen directo los repositorios de evidencias y catálogo. Nada impide que todo dependa de todo. | La más baja: es lo que produce el esqueleto del Sprint 1 si nadie decide otra cosa. | Alta para una persona. Media para tres desde la semana 8: chocan en los mismos archivos y en las mismas migraciones de Alembic. |
| **B. Monolito modular** (la elegida) | La misma que A, que ya alcanza. Si un módulo lo justificara, su frontera ya existe para extraerlo. | La mejor de las viables: cada regla vive en un módulo, y los RF Posteriores (RF-18, RF-37, RF-38) entran como módulos nuevos sin tocar los existentes. | Baja-media. Agrega disciplina (interfaces de módulo, `import-linter`), no infraestructura. | Alta en los dos casos. Para una persona cuesta casi lo mismo que A. Para tres permite repartir módulos con poca colisión. El Sprint 1 se reutiliza completo. |
| **C. Microservicios** (identidad, catálogo, programa, expediente, dictamen, avisos y bitácora, con gateway y broker) | Máxima, y ningún RNF la pide: escalar evidencias por separado no sirve con 30 usuarios. | Mala para este dominio. "Otorgar" (RD-09) necesita el estado de todos los criterios, la Opinión final y el 100 % de obligatorios, que estarían en tres servicios. RF-17 cruza análisis de riesgos y calificación. Cada regla sería una llamada remota o una réplica con consistencia eventual. | Muy alta. RNF-03 exige un outbox por servicio, RNF-01 se aplica igual en siete lugares y Docker Compose pasa de 3 a unas 9 piezas. | Muy baja. La infraestructura se comería buena parte de las 256 h antes de entregar un RF. Con siete despliegues es más difícil cumplir "0 ventanas en fechas críticas" de RNF-08. |
| **D. Cliente-servidor con MVC renderizado en el servidor** (Django o FastAPI + Jinja) | Suficiente, igual que A. | Buena para formularios y tablas, pero mezcla la presentación con el contrato, y los criterios del SRS están escritos contra códigos HTTP (403, 422, 401). | Baja en CRUD y alta justo donde SGPIS exige: RNF-18 (varios archivos con progreso mientras se navega) necesita JavaScript de todos modos. Con Django se reescriben las tareas T-02 a T-12. | Media. Ahorra el frontend separado, pero tira trabajo del Sprint 1 y contradice HU-23. |
| **E. Event-driven / serverless** (funciones, API Gateway, eventos del bucket, colas gestionadas) | Automática y casi sin costo en reposo. Encaja natural con RNF-07 y RNF-12. | Media-baja: la lógica se reparte entre funciones, reglas de eventos y permisos del proveedor, y RNF-01 vive en una biblioteca compartida. | Alta. Las pruebas locales dejan de ser `docker compose up` + `pytest` (la definición de terminado), aparecen los arranques en frío y los eventos duplicados contra RNF-03. | Baja. Nadie del equipo conoce el stack y ata el proyecto a un proveedor antes de saber quién paga (RD-12, RNF-05). |

**Por qué B y no A, si A es más simple.** Las dos tienen la misma infraestructura; la diferencia está en las fronteras. SGPIS tiene reglas que cruzan dominios: el dictamen depende del expediente, y la calificación depende del análisis de riesgos. Sin fronteras, esas dependencias se vuelven una red donde cambiar una tabla rompe tres servicios. El costo extra de B frente a A son unas horas de definir interfaces al inicio, y lo recupera la primera vez que dos personas trabajan en paralelo.

## Consecuencias

**Positivas**

- RNF-01, RNF-02 y RNF-04 se cumplen con una sola política en el componente de seguridad. La prueba de las 20 combinaciones usuario/parque de RNF-01 cubre todas las rutas de una vez.
- RNF-03 se cumple escribiendo la bitácora en la misma transacción que la operación. Los intentos denegados se confirman en una transacción aparte para que no se pierdan con el rollback del 403.
- Un solo artefacto desplegable. Con solo dos procesos y un comando de despliegue, es realista no desplegar durante las fechas críticas de RNF-08.
- Todo el Sprint 1 se conserva: T-04 es el componente de bitácora, T-12 la base del componente de seguridad y T-03 la unidad de trabajo por solicitud.
- El diseño es comprobable con lo que ya tenemos: el reloj inyectable y el puerto de almacenamiento con implementación en memoria permiten probar plazos, bloqueos y archivos sin `sleep` ni servicios externos.

**Negativas y cómo se controlan**

| Consecuencia | Control |
|---|---|
| Un solo servidor es un punto único de falla. | RNF-08 permite unas 7.2 h de caída al mes. Hay monitoreo externo de `/health` cada 5 minutos. La API no guarda estado en memoria, así que agregar una segunda instancia detrás del proxy es un cambio de configuración. |
| Las fronteras de módulo se erosionan con la presión del calendario. | `import-linter` en CI, y en la revisión de PR la regla "de otro módulo solo se llama su servicio". |
| Si el proceso programado se cae a medianoche, no corre la revisión diaria. | La revisión procesa "todo lo vencido que no se ha procesado" en vez de "lo de hoy", y es idempotente por restricción única. Hay alerta si la última ejecución tiene más de 26 h. |
| Escalar un módulo por separado no es posible sin extraerlo. | Ningún RNF lo pide. Si el piloto lo pidiera, el módulo ya tiene frontera e interfaz. |
| El proveedor cloud sigue abierto. | El diagrama de despliegue describe lo que se necesita (VM con Docker, PostgreSQL gestionado y bucket S3 en región de México o EE. UU.), no una marca. La elección se registra como ADR-004 antes del piloto, cuando AMPIP confirme el presupuesto. |

**Cuándo revisar esta decisión.** Si AMPIP sube la disponibilidad pedida a 99.9 % o más, si el número de parques pasa de 200 (la cota de la prueba de humo de RNF-10), o si un módulo concentra más del 50 % de la carga medida en la prueba de RNF-16.

---

# ADR-002: Los archivos de evidencia suben a través de la API

**Fecha:** 2026-10-11 · **Estado:** Aceptado · **Difiere de la propuesta del agente.**

**Contexto.** RNF-07 pide confirmar la recepción de un archivo en 1 s o menos con 30 cargas simultáneas, y RF-06 permite archivos de hasta 100 MB. El agente propuso que el navegador suba directo al bucket con una URL prefirmada y que después llame a la API para confirmar: el archivo nunca pasaría por el backend.

**Decisión.** En v1 el archivo sube a la API en `multipart/form-data` (`POST /parques/{parque_id}/evidencias` de `openapi.yaml`). FastAPI lo recibe en un archivo temporal en disco, no en memoria. El servicio valida tamaño, formato y que no sea video (RF-06) contra el contenido real, sube al bucket y crea los registros y la bitácora en una transacción.

**Por qué no la carga directa ahora.**

1. **RF-06 se valida sobre el archivo, no sobre lo que declara el cliente.** Con carga directa, la API se entera del archivo después de que ya está en el bucket. Para rechazar un `.mp4` renombrado a `.jpg` tendría que descargarlo de nuevo y revisarlo, y además limpiar los objetos huérfanos que dejan las confirmaciones que nunca llegan.
2. **RF-05-AC-8 (cuatro fotos, una rechazada, tres creadas) es una sola respuesta** con `creadas` y `rechazadas`. Con carga directa son 1 + 4 + 1 llamadas, y el estado parcial vive en el navegador del celular de la APPI, que es justo donde la señal es mala (RNF-09).
3. **Las pruebas siguen siendo `pytest` contra la API.** Con carga directa, cada prueba de RF-05 y RF-06 necesita el bucket (MinIO) levantado.
4. **RNF-07 mide desde que el archivo terminó de llegar hasta la confirmación**, no la transferencia. Con el archivo ya en disco local, validar, subir al bucket en la misma región y escribir en PostgreSQL entra en el segundo, salvo que la prueba de carga diga otra cosa.

**Consecuencias.** El backend necesita disco temporal y tiempo de espera de solicitud suficientes para 100 MB desde redes lentas. Por eso uvicorn usa 2 procesos y el proxy permite cuerpos de 100 MB con tiempo de espera largo. **Criterio para revertir:** si la prueba de carga de RNF-07 (k6, 30 cargas simultáneas de 90 MB) no cumple, se agregan `POST /parques/{parque_id}/cargas` (URL prefirmada) y `POST /parques/{parque_id}/cargas/{carga_id}/confirmacion`. Son endpoints nuevos y no rompen v1 (S04-A2, regla de versionado).

# ADR-003: Sesión en servidor con token JWT

**Fecha:** 2026-10-11 · **Estado:** Aceptado (ratifica la decisión del Sprint 1, T-10)

**Contexto.** RF-26-AC-5 pide que el token deje de servir al cerrar sesión, y RF-26-AC-6 que la sesión expire tras 60 minutos sin actividad. Un JWT sin estado no cumple ninguno de los dos.

**Decisión.** El token es un JWT firmado con un claim `sid`. El componente de seguridad valida la firma y, además, que la fila `sid` de la tabla `sesiones` no esté revocada y tenga uso en los últimos 60 minutos. Cada solicitud válida actualiza `ultimo_uso`.

**Consecuencias.** Cuesta una consulta por solicitud, que es despreciable con 30 usuarios concurrentes. A cambio, hay revocación inmediata (cierre de sesión, baja de usuario en RF-29, restablecimiento de contraseña) y la API no guarda estado en memoria, que es lo que permite escalar a dos instancias.

---

# 4. Diagramas

| Diagrama | Fuente | Imagen | Qué muestra |
|---|---|---|---|
| C4 nivel 2: contenedores | `diagrama_componentes.puml` (primer bloque) | `imagenes/diagrama_componentes_contenedores.png` | Los cuatro tipos de usuario, la SPA, el proxy, la API, el proceso programado, PostgreSQL, el bucket, el correo y el monitoreo, con el protocolo de cada interfaz (JSON/HTTPS con Bearer, SQL sobre TLS, API S3, SMTP). |
| C4 nivel 3: componentes del backend | `diagrama_componentes.puml` (segundo bloque) | `imagenes/diagrama_componentes_backend.png` | Los routers, los cinco módulos de dominio y los componentes transversales, con sus dependencias. Muestra la regla de capas: los routers no tocan repositorios y solo el registro de bitácora escribe eventos. |
| Despliegue | `diagrama_despliegue.puml` | `imagenes/diagrama_despliegue.png` | La VM con Docker Compose (proxy, api y worker), PostgreSQL gestionado y bucket en región de México o EE. UU., la descarga directa con URL firmada, el CI de GitHub Actions con su registro de imágenes y el ambiente de desarrollo del Sprint 1 (Postgres y MinIO en Docker Compose). |
| Clases del dominio | `diagrama_clases.puml` (primer bloque) | `imagenes/diagrama_clases.png` | 34 clases en seis paquetes, con atributos, composición, agregación, asociación y multiplicidades en ambos extremos. |
| Enumeraciones | `diagrama_clases.puml` (segundo bloque) | `imagenes/diagrama_clases_enumeraciones.png` | Las 10 enumeraciones principales; las demás tienen los valores de `openapi.yaml`. |

Cómo leer el diagrama de clases: **Expediente** es la raíz de agregado. Representa la participación de un parque en una generación, y de él cuelgan por composición todo lo que se evalúa (criterios, evidencias, calificaciones, fases) y todo lo que se decide (Opiniones, comité, dictamen). El **Parque** existe antes y después de sus expedientes. El **Catálogo** se comparte entre generaciones y no se compone con nada del expediente; `CriterioExpediente` solo lo referencia. La única agregación real es **ArchivoAlmacenado**: un mismo archivo sustenta evidencias de varios criterios (RF-05-AC-7) y sobrevive a cualquiera de ellas.

---

# 5. Revisión crítica de la propuesta del agente

El agente trabajó con contexto separado: leyó el SRS y los documentos del Sprint 1, y no vio el contrato de S04-A2 ni mi borrador. Su análisis de estilos es bueno, y coincido con su recomendación (monolito modular). Las diferencias están en dos niveles: una decisión de arquitectura (ADR-002) y cinco decisiones en el modelo de dominio. También adopté tres ideas suyas que mi borrador no tenía.

## 5.1 Decisiones del modelo de dominio que difieren de la propuesta del agente

**Decisión 1. Parque sin herencia: un histórico es un estado, no un subtipo.**
*Agente:* `abstract Parque` con dos subclases, `ParqueInscrito` (con tipo de PI y expedientes) y `ParqueHistorico` (datos mínimos). Las asignaciones de rol APPI apuntan a `ParqueInscrito`.
*Mío:* una sola clase `Parque` con `estado: EstadoParque {ACTIVO, INACTIVO, HISTORICO}`, el tipo de PI en `PeriodoTipoPI [0..*]` y `Expediente [0..*]`.
*Por qué:* un objeto no puede cambiar de clase. Si un parque dado de alta como histórico (RF-31-AC-2) entra a la generación 2028, con herencia habría que borrar el `ParqueHistorico` y crear un `ParqueInscrito` nuevo, y se perdería la identidad que usan la bitácora (`parqueId`) y el historial de RF-31-AC-1, que tiene que mostrar las dos etapas en una sola vista. El propio agente dejó esta duda abierta (su pregunta 13: si un histórico puede reactivarse). Con un estado, la respuesta "sí" no cuesta nada y la respuesta "no" se impone con una regla. Es además lo que ya hace el contrato de API: un solo recurso `/parques` con `tipo_registro`.

**Decisión 2. Opinión de Cumplimiento sin herencia y con multiplicidad 0..2.**
*Agente:* `OpinionCumplimiento` abstracta con `OpinionIntermedia` (sin atributos propios) y `OpinionFinal` (con `favorable`), y `Expediente "1" *-- "0..*" OpinionIntermedia`.
*Mío:* una clase con `tipo: TipoOpinion` y `favorable: bool [0..1]`, y `Expediente "1" *-- "0..2" OpinionCumplimiento`.
*Por qué:* una subclase que no agrega ni atributos ni comportamiento no justifica una jerarquía, que en el ORM significa otra tabla o una columna discriminadora para un solo campo. Además, **la multiplicidad del agente contradice el SRS**: el glosario (1.3) dice que hay "una intermedia y una final por parque, en cada generación", y el agente permite intermedias ilimitadas. Las invariantes quedan como reglas del servicio: como máximo una de cada tipo, y `favorable` obligatorio si y solo si el tipo es FINAL. RF-12-AC-3 y RF-12-AC-6 ya tienen pruebas contra esas reglas.

**Decisión 3. El dictamen pertenece al expediente, no a la sesión de comité.**
*Agente:* `SesionComite "1" *-- "0..1" Dictamen`: el dictamen solo existe dentro de una sesión.
*Mío:* `Expediente "1" *-- "0..*" Dictamen`, con capturador y firmante como asociaciones a `Usuario`.
*Por qué:* el SRS tiene un caso que la composición del agente vuelve imposible. **RF-14-AC-8** pide registrar "no otorgar" para un parque con 60 % de obligatorios, sin autoevaluación revisada y sin Opinión final favorable. Pero **RF-15** impide abrir la sesión de comité justo en ese caso (sin autoevaluación revisada y sin Opinión final favorable no hay sesión). Si el dictamen solo existe dentro de una sesión, el "no otorgar" de RF-14-AC-8 no se puede registrar nunca. Con el dictamen colgando del expediente, Coordinación lo captura sin sesión (RF-14 dice "Coordinación AMPIP o el consultor de comité"), y cuando sí hay sesión, el consultor de comité lo captura mientras está abierta. Encontrar esto me llevó a una pregunta para AMPIP que el SRS no resuelve: ¿un "no otorgar" pasa por comité o lo decide Coordinación? La agrego a los pendientes del SRS.

**Decisión 4. Sin asociación duplicada entre Expediente y VersionCatalogo.**
*Agente:* `Generacion --> VersionCatalogo` y además `Expediente --> VersionCatalogo`.
*Mío:* solo `Generacion "0..*" --> "1" VersionCatalogo`. La versión de un expediente se navega por su generación.
*Por qué:* RF-01-AC-5 dice que la versión es de la generación y que cada parque se evalúa contra la de su generación. Con dos asociaciones, nada impide que un expediente de 2027 apunte a "catalogo-2023-v2" mientras su generación usa la v1, y RF-01-AC-3 mostraría la versión equivocada. Prefiero una sola fuente de verdad. Cuando entre la renovación (RD-06, RF-38), que evalúa contra la versión vigente en ese momento, ese caso tendrá su propia entidad de ciclo con su propia versión, sin reabrir esta.

**Decisión 5. El modelo cubre el alcance de 12 semanas, no el semestre completo.**
*Agente:* incluye `Distintivo`, `SolicitudRenovacion`, `Prorroga`, `VisitaValidacion`, `Hallazgo`, `Auditoria` con dos subclases y `Aviso`, todos de RF con prioridad Posterior. Son 46 clases y 20 enumeraciones.
*Mío:* 34 clases. Lo Posterior queda fuera, como en `openapi.yaml`, y la vigencia del distintivo (RD-08) vive por ahora en `Dictamen.vigenciaHasta`, que se llena al firmar un "otorgar".
*Por qué:* el diagrama de clases es la base de las migraciones de S05-S06. Una clase en el diagrama se vuelve una tabla que alguien crea, prueba y mantiene. Modelar `Distintivo` hoy, sin los criterios de RF-38 implementados, fija decisiones (estados, transiciones) que el cliente no ha validado: RD-08 tiene la vigencia de tres años como pendiente. Agregarlo después es una migración que no rompe nada.

## 5.2 Lo que adopté del agente y no tenía mi borrador

| Idea del agente | Por qué la adopté |
|---|---|
| `VersionCatalogo *-- 10 Estandar *-- 1..* Subestandar *-- 1..* Criterio`, en lugar de `estandar: int` y `subestandar: String` como atributos del criterio | Los estándares tienen nombre ("Seguridad física") y el cálculo de RF-08 agrupa por estándar. Con los atributos sueltos, el nombre se repetiría en 286 filas. |
| `Evidencia --> DefinicionFase` en lugar de `fase: String` | La secuencia de fases vive en datos (conflicto C-15). Con un texto libre, una fase renombrada deja evidencias huérfanas. |
| `import-linter` en CI para las fronteras de módulo | Hace que la frontera del ADR-001 se compruebe en cada PR y no dependa de la memoria de quien revisa. |

## 5.3 Lo que el agente vio y yo no

Del análisis del agente tomo dos riesgos que no tenía registrados:

- **La bitácora registra que se emitió la URL firmada, no la descarga real**, que ocurre en el bucket (su pregunta 5). Para RNF-03 lo acepto, y queda documentado en `GET /evidencias/{evidencia_id}/contenido`.
- **La clasificación de un archivo como "de seguridad" o "administrativo" no está definida en el SRS** (su pregunta 3). Mi modelo la pone en `Evidencia.esAdministrativa`, que decide la APPI al subir. Hay que confirmar con AMPIP si debería derivarse del criterio.

Las dos van a la lista de pendientes con el cliente.
