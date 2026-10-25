# Prompt de generación de la especificación (Parte 1)

Agente: Claude (Anthropic), sesión independiente. Insumos entregados (esta actividad se hizo antes que S04_A1, por eso no incluye los diagramas de clases ni de componentes; ver `decisiones_y_trazabilidad.md`, sección 1): `SRS_final.md` v1.4 (31 RF, 110 AC; su anexo trae la matriz RF ↔ caso de uso del diagrama de S02_A1) y `stack_decision.md` (S01_A2).

```text
Eres arquitecto de APIs. Diseña la API REST del backend de SGPIS (Sistema de Gestión
del Programa Parque Industrial Seguro, AMPIP). Backend: Python 3.12 + FastAPI,
PostgreSQL 16. Frontend: React (SPA) que consume esta API.

Insumos: el SRS (requerimientos funcionales con criterios Given-When-Then con ID
RF-XX-AC-Y, más la matriz de trazabilidad RF ↔ casos de uso) y la decisión de stack.

Genera una especificación OpenAPI 3.0.3 en YAML que incluya:
- Todos los endpoints agrupados por recurso (tags), mínimo 3 recursos.
- Métodos HTTP correctos (GET, POST, PUT, PATCH, DELETE).
- Códigos de respuesta apropiados por operación (200, 201, 400, 401, 403, 404, 422, 500).
- Esquemas de request body y response body en components/schemas.
- Seguridad con Bearer Token (JWT).
- En cada operación, la extensión x-acceptance-criteria con la lista de IDs de los
  criterios de aceptación del SRS que esa operación satisface.

Alcance: los RF con prioridad "MVP feb-2027" y "2027". Los RF con prioridad
"Posterior" quedan fuera.
```
