# Arquitectura del equipo: SGPIS

**Equipo:** 19 (Ángel Kociankowski, Leonardo Cossío, Erick Ramírez)
**Actividad:** S05-S06-A1, Parte 0
**Insumos:** `../S03_A1/SRS_equipo.md` v2.0; ADR, diagrama de componentes y diagrama de despliegue de S04_A1 de los tres (`insumos/`); `../S03_A2/sprint1_planning.md` y `../S03_A2/tareas_tecnicas.md`; `openapi_equipo.yaml`
**Diferencias con los diseños individuales:** `diferencias_diseno.md`, secciones 5 y 6.3

## Decisión

Cliente-servidor. Una SPA en React consume una API REST, y el backend es un monolito modular en capas, con un worker aparte para lo que corre fuera de una solicitud.

Los tres ADR individuales llegaron al mismo estilo: monolito modular en capas, con microservicios como la alternativa descartada. Tomamos como base el de Ángel porque es el único con vista de componentes (C4 nivel 3) y lo ajustamos en estos puntos:

1. El ADR original suponía un solo desarrollador y ahora somos tres. El argumento contra microservicios sigue en pie, porque descansaba en que RD-09, RF-17 y RNF-01 necesitan una transacción y un solo punto de autorización. Lo que cambia es la regla de fronteras entre módulos: con tres personas trabajando en paralelo es más fácil romperla, así que se revisa en cada PR.
2. El contrato del equipo usa `/api` en lugar de `/api/v1` y agrupa la autenticación en `/auth/register`, `/auth/login`, `/auth/me` y `/auth/logout` (decisión D-01).
3. El JWT lleva `exp` tomado de `JWT_EXPIRATION`, y además la sesión `sid` se valida en cada solicitud para cerrar sesión (RF-26-AC-5) y expirar por inactividad (RF-26-AC-6). Se implementa en S05-S06-A2; en S05-S06-A1 las rutas todavía no exigen token, como pide la actividad.
4. Para desarrollo, `docker compose` levanta PostgreSQL 16 y la API (tarea T-01 del Sprint 1). El esquema se crea con `esquema_bd.sql` al primer arranque del contenedor. Mailpit y el worker entran cuando se implementen correo y revisión de plazos.
5. El borrador había dejado fuera del nivel 3 dos piezas que el S04 de Ángel sí tenía: la cola de correos (outbox) y el módulo de reportes. Las recuperamos. La outbox entra como `servicios/notificaciones`, con la frontera del módulo de Notificaciones de Leonardo: los demás módulos le piden el correo, él lo escribe en la misma transacción que el cambio que lo provoca y el worker lo envía. `servicios/reportes` solo lee (Q-06).
6. Evidencias se queda dentro de `servicios/expediente`, no como módulo aparte como lo tenía Leonardo. Aceptar una evidencia y calificar el criterio cambian estados de las dos cosas en una sola transacción (RF-17, RF-27), y separarlas obligaría a coordinar dos módulos para una sola regla (Q-06).
7. Los archivos se suben a través de la API en multipart, como en los diseños de Ángel y Erick, no directo al bucket como se infiere del contrato de Leonardo. Así el servidor valida tamaño y formato (RF-06) sobre el archivo real y no sobre lo que declara el cliente (Q-02).

## Vista de contenedores (C4 nivel 2)

![Contenedores](imagenes/arquitectura_contenedores.png)

