# Priorización comparada: agente Product Owner y equipo

**Entrada:** `backlog_completo.md` (22 historias, 111 story points) y `SRS_equipo.md`
**Priorización del agente, sin editar:** `evidencia_agente/priorizacion_PO_agente.md`

## 1. Los dos métodos

El agente usó WSJF: sumó valor de negocio, criticidad en el tiempo y reducción de riesgo, cada uno de 1 a 10, dividió entre los story points y después movió tres historias por dependencias técnicas.

Yo no puse puntajes. Ordené con dos preguntas, en este orden: qué necesita existir para que la siguiente historia se pueda probar de punta a punta, y qué le pidió el cliente real de AMPIP para el primer mes. Cuando una historia no dependía de otra y el cliente no la mencionó, decidí por el uso diario: lo que Coordinación AMPIP, la APPI o el consultor van a abrir todos los días va antes que lo que se abre una vez al año.

## 2. Comparación

| Historia | Agente | Equipo | Diferencia |
|---|---|---|---|
| HU-01 Iniciar sesión | 3 | 1 | +2 |
| HU-02 Generación y parques | 2 | 2 | 0 |
| HU-03 Cargar catálogo | 1 | 3 | −2 |
| HU-04 Usuarios y roles | 4 | 4 | 0 |
| HU-06 Autoevaluación | 5 | 5 | 0 |
| HU-15 Historial de parques | 19 | 6 | +13 |
| HU-14 Fechas del programa | 6 | 7 | −1 |
| HU-05 Asignar consultor | 8 | 8 | 0 |
| HU-07 Subir evidencias | 9 | 9 | 0 |
| HU-08 Revisar y observar | 10 | 10 | 0 |
| HU-10 Análisis de riesgos | 11 | 11 | 0 |
| HU-09 Calificar criterios | 12 | 12 | 0 |
| HU-12 Cálculo de cumplimiento | 7 | 13 | −6 |
| HU-13 Vista de avance AMPIP | 20 | 14 | +6 |
| HU-11 Plan de trabajo | 15 | 15 | 0 |
| HU-17 Opinión de Cumplimiento | 14 | 16 | −2 |
| HU-18 Sesión de comité | 22 | 17 | +5 |
| HU-19 Dictamen | 16 | 18 | −2 |
| HU-16 Bitácora (consulta) | 13 | 19 | −6 |
| HU-20 Reporte mensual | 17 | 20 | −3 |
| HU-22 Avisos de vencimiento | 21 | 21 | 0 |
| HU-21 Vista corporativa | 18 | 22 | −4 |

La columna "Diferencia" es cuántos lugares sube (+) o baja (−) la historia en mi orden respecto al del agente.

## 3. Dónde coincidimos

Coincidimos en más de lo que esperaba. Las cinco primeras posiciones tienen las mismas historias, solo en distinto orden. El núcleo de la épica E2 (asignar consultor, subir, revisar, análisis de riesgos y calificar) quedó en las mismas posiciones, de la 8 a la 12, y en el mismo orden. Diez historias quedaron en el mismo lugar exacto.

También coincidimos en mandar al fondo los avisos de vencimiento. El argumento del agente es correcto: ningún parque de la generación 2027 tiene un distintivo por vencer durante el semestre.

El ajuste por dependencias del agente atrapó dos errores reales que su propia fórmula había cometido. WSJF dejaba a HU-04 (usuarios) en el lugar 18 y a HU-07 (subir evidencias) en el 13, después de revisar y calificar. El agente las subió.

## 4. Dónde diferimos y por qué

### Iniciar sesión antes que el catálogo

El agente puso el catálogo primero porque tiene el WSJF más alto. RF-01-AC-1 empieza con "Coordinación AMPIP inició sesión con ese rol": la carga del catálogo no se puede probar sin sesión ni roles. Es una dependencia que el ajuste del agente no detectó porque estaba escrita dentro del AC y no en la lista de RF de la historia.

### Historial de parques: del 19 al 6

Es la diferencia más grande y la más importante. El miembro del comité de AMPIP, cuando le pregunté qué era indispensable desde el primer mes, contestó con dos cosas: el historial de todos los parques con programa y la autoevaluación (P3, Parte C). El agente le dio criticidad 4 de 10 y lo justificó diciendo que aporta contexto pero no hace falta para operar la generación en curso. Desde la lógica del sistema tiene sentido; desde la del cliente, no. Además el historial casi no depende de las otras historias: el alta de un parque histórico con datos mínimos (RF-31-AC-2) se puede entregar antes de que exista una sola evidencia, y le da a AMPIP algo útil desde el primer sprint.

### Cálculo de cumplimiento: del 7 al 13

El agente lo puso antes de que exista la carga de evidencias o la calificación de criterios. En ese punto el cálculo solo produce 0 % para todos los parques y no se puede validar contra un caso real. Lo dejé inmediatamente después de calificar criterios (HU-09), que es cuando los porcentajes empiezan a significar algo.

### Vista de avance de AMPIP: del 20 al 14

WSJF divide entre el tamaño, así que castiga a toda historia de 8 puntos sin importar su valor. El agente le dio valor 9 y aun así la mandó al lugar 20. Es la pantalla que Coordinación AMPIP va a abrir todos los días para saber en qué fase va cada parque, que hoy reconstruye con Excel y correo. La puse justo después del cálculo de cumplimiento, porque necesita esas cifras para mostrar algo.

### Comité antes que dictamen

El agente dejó el dictamen en el lugar 16 y la sesión de comité en el 22. Es un error de dependencia: el dictamen se captura dentro de la sesión de comité, y la validación del expediente (RF-15) ocurre al abrir esa sesión. Con el orden del agente, el dictamen se tendría que probar sin comité y sin la validación que lo protege. El argumento del agente para mandar el comité al fondo ("ocurre al final del programa") aplica igual al dictamen, así que los dos van juntos, en el orden en que ocurren.

### Bitácora: del 13 al 19

El agente le dio la calificación más alta de reducción de riesgo y la subió. Estoy de acuerdo en que el riesgo existe: son análisis de riesgos, planes de contingencia y ubicación de cámaras. Pero ese riesgo lo cubre el registro en bitácora, que está en la definición de terminado de todas las historias desde el primer sprint. HU-16 es solo la pantalla de consulta con filtros, y esa puede esperar a que haya meses de operación que consultar. El agente trató el registro y la consulta como una sola cosa.

### Vista corporativa al último

Diferencia menor. El agente desempató historias en 3.00 por valor de negocio, y la vista corporativa quedó arriba del historial por ese desempate. Para mí es la historia de menor uso del backlog.

## 5. Qué saco de la comparación

WSJF es un buen método cuando los números que entran están bien calibrados. Aquí el juicio quedó escondido en los puntajes de 1 a 10, y el agente los asignó leyendo las etiquetas de prioridad del SRS. Con esa información no podía saber que una frase del cliente real pesa más que una etiqueta "MVP", ni que el cálculo de cumplimiento no vale nada sin datos calificados. Donde el orden dependía de leer un criterio de aceptación con cuidado (sesión antes de catálogo, comité antes de dictamen), el agente se equivocó; donde dependía de la lista de RF de la historia, acertó.

El orden de la columna "Equipo" es el que proponemos para la columna Backlog del tablero de GitHub Projects. Se revisa con el equipo al planear el primer sprint.
