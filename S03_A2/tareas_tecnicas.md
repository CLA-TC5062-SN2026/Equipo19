# Tareas técnicas del Sprint 1

**Proyecto:** SGPIS (AMPIP), Equipo 19, TC5062
**Sprint Backlog:** HT-01 (esqueleto técnico del backend) y HU-01 (autenticación, API). Selección y capacidad en `sprint1_planning.md`.
**Descomposición del agente, sin editar:** `evidencia_agente/descomposicion_agente.md`

Cada tarea dura 4 horas o menos, tiene un rol responsable y un criterio de done que se comprueba con una prueba, un comando o una revisión concreta. Los criterios de aceptación que cubre cada tarea remiten a `S03_A1/SRS_equipo.md`. Además de su criterio propio, ninguna tarea se cierra sin cumplir los puntos de nivel tarea de `definition_of_done.md`.

## Resumen

| Elemento | Tareas | Horas |
|---|---|---|
| HT-01 Esqueleto técnico del backend | T-01 a T-06 | 17 |
| HU-01 Iniciar sesión, cerrar sesión y recuperar contraseña (API) | T-07 a T-14 | 22 |
| **Total** | **14** | **39** |

| Rol | Horas |
|---|---|
| Backend | 25 |
| QA | 6 |
| DevOps | 6 |
| Seguridad | 2 |

Backend concentra 25 de las 39 horas. Es lo esperado en un sprint sin frontend, y por eso las tareas de backend están cortadas para que dos personas puedan trabajarlas en paralelo: T-08 a T-11 tocan endpoints distintos y solo comparten el modelo de T-07.

## HT-01 Esqueleto técnico del backend

| ID | Tarea | Rol | Horas | Criterio de done | Cubre |
|---|---|---|---|---|---|
| T-01 | Estructura del repo, docker compose con PostgreSQL 16 y .env.example | DevOps | 3 | Otro integrante, en una máquina sin el proyecto, clona el repo, ejecuta `docker compose up -d` y `uv run uvicorn` siguiendo solo el README, y la API arranca. El repo no contiene ningún `.env`. | 2.4, DoD |
| T-02 | Esqueleto FastAPI: configuración con pydantic-settings, GET /health y manejador de errores en español | Backend | 3 | GET /health responde 200 con la versión y el estado de la conexión a la base. Un error no controlado responde 500 con un mensaje en español y sin traza en el cuerpo. | RNF-11, DoD |
| T-03 | SQLAlchemy 2.0 y Alembic: sesión por solicitud y migración inicial | Backend | 3 | `alembic upgrade head` sobre una base vacía y `alembic downgrade base` terminan sin error. Una prueba confirma que la sesión de base se cierra al terminar cada solicitud. | 2.4 |
| T-04 | Bitácora de solo append: tabla, función registrar_evento y usuario de base sin UPDATE ni DELETE sobre ella | Backend | 3 | Una prueba inserta un evento con fecha, usuario, rol, acción, recurso y resultado. Un UPDATE y un DELETE sobre la tabla con el usuario de base de la aplicación fallan por permisos. | RNF-03, RF-35 |
| T-05 | pytest con httpx y base de prueba aislada por prueba | QA | 2 | Dos pruebas que escriben la misma fila pasan en cualquier orden. `uv run pytest` termina en verde en una máquina recién clonada. | DoD |
| T-06 | GitHub Actions: ruff y pytest con PostgreSQL de servicio en cada PR; rama main protegida | DevOps | 3 | Un PR de prueba con una prueba fallida no se puede fusionar. Con todo en verde y la aprobación de otro integrante, sí. Nadie puede hacer push directo a main. | DoD |

## HU-01 Iniciar sesión, cerrar sesión y recuperar contraseña (API)

