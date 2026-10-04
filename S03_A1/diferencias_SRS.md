# Diferencias entre los SRS individuales y consolidación del SRS de equipo

**Proyecto:** SGPIS (AMPIP), equipo Gpo 10, TC5062
**Insumos:** `insumos/SRS_individuales/SRS_final_Angel.md`, `SRS_final_Leonardo.md`, `SRS_final_Erick.md`
**Resultado:** `SRS_equipo.md` versión 2.0 (39 RF, 18 RNF, 16 RD, 150 AC)
**Análisis del agente, sin editar:** `evidencia_agente/analisis_diferencias_agente.md`
**Abreviaturas:** en las tablas, A es el SRS de Leonardo Cossío y B el de Erick Ramírez; SRS-A y SRS-B son los mismos documentos en las citas del SRS de equipo.

## 1. Cómo se hizo

Juntamos los tres `SRS_final.md` de S02-A1 y se los dimos al agente analista de diferencias con un prompt que le prohibía resolver conflictos (el prompt está en `evidencia_agente/prompts_agentes.md`). El agente entregó tres tablas: 17 requerimientos en consenso, los gaps de cada integrante y 19 conflictos con una recomendación para cada uno.

Las recomendaciones del agente fueron el punto de partida de la discusión. En cinco conflictos (C-03, C-15, C-17, C-19 y la parte de Evaluación de Desempeño de C-07) el agente no recomendó nada o recomendó algo que cambiamos; la sección 4 explica por qué.

Tomamos como base el SRS de Ángel por tres razones. Es el único con criterios de aceptación escritos por RF contra un endpoint, un mensaje o una cifra concreta, que es lo que vamos a necesitar para las pruebas. Ya estaba mapeado al diagrama de casos de uso. Y es el único que incorpora la entrevista con el cliente real de AMPIP (Parte C); Erick adoptó esa misma Parte C en su transcript y Leonardo no la usó. Tomar esa base no significa aceptar todo lo que trae: la tabla de conflictos registra dónde ganó la versión de Leonardo o la de Erick.

Para no romper la trazabilidad, ningún ID del SRS de Ángel cambió de significado. Lo nuevo entró de dos formas: criterios de aceptación agregados al final de un RF existente (RF-01-AC-5, RF-05-AC-5 a AC-10, RF-06-AC-6 y AC-7, RF-08-AC-4 y AC-5, RF-11-AC-5 y AC-6, RF-19-AC-4 y AC-5) y RF, RNF y RD nuevos con número consecutivo (RF-32 a RF-39, RNF-15 a RNF-18, RD-14 a RD-16). Cada AC agregado cita entre paréntesis el ID original del SRS de donde salió.

## 2. Qué aportó cada integrante

| Integrante | Aporte al SRS de equipo |
|---|---|
| Ángel Kociankowski | Estructura base y numeración (RF-01 a RF-31, RNF-01 a RNF-14, RD-01 a RD-13, 110 AC). Única entrevista con el cliente real (Parte C), de donde salen el dictamen binario (RD-09), las fechas de término y actualización con atraso (RF-30) y el historial de parques (RF-31). Separación entre estado de la evidencia y estado de calificación del criterio (RF-27). Reglas del dominio que solo conoce alguien que trabaja en el programa: generación, comité con consultor de comité, firma del Director General, análisis de riesgos como candado de los estándares 2, 3 y 7, política de seguridad como precondición de las Opiniones, restricción de evidencias de seguridad para Coordinación AMPIP. RNF con métrica y forma de verificación. |
| Leonardo Cossío | Gestión explícita de fases con bloqueo de avance y excepción de AMPIP (base de RF-32). Evaluación de Desempeño con folio (RF-33). Cumplimiento de recomendados por separado y cálculo global por suma de criterios (RF-08-AC-4 y AC-5). Metadatos mínimos de la evidencia (RF-05-AC-5). Catálogo con versiones anteriores conservadas en solo lectura (RF-01-AC-5). Plazos de aviso configurables y sin duplicados (RF-19-AC-4 y AC-5). Lista de eventos de bitácora, incluidos intentos de acceso denegados (RF-35). Cifrado en tránsito y en reposo (RNF-15). Tiempos de respuesta de consultas y tablero (RNF-16, RNF-17). Carga sin bloquear la pantalla (RNF-18). Matriz de permisos por rol, que se usará como insumo para el diseño de API. |
| Erick Ramírez | Varios usuarios APPI con un contacto principal (RF-34). Recomendaciones del consultor separadas de las observaciones (RF-36). Visita de validación con hallazgos (RF-37). Estados del distintivo, solicitud de renovación y prórroga (RF-38, RD-16). Avisos de documentos críticos (RF-39). Evidencia vinculada a varios criterios (RF-05-AC-7), eliminación lógica (RF-05-AC-9) y carga de varios archivos (RF-05-AC-8). Motivo obligatorio en el cambio de tipo de PI (RF-11-AC-5). Bitácora de consultas y descargas, y bitácora consultable solo por AMPIP (RF-35). Trazabilidad de decisiones (RD-14) y regla de evidencia suficiente (RD-15). Capacidad de 100 a 200 parques como cota de prueba (RNF-10). Una lista honesta de pendientes de validación, que pasó casi completa a "Supuestos y pendientes con el cliente". |

