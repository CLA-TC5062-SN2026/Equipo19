# SGPIS backend

API REST de `openapi_equipo.yaml` v2.0.0 con FastAPI, SQLAlchemy 2.0 y PostgreSQL 16. Todas las rutas cuelgan de `/api`. Salvo `/salud`, `/auth/login` y `/auth/register`, todas exigen `Authorization: Bearer <JWT>` y validan el rol y la relación con el parque (`app/permisos.py`).

## Levantar con Docker

```bash
cp .env.example .env
docker compose up --build
curl http://localhost:8000/api/salud
```

Antes de `docker compose up`, cambia en `.env` `POSTGRES_PASSWORD`, `JWT_SECRET` y las contraseñas de la semilla.

`db` carga `db/esquema_bd.sql` desde `/docker-entrypoint-initdb.d/` solo la primera vez (volumen vacío). Para recrear la base: `docker compose down -v`.

## Levantar sin Docker

```bash
uv sync
createdb sgpis && psql -d sgpis -v ON_ERROR_STOP=1 -f db/esquema_bd.sql
DATABASE_URL=postgresql+psycopg://usuario:contrasena@localhost:5432/sgpis uv run uvicorn app.main:app --reload
```

## Primera cuenta

Con todas las rutas protegidas, la primera cuenta de Coordinación AMPIP se crea en el servidor:

```bash
uv run python -m app.alta_inicial --correo coordinacion@ampip.mx --nombre "Coordinación AMPIP"
```

El comando muestra un token de invitación una sola vez; la contraseña se fija con `POST /api/auth/register`.

## Datos de arranque (solo desarrollo)

```bash
uv run python -m app.semilla
uv run python -m app.semilla --demo
```

La primera carga el catálogo sintético y la generación 2027. Con `--demo` agrega la APPI de demostración y la invitación para el video de A2. Usa `SEMILLA_CORREO`, `SEMILLA_CONTRASENA` y `SEMILLA_APPI_CONTRASENA` del `.env`. Es idempotente.

Para la demo de S11, después de la semilla:

```bash
uv run --env-file .env python -m app.demo_s11
```

Crea los datos con la API, como lo haría Coordinación o el consultor, salvo la calificación de criterios: RF-27 no
tiene endpoint, así que el avance se escribe directo en `criterio_parque` y en su historial (el script lo explica en su
encabezado). Las cuentas usan `DEMO_CONTRASENA`. Es idempotente.

Documentación interactiva: http://localhost:8000/api/docs

## CORS

El frontend corre en otro origen (`http://localhost:5173`). `app/main.py` registra `CORSMiddleware` con `URL_SPA` más
los orígenes de `CORS_ORIGENES` (separados por coma). Los errores 401/403/422 también llevan el encabezado, para que el
navegador deje leer el mensaje (`tests/test_cors.py`).

## Pruebas

Necesitan un PostgreSQL 16 local con un usuario que pueda crear bases (por defecto `postgresql://postgres@localhost:5432/postgres`, se cambia con `SGPIS_TEST_ADMIN_URL`). Cada prueba corre sobre una base nueva clonada de `db/esquema_bd.sql`, y cada respuesta se valida contra `../S05_S06_A1/openapi_equipo.yaml`.

```bash
uv sync
uv run pytest
```

Resultado esperado: 105 pruebas aprobadas.

Con la base del `docker compose` basta apuntar al usuario del contenedor, que puede crear bases:
`SGPIS_TEST_ADMIN_URL="postgresql://sgpis:<POSTGRES_PASSWORD>@localhost:5432/postgres" uv run pytest`.
`tests/test_trazabilidad_s11.py` agrega las pruebas de AC que el código ya cumplía sin prueba con nombre (S11).

## Calidad de código (S09_A1)

```bash
bash scripts/calidad.sh
uv run pytest --cov=app --cov-report=term-missing
uv run pytest tests/medicion_s09.py -s -q
```

`calidad.sh` corre pylint, flake8, mypy y bandit con la configuración de `pyproject.toml` y `.flake8`. `medicion_s09.py` imprime las sentencias SQL y los tiempos de GET /parques con 10, 41 y 80 parques.

`tests/test_caracterizacion_s09.py` fija el comportamiento de PATCH /parques, PATCH /usuarios y GET /parques antes de refactorizar; `tests/test_refactorizacion_s09.py` reproduce los defectos CR-03 y CR-04. El análisis y las refactorizaciones están en `../S09_A1/`.

## Estructura

| Ruta | Contenido |
|---|---|
| `app/main.py` | Aplicación, routers bajo `/api`, OpenAPI con el schema `Error` |
| `app/config.py` | Variables de entorno (pydantic-settings) |
| `app/db.py` | Motor y sesión por solicitud (psycopg 3) |
| `app/modelos.py` | ORM 1:1 de `db/esquema_bd.sql` (no crea tablas) |
| `app/esquemas.py` | Request y response en camelCase |
| `app/errores.py` | Handlers globales: todo error sale como `{codigo, mensaje, detalles}` |
| `app/seguridad.py` | bcrypt, emisión y validación del JWT y de la sesión, dependencias de autenticación |
| `app/permisos.py` | Mapa de permisos por rol y parque, dependencia `autorizar` (403 + bitácora) |
| `app/comun.py` | Usuario que registra, fechas en CDMX, paginación, orden, bitácora |
| `app/servicios.py` | Expediente vigente, tipo de PI, criterios aplicables, cumplimiento |
| `app/routers/` | Un router por grupo de recursos del contrato |

## Decisiones provisionales

Las revisiones del equipo sobre el código que generó el agente están en `../S05_S06_A1/revision_sql.md` (CRUD) y `../S05_S06_A2/revision_seguridad.md` (autenticación y permisos).

- **Autenticación y permisos.** Todas las rutas salvo `/salud`, `/auth/login` y `/auth/register` exigen `Authorization: Bearer` (401 sin token válido). El mapa ruta -> perfiles autorizados está en `app/permisos.py` (`PERMISOS`); la dependencia `autorizar` lo aplica a cada router protegido, lee rol, parque, desarrollador y asignaciones de la base, responde 403 con el schema `Error` y registra el intento en la bitácora con resultado `denegado`. Si una ruta protegida no tiene entrada en el mapa, la API no arranca. El actor de las escrituras (`registradoPor`, `cargadoPor`, bitácora...) es siempre el usuario autenticado.
- **CSV del catálogo.** El archivo no trae clave, categoría de evidencia ni nombres de estándar. La clave se arma como `subestandar.n` (consecutivo dentro del subestándar), la categoría queda en `seguridad` y los nombres como "Estándar N" / "Subestándar N.M".
- **Parques históricos.** No tienen expediente; sus subrecursos (criterios, fases, plan, etc.) responden 404 `sin_expediente`.
- **Atrasos.** Mientras no exista el worker, `atrasado` se calcula al consultar (fecha comprometida vencida y criterio no cumplido) además de la marca `fecha_marca_atraso`.
- **Invitaciones.** `POST /usuarios` deja el enlace de un solo uso y el correo en el outbox (`mensaje_correo`); falta el worker que los envía. `/auth/register` consume el enlace.
