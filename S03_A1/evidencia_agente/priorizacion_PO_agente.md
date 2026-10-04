# Salida del Agente 3: priorización del backlog como Product Owner

> Salida sin editar del agente en rol de Product Owner (prompt en `prompts_agentes.md`). La comparación con la priorización del equipo está en `priorizacion_comparada.md`.

## Método

Como Product Owner de SGPIS, prioricé las 22 historias con WSJF (Weighted Shortest Job First):

WSJF = (Valor de negocio + Criticidad en el tiempo + Reducción de riesgo / habilitación) ÷ Story points

Cada componente se calificó de 1 a 10:

- **Valor de negocio:** cuánto resuelve un problema actual de AMPIP, la APPI o el consultor descrito en el SRS (Excel, correo, carpetas sueltas, falta de visibilidad).
- **Criticidad en el tiempo:** qué tan pronto se necesita para operar la generación que arranca en febrero de 2027. Se tomó la prioridad del SRS (MVP feb-2027, 2027, Posterior) como referencia.
- **Reducción de riesgo / habilitación:** cuánto reduce riesgo técnico o de seguridad, o cuánto habilita otras historias.

Después del cálculo apliqué un ajuste por dependencias técnicas para que ninguna historia quede antes de otra que necesita para funcionar.

## Puntajes

| Historia | Valor | Criticidad | Riesgo / habilitación | SP | WSJF |
|---|---|---|---|---|---|
| HU-03 Cargar catálogo | 8 | 9 | 9 | 5 | 5.20 |
| HU-02 Generación y parques | 7 | 9 | 9 | 5 | 5.00 |
| HU-01 Iniciar sesión | 5 | 9 | 10 | 5 | 4.80 |
| HU-10 Análisis de riesgos | 5 | 4 | 5 | 3 | 4.67 |
| HU-14 Fechas del programa | 6 | 5 | 3 | 3 | 4.67 |
| HU-06 Autoevaluación | 9 | 8 | 6 | 5 | 4.60 |
| HU-12 Cálculo de cumplimiento | 9 | 7 | 6 | 5 | 4.40 |
| HU-05 Asignar consultor | 4 | 5 | 4 | 3 | 4.33 |
| HU-08 Revisar y observar evidencias | 8 | 7 | 5 | 5 | 4.00 |
| HU-09 Calificar criterios | 8 | 6 | 5 | 5 | 3.80 |
| HU-16 Bitácora | 6 | 5 | 8 | 5 | 3.80 |
| HU-17 Opinión de Cumplimiento | 8 | 4 | 4 | 5 | 3.20 |
| HU-07 Subir evidencias | 9 | 8 | 7 | 8 | 3.00 |
| HU-11 Plan de trabajo | 6 | 5 | 4 | 5 | 3.00 |
| HU-19 Dictamen | 9 | 3 | 3 | 5 | 3.00 |
| HU-20 Reporte mensual | 5 | 3 | 1 | 3 | 3.00 |
| HU-21 Vista corporativa | 3 | 2 | 1 | 2 | 3.00 |
| HU-04 Usuarios y roles | 6 | 9 | 8 | 8 | 2.88 |
| HU-15 Historial de parques | 6 | 4 | 3 | 5 | 2.60 |
| HU-13 Vista de avance AMPIP | 9 | 7 | 4 | 8 | 2.50 |
| HU-22 Avisos de vencimiento | 6 | 2 | 2 | 5 | 2.00 |
| HU-18 Sesión de comité | 7 | 3 | 4 | 8 | 1.75 |

## Orden final (después del ajuste por dependencias)

| # | Historia | WSJF | Ajuste |
|---|---|---|---|
| 1 | HU-03 Cargar catálogo | 5.20 | |
| 2 | HU-02 Generación y parques | 5.00 | |
| 3 | HU-01 Iniciar sesión | 4.80 | |
| 4 | HU-04 Usuarios y roles | 2.88 | Sube de 18 a 4: la autoevaluación y la carga de evidencias necesitan usuarios APPI. |
| 5 | HU-06 Autoevaluación | 4.60 | |
| 6 | HU-14 Fechas del programa | 4.67 | |
| 7 | HU-12 Cálculo de cumplimiento | 4.40 | |
| 8 | HU-05 Asignar consultor | 4.33 | |
| 9 | HU-07 Subir evidencias | 3.00 | Sube de 13 a 9: la revisión necesita evidencias cargadas. |
| 10 | HU-08 Revisar y observar evidencias | 4.00 | |
| 11 | HU-10 Análisis de riesgos | 4.67 | Baja de 4 a 11: se coloca justo antes de HU-09, que es la historia que lo usa. |
| 12 | HU-09 Calificar criterios | 3.80 | |
| 13 | HU-16 Bitácora | 3.80 | |
| 14 | HU-17 Opinión de Cumplimiento | 3.20 | |
| 15 | HU-11 Plan de trabajo | 3.00 | |
| 16 | HU-19 Dictamen | 3.00 | |
| 17 | HU-20 Reporte mensual | 3.00 | |
| 18 | HU-21 Vista corporativa | 3.00 | |
| 19 | HU-15 Historial de parques | 2.60 | |
| 20 | HU-13 Vista de avance AMPIP | 2.50 | |
| 21 | HU-22 Avisos de vencimiento | 2.00 | |
| 22 | HU-18 Sesión de comité | 1.75 | |

Los empates en 3.00 se resolvieron por valor de negocio.

## Por qué estas historias van al tope

1. **HU-03 Cargar catálogo.** Sin catálogo no hay criterios, y sin criterios no existe autoevaluación, evidencia ni cálculo. Es la base de datos de dominio de todo el sistema y tiene el WSJF más alto.
2. **HU-02 Generación y parques.** Cada criterio aplica según el tipo de PI del parque; sin parques dados de alta en una generación, el catálogo no se puede aplicar a nadie.
3. **HU-01 Iniciar sesión.** Es el punto de entrada y una condición de seguridad para manejar información sensible. Su valor de negocio directo es bajo, pero habilita todo lo demás.
4. **HU-04 Usuarios y roles.** Su WSJF es bajo por el tamaño, pero sin usuarios con rol APPI ni consultor el flujo central no se puede probar.
5. **HU-06 Autoevaluación.** Es el primer valor tangible para la APPI: deja de filtrar el checklist a mano. El SRS la marca como confirmada por el cliente real.

## Por qué estas historias van al fondo

1. **HU-18 Sesión de comité.** El comité ocurre al final del programa de diez meses. Es una historia grande (8 SP) con poca criticidad en el tiempo para el arranque de la generación.
2. **HU-22 Avisos de vencimiento.** El primer distintivo de la generación 2027 se otorga al final del programa y vence años después; el aviso no tiene uso durante el semestre.
3. **HU-13 Vista de avance AMPIP.** Tiene alto valor, pero es grande y depende de que existan datos de cumplimiento. Mientras tanto, AMPIP puede consultar el expediente de cada parque.
4. **HU-15 Historial de parques.** Aporta contexto, pero no es necesario para operar la generación en curso.
5. **HU-21 Vista corporativa.** Usuario ocasional de solo lectura; su valor es bajo frente al resto.

## Supuestos

- La capacidad del equipo y la duración de los sprints no se conocen; el orden no está agrupado por sprint.
- Los puntajes de valor se asignaron a partir de la prioridad del SRS y de los problemas descritos en `proyecto_base.md`; no se validaron con AMPIP.
- El ajuste por dependencias solo movió historias cuando una dependencia técnica impedía probar la siguiente.
