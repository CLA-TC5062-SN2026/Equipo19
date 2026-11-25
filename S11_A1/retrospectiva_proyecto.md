# Retrospectiva del proyecto SGPIS

**Equipo 19:** Ángel Kociankowski (Product Owner), Leonardo Cossío (Scrum Master), Erick Ramírez
**Curso:** TC5062, Análisis, diseño y construcción de software, Grupo 10
**Cierre:** semana 11, noviembre de 2026
**Evidencia:** `S11_A1/matriz_trazabilidad.md`, capturas en `docs/img/`, pruebas en `backend/tests/` y `frontend/e2e/flujos_s11.py`

---

## Sección A. Retrospectiva SCRUM

### Qué salió bien

Los requerimientos aguantaron todo el semestre. Consolidar tres SRS individuales en uno de equipo nos costó la semana 3 completa: 19 conflictos documentados en `S03_A1/diferencias_SRS.md`, todos ratificados por los tres. A cambio, desde S05 no tuvimos que reabrir ninguna discusión de alcance ni de reglas de negocio, y los 150 criterios de aceptación con valores concretos nos dieron las pruebas casi escritas. Cada prueba del backend lleva el AC que verifica en el nombre (`test_RF_26_AC_3_bloqueo_tras_5_intentos`), y por eso la matriz de trazabilidad salió de leer el código.

Diseñamos con el contrato primero. En S04 cada uno diseñó su OpenAPI, en S05-S06 lo consolidamos en `openapi_equipo.yaml` y a partir de ahí la regla fue que el contrato manda. Las pruebas validan cada respuesta contra el contrato (`backend/tests/conftest.py`): si un endpoint devuelve un campo de más o un código que el contrato no declara, la prueba falla. Eso nos ahorró las discusiones de "en mi máquina sí funciona" entre backend y documentación.

Concentramos los permisos en un solo lugar. El cliente fue muy claro en que si la información de un parque llega a otro, los desarrolladores dejan de confiar. Pusimos toda la autorización en `backend/app/permisos.py`, con un mapa de ruta a roles y reglas por parque, y la API no arranca si una ruta protegida no está en el mapa. Hay pruebas que recorren todas las rutas sin token y con token alterado. En S09 el code review buscó a propósito accesos a parques ajenos cambiando el id en la URL y no encontró ninguno.

La planeación del Sprint 1 fue honesta. El agente propuso 15 story points para el primer sprint sin justificar la capacidad. Medimos la real (3 personas × 8.5 h × 2 semanas, menos eventos: 42.75 h) y comprometimos 39 h. Esa medición la seguimos usando en S09 para traducir la deuda técnica a sprints.

### Qué no salió bien

Construimos por capas y no por historias. El semestre fue base de datos y API en S05-S06, frontend en S07-S08 y calidad en S09. Para la semana 9 el backend tenía 51 operaciones y 94 % de cobertura, y ninguna historia de usuario estaba terminada de punta a punta. El costo apareció en la semana 11: el cliente HTTP del frontend de S07-S08 seguía apuntando a `/api/v1/sesiones`, la ruta del contrato individual de S04, y no a `/api/auth/login` del backend del equipo. El backend tampoco tenía CORS. La integración real de frontend y backend se hizo en esta semana. Funcionó, pero tendría que haber existido desde S07.

Dejamos fuera justo lo que el cliente usa todos los días. En la entrevista de la semana 2, lo indispensable para arrancar la generación incluía la carga de evidencias con la revisión del consultor. No la construimos. Decidimos hacer primero lo que necesitaban todas las demás historias (sesión, permisos, expediente, fases), y la evidencia requería además un almacenamiento de objetos que nunca configuramos. Al final, 9 de los 17 RF sin implementar son la evidencia o dependen de ella: calificación, bloqueo por análisis de riesgos, Opinión, comité, dictamen, Evaluación de Desempeño y recomendaciones del consultor.