## 3. Consenso

Los 17 requerimientos que aparecen en los tres SRS (tabla 1 del análisis del agente) entraron al SRS de equipo con el ID y la redacción de la base. En ninguno de ellos había diferencia de fondo, solo de detalle, y el detalle mayor estaba en la base. Los tres coincidimos en lo que define al sistema: catálogo O/R/NA por cuatro tipos de PI, autoevaluación filtrada, evidencias con revisión y versiones, recálculo al cambiar el tipo de PI, vista de cartera, aislamiento entre parques, bitácora no modificable, Opinión del consultor y dictamen con condiciones previas.

## 4. Resolución de conflictos

La columna "Ratificado" se marca en la sesión de equipo en que se revisó la propuesta. Una resolución sin marca sigue abierta y no se implementa.

| ID | Tema | Versiones | Resolución | Razón | Ratificado |
|---|---|---|---|---|---|
| C-01 | Quién revisa evidencias | Ángel y A: consultor. B: evaluador de AMPIP; el consultor solo recomienda. | El consultor asignado revisa y califica. No hay rol de evaluador de AMPIP. Las recomendaciones de B se conservan como RF-36. | El cliente real habló de "un dictamen del consultor dando el visto bueno" (P2, Parte C). Un rol interno de revisión no aparece en ninguna fuente de AMPIP. | [ ] |
| C-02 | Estados de evidencia | Ángel: enviada, observada, aceptada, más estado del criterio. A: pendiente, enviada, observada, aceptada. B: aprobado, rechazado, observado. | Modelo de Ángel (RF-05, RF-27). El "pendiente" de A es el estado del criterio sin evidencia. El "rechazado" de B queda como "observada", porque la APPI siempre puede subir otra versión. | Separar evidencia y criterio permite que un criterio tenga varias evidencias en distintos estados, que es como trabaja el consultor. | [ ] |
| C-03 | Coordinación AMPIP ve el contenido de evidencias de seguridad | Ángel: no, solo el estado y las administrativas. A y B: sí. | Se mantiene la versión de Ángel (RF-07, RNF-02). | Análisis de riesgos, plan de contingencia y ubicación de cámaras exponen al parque si se filtran. Coordinación no necesita el contenido para administrar el programa; quien lo evalúa es el consultor. El agente dejó esta decisión al equipo y advirtió que era una decisión que solo había tomado Ángel. | [ ] |
| C-04 | Quién cambia el tipo de PI | Ángel: Coordinación. A: usuario autorizado. B: la APPI solicita y AMPIP autoriza. | Coordinación AMPIP lo ejecuta con motivo obligatorio (RF-11-AC-5). La solicitud en línea de la APPI queda fuera del semestre. | Toma de B lo importante (motivo, aprobador y fecha en el historial) sin construir un segundo flujo de aprobación en 12 semanas. | [ ] |
| C-05 | Tamaño máximo de archivo | Ángel: 100 MB. A: parametrizable. B: 50 MB. | Parametrizable por Coordinación, valor inicial 100 MB, máximo configurable 100 MB (RF-06, AC-6 y AC-7). | Ningún valor viene de AMPIP. Parametrizar cuesta poco y deja a AMPIP bajar a 50 MB si el almacenamiento sale caro. | [ ] |
| C-06 | Video como evidencia | Ángel y B: fuera. A: requerido. | Fuera (RF-06-AC-4). La evidencia de CCTV se sube como foto o captura con fecha visible. | Así la acepta hoy el consultor (P3, Parte B), y el video multiplica el costo de almacenamiento de una asociación civil (RD-12). | [ ] |
| C-07 | Condiciones para "otorgar" | Ángel: autoevaluación revisada, Opinión final favorable y 100 % de O. A: dos Opiniones, Evaluación de Desempeño y mínimos de AMPIP. B: autoevaluación terminada, O cumplidos, hallazgos cerrados y visto bueno. | Se mantiene RD-09 de Ángel. La Evaluación de Desempeño se registra (RF-33) y no es condición por ahora. Los hallazgos cerrados de B se vuelven condición solo cuando entren las visitas (RF-37, posterior). | RD-09 sale de la Parte C. Las tres versiones coinciden en lo central: sin autoevaluación terminada y sin visto bueno del consultor no hay distintivo. | [ ] |
| C-08 | Quién decide el dictamen | Ángel: el comité captura y el Director General firma. A: no lo define. B: AMPIP registra. | Versión de Ángel (RF-14). | Es la única que define el momento en que se valida la regla de "otorgar". | [ ] |
| C-09 | Plazos de aviso de vencimiento | Ángel: 6 y 3 meses. A: configurable. B: 90, 60 y 30 días. | Configurables; 6 y 3 meses como valores iniciales (RF-19-AC-4). Sin duplicados (RF-19-AC-5). | Ninguna cifra viene del cliente real. Con plazos configurables, AMPIP puede poner los de B sin cambiar código. | [ ] |
| C-10 | Vigencia del distintivo | Ángel: 3 años. A: parametrizable. B: pendiente. | Parametrizable, valor inicial 3 años (RD-08). | Los 3 años vienen de la entrevista simulada; el cliente real no los confirmó. | [ ] |
| C-11 | Cifras de cumplimiento | Ángel: % de O y avance general O+R. A: % de O y % de R. B: sin fórmula. | Tres cifras: obligatorios, recomendados y avance general, con el global calculado sobre la suma de criterios (RF-08-AC-4 y AC-5). | No se contradicen, se complementan. El % de O decide el dictamen; los otros dos informan. | [ ] |
| C-12 | NA a solicitud de la APPI | Ángel y A: NA solo del catálogo. B: la APPI puede pedirlo con justificación. | NA solo del catálogo (RF-04-AC-2). La excepción queda en pendientes. | B mismo lo marcó como pendiente de validar. Abrirlo sin confirmación permite a un parque quitarse obligatorios. | [ ] |
| C-13 | Alta de parque | Ángel y A: Coordinación AMPIP. B: la APPI se registra y AMPIP acepta o rechaza. | Coordinación AMPIP da de alta a partir de la carta de inscripción. La solicitud en línea queda fuera del semestre. | El alta ocurre una vez por parque y por generación; un flujo de solicitud no paga su costo en el MVP. | [ ] |
| C-14 | Versiones de catálogo | Ángel: una activa por generación. A: varias versiones con validación y consulta histórica. | Una activa por generación; las anteriores en solo lectura (RF-01-AC-5). La comparación entre versiones sigue fuera. | Conserva lo que A pedía para la trazabilidad (RN-14 de A) sin construir comparación de versiones. | [ ] |
| C-15 | Fases del programa | Ángel: 9. A: 7. B: secuencia por validar. | Las 9 fases de Ángel, guardadas como datos y no en código (RF-32). | Las 9 incluyen las 7 de A y separan la Opinión intermedia de la final y el dictamen, que en el sistema son eventos distintos. Guardarlas como datos atiende la duda de B. | [ ] |
| C-16 | Rendimiento | Ángel: 2 s en lista de evidencias, 1 s en confirmación de carga. A: 3 s en consultas, 5 s en tablero. B: sin cifra. | Se combinan: RNF-06 y RNF-07 de Ángel más RNF-16 y RNF-17 de A. Todas marcadas como propuestas del equipo. | No se contradicen; miden cosas distintas. B tenía razón en que ninguna viene de AMPIP, y así quedó escrito. | [ ] |
| C-17 | Capacidad | Ángel: 41 a 80 parques. B: 100 a 200. | Diseño y métrica para 80 parques; prueba de humo con 200 (RNF-10). | El programa tiene hoy alrededor de 41 parques y crece hacia 70 u 80. Probar con 200 cuesta poco y cubre la estimación de B. | [ ] |
| C-18 | Retención de evidencias | Ángel: 6 años. A y B: pendiente. | 6 años como propuesta (RNF-14), pendiente de AMPIP. | Hace falta una cifra para escribir la prueba de depuración. | [ ] |
| C-19 | Una evidencia para varios criterios | Ángel: una por criterio. A: varias por criterio. B: una vinculada a varios. | Un archivo se puede vincular a varios criterios y cada vínculo tiene su propio estado de revisión (RF-05-AC-7). | El Reglamento Interno sustenta varios criterios. Si el estado viviera en el archivo, aceptarlo para un criterio lo aceptaría para todos. | [ ] |

