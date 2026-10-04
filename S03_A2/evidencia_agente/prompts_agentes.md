# Prompts de los agentes usados en S03-A2

Igual que en S03-A1, cada agente se corrió como una pasada separada, con contexto aislado. Las salidas sin editar están en esta carpeta; las decisiones sobre ellas están en `sprint1_planning.md`, `tareas_tecnicas.md` y `definition_of_done.md`.

| Agente | Insumos | Salida |
|---|---|---|
| 1. Facilitador del Sprint Planning | `backlog_completo.md`, `priorizacion_comparada.md` (S03-A1) | `sprint_goal_agente.md` |
| 2. Descomposición técnica | Sprint Goal y selección ajustados por el equipo, `SRS_equipo.md`, `stack_decision.md` | `descomposicion_agente.md` |
| 3. Definition of Done | `backlog_completo.md`, `SRS_equipo.md` | `dod_agente.md` |

## Agente 1. Facilitador del Sprint Planning

```text
Actúa como facilitador del Sprint Planning del Sprint 1 de SGPIS. Recibes el Product
Backlog completo (22 historias, story points en Fibonacci) y el orden de prioridad
acordado por el equipo.

Contexto: equipo de 3 integrantes, sprint de 2 semanas, cada integrante dedica de 8 a
9 horas por semana al proyecto.

1. Propón un Sprint Goal concreto, medible y alcanzable en el sprint.
2. Estima la capacidad del equipo en story points y explica cómo la calculaste.
3. Selecciona las historias del Sprint Backlog y justifica cada una.
4. Señala riesgos del sprint.
```

## Agente 2. Descomposición técnica

```text
Eres tech lead de SGPIS. Stack: Python 3.12, FastAPI, SQLAlchemy 2.0 + Alembic,
PostgreSQL 16 en Docker, pytest + httpx, uv; React + Vite en frontend.

El equipo acordó para el Sprint 1: un habilitador técnico (esqueleto del backend) y la
historia HU-01 (autenticación). Recibes los criterios de aceptación RF-26-AC-1 a AC-6.

Descompón cada elemento en tareas técnicas. Cada tarea debe:
- ser completable en 4 horas o menos,
- tener un rol responsable (backend dev, frontend dev, QA, DevOps),
- tener un criterio de done claro.
```

## Agente 3. Definition of Done

```text
Propón una Definition of Done para SGPIS: la lista de condiciones que una historia de
usuario debe cumplir para considerarse terminada. Considera el stack (FastAPI,
PostgreSQL, React) y que el sistema maneja información de seguridad de parques
industriales.
```
