# Salida del Agente 1: análisis de diferencias entre los tres SRS individuales

> Salida sin editar del agente analista de diferencias (prompt en `prompts_agentes.md`). Las resoluciones finales están en `diferencias_SRS.md`.

## Panorama de los insumos

| Documento | Versión | RF | RNF | RD / RN | AC | Formato de AC | Fuente de stakeholder |
|---|---|---|---|---|---|---|---|
| SRS_final_Angel.md | 1.4 | 31 | 14 | 13 RD | 110 | Dado/cuando/entonces por RF, con ejemplos concretos, códigos HTTP y mensajes | Entrevista simulada (Parte A), consultor (Parte B) y cliente real, miembro del comité de AMPIP (Parte C) |
| SRS_final_Leonardo.md | 1.1 | 24 | 9 | 9 RD + 20 RN | 56 | Tabla general en la sección 8, separada de los RF | Entrevista con modelo de IA; la sección "cliente real" está respondida desde el diseño del sistema ("nuestro backend"), no por AMPIP |
| SRS_final_Erick.md | sin versión | 20 | 8 | 11 RD | 60 | Dado/cuando/entonces por RF | Entrevista simulada extensa; para el stakeholder real reutiliza la Parte C de Ángel (lo declara en su transcript) |

Observación: los tres SRS describen el mismo sistema con la misma fuente base (`proyecto_base.md` es idéntico en los tres paquetes). La única evidencia de cliente real es la Parte C de Ángel; Erick la adopta de forma explícita y Leonardo no la usa.

## 1. Consenso (presente en los tres)

| # | Requerimiento | Ángel | Leonardo Cossío | Erick Ramírez |
|---|---|---|---|---|
| 1 | Catálogo de criterios con marca O/R/NA por cuatro tipos de PI | RF-01, RD-01 | RF-11, RD-02 a RD-04, RF-23 | RF-04, def. 1.3 |
| 2 | Alta de parque | RF-02 | RF-23 | RF-01 |
| 3 | Usuarios con roles y control de acceso por rol | RF-03, RNF-02 | RNF-01, RNF-07 | RNF-01, RF-16 |
| 4 | Asignar consultor a parque | RF-10 | RF-23, RF-18 | RF-08 |
| 5 | Autoevaluación de los criterios aplicables al tipo de PI | RF-04 | RF-03 | RF-04 |
| 6 | Carga de evidencias por criterio con revisión y observaciones | RF-05, RF-27 | RF-04 a RF-09 | RF-05 a RF-07 |
| 7 | Nueva versión de una evidencia observada sin perder la anterior | RF-05-AC-4 | RF-08 | RF-05-AC-2 |
| 8 | Recalcular criterios aplicables al cambiar el tipo de PI, conservando lo anterior | RF-11 | RF-10 a RF-13 | RF-10 |
| 9 | Vista consolidada de cartera para AMPIP | RF-07, RF-21 | RF-17 | RF-13 |
| 10 | Aislamiento de información entre parques; consultor limitado a sus parques | RNF-01 | RNF-02, RF-18 | RNF-02 |
| 11 | Bitácora no modificable por usuarios | RNF-03 | RF-22 | RF-14, RNF-03 |
| 12 | Evidencias sin enlace público | RNF-02, RNF-05 | RNF-03 | RNF-08 |
| 13 | Opinión de Cumplimiento o visto bueno del consultor | RF-12 | RF-24 | RF-18 |
| 14 | Dictamen y otorgamiento del distintivo con condiciones previas | RF-14, RD-09 | RD-07, RF-01 | RF-11, RD-04 |
| 15 | Aviso de vencimiento del distintivo | RF-19 | RF-19 a RF-21 | RF-12 |
| 16 | Autenticación obligatoria | RF-26 | RNF-06 | RNF-01 |
| 17 | Archivos de evidencia fuera de la base de datos relacional | 2.1, RNF-05 | RNF-05 | (implícito en RNF-08) |

## 2. Gaps

### 2.1 Solo en el SRS de Ángel

