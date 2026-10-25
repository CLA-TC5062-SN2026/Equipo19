# Prompt del agente usado en S04-A1

El agente se corrió una sola vez, con contexto aislado: recibió el SRS de equipo y los documentos del Sprint 1, y no vio el contrato de API de S04-A2 ni mi borrador de diagramas. Sus salidas, sin editar, están en esta carpeta. Las decisiones sobre esas salidas son mías y están en `../decision_arquitectonica.md`, sección 5.

| Insumos | Salidas |
|---|---|
| `S03_A1/SRS_equipo.md`, `S03_A2/tareas_tecnicas.md`, `S03_A2/sprint1_planning.md` | `analisis_estilos_agente.md`, `diagrama_clases_agente.puml` y su imagen `diagrama_clases_agente.png` (renderizada por mí con PlantUML; el agente no la renderizó) |

```text
Eres arquitecto de software. Trabajas sobre SGPIS (Sistema de Gestión del Programa Parque
Industrial Seguro, de AMPIP). Insumos (léelos completos): SRS_equipo.md (39 RF, 18 RNF, 16 RD,
con criterios Given-When-Then), tareas_tecnicas.md y sprint1_planning.md (Sprint 1 ya en
curso; ahí está el stack que el equipo ya eligió).

Contexto del equipo: tres estudiantes, 12 semanas, ~8.5 h/semana cada uno; la actividad se
evalúa de forma individual ("tú, un desarrollador").

Entrega DOS archivos, en español, sin rodeos:

1. analisis_estilos_agente.md
   - Extrae los RNF que de verdad condicionan la arquitectura (cita IDs) y explica por qué
     cada uno pesa.
   - Propón al menos 3 estilos alternativos (por ejemplo: monolito en capas, monolito
     modular, microservicios, cliente-servidor con MVC, event-driven/serverless). Para cada
     uno: descripción breve aplicada a SGPIS y trade-offs concretos en escalabilidad,
     mantenibilidad, complejidad de implementación y adecuación al equipo. Termina con una
     tabla comparativa y tu recomendación justificada.
   - Lista también las preguntas o riesgos que no puedes resolver con el SRS.

2. diagrama_clases_agente.puml
   - Diagrama de clases UML del dominio en PlantUML, con las entidades principales que
     identifiques en el SRS, atributos principales con tipo, relaciones (asociación,
     composición, agregación, herencia donde corresponda) y multiplicidades en ambos
     extremos. Usa enums donde el SRS define listas cerradas.
   - Al inicio, en comentarios, explica brevemente los supuestos que tomaste.
```

Los diagramas de componentes (C4) y de despliegue los generé con Claude Code en esta misma sesión, tomando como base la recomendación del agente y el stack del Sprint 1, y los revisé contra los RNF que cita el ADR.