```plantuml
@startuml arquitectura_contenedores
!include <C4/C4_Container>
title SGPIS: contenedores (C4 nivel 2), acordado por el equipo 19
LAYOUT_TOP_DOWN()

Person(coord, "Coordinación AMPIP", "Catálogo, generaciones, parques, usuarios, asignaciones, fases, configuración y bitácora.")
Person(dg, "Director General AMPIP", "Firma el dictamen (RF-14).")
Person(appi, "APPI", "Autoevalúa y sube evidencias, a menudo desde el celular (RNF-09).")
Person(consultor, "Consultor", "Asignado: revisa, califica, recomienda y emite Opiniones. De comité: lectura temporal (RF-13).")
Person(corp, "Gerente corporativo", "Lectura del avance de sus parques (RF-23).")

System_Boundary(sgpis, "SGPIS") {
  Container(spa, "Aplicación web (SPA)", "React 18, TypeScript, Vite", "Formularios, tablas y gráficas. Token solo en memoria. No decide permisos.")
  Container(api, "API REST", "Python 3.12, FastAPI, SQLAlchemy 2.0, Pydantic v2", "Implementa openapi_equipo.yaml bajo /api. Único punto de autorización (RNF-01, RNF-02, RNF-04).")
  Container(worker, "Worker", "Python 3.12, misma imagen", "Plazos diarios a las 00:00 CDMX (RF-09, RF-30) y outbox de correo con 3 reintentos (RNF-12).")
  ContainerDb(db, "Base de datos", "PostgreSQL 16", "Esquema de esquema_bd.sql: dominio, sesiones, outbox y bitácora de solo append (RNF-03).")
  ContainerDb(objetos, "Almacenamiento de evidencias", "Bucket privado compatible con S3", "Archivos hasta el límite configurado (RF-06). Sin URL pública (RNF-15).")
}
System_Ext(correo, "Correo transaccional", "SMTP con TLS; Mailpit en desarrollo.")

Rel(coord, spa, "Usa", "HTTPS")
Rel(dg, spa, "Firma dictámenes", "HTTPS")
Rel(appi, spa, "Sube evidencias", "HTTPS")
Rel(consultor, spa, "Revisa y califica", "HTTPS")
Rel(corp, spa, "Consulta avance", "HTTPS")
Rel(spa, api, "JSON y multipart; Authorization: Bearer <JWT>", "HTTPS /api")
Rel(api, db, "SQL; sesión validada en cada solicitud; bitácora en la misma transacción", "TCP 5432")
Rel(api, objetos, "Guarda y lee archivos", "API S3")
Rel(worker, db, "Atrasos, outbox", "TCP 5432")
Rel(worker, correo, "Invitaciones, recuperación, avisos", "SMTP 587")
SHOW_LEGEND()
@enduml
```

## Vista de componentes de la API (C4 nivel 3)

![Componentes](imagenes/arquitectura_componentes.png)

```plantuml
@startuml arquitectura_componentes
!include <C4/C4_Component>
title SGPIS: componentes de la API (C4 nivel 3)
LAYOUT_TOP_DOWN()

Container(spa, "SPA", "React")
ContainerDb(db, "PostgreSQL 16", "esquema_bd.sql")

Container_Boundary(api, "API REST (backend/app)") {
  Component(routers, "routers/", "FastAPI APIRouter", "Un router por grupo de recursos del contrato. Solo traduce HTTP.")
  Component(esquemas, "esquemas/", "Pydantic v2, camelCase", "Request y response de openapi_equipo.yaml.")
  Component(errores, "errores.py", "Exception handlers", "Toda respuesta de error sale con el schema Error {codigo, mensaje, detalles}.")
  Component(auth, "auth/ (S05-S06-A2)", "Dependencias FastAPI", "Valida JWT y sesión sid; control de acceso por rol y por parque.")
  Component(m_cat, "servicios/catalogo", "Dominio", "Versiones, criterios, marcas O/R/NA (RF-01, RF-24, RF-25).")
  Component(m_org, "servicios/organizacion", "Dominio", "Generaciones, parques, tipo de PI, usuarios, asignaciones, contacto principal, fases, configuración (RF-02, RF-03, RF-10, RF-11, RF-28 a RF-32, RF-34).")
  Component(m_exp, "servicios/expediente", "Dominio", "Autoevaluación, evidencias y vínculos, calificación, plan de trabajo, análisis de riesgos, cumplimiento, recomendaciones (RF-04 a RF-09, RF-16, RF-17, RF-27, RF-36).")
  Component(m_dic, "servicios/dictamen", "Dominio", "Opiniones, Evaluación de Desempeño, comité y dictamen (RF-12 a RF-15, RF-33).")
  Component(m_rep, "servicios/reportes", "Solo lectura", "Reporte mensual para Dirección y vista del gerente corporativo (RF-21, RF-23).")
  Component(notif, "servicios/notificaciones", "Transversal", "Escribe en la outbox de correo dentro de la misma transacción; el worker la envía (RNF-12).")
  Component(bitacora, "servicios/bitacora", "Transversal", "Inserta registros en la misma transacción y los consulta (RF-35, RNF-03).")
  Component(modelos, "modelos/", "SQLAlchemy 2.0 ORM", "Mapeo 1:1 de las tablas de esquema_bd.sql. Un módulo no lee tablas de otro.")
}

Rel(spa, routers, "HTTPS")
Rel(routers, esquemas, "Valida con")
Rel(routers, auth, "Depende de")
Rel(routers, m_cat, "Llama")
Rel(routers, m_org, "Llama")
Rel(routers, m_exp, "Llama")
Rel(routers, m_dic, "Llama")
Rel(routers, m_rep, "Llama")
Rel(m_rep, m_exp, "Consulta cifras")
Rel(m_org, notif, "Invitaciones")
Rel(m_exp, notif, "Avisos de observación")
Rel(m_exp, m_cat, "Consulta marcas")
Rel(m_dic, m_exp, "Consulta estados y cumplimiento")
Rel(m_org, bitacora, "Registra")
Rel(m_exp, bitacora, "Registra")
Rel(m_cat, modelos, "Usa")
Rel(m_org, modelos, "Usa")
Rel(m_exp, modelos, "Usa")
Rel(m_dic, modelos, "Usa")
Rel(bitacora, modelos, "Usa")
Rel(notif, modelos, "Usa")
Rel(modelos, db, "SQL (psycopg 3)")
SHOW_LEGEND()
@enduml
```