La Definition of Done prometió cosas que no hicimos. Integración continua desde la tarea T-06 del Sprint 1, migraciones con Alembic y `ruff` como linter. En S09 calculamos que una cuarta parte de la deuda técnica (8.5 de 33 horas) era proceso acordado y no construido. Las pruebas existen y pasan, pero nada las corre solo cuando alguien sube un cambio.

El tablero Kanban dejó de reflejar el trabajo. RF-11 (cambio de tipo de PI) y RF-24 (evidencia suficiente) quedaron implementados en S05-S06 porque venían en el contrato, pero no tenían historia en el backlog, así que ese avance nunca se vio en el tablero. Además, el frontend vivió como zip fuera del repositorio hasta esta semana.

### Qué haríamos diferente

1. Una historia completa por sprint, de la base a la pantalla. Para el Sprint 1 habría bastado HU-01 (login) con su pantalla y HU-02 (alta de parque) con la suya. Así el problema de rutas que encontramos en la semana 11 habría salido en la semana 5.
2. Atacar primero el riesgo técnico de lo indispensable. La evidencia necesitaba un bucket y nadie había configurado uno. Habríamos levantado MinIO en el `docker compose` desde S05 y subido el primer archivo antes de pulir el resto.
3. La CI desde el primer commit. Un flujo de GitHub Actions que corra `pytest` contra PostgreSQL cuesta una tarde, y lo pospusimos hasta que fue deuda.
4. Toda RF en alcance con su historia antes del primer endpoint. Así lo que se construye se ve en el tablero, y lo que no se construye también.
5. Tipos del frontend generados del contrato. En S07-S08 decidimos JavaScript con JSDoc y dejamos escrito que reconsideraríamos si aparecían errores de forma de datos. Aparecieron: el cliente esperaba `problem+json` y el backend responde `{codigo, mensaje, detalles}`. Con tipos generados de `openapi_equipo.yaml`, el compilador lo habría marcado.

### Uso de herramientas agentes

Usamos Claude (Claude Code y el chat) en todas las fases. La regla que nos pusimos desde S01 fue que nada generado entraba al repositorio sin que alguien lo leyera, y que la salida original del agente se guardaba en `evidencia_agente/` para poder comparar.

#### Dónde fue más útil

- Requerimientos. Comparar tres SRS de unos 180 KB y listar consensos, huecos y 19 conflictos con el ID de cada versión. A mano habría sido una tarde completa con omisiones seguras.
- Revisión de diseño con un segundo agente. En el S04 de Ángel un agente generó el OpenAPI v0 y otro, sin ver la conversación del primero, lo revisó contra principios REST: 20 observaciones, de las que adoptamos 19. Repetimos el esquema en S05-S06 y en S09, y fue lo que mejor funcionó. El revisor independiente encontró en S05-S06 que nuestra corrección del modelo de dictamen se había pasado de restrictiva.
- Pruebas y rendimiento. En S09 el agente midió las consultas de `GET /parques` (643 consultas SQL para 80 parques) y propuso la versión con 10. También escribió las pruebas de caracterización antes de refactorizar, que eran justo las que nos faltaban.
- Integración final. En esta semana el agente construyó las pantallas de login, tablero, alta, edición y baja sobre los componentes de S07, agregó CORS al backend y escribió la prueba de punta a punta con Playwright. También encontró que varias reglas de permisos ya funcionaban pero ninguna prueba las nombraba, y escribió esas pruebas (`tests/test_trazabilidad_s11.py`) para poder citarlas en la matriz.

#### Dónde generó trabajo extra