Generación (RF-28); plan de trabajo con responsable, fecha comprometida y atraso (RF-09); registro de revisión del análisis de riesgos (RF-16) y bloqueo de estándares 2, 3 y 7 sin él (RF-17); política de seguridad como precondición de las Opiniones (RF-12-AC-4); comité con consultor de comité de acceso temporal (RF-13) y validación del expediente antes de abrirlo (RF-15); firma del dictamen por el Director General (RF-14); vista del gerente corporativo (RF-23); Coordinación AMPIP sin acceso al contenido de evidencias de seguridad (RF-07, RNF-02); datos personales del estándar 7 (RNF-04); restricción de descarga del archivo maestro del catálogo (RF-25); evidencia suficiente por criterio (RF-24); auditorías del subestándar 1.4 (RF-18, RF-20); reporte mensual de Dirección (RF-21) y reporte para asociados (RF-22); Administrador técnico; zona horaria (RNF-11); canal de correo (RNF-12); respaldos (RNF-13); retención de 6 años (RNF-14); disponibilidad 99 % (RNF-08); carga desde navegador móvil (RNF-09); estado de calificación del criterio separado del estado de la evidencia (RF-27).

### 2.2 Solo en el SRS de Leonardo

Gestión explícita de fases con estados pendiente/en proceso/completada y bloqueo de avance salvo excepción de AMPIP (RF-02); metadatos mínimos de evidencia (RF-05); Evaluación de Desempeño como resultado formal con folio (RF-24); porcentaje de R por separado y cumplimiento global calculado sobre la suma de criterios, no como promedio de estándares (RF-14, RF-15); "NA" en lugar de 0 % cuando no hay criterios de una categoría (RF-14); periodo de anticipación de alertas configurable y sin duplicados (RF-21); catálogo con múltiples versiones y validación antes de activarlo (RF-23); cifrado TLS y en reposo (RNF-03); tiempos de respuesta de 3 s p95 y 5 s para el tablero (RNF-08, RNF-09); progreso de carga sin bloquear la interfaz (RNF-08).

### 2.3 Solo en el SRS de Erick

Solicitud de incorporación con aceptación o rechazo de AMPIP (RF-02); rol de evaluador de AMPIP separado del consultor (2.3, RF-06, RF-08); visita de validación con hallazgos y acciones correctivas (RF-09); solicitud de cambio de tipo de PI por la APPI con autorización de AMPIP (RF-10); una evidencia vinculada a varios criterios (RF-05-AC-1); eliminación lógica de evidencias (RF-05-AC-3); recomendaciones internas del consultor (RF-15); varios usuarios APPI con un contacto principal (RF-16); solicitud de renovación sin extender la vigencia (RF-17); estados del distintivo, incluida la prórroga (RF-11-AC-4, RD-11); avisos de documentos críticos con vencimiento (RF-12-AC-2); excepción de NA con justificación (RF-04-AC-3); carga de varios archivos en una operación (RNF-04); capacidad de 100 a 200 parques (RNF-05).

### 2.4 En dos de tres

| Requerimiento | Lo tienen | Falta en |
|---|---|---|
| Historial de parques del programa | Ángel RF-31, B RF-19 | A |
| Fecha anual de término o actualización del programa con atraso | Ángel RF-30, B RF-20 | A |
| Baja de usuarios sin perder su historial | Ángel RF-29, A RNF-07 | B (solo retira asignaciones, RF-08-AC-3) |
| Cálculo de cumplimiento con NA fuera del denominador | Ángel RF-08, A RF-14/RF-16 | B (lo supone en RF-11-AC-1, sin RF de cálculo) |
| Bitácora de consultas y descargas, no solo de cambios | Ángel RNF-03, B RF-14 | A (registra operaciones de cambio) |
| "NA" o "No aplica" en lugar de 0 % | Ángel RF-08-AC-3, A RF-14 | B |
| Video excluido como formato de evidencia | Ángel RF-06, B 1.2 | A (lo exige) |

## 3. Conflictos