## Entorno de desarrollo

| Servicio | Imagen o comando | Puerto | Nota |
|---|---|---|---|
| `db` | `postgres:16-alpine` | 5432 | Monta `backend/db/esquema_bd.sql` en `/docker-entrypoint-initdb.d/`; las tablas se crean al primer arranque. |
| `api` | `uvicorn app.main:app` | 8000 | Lee `DATABASE_URL` y, desde S05-S06-A2, `JWT_SECRET` y `JWT_EXPIRATION` del `.env`. El repo solo trae `.env.example`. |

Producción conserva el despliegue de S04_A1 de Ángel (`insumos/Angel_S04_A1_v2/diagrama_despliegue.puml`): un servidor con Docker Compose detrás de Caddy, que también sirve los archivos estáticos de la SPA (Q-05), bucket privado y monitoreo de `/api/salud` cada 5 minutos.

La base de datos de producción es PostgreSQL 16 gestionado por el proveedor, no un contenedor dentro del Compose como lo proponía Erick. Con el servicio gestionado, el respaldo diario y la retención de 30 días de RNF-13 se configuran en el proveedor; con la base en un contenedor tendríamos que escribir, programar y vigilar ese respaldo nosotros (Q-04). En desarrollo la base sí corre en el Compose.

Queda pendiente para el Sprint 2 lo que Ángel tenía en su despliegue y todavía no existe en el repositorio (Q-09):

- Integración continua en GitHub Actions: `ruff` y las pruebas de `backend/tests` contra un PostgreSQL de servicio.
- MinIO en el Compose de desarrollo, para probar la carga de evidencias contra un S3 local antes de tocar el bucket real.

## Reglas que el equipo se compromete a respetar

- El contrato manda. Un endpoint que no está en `openapi_equipo.yaml` no se programa; si hace falta, primero se cambia el contrato en un PR que revisan los otros dos.
- Las tablas salen de `esquema_bd.sql`, y los modelos ORM las reflejan sin agregar columnas por su cuenta. Un cambio de tabla actualiza en el mismo PR el SQL, el diagrama de clases y el contrato si toca un schema.
- Un módulo llama a los servicios de otro, nunca a sus modelos.
- Ningún secreto en el repositorio: `JWT_SECRET` y la contraseña de la base viven en `.env`, que está en `.gitignore`.