| ID | Tarea | Rol | Horas | Criterio de done | Cubre |
|---|---|---|---|---|---|
| T-07 | Modelos Usuario, Rol y Sesión con migración; comando de semilla del primer usuario de Coordinación AMPIP | Backend | 3 | La migración aplica y revierte. `uv run python -m sgpis.semilla` crea el usuario de Coordinación AMPIP con el correo y la contraseña tomados de variables de entorno, y no lo duplica si se corre dos veces. | RF-03, RF-26 |
| T-08 | POST /auth/login con argon2, mensaje de error genérico y registro en bitácora | Backend | 3 | Correo inexistente y contraseña incorrecta devuelven el mismo código y el mensaje "Correo o contraseña incorrectos". Inicio exitoso y fallido quedan en la bitácora. | RF-26-AC-1, RF-26-AC-2 |
| T-09 | Bloqueo de 15 minutos tras 5 intentos fallidos consecutivos | Backend | 2 | El sexto intento, aun con la contraseña correcta, devuelve "Cuenta bloqueada temporalmente; intente de nuevo en 15 minutos". Con el reloj simulado en el minuto 15 el inicio se acepta. | RF-26-AC-3 |
| T-10 | Sesiones guardadas en servidor con expiración por 60 minutos de inactividad y POST /auth/logout | Backend | 3 | Un token usado después de cerrar sesión recibe 401. Un token sin uso durante 60 minutos (reloj simulado) recibe 401. Cada solicitud válida reinicia la ventana de 60 minutos. | RF-26-AC-5, RF-26-AC-6 |
| T-11 | Recuperación de contraseña: POST /auth/recuperacion y POST /auth/restablecimiento con token de un solo uso de 30 minutos; correo por consola en desarrollo | Backend | 3 | El token restablece la contraseña una sola vez. Un segundo uso, o un uso en el minuto 31, se rechaza. La respuesta a una solicitud de recuperación es la misma exista o no el correo. | RF-26-AC-4 |
| T-12 | Dependencia requiere_rol reutilizable: 401 sin sesión, 403 sin el rol e intento denegado en bitácora | Backend | 2 | Un endpoint de prueba reservado a Coordinación AMPIP responde 401 sin token, 403 a un usuario APPI y a un consultor, y cada 403 deja un registro con resultado "denegado". | RNF-01, RF-35-AC-2 |
| T-13 | Pruebas automatizadas de RF-26-AC-1 a RF-26-AC-6 nombradas con su ID | QA | 4 | Existen seis pruebas `test_rf26_ac1` a `test_rf26_ac6`, en verde en GitHub Actions. Las que dependen del tiempo usan reloj simulado; ninguna usa sleep. | RF-26-AC-1 a AC-6 |
| T-14 | Revisión de seguridad del flujo de autenticación | Seguridad | 2 | El PR de HU-01 incluye el checklist revisado: sin enumeración de usuarios, verificación de hash en tiempo constante, contraseñas y tokens fuera de logs y de mensajes de error, token en cabecera Authorization, parámetros de argon2 documentados. Cada hallazgo abierto queda como issue. | RNF-01, DoD |

## Orden y dependencias

T-01 va primero y bloquea todo lo demás. T-02, T-03 y T-05 pueden avanzar en paralelo en cuanto existe el repo. T-04 necesita T-03. T-06 necesita T-05, porque el CI corre las pruebas.

En HU-01, T-07 va primero. T-08, T-10, T-11 y T-12 pueden ir en paralelo sobre el modelo de T-07. T-09 necesita T-08. T-13 se escribe junto con cada endpoint y se cierra al final. T-14 se hace sobre el PR de HU-01 ya armado.

## Cómo quedan en GitHub Projects

Cada tarea es un issue con el prefijo de su ID (por ejemplo, "T-08 · POST /auth/login…") y es sub-issue de su elemento padre: HT-01 es un issue nuevo y HU-01 es el issue #1. Cada tarea lleva las etiquetas `tarea`, `sprint:1`, `rol:…` y `horas:N`, y entra al tablero "Tablero Kanban S03" en la columna "Sprint actual", junto con HT-01 y HU-01. Además, el cuerpo de cada padre lleva la lista de sus tareas como casillas, así que el avance se ve aunque el tablero no muestre sub-issues. El script `github/crear_tareas_sprint1.sh` lo hace todo.