- Lo que parece terminado sin estarlo. Al backlog v0 le faltaba la historia de análisis de riesgos, sin la cual no se podían calificar 3 de los 10 estándares. La propuesta de autenticación de S03 era un JWT sin estado, que no puede cumplir ni el cierre de sesión ni la expiración por inactividad de RF-26. El modelo de dictamen de S05-S06 tenía `sesion_comite_id NOT NULL`, lo que impedía registrar el "no otorgar" de RF-14-AC-8. Los tres pasaban cualquier revisión de forma y fallaban contra el SRS.
- Documentación que contradice al código. En S07-S08 los documentos que redactó el agente citaban un endpoint y un código de estado distintos a los del código, y la integración de A2 se hizo contra un backend mínimo en SQLite en lugar del backend del equipo. Las dos cosas salieron hasta que revisamos las entregas.
- El paso por humanizer alteró código. En S09, al reescribir la prosa para que sonara a nosotros, el agente modificó bloques de código dentro de los documentos. Tuvimos que restaurarlos desde la fuente y agregar un script que verificara que código y números no cambiaran.
- Atribuciones inventadas. En S05-S06 el agente atribuyó aportaciones a integrantes del equipo sin tener cómo saberlo. Lo marcó el revisor independiente y lo corregimos.

#### Si cambió nuestra forma de programar

Sí. Pasamos más tiempo especificando y revisando que tecleando. El AC va antes que el código y en el nombre de la prueba. Cuando el agente genera algo importante, otro agente sin contexto lo revisa contra el SRS antes de que lo veamos nosotros. También aprendimos que el agente produce muy rápido sobre lo que le damos, con sus aciertos y sus huecos: un SRS preciso dio pruebas precisas, y un contrato individual desactualizado dio un frontend que hablaba con una API que ya no existía.

---

## Sección B. Consistencia problema-solución

### El problema de la semana 2

En `proyecto_base.md` describimos así la situación del programa: AMPIP no tiene una vista consolidada del avance de cada parque, el consultor revisa evidencias en carpetas sueltas, la APPI filtra a mano qué criterios le aplican y mide su avance sin separar obligatorios de recomendados, y nadie sabe con precisión qué obligatorios faltan ni cuándo vence el distintivo. La entrevista con el cliente real, un miembro del comité de AMPIP, agregó tres cosas: se enteran del atraso por las fechas de término y de actualización anual del programa, necesitan desde el primer mes el historial de todos los parques y la autoevaluación, y el distintivo nunca se entrega con la autoevaluación sin terminar.

### Qué resuelve la aplicación, con evidencia

| Problema de la semana 2 | Qué hace SGPIS | Evidencia |
|---|---|---|
| AMPIP no tiene vista consolidada del avance | Tablero con los parques de la generación: fase (n de 9), porcentaje de obligatorios cumplidos, criterios atrasados y actualización anual vencida, más cuatro indicadores arriba | `docs/img/03_tablero.png`; `GET /parques`, `GET /parques/{id}/cumplimiento`; RF-07, RF-08 y RF-32 en la matriz |
| AMPIP se entera del atraso por la fecha de actualización anual (cliente real, P1) | El parque con la fecha vencida aparece marcado en el tablero y en su expediente, y el tablero filtra por "Actualización anual: vencida" | Etiqueta en `03_tablero.png` y `04_detalle.png`; `test_parques.py::test_RF_30_AC_2_y_AC_3_atraso_y_actualizacion_anual`; paso 7 del E2E |
| La APPI filtra a mano qué criterios aplican | La API entrega solo los criterios O y R del tipo de PI vigente y recalcula si el tipo cambia, sin perder el porcentaje anterior | `test_expediente.py::test_RF_04_AC_1_solo_criterios_aplicables`, `test_trazabilidad_s11.py::test_RF_11_AC_2_conserva_porcentaje_de_la_clasificacion_anterior`; tabla de criterios en `04_detalle.png` |
| El avance no separa obligatorios de recomendados | Tres cifras (obligatorios, recomendados, avance general) por estándar y total, sumando criterios y no promediando porcentajes | Sección "Cumplimiento" de `04_detalle.png`; `test_RF_08_*` |
| No se sabe qué obligatorios faltan | El expediente lista los criterios no cumplidos, con los atrasados arriba | `04_detalle.png` (criterio 4.1.1 "No cumplido · Atrasado") |
| La información de un parque no debe llegar a otro | La APPI solo ve su parque; el consultor, solo sus asignados; el gerente, solo los de su desarrollador. Todo intento negado queda en la bitácora | `docs/img/10_appi.png`; `test_permisos.py::test_RNF_01_aislamiento_entre_parques`, `::test_RF_35_AC_2_el_403_queda_en_bitacora`; paso 10 del E2E |
| Historial de todos los parques (cliente real, P3) | Alta de parque histórico con datos mínimos y consulta del historial por parque | `test_parques.py::test_RF_31_AC_1_historial`, `::test_RF_31_AC_2_alta_parque_historico`; el parque histórico aparece en `03_tablero.png` |
| Autoevaluación desde el primer mes (cliente real, P3) | La APPI puede autoevaluar por API los criterios que le aplican | `test_expediente.py::test_RF_04_*`; sin pantalla |

