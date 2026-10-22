# SGPIS backend

API REST de `openapi_equipo.yaml` v2.0.0 con FastAPI, SQLAlchemy 2.0 y PostgreSQL 16. Todas las rutas cuelgan de `/api`. Salvo `/salud`, `/auth/login` y `/auth/register`, todas exigen `Authorization: Bearer <JWT>` y validan el rol y la relación con el parque (`app/permisos.py`).

## Levantar con Docker

```bash
cp .env.example .env        # cambiar POSTGRES_PASSWORD, JWT_SECRET y las contraseñas de la semilla
docker compose up --build
curl http://localhost:8000/api/salud
```

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
uv run python -m app.semilla          # catálogo sintético y generación 2027
uv run python -m app.semilla --demo   # además, APPI de demostración e invitación para el video de A2
```

Usa `SEMILLA_CORREO`, `SEMILLA_CONTRASENA` y `SEMILLA_APPI_CONTRASENA` del `.env`. Es idempotente.

Documentación interactiva: http://localhost:8000/api/docs

## Pruebas

Necesitan un PostgreSQL 16 local con un usuario que pueda crear bases (por defecto `postgresql://postgres@localhost:5432/postgres`, se cambia con `SGPIS_TEST_ADMIN_URL`). Cada prueba corre sobre una base nueva clonada de `db/esquema_bd.sql`, y cada respuesta se valida contra `../S05_S06_A1/openapi_equipo.yaml`.

```bash
uv sync
uv run pytest
```

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