## Ajustes a la descomposición del agente

El agente entregó 9 tareas, 35 horas. Las revisé contra los criterios de aceptación de RF-26 y contra la definición de terminado. Encontré cuatro problemas de fondo y varios de forma.

### Un error técnico en el diseño de sesión

El agente propuso JWT sin estado, con "expiración a los 60 minutos". Eso no cumple dos criterios del SRS. RF-26-AC-5 pide que al cerrar sesión el token se invalide y cualquier solicitud posterior reciba 401, y un JWT sin estado sigue siendo válido hasta que expira. RF-26-AC-6 pide expiración por 60 minutos de inactividad, es decir, una ventana que se reinicia con cada solicitud, mientras que un JWT expira 60 minutos después de emitido aunque el usuario esté trabajando. La sesión tiene que vivir en el servidor (T-10). Es el cambio más importante, porque con la propuesta original las pruebas de AC-5 y AC-6 no habrían podido pasar.

### Tareas de más de 4 horas

Había tres. "Configurar el proyecto" (6 h) se dividió en T-01, T-02 y T-03. "Login con JWT y bloqueo" (6 h) se dividió en T-08 y T-09. "Pantalla de login en React" (5 h) salió del sprint con HU-23 (ver `sprint1_planning.md`, sección 4).

### Lo que faltaba

- La bitácora (T-04). La exige RNF-03 y la exige la definición de terminado; sin ella, ninguna historia podría cerrarse.
- La autorización por rol reutilizable (T-12). El agente resolvió la autenticación y no la autorización; RNF-01 pide 403 en cada endpoint, y conviene escribirlo una sola vez.
- La base de pruebas aislada (T-05). Sin ella, las pruebas de T-13 dependen del orden en que corren.
- La creación del primer usuario (T-07). Sin alta de usuarios en el sprint (HU-04 viene después), alguien tiene que poder entrar la primera vez.
- La revisión de seguridad (T-14). Es un flujo de autenticación para un sistema con información de seguridad de parques industriales; no lo cierro sin revisarlo contra los errores comunes: enumeración de usuarios, contraseñas en logs y comparaciones de hash que filtran tiempo.

### Lo que sobraba

- **CD con despliegue automático.** No hay servidor donde desplegar. T-06 configura solo integración continua.
- **SendGrid para el correo de recuperación.** Agrega un servicio externo, una llave secreta y una decisión que le toca a AMPIP (RNF-12). En desarrollo el correo se escribe en consola; el proveedor real se elige antes del piloto.
- **"Documentar la API" como tarea aparte.** FastAPI genera la documentación OpenAPI con cada endpoint. Que cada endpoint aparezca descrito en `/docs` es un punto de la definición de terminado, no una tarea.

### Criterios de done que no se podían comprobar

"El proyecto corre localmente", "el usuario puede iniciar sesión" o "la documentación está actualizada" no dicen quién lo comprueba ni cómo. Reescribí cada criterio para que se verifique con una prueba nombrada, un comando o una revisión concreta. La meta de "cobertura de al menos 80 %" la cambié por una prueba por criterio de aceptación, nombrada con su ID. Un porcentaje de cobertura se puede alcanzar con pruebas que no prueban nada de lo que el cliente pidió.

### Resultado

| | Agente | Final |
|---|---|---|
| Tareas | 9 | 14 |
| Horas | 35 | 39 |
| Tareas de más de 4 h | 3 | 0 |
| Criterios de aceptación de RF-26 cubiertos por una prueba nombrada | 0 | 6 |
| Tareas de frontend | 1 (5 h) | 0, movida a HU-23 |

Pasar de 35 a 39 horas con cinco tareas más se explica porque las tareas nuevas son cortas (2 y 3 horas) y porque salieron la pantalla de React (5 h) y la tarea de documentación (2 h).