## 5. Gaps no adoptados

| Gap | Origen | Decisión |
|---|---|---|
| Solicitud de incorporación con aceptación o rechazo en línea | SRS-B RF-02 | Fuera del semestre (C-13). |
| Solicitud de cambio de tipo de PI por la APPI | SRS-B RF-10-AC-1/AC-2 | Fuera del semestre (C-04); el motivo sí entró. |
| Excepción de NA con justificación | SRS-B RF-04-AC-3, RD-06 | Pendiente con AMPIP (C-12). |
| Respuesta en texto de la APPI a una observación, con cierre por AMPIP | SRS-B RF-07 | No entra como RF. La APPI responde subiendo una versión nueva (RF-05-AC-4) y el consultor decide; un hilo de mensajes por observación se evalúa después del MVP. |
| Contenido mínimo del aviso de vencimiento (parque, fecha, días restantes, estado) | SRS-A RF-20 | Se usa como contenido del aviso al diseñar RF-19; no se escribió como AC. |
| Reglas de negocio RN-01 a RN-20 | SRS-A sección 6 | Repiten RD y RF ya presentes; no se copiaron como sección aparte. |
| Vista de expediente con "siguiente acción" | SRS-B RNF-07 | Se toma como criterio de diseño de la pantalla de expediente; no tiene métrica verificable. |

