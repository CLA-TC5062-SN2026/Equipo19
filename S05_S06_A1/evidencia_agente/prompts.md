# Prompts usados con el agente (S05-S06-A1)

Las salidas del agente se guardan sin editar en esta carpeta (`analisis_diferencias_agente.md`, `esquema_bd_v0.sql`) y en el historial de git del backend (commit "v0 generado por el agente"). Las correcciones están en `revision_sql.md`.

## Prompt 0: análisis de diferencias de los tres diseños (Parte 0)

Las decisiones del equipo sobre cada conflicto están en `diferencias_diseno.md`, sección 6.

```text
Eres un analista de diseño de software. Un equipo de tres personas (Ángel, Leonardo, Erick) diseñó por separado, para el mismo sistema (SGPIS, AMPIP), una especificación OpenAPI, un diagrama de clases y una arquitectura de componentes. Tu trabajo es el análisis de diferencias que el equipo usará para consolidar. NO resuelvas los conflictos: el equipo los resuelve. Puedes dar una recomendación por conflicto, marcada como recomendación.

Insumos (lee todo antes de escribir; todos bajo S05_S06_A1/insumos/):
- Ángel: `Angel_S04_A2_v2/openapi.yaml`, `Angel_S04_A1_v2/diagrama_clases.puml`, `Angel_S04_A1_v2/diagrama_componentes.puml`, `Angel_S04_A1_v2/decision_arquitectonica.md`. (Hay también una versión anterior `Angel_*_v1`, hecha contra su SRS individual; úsala solo si necesitas aclarar algo, el diseño que cuenta es el v2.)
- Leonardo: `Leonardo_S04_A2/openapi.yaml`, `Leonardo_S04_A1/diagrama_clases.puml`, `Leonardo_S04_A1/diagrama_componentes.puml`, `Leonardo_S04_A1/decision_arquitectonica.md`.
- Erick: `Erick_S04_A2/openapi.yaml`, `Erick_S04_A1/diagrama_clases_agente.puml`, `Erick_S04_A1/diagrama_componentes_agente.puml`, `Erick_S04_A1/decision_arquitectonica.md`.
- Referencia: el SRS de equipo `S03_A1/SRS_equipo.md` (IDs RF-XX-AC-Y) y el borrador de consolidación que ya existe, `S05_S06_A1/openapi_equipo.yaml` y `S05_S06_A1/diagrama_clases_equipo.puml`. Usa el borrador solo para la columna "en el borrador", no como un cuarto diseño.

Escribe un solo archivo: `S05_S06_A1/evidencia_agente/analisis_diferencias_agente.md`, con estas secciones:

1. OpenAPI. Agrupa las operaciones por recurso o propósito (no hace falta listar cada operación una por una cuando un grupo es consenso). Tres tablas:
   a) Consenso: propósitos que los tres cubren. Columnas: propósito, ruta y método de cada integrante, ¿en el borrador?
   b) Gaps: propósitos que solo uno o dos cubren. Columnas: propósito, quién lo propone, ruta, RF/AC del SRS que lo justifica (o "sin RF"), prioridad del RF en el SRS, ¿en el borrador?
   c) Conflictos: mismo propósito con distinto diseño (nombre de ruta, método, esquema del body, códigos de respuesta, autenticación). Columnas: ID (O-01...), propósito, diseño de cada uno, por qué importa, recomendación.
   Además, una tabla corta de diferencias transversales: ruta base y versión, esquema de seguridad (nombre, JWT con o sin sesión), formato de error, paginación, convención de nombres (camelCase o snake_case), cobertura de x-acceptance-criteria (cuántos AC del SRS cubre cada contrato; calcúlalo con un script).
2. Diagrama de clases. Las mismas tres tablas (consenso, gaps, conflictos con IDs K-01...). Señala especialmente: cómo modela cada uno los roles (herencia o atributo), la relación evidencia–criterio, las fases, la bitácora, el expediente por generación, y si los atributos de cada clase corresponden a los campos de su propio OpenAPI.
3. Arquitectura. Estilo elegido por cada uno, contenedores, almacenamiento de archivos, autenticación, procesos en segundo plano, despliegue. Tabla de consenso y tabla de conflictos (IDs Q-01...).
4. Resumen en cifras: operaciones, rutas y schemas de cada contrato; clases de cada diagrama.

Sé preciso: cita rutas y nombres reales de los archivos, sin inventar. Escribe en español. Es un análisis de agente que se guarda sin editar como evidencia, así que no hace falta pulir redacción, pero sí exactitud.

Responde en menos de 200 palabras: cuántos consensos, gaps y conflictos encontraste en cada artefacto, y los 5 conflictos que consideras más importantes de resolver.
```

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
