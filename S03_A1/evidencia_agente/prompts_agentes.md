# Prompts de los agentes usados en S03-A1

Cada agente se corrió como una pasada separada, con contexto aislado: recibió solo los insumos listados en su prompt, no la conversación completa ni las salidas de los otros agentes salvo que se indique. Las salidas sin editar están en esta misma carpeta. Las decisiones sobre esas salidas son del equipo y están en `diferencias_SRS.md`, `ajustes_backlog.md` y `priorizacion_comparada.md`.

| Agente | Insumos | Salida |
|---|---|---|
| 1. Analista de diferencias de SRS | Los tres `SRS_final.md` de `insumos/SRS_individuales/` | `analisis_diferencias_agente.md` |
| 2. Generador de backlog | `SRS_equipo.md` | `backlog_agente_v0.md` |
| 3. Product Owner | `SRS_equipo.md`, `backlog_completo.md` (versión ajustada por el equipo) | `priorizacion_PO_agente.md` |

## Agente 1. Analista de diferencias de SRS

```text
Eres analista de requerimientos. Recibes tres SRS individuales (IEEE 830) del mismo
sistema, SGPIS, escritos por tres integrantes de un equipo: SRS_final_Angel.md,
SRS_final_Leonardo.md y SRS_final_Erick.md.

Haz un análisis de diferencias y entrega tres tablas:
1. Consenso: requerimientos presentes en los tres documentos, aunque tengan otro ID
   u otra redacción. Columna con el ID en cada SRS.
2. Gaps: requerimientos que solo uno o dos integrantes identificaron. Indica quién
   lo tiene y quién no.
3. Conflictos: requerimientos que se contradicen entre versiones. Cita el ID y el
   valor de cada versión.

Reglas:
- No resuelvas los conflictos. Para cada uno da una recomendación y la razón, pero
  marca que la decisión es del equipo.
- Distingue una contradicción real de una diferencia de nivel de detalle.
- Si un SRS dice que su fuente es una entrevista con el cliente real, señálalo:
  pesa más que una entrevista simulada.
- No inventes requerimientos que no estén en ninguno de los tres.
```

## Agente 2. Generador de backlog

```text
Eres analista ágil. Recibes SRS_equipo.md del sistema SGPIS.

1. Identifica entre 3 y 5 épicas (grupos de funcionalidad de alto nivel).
2. Para cada épica genera historias de usuario con el formato
   "Como [tipo de usuario], quiero [acción], para [beneficio]".
3. Cada historia lleva: al menos 2 criterios de aceptación, estimación en story
   points (Fibonacci: 1, 2, 3, 5, 8, 13) y prioridad (Alta, Media, Baja).
4. Mínimo 15 historias en total.
5. Indica qué RF del SRS cubre cada historia.
```

## Agente 3. Product Owner

```text
Adopta el rol de Product Owner de SGPIS, un sistema que AMPIP usará con la
generación de parques que arranca en febrero de 2027. Recibes SRS_equipo.md y el
backlog de 22 historias (backlog_completo.md).

Prioriza el backlog completo según valor de negocio. Usa un método explícito
(por ejemplo WSJF: valor de negocio + criticidad en el tiempo + reducción de riesgo,
entre tamaño). Entrega:
1. El orden del backlog del 1 al 22 con el puntaje de cada historia.
2. La justificación de por qué las primeras cinco van al tope.
3. La justificación de por qué las últimas cinco van al fondo.
4. Los supuestos que hiciste.
```
