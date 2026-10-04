# Definition of Done de SGPIS

**Proyecto:** SGPIS (AMPIP), Equipo 19, TC5062
**Vigente desde:** Sprint 1 (5 de octubre de 2026). Se revisa en cada retrospectiva.
**Propuesta del agente, sin editar:** `evidencia_agente/dod_agente.md`

Una historia de usuario está terminada cuando cumple todos los puntos de esta lista. Si falta uno, no se presenta en la revisión del sprint y regresa al Sprint Backlog o al Product Backlog; no existe "terminada al 90 %". Cada punto dice cómo se comprueba, para que ningún cierre dependa de la opinión de quien escribió el código.

La lista está pensada para nuestras condiciones reales: tres estudiantes con 8 a 9 horas por semana, sin servidor de despliegue y con integración continua solo a partir de la tarea T-06 del Sprint 1. Por eso no aparecen ambiente de staging ni despliegue continuo, y la sección 4 dice cuándo entra cada cosa que hoy falta.

## 1. Nivel tarea

Una tarea del tablero se cierra cuando:

| # | Punto | Cómo se comprueba |
|---|---|---|
| T1 | Cumple el criterio de done escrito en la tarea. | Quien la cierra lo verificó como dice el criterio; si el criterio es una prueba, la prueba está en el PR. |
| T2 | Sus horas reales quedan anotadas en un comentario del issue. | Comentario "Horas reales: N". Con esto calculamos la velocidad para planear el Sprint 2. |

## 2. Nivel historia

### Código

| # | Punto | Cómo se comprueba | Por qué en este proyecto |
|---|---|---|---|
| H1 | El cambio entra a main por pull request, desde una rama propia, y el PR cierra el issue ("Closes #N"). | Regla de protección de main: nadie hace push directo. | Trazabilidad de cada cambio hasta su historia y su requerimiento. |
| H2 | `ruff check` y `ruff format --check` sin errores. | Job de lint en GitHub Actions. | Tres personas escribiendo Python con estilos distintos; el formato no se discute en las revisiones. |
| H3 | Las migraciones de Alembic están incluidas y aplican sobre una base vacía. | El CI ejecuta `alembic upgrade head` antes de las pruebas. | Un cambio de modelo sin migración funciona en una máquina y falla en las otras dos. |
| H4 | Ningún secreto en el repositorio: contraseñas, tokens y llaves viven en `.env`, que no se versiona; `.env.example` se actualiza si hay variables nuevas. | Revisión del PR con el diff a la vista; `.env` en `.gitignore`. | Una credencial filtrada en un repo de la organización del curso es un incidente, aunque sea de desarrollo. |

### Pruebas

| # | Punto | Cómo se comprueba | Por qué en este proyecto |
|---|---|---|---|
| H5 | Cada criterio de aceptación de la historia tiene al menos una prueba automatizada que lleva su ID en el nombre (por ejemplo, `test_rf26_ac3_bloqueo_tras_cinco_intentos`). | `grep` del ID en `tests/`; la lista de AC del issue tiene sus casillas marcadas. | El SRS de equipo tiene 150 AC escritos para ser probados. Con el ID en el nombre, se sabe qué requerimiento falló cuando una prueba falla. |
| H6 | Todo endpoint nuevo tiene prueba de 401 sin sesión y de 403 para un rol sin permiso y para un usuario de otro parque. | Pruebas en el PR. | RNF-01: la información de un parque no la ve otro parque ni un consultor que no lo tiene asignado. Es el requisito que más daño hace si falla. |
| H7 | La suite completa de pytest pasa en el CI, no solo las pruebas nuevas. | Último run de GitHub Actions sobre el PR, en verde. | Un cambio en sesiones puede romper una historia ya terminada. |
| H8 | Ninguna prueba depende del reloj real ni del orden de ejecución. | Revisión del PR: sin `sleep`; las reglas de tiempo (bloqueo de 15 min, inactividad de 60, enlace de 30) se prueban con reloj simulado. | Las pruebas de tiempo que fallan a veces terminan ignoradas, y entonces ya no protegen nada. |

### Seguridad y datos

| # | Punto | Cómo se comprueba | Por qué en este proyecto |
|---|---|---|---|
| H9 | Toda operación que crea, cambia, consulta o descarga información de un parque deja registro en la bitácora, y los accesos denegados también. | Una prueba por operación verifica que existe el registro. | RNF-03 y RF-35. AMPIP tiene que poder saber quién vio el plan de contingencia de un parque. |
| H10 | Ningún dato real de AMPIP ni de los parques en el repositorio, en fixtures o en capturas: catálogo, nombres de parques, evidencias, correos. Se usan datos sintéticos. | Revisión del PR. | El catálogo es propiedad de AMPIP (RD-05) y las evidencias son información de seguridad. Un repo de curso no es lugar para ninguna de las dos cosas. |
| H11 | Contraseñas, tokens y enlaces de recuperación nunca aparecen en logs, en respuestas de error ni en la bitácora. | Revisión del PR; prueba de que el mensaje de error de login no distingue entre correo inexistente y contraseña incorrecta. | Es la forma más común de filtrar credenciales en sistemas pequeños. |

### Comportamiento y documentación

