# Prompts de los agentes usados en S04-A2

Cada agente se corrió en una pasada separada, con su propio contexto. Las salidas sin editar están en esta carpeta. Las decisiones sobre esas salidas son mías y están en `revision_rest.md` y en `decisiones_y_trazabilidad.md`.

| Agente | Insumos | Salida |
|---|---|---|
| 1. Generador de la especificación | `S03_A1/SRS_equipo.md`, `S03_A2/tareas_tecnicas.md` | `openapi_v0.yaml` |
| 2. Revisor REST | `openapi_v0.yaml` (y el SRS solo para confirmar reglas) | `revision_rest_agente.md` |
| 3. Generador de diagramas de secuencia | `openapi.yaml` final, `S03_A2/tareas_tecnicas.md` | `../secuencia_flujo1.puml`, `../secuencia_flujo2.puml` |

## Agente 1. Generador de la especificación OpenAPI

```text
Eres arquitecto de APIs. Recibes SRS_equipo.md (SGPIS, 39 RF con criterios Given-When-Then)
y tareas_tecnicas.md del Sprint 1 (backend FastAPI + PostgreSQL + almacenamiento de objetos).

Genera una especificación OpenAPI 3.0.3 en YAML para la API del backend:
1. Todos los endpoints agrupados por recurso (tags), mínimo 3 recursos.
2. Métodos HTTP correctos y códigos de respuesta por operación (200, 201, 400, 401, 403, 404,
   422, 500, y los que hagan falta).
3. Esquemas de request y response en components/schemas.
4. Seguridad Bearer con JWT, global; los endpoints públicos con security: [].
5. En cada operación, la extensión x-acceptance-criteria con los IDs del SRS que satisface.
6. Excluye los RF con prioridad "Posterior".

Reglas:
- La API va en español (rutas y campos), como el SRS.
- Respeta las rutas que el SRS o las tareas del Sprint 1 ya nombran.
- No inventes reglas de negocio que no estén en el SRS.
```

## Agente 2. Revisor REST

```text
Eres revisor de diseño de APIs REST. Revisa openapi_v0.yaml (API de SGPIS). El SRS que la
origina es SRS_equipo.md; consúltalo solo para confirmar una regla de negocio. La API está en
español a propósito; no lo marques como problema.

Evalúa contra:
1. Uso correcto de verbos HTTP según la semántica de cada operación.
2. Naming: sustantivos, plural para colecciones, lowercase, kebab-case, anidación razonable.
3. Idempotencia: PUT/DELETE/PATCH que no lo son, POST que deberían ser PUT por clave natural
   (y al revés).
4. Códigos de estado: 200/201/202/204, Location en 201, errores 400/401/403/404/409/422/423/500,
   y si el esquema de error alcanza.
5. Cualquier problema que impida implementar el contrato tal cual.

No edites el YAML. Entrega una tabla de hallazgos (ID, principio, ruta, problema,
recomendación concreta, severidad) y una sección breve "Lo que está bien".
Prioriza hallazgos reales sobre cantidad.
```

## Agente 3. Diagramas de secuencia

```text
Con openapi.yaml (versión corregida) genera dos diagramas de secuencia UML en PlantUML para
SGPIS. Participantes obligatorios: Cliente (Browser), Frontend (React SPA),
Backend API (FastAPI /api/v1) y Base de datos (PostgreSQL); agrega el almacenamiento de objetos
donde se suben archivos.

Flujo 1: inicio de sesión (POST /sesiones con sus tres resultados: bloqueo 423, credenciales
incorrectas 401, éxito 201), una solicitud protegida a un parque ajeno (401 por sesión vencida,
403 con registro en bitácora, 200) y el cierre de sesión (DELETE /sesiones/actual).

Flujo 2: la APPI sube varias evidencias (POST /parques/{parque_id}/evidencias con éxito parcial),
el consultor acepta una (PATCH /evidencias/{evidencia_id}) y califica el criterio
(POST .../calificaciones) con el bloqueo de RF-17 si no hay análisis de riesgos vigente.

Usa exactamente las rutas, códigos y mensajes del contrato. Marca en cada bloque los IDs de
los criterios que ilustra.
```

Los dos diagramas se revisaron contra el contrato después de las correcciones de la Parte 2. Un ajuste: la respuesta de `POST .../calificaciones` ya no muestra `Location`, porque las calificaciones no tienen GET individual (hallazgo R-11).
