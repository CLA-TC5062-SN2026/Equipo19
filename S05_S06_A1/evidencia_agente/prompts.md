# Prompts usados con el agente (S05-S06-A1)

Las salidas del agente se guardan sin editar en esta carpeta (`esquema_bd_v0.sql`) y en el historial de git del backend (commit "v0 generado por el agente"). Las correcciones están en `revision_sql.md`.

## Prompt 1: esquema de base de datos (Parte 1)

```text
Eres un ingeniero de bases de datos. Genera el esquema físico inicial (versión v0) de la base de datos de un sistema
llamado SGPIS para PostgreSQL 16.

Insumos (léelos completos antes de escribir):
- Diagrama de clases consolidado: diagrama_clases_equipo.puml
- Contrato OpenAPI del equipo: openapi_equipo.yaml (los schemas de components/schemas son la referencia de tipos y
  nombres de campos)

Escribe un solo archivo: evidencia_agente/esquema_bd_v0.sql

Requisitos del archivo:
- CREATE TABLE para todas las entidades del diagrama de clases (las enumeraciones pueden ser tipos ENUM o CHECK, tú
  decides).
- PRIMARY KEY en cada tabla.
- FOREIGN KEY que reflejen las relaciones del diagrama (cardinalidad y tabla referenciada).
- NOT NULL y UNIQUE donde el dominio lo requiera.
- Tipos de dato coherentes con los schemas del OpenAPI (uuid, date, timestamptz, etc.).
- Índices en columnas de búsqueda frecuente (correo, nombre, llaves foráneas usadas en filtros).
- Nombres de tablas y columnas en snake_case, en español, sin acentos.
- El script debe poder ejecutarse completo sobre una base vacía con `psql -v ON_ERROR_STOP=1 -f`.

Esto es un borrador que el equipo revisará después, así que no te autocorrijas ni lo pulas en varias pasadas: genera
tu mejor versión en un intento, ejecútala una vez para confirmar que corre y, si falla por un error de sintaxis,
arréglalo solo lo necesario para que corra.
```

## Prompt 2: servicios CRUD (Parte 2)

```text
Eres un desarrollador Python. A partir de la especificación OpenAPI 3.0 openapi_equipo.yaml y del esquema
esquema_bd.sql, genera una API REST funcional.

Insumos: openapi_equipo.yaml (fuente de verdad de rutas, métodos, códigos de respuesta y schemas JSON),
esquema_bd.sql (tablas ya definidas; no las cambies ni generes otras), catalogo_sintetico.csv.

Tecnologías obligatorias:
- Python 3.12, FastAPI, Uvicorn, SQLAlchemy 2.0 (ORM declarativo, estilo Mapped[...]) sobre las tablas existentes,
  psycopg 3, Pydantic v2, pydantic-settings, python-multipart.
- PostgreSQL 16. La conexión sale de la variable de entorno DATABASE_URL; incluye un .env.example (sin secretos
  reales) y un docker-compose.yml con un servicio db (postgres:16-alpine) que cargue esquema_bd.sql desde
  /docker-entrypoint-initdb.d/ y un servicio api.
- Gestión de dependencias con uv (pyproject.toml).
- IMPORTANTE: por ahora NO quiero seguridad. Ninguna ruta debe pedir token ni validar roles; la autenticación JWT se
  agrega en la siguiente actividad. No implementes /auth/*.

Estructura: todo bajo backend/ (paquete app/ con main.py, configuración, conexión a BD, modelos, esquemas Pydantic y
routers; copia de esquema_bd.sql en backend/db/; README.md corto). Prefijo de rutas: /api.

Implementa, con las rutas, métodos, cuerpos y códigos de respuesta EXACTOS del YAML, estas operaciones:
- Operación: GET /salud
- Catálogo: GET y POST /versiones-catalogo (POST recibe el CSV multipart), GET /versiones-catalogo/{versionId},
  GET y PATCH /criterios/{criterioId}
- Generaciones: GET y POST /generaciones, GET /generaciones/{generacionId}
- Parques: GET y POST /parques, GET y PATCH /parques/{parqueId}, PUT /parques/{parqueId}/tipo-pi,
  GET /parques/{parqueId}/tipos-pi, POST /parques/{parqueId}/actualizaciones-anuales,
  GET /parques/{parqueId}/actualizaciones-anuales/{actualizacionId}
- Usuarios: GET y POST /usuarios, GET y PATCH /usuarios/{usuarioId}, GET /parques/{parqueId}/usuarios,
  PUT /parques/{parqueId}/contacto-principal
- Asignaciones: GET y POST /parques/{parqueId}/asignaciones-consultor,
  GET /parques/{parqueId}/asignaciones-consultor/{asignacionId}
- Criterios del parque: GET /parques/{parqueId}/criterios, GET /parques/{parqueId}/criterios/{criterioId}
- Autoevaluación: GET /parques/{parqueId}/autoevaluaciones, GET y PUT /parques/{parqueId}/autoevaluaciones/{criterioId}
- Cumplimiento: GET /parques/{parqueId}/cumplimiento
- Plan de trabajo: GET y POST /parques/{parqueId}/plan-trabajo, GET, PATCH y DELETE
  /parques/{parqueId}/plan-trabajo/{renglonId}
- Análisis de riesgos: GET y POST /parques/{parqueId}/revisiones-analisis-riesgos,
  GET /parques/{parqueId}/revisiones-analisis-riesgos/{revisionId}
- Fases: GET /parques/{parqueId}/fases, POST /parques/{parqueId}/fases/{fase}/cierre, POST /parques/{parqueId}/avances-fase
- Configuración: GET y PATCH /configuracion
- Bitácora: GET /bitacora

Requisitos de comportamiento:
- Respuestas JSON en camelCase como en los schemas; 404 si el recurso de la ruta no existe; datos inválidos con el
  código que indica el YAML (422 en general). Los errores salen con el schema Error del YAML.
- Aplica las reglas de negocio que el YAML describe en cada operación cuando sean directas (mensajes de error
  literales incluidos).

Esto es un borrador que el equipo revisará después: genera tu mejor versión en un intento, sin pasadas de pulido.
Levanta la API una vez para confirmar que arranca y que GET /api/salud responde; si no arranca, arregla solo lo
necesario. No escribas pruebas automatizadas.
```