## 6. Mapa de IDs individuales a IDs del SRS de equipo

Sirve para que cada integrante encuentre dónde quedó lo que escribió.

| SRS individual | ID original | ID en `SRS_equipo.md` |
|---|---|---|
| A | RF-01, RF-02 | RF-32 (fases), RF-14 (otorgamiento) |
| A | RF-03 | RF-04 |
| A | RF-04, RF-05 | RF-05 (AC-5, AC-8), RF-06 |
| A | RF-06 a RF-09 | RF-05, RF-27, RF-05-AC-6, RF-05-AC-10 |
| A | RF-10 a RF-13 | RF-11 (AC-4 a AC-6), RF-01 |
| A | RF-14 a RF-16 | RF-08 (AC-3 a AC-5), RD-01, RD-02 |
| A | RF-17 | RF-07, RF-32, RF-30 |
| A | RF-18 | RF-10, RNF-01 |
| A | RF-19 a RF-21 | RF-19 (AC-4, AC-5) |
| A | RF-22 | RF-35 |
| A | RF-23 | RF-01-AC-5, RF-02, RF-10, RF-29 |
| A | RF-24 | RF-12, RF-33 |
| A | RNF-01 a RNF-09 | RF-03, RNF-01, RNF-15, RNF-03, 2.4, RF-26, RF-29, RNF-16, RNF-18, RNF-17 |
| A | RD-07, RD-08 | RD-09 (C-07), RD-08 (C-10) |
| B | RF-01 | RF-02 (C-13) |
| B | RF-03 | RF-32 |
| B | RF-04 | RF-04 (AC-3 no adoptado, C-12) |
| B | RF-05 | RF-05 (AC-6, AC-7, AC-9) |
| B | RF-06, RF-07 | RF-05, RF-27 (C-01, C-02) |
| B | RF-08 | RF-10 |
| B | RF-09 | RF-37 |
| B | RF-10 | RF-11 (AC-5, AC-6) |
| B | RF-11 | RF-14, RF-38 |
| B | RF-12 | RF-19, RF-39, RF-34-AC-3 |
| B | RF-13 | RF-07, RF-32 |
| B | RF-14 | RF-35 |
| B | RF-15 | RF-36 |
| B | RF-16 | RF-34 |
| B | RF-17 | RF-38 |
| B | RF-18 | RF-12 |
| B | RF-19 | RF-31 |
| B | RF-20 | RF-30 |
| B | RNF-01 a RNF-08 | RF-26, RNF-01, RF-35, RF-05-AC-8, RNF-10, RF-06, RF-32, RNF-15 |
| B | RD-05, RD-08 a RD-11 | RD-15, RD-14, RD-16 |

## 7. Lo que queda abierto

Las resoluciones C-03, C-12, C-15 y C-17 dependen de supuestos que hay que confirmar con AMPIP, y están listadas en "Supuestos y pendientes con el cliente" del SRS de equipo. RF-32, RF-33, RF-35 y RF-36 todavía no tienen caso de uso en el diagrama; se agregan antes del diseño de API.