| ID | Tema | Ángel | Leonardo Cossío | Erick Ramírez | Recomendación del agente (decisión del equipo) |
|---|---|---|---|---|---|
| C-01 | Quién revisa evidencias | Consultor asignado | Consultor externo | Evaluador de AMPIP; el consultor solo recomienda | Consultor asignado: lo respaldan dos SRS y la Parte C ("dictamen del consultor dando el visto bueno") |
| C-02 | Estados de evidencia | enviada, observada, aceptada + estado del criterio aparte | pendiente, enviada, observada, aceptada | aprobado, rechazado, observado | Modelo de Ángel: separa evidencia y criterio; "pendiente" de A equivale a criterio sin evidencia |
| C-03 | AMPIP ve contenido de evidencias de seguridad | No (solo estado y administrativas) | Sí, en modo consulta | Sí, porque revisa | Requiere decisión del equipo; el riesgo de exposición favorece la versión de Ángel |
| C-04 | Quién cambia el tipo de PI | Coordinación AMPIP directo | "Usuario autorizado" directo | APPI solicita, AMPIP autoriza | Coordinación AMPIP con motivo obligatorio |
| C-05 | Tamaño máximo de archivo | 100 MB | Parametrizable, sin valor | 50 MB | Parametrizable con valor inicial |
| C-06 | Video como evidencia | Fuera | Requerido | Fuera | Fuera (dos de tres, más costo de almacenamiento) |
| C-07 | Condiciones para otorgar | Autoevaluación revisada + Opinión final favorable + 100 % de O | 2 Opiniones + Evaluación de Desempeño + mínimos de AMPIP | Autoevaluación terminada + O cumplidos + hallazgos cerrados + visto bueno | Versión de Ángel (Parte C) |
| C-08 | Quién decide el dictamen | Comité captura, Director General firma | No definido | AMPIP registra | Versión de Ángel |
| C-09 | Plazos de aviso de vencimiento | 6 y 3 meses | Configurable | 90, 60 y 30 días | Configurable con valores iniciales |
| C-10 | Vigencia del distintivo | 3 años (sin confirmar) | Parametrizable | Pendiente | Parametrizable con valor inicial de 3 años |
| C-11 | Cifras de cumplimiento | % de O y avance general (O+R) | % de O y % de R separados | Sin fórmula | Mostrar las tres cifras |
| C-12 | NA a solicitud de la APPI | No; NA solo del catálogo | No | Sí, con justificación (pendiente de validar) | NA solo del catálogo hasta que AMPIP confirme |
| C-13 | Quién da de alta el parque | Coordinación AMPIP | AMPIP | APPI se registra; AMPIP acepta o rechaza | Coordinación AMPIP |
| C-14 | Versiones de catálogo | Una activa por generación | Varias versiones con validación y consulta histórica | Sin definir | Una activa por generación y las anteriores en solo lectura |
| C-15 | Fases del programa | 9 fases | 7 fases | Configurables, secuencia por validar | Requiere decisión del equipo |
| C-16 | Rendimiento | 2 s p95 en lista de evidencias, 1 s en confirmación de carga | 3 s p95 en consultas, 5 s en tablero | Sin cifra, por decisión explícita | Combinar como propuestas del equipo |
| C-17 | Capacidad | 41 a 80 parques | Sin cifra | 100 a 200 parques | Requiere decisión del equipo |
| C-18 | Retención de evidencias | 6 años desde la firma del dictamen | Pendiente | Pendiente | Adoptar 6 años como propuesta, pendiente de AMPIP |
| C-19 | Una evidencia para varios criterios | Una evidencia por criterio (implícito) | Varias evidencias por criterio | Una evidencia vinculada a varios criterios | Requiere decisión del equipo |

## Observaciones del agente sobre la calidad de los insumos

- El SRS de Leonardo separa los criterios de aceptación de los RF y varios son difíciles de probar (por ejemplo RF-01-AC-1, "debe permitir gestionar el proceso"). Sus reglas de negocio RN-01 a RN-20 repiten en buena parte los RD.
- El SRS de Erick deja varios pendientes de validación sin valor por omisión, lo que impide escribir pruebas para vigencia, renovación y retención.
- El SRS de Ángel es el más extenso y el único con AC ligados a endpoints y mensajes. Al ser la base más probable para consolidar, conviene revisar que no absorba sin discusión decisiones que solo él tomó (por ejemplo, el ocultamiento de evidencias de seguridad a Coordinación AMPIP).