| # | Punto | Cómo se comprueba | Por qué en este proyecto |
|---|---|---|---|
| H12 | Los mensajes al usuario están en español de México y coinciden exactamente con el texto del AC cuando el AC lo fija. Las fechas se calculan en America/Mexico_City. | Las pruebas de H5 comparan el texto exacto; prueba de fecha en el límite del día. | RNF-11. Un atraso marcado un día antes por la zona horaria del servidor es un error que AMPIP ve. |
| H13 | El endpoint aparece en `/docs` (OpenAPI) con descripción, ejemplo de solicitud y sus respuestas de error. | Revisión del PR en `/docs`. | FastAPI la genera sola; nos toca completar descripciones y ejemplos. El diseño de API de las próximas semanas parte de ahí. |
| H14 | Si cambian pasos de arranque, dependencias o variables de entorno, el README está actualizado en el mismo PR. | Revisión del PR. | El criterio 1 del Sprint Goal: cualquiera levanta el proyecto siguiendo solo el README. |

### Revisión y aceptación

| # | Punto | Cómo se comprueba | Por qué en este proyecto |
|---|---|---|---|
| H15 | Otro integrante, que no escribió el código, aprobó el PR. | Regla de protección de main: una aprobación obligatoria. | Somos tres; sin esta regla, cada quien terminaría revisando solo su propio código. |
| H16 | Las tareas de la historia están cerradas con sus horas reales. | Sub-issues cerrados en el tablero. | Velocidad del equipo para el siguiente sprint. |
| H17 | El Product Owner vio los criterios de aceptación funcionando en la revisión del sprint y aceptó la historia. | Registro en el issue: "Aceptada en revisión del Sprint N". | Pasar las pruebas no es lo mismo que resolver lo que AMPIP necesita; esa diferencia la juzga el PO. |

## 3. Nivel incremento (cierre del sprint)

| # | Punto | Cómo se comprueba |
|---|---|---|
| I1 | main levanta desde un clon limpio con `docker compose up -d` y los pasos del README, en una máquina distinta a la del autor del último cambio. | En vivo, al inicio de la revisión del sprint. |
| I2 | El último run de main en GitHub Actions está en verde. | Pestaña Actions. |
| I3 | Las historias que no cumplen todos los puntos de la sección 2 regresan al backlog con una nota de qué faltó. | Columna "Sprint actual" vacía al cierre. |

## 4. Lo que todavía no está y cuándo entra

| Punto | Por qué no está hoy | Cuándo entra |
|---|---|---|
| Pruebas de componente en Vitest y revisión en Chrome y Safari de Android e iOS (RNF-09) | No hay frontend hasta el scaffolding de las semanas 7 y 8. | En el primer sprint con frontend, empezando por HU-23. |
| Despliegue continuo a un servidor | No tenemos servidor; el curso no lo ha pedido. | Cuando exista ambiente de despliegue. |
| Pruebas de carga (RNF-07, RNF-10, RNF-16, RNF-17) | Sin datos ni pantallas de cartera no hay qué medir. | En el sprint de HU-13, la vista de avance de AMPIP. |
| Integración continua | Se construye en T-06 del Sprint 1. | Mientras T-06 no esté cerrada, quien abre el PR corre `uv run pytest` en local y pega la salida en el PR. Al cerrarse T-06, H2, H3, H7 e I2 se comprueban en Actions. |

## 5. Cambios respecto a la propuesta del agente

El agente propuso 12 puntos. Era una DoD correcta para cualquier proyecto y por eso no servía para este: nada en ella cambiaba si el sistema fuera una tienda en línea. Tenía tres problemas.

**Puntos imposibles de cumplir hoy.** "Desplegada en staging" y "pipeline de CI/CD en verde" suponen infraestructura que no existe. Una DoD que no se puede cumplir deja de aplicarse desde la primera historia, y después nadie la respeta. Los quité y los pasé a la sección 4, con la fecha en que entran.

**Puntos que no se pueden verificar.** "Buenas prácticas de seguridad", "rendimiento aceptable", "documentación actualizada" y "sin bugs críticos" no dicen quién decide ni cómo. Los reemplacé por puntos concretos: H6, H9, H10 y H11 en seguridad; H13 y H14 en documentación. El rendimiento quedó en la sección 4, porque hoy no hay qué medir.

**Una métrica que mide lo que no importa.** "Cobertura mínima del 80 %" se cumple con pruebas que recorren código sin comprobar ningún requerimiento. La cambié por H5: una prueba por criterio de aceptación, nombrada con su ID. Si después queremos un piso de cobertura, lo decidimos con datos del Sprint 1 en la retrospectiva.

Conservé, reescritos para que se puedan comprobar, cinco puntos del agente: revisión por otro integrante (H15), criterios de aceptación cumplidos (H5), aprobación del PO (H17), estilo de código (H2) y suite de pruebas en verde (H7).

Agregué lo que es propio de SGPIS y no habría aparecido en una DoD genérica: bitácora en cada operación (H9), cero datos reales de AMPIP en el repositorio (H10), aislamiento entre parques probado en cada endpoint (H6), mensajes y fechas de México (H12) y horas reales por tarea para medir la velocidad (T2 y H16).
