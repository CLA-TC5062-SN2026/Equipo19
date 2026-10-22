# SGPIS backend

API REST de `openapi_equipo.yaml` v2.0.0 con FastAPI, SQLAlchemy 2.0 y PostgreSQL 16. Todas las rutas cuelgan de `/api`. **Todavía sin autenticación**: ninguna ruta pide token ni valida rol; JWT y permisos llegan en S05-S06-A2.

## Levantar con Docker

```bash
cp .env.example .env        # cambiar POSTGRES_PASSWORD
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

Datos de arranque (catálogo sintético y generación 2027, idempotente):

```bash
uv run python -m app.semilla
```

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
| `app/comun.py` | Usuario que registra, fechas en CDMX, paginación, orden, bitácora |
| `app/servicios.py` | Expediente vigente, tipo de PI, criterios aplicables, cumplimiento |
| `app/routers/` | Un router por grupo de recursos del contrato |

## Decisiones provisionales

La revisión del equipo sobre el código que generó el agente está en `../S05_S06_A1/revision_sql.md`, sección 3.

- **Quién registra.** Sin sesión no hay usuario autenticado. Los campos `registradoPor`, `cargadoPor`, `cambiadoPor`, `cerradaPor`, `actualizadoPor` y el `usuario_id` de la bitácora se llenan con un usuario técnico (`USUARIO_SISTEMA_CORREO`, rol `administrador_tecnico`, estado `pendiente_activacion`) que se crea solo la primera vez que hace falta. Todo pasa por la dependencia `usuario_actual` de `app/comun.py`; en S05-S06-A2 se cambia por la que lee el JWT.
- **CSV del catálogo.** El archivo no trae clave, categoría de evidencia ni nombres de estándar. La clave se arma como `subestandar.n` (consecutivo dentro del subestándar), la categoría queda en `seguridad` y los nombres como "Estándar N" / "Subestándar N.M".
- **Parques históricos.** No tienen expediente; sus subrecursos (criterios, fases, plan, etc.) responden 404 `sin_expediente`.
- **Atrasos.** Mientras no exista el worker, `atrasado` se calcula al consultar (fecha comprometida vencida y criterio no cumplido) además de la marca `fecha_marca_atraso`.
- **Invitaciones.** `POST /usuarios` deja el enlace de un solo uso y el correo en el outbox (`mensaje_correo`); falta el worker que los envía y `/auth/register`.
