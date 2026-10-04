# Sprint 1 Planning

**Proyecto:** SGPIS (AMPIP), Equipo 19, TC5062
**Sprint:** 1, del lunes 5 al domingo 18 de octubre de 2026 (semanas 4 y 5 del curso)
**Entrada:** `S03_A1/backlog_completo.md` (22 historias, 111 story points) y el orden de `S03_A1/priorizacion_comparada.md`
**Propuesta del agente, sin editar:** `evidencia_agente/sprint_goal_agente.md`

## 1. Sprint Goal

**Al cierre del Sprint 1, la API del SGPIS corre igual en las máquinas de los tres integrantes y en GitHub Actions, autentica usuarios con las reglas de RF-26 y rechaza con 403 a cualquier rol sin permiso, dejando cada inicio de sesión y cada acceso denegado en una bitácora que nadie puede editar.**

Es la base sobre la que se monta todo lo demás. El sistema va a guardar análisis de riesgos, planes de contingencia y ubicación de cámaras de parques industriales; no quiero cargar un solo dato del programa antes de tener control de acceso y bitácora funcionando y probados.

El goal se cumple si en la revisión del sprint se demuestra todo esto:

| # | Evidencia | Cómo se comprueba |
|---|---|---|
| 1 | Un integrante que no escribió el código levanta la API desde un clon limpio siguiendo solo el README. | En vivo, en la revisión. |
| 2 | Cada PR corre ruff y pytest en GitHub Actions, y main no acepta push directo ni fusiones sin aprobación. | Historial de Actions y configuración de la rama. |
| 3 | Las seis pruebas `test_rf26_ac1` a `test_rf26_ac6` están en verde en Actions. | Último run de main. |
| 4 | Un endpoint reservado a Coordinación AMPIP responde 403 a un usuario APPI y a un consultor, y cada intento queda en bitácora como "denegado". | Demo desde `/docs` y consulta a la tabla de bitácora. |
| 5 | Un UPDATE sobre la bitácora con el usuario de base de la aplicación falla por permisos. | Prueba automatizada de T-04. |

## 2. Capacidad del equipo

| Concepto | Horas |
|---|---|
| 3 integrantes × 8.5 h por semana × 2 semanas | 51.0 |
| Menos eventos del sprint por integrante: revisión 1 h, retrospectiva 0.75 h, dailies asíncronas 1 h | −8.25 |
| **Capacidad neta para tareas** | **42.75** |
| **Comprometido (14 tareas)** | **39.0** |
| Holgura | 3.75 (9 %) |

Planeé por horas y no por story points porque es el primer sprint: no tenemos velocidad histórica, y convertir story points a horas con una regla inventada daría una capacidad que solo parece precisa. Al cierre vamos a registrar las horas reales de cada tarea; con eso, el Sprint 2 ya se puede planear también con velocidad en story points.

Dejé la holgura en 9 % a propósito. El esqueleto técnico es trabajo que ninguno de los tres ha hecho en este stack, y es donde más se equivocan las estimaciones de un primer sprint.

## 3. Sprint Backlog

| Elemento | SP | Horas de tareas | Por qué entra |
|---|---|---|---|
| HT-01 Esqueleto técnico del backend (habilitador) | Sin SP | 17 | Repo, base de datos, migraciones, bitácora, pruebas y CI. Toda historia lo necesita, y la definición de terminado no se puede cumplir sin él: no hay forma de exigir "pruebas en verde en CI" si no existe CI. |
| HU-01 Iniciar sesión, cerrar sesión y recuperar contraseña (API) | 5 | 22 | Primera en el orden de prioridad. Todos los criterios de aceptación del SRS suponen una sesión iniciada con un rol, empezando por el de cargar el catálogo (RF-01-AC-1). |
| **Total** | **5** | **39** | |

El detalle de las 14 tareas, con rol, horas y criterio de done, está en `tareas_tecnicas.md`.

## 4. Lo que no entra y por qué

**HU-03 (cargar catálogo) y HU-02 (generación y parques).** Al descomponerlas, las dos sumaban unas 30 horas más; con ellas el sprint quedaba en más de 60 horas contra 42.75 de capacidad. Además, al revisar los criterios encontré una dependencia que no habíamos visto en S03-A1: en RF-28-AC-1 la generación se crea asociada a una versión del catálogo ("catalogo-2023-v1"), así que HU-02 no se puede probar sin HU-03. Para el Sprint 2 el orden es HU-03 y luego HU-02. Lo registro como pronóstico, no como compromiso.

**Las pantallas de inicio de sesión.** El calendario del curso pone el scaffolding de frontend en las semanas 7 y 8. Construir React ahora, antes de esa base, es hacer dos veces el trabajo. Como Product Owner dividí HU-01:

- HU-01 conserva la API y sus seis criterios de aceptación, que se verifican contra endpoints.
- HU-23 "Pantallas de inicio de sesión y recuperación de contraseña" (3 SP, prioridad Alta, épica E1) entra al backlog y se planea en el primer sprint con frontend.

Sé que separar API y pantalla rompe la idea de rebanada vertical. Lo acepto en este sprint porque el calendario del curso manda el orden de las capas y porque los criterios de RF-26 ya están escritos contra respuestas de la API (códigos 401, mensajes exactos), no contra elementos de pantalla.

## 5. Evaluación de la propuesta del agente