Con el escenario de demostración, el tablero responde de un vistazo lo que hoy se arma con archivos, correos y reuniones: de ocho parques, tres tienen criterios atrasados, dos tienen la actualización anual vencida y cuatro van por debajo de 50 % de obligatorios.

Una aclaración: esas cifras de cumplimiento las carga `app/demo_s11.py` directo en la base, porque la calificación de criterios (RF-27) no tiene endpoint. El cálculo y su presentación sí son reales y están probados. El dato que les da origen todavía no se puede capturar desde el sistema.

### Qué no resolvimos

| Parte del problema | Estado | Por qué |
|---|---|---|
| El consultor revisa evidencias en carpetas sueltas | Sin resolver | En el orden de trabajo la evidencia quedó al final, y además requería un almacenamiento de objetos que no configuramos. Arrastra la calificación (RF-27), la Opinión (RF-12) y el comité y dictamen (RF-13 a RF-15). |
| No se sabe cuándo vence el distintivo | Sin resolver | El registro del distintivo (RF-38) quedó fuera del entregable de 12 semanas desde el SRS. Los avisos (RF-19) necesitan además el worker que nunca construimos. |
| Autoevaluación (prioridad del cliente real) | Resuelto en la API, sin pantalla | Faltó tiempo: el endpoint funciona y tiene pruebas, y la pantalla no entró en la integración de esta semana. |
| Expediente completo para el comité ("autoevaluación revisada y visto bueno del consultor") | Sin resolver | Depende de la cadena de evidencias. El modelo de dictamen sí quedó corregido para registrar un "no otorgar" sin sesión de comité. |
| Reporte mensual para Dirección | Sin resolver | El módulo de reportes nunca se empezó. Casi todos sus datos (fase y atrasos por parque) ya están en el tablero. |
| Avisos por correo (invitaciones, contacto principal, recuperación de contraseña) | Parcial | Los correos se escriben en la cola de la base, pero el proceso que los envía no existe. |

### Qué le demostraríamos primero al cliente

Le abriríamos el tablero con el filtro "Actualización anual: vencida".

El miembro del comité nos dijo que así es como hoy se enteran de que un parque se atrasó: por la fecha de término y de actualización anual del programa. Es la única pregunta de su entrevista que la aplicación contesta completa, desde la pantalla, sin pasos manuales: Coordinación registra las fechas en el expediente y el parque aparece marcado en cuanto la fecha vence. Si eso le sirve, confirmamos que el tablero responde a la forma en que AMPIP detecta hoy los atrasos.

Lo segundo sería entrar como la APPI de un parque y mostrar que ve su parque y nada más. Es la condición para que los desarrolladores acepten usar la plataforma, y está probada en cada ruta.

Después le diríamos lo que falta antes de que nos lo pregunte: la autoevaluación, que nos pidió para el primer mes, funciona en la API pero no tiene pantalla, y la carga de evidencias no existe. Si la generación de febrero de 2027 fuera a arrancar con SGPIS, esas dos serían las primeras historias del siguiente sprint.