El agente propuso este goal: "Establecer la base funcional del SGPIS: los usuarios pueden autenticarse y Coordinación AMPIP puede configurar la generación 2027, dar de alta parques y cargar el catálogo de criterios". Para cumplirlo seleccionó HU-01, HU-02 y HU-03, con 15 story points.

### ¿Es realista?

No. Tiene tres problemas.

- **Capacidad.** El agente supuso que un equipo nuevo completa "alrededor de 5 story points por integrante" en su primer sprint. Esa cifra no sale de nuestros datos ni de ninguna regla del curso; el agente la eligió para que la suma diera 15 y coincidiera con su selección. Cuando descompuse las tres historias en tareas, sumaban más de 60 horas, contra 42.75 disponibles.
- **Trabajo invisible.** No contó el esqueleto técnico. Sin repo configurado, base de datos, migraciones y CI no se puede entregar ninguna de las tres historias, y ese trabajo son 17 horas.
- **Dependencia.** Puso HU-02 antes que HU-03 sin notar que la generación necesita una versión del catálogo.

### ¿Está enfocada en entregar valor?

A medias. Las historias apuntan a valor real, pero el goal no se puede medir: "establecer la base funcional" no dice qué tiene que funcionar ni cómo se comprueba. El goal final se verifica con cinco evidencias concretas (sección 1).

### Cambios

| Aspecto | Propuesta del agente | Versión final | Razón |
|---|---|---|---|
| Goal | "Establecer la base funcional" | API con autenticación, control por rol y bitácora, verificable con cinco evidencias | Medible y alineado a lo que el sistema protege. |
| Unidad de capacidad | 15 SP por regla genérica | 42.75 horas netas | Sin velocidad histórica, las horas son la única medida que podemos defender. |
| Selección | HU-01, HU-02, HU-03 | HT-01 y HU-01 | Capacidad real y dependencia HU-03 → HU-02. |
| Frontend | Incluido implícitamente | Separado en HU-23 | Calendario del curso (semanas 7 y 8). |
| Plan si sobra tiempo | Adelantar HU-04 | Adelantar las primeras tareas de HU-03 | HU-03 es la siguiente en dependencia; HU-04 no desbloquea nada en el Sprint 2. |

## 6. Roles SCRUM en este Sprint Planning

**Product Owner: Ángel Kociankowski.** Tengo la relación con AMPIP y conozco el programa como consultor, así que el valor lo defiendo yo. En esta planeación decidí el porqué del sprint (el goal), qué entra y qué sale del Sprint Backlog, y la división de HU-01 en HU-01 y HU-23.

**Scrum Master: rota cada sprint entre Leonardo Cossío y Erick Ramírez.** Quien lo tenga en el Sprint 1 se define en la reunión de arranque. Facilita los eventos, cuida el timebox, vigila que la definición de terminado se cumpla y quita bloqueos. No asigna tareas ni decide alcance.

**Developers: los tres integrantes.** Deciden el cómo: la descomposición en tareas, las horas de cada una y cuánto trabajo cabe en el sprint. Nadie les asigna trabajo; cada quien toma tareas de la columna "Sprint actual" del tablero.

En un equipo de tres, yo soy Product Owner y también Developer, y ese doble papel tiene un riesgo: que el PO presione las estimaciones para meter más alcance. Lo controlamos así: las horas de cada tarea las propone quien la va a hacer, y si el sprint se pasa de capacidad, el que recorta alcance soy yo, nunca las horas.

La actividad pide registrar cada tarea con un responsable "con el rol indicado". En el tablero cada tarea lleva una etiqueta de rol (`rol:backend`, `rol:qa`, `rol:devops`, `rol:seguridad`) y queda asignada a mí, como pide la instrucción. Al arrancar el sprint, cada integrante se reasigna las tareas que toma.

## 7. Riesgos

| Riesgo | Señal temprana | Qué hacemos |
|---|---|---|
| El esqueleto técnico se alarga (Docker, Alembic, CI en tres máquinas distintas) | T-01 o T-06 sin cerrar al terminar la primera semana | El SM lo levanta en la daily; T-01 y T-06 se trabajan en pareja; se cede T-14 si hace falta. |
| Las pruebas que dependen del tiempo (bloqueo de 15 minutos, inactividad de 60) quedan frágiles | Pruebas que pasan local y fallan en CI | Reloj simulado desde el diseño (criterio de done de T-13); ninguna prueba usa sleep. |
| Disponibilidad desigual por otras materias | Tareas sin dueño a mitad del sprint | Las tareas de backend son intercambiables; la holgura de 3.75 h absorbe una ausencia corta. |
| Datos reales de AMPIP en el repositorio | Un CSV o fixture con nombres reales de parques | La definición de terminado prohíbe datos reales en el repo; se revisa en cada PR. |

## 8. Eventos del sprint

| Evento | Cuándo | Duración |
|---|---|---|
| Sprint Planning | 3 y 4 de octubre (esta entrega) | Incluida en S03 |
| Daily asíncrona | Lunes, miércoles y viernes, en el canal del equipo: qué terminé, qué sigue, qué me bloquea | 10 min por integrante |
| Sprint Review | Al cierre, en la sesión de equipo de la semana 5 | 1 h |
| Retrospectiva | Inmediatamente después de la revisión | 45 min |
