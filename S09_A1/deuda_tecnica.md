# Reflexión sobre deuda técnica

**Actividad:** S09_A1, Auditoría de calidad de código
**Proyecto:** SGPIS (AMPIP)
**Equipo 19:** Ángel Sebastián Kociankowski Montelongo (Product Owner) · Leonardo Cossío Dinorín (Scrum Master) · Erick Noé Ramírez Olvera
**Curso:** TC5062, Análisis, diseño y construcción de software (Gpo 10)
**Agente utilizado:** Claude (Anthropic), como revisor técnico automatizado

Los números de línea citados son del código original de `main`, antes de las refactorizaciones.

## 1. ¿Cuánta deuda técnica tiene el proyecto y cómo la medimos?

### La cifra

Hoy el backend de SGPIS tiene unas 33 horas de deuda técnica pendiente, después de pagar 8 horas en esta actividad (R1, R2, R3 y las pruebas de caracterización). Con la capacidad neta que medimos en el Sprint 1, 42.75 horas por sprint para los tres, eso equivale a tres cuartas partes de un sprint completo sin entregar nada nuevo.

La cifra sale del método SQALE (Letouzey, 2012), que mide la deuda en el tiempo que cuesta corregir cada incumplimiento y no en número de avisos. El método pide tres cosas: una lista de reglas que definen el código correcto para el proyecto, un costo de corrección por regla y la suma de esos costos. Nuestras reglas son las de `clasificacion_problemas.md` y los hallazgos de `code_review.md`. Los costos los estimamos nosotros, por grupo, a partir de lo que nos tomaron las tres refactorizaciones de esta semana:

| Origen | Deuda pendiente | Horas |
|---|---|---|
| Análisis estático | I-1: dividir `reemplazar_tipo_pi`, `actualizar_usuario` y `_leer_csv` (con sus pruebas de caracterización) | 8 |
| | I-4: tipar como `Literal` las columnas ENUM de los 36 modelos | 4 |
| | I-5: anotar `db: Session` en 28 funciones | 1.5 |
| | I-2 e I-3: unificar la consulta de asignación vigente; registrar en el log la excepción de `/salud` | 1 |
| | M-1, M-2 y el resto de menores: docstrings de `servicios.py`, alias de parámetros de ruta, formato y código muerto | 5 |
| Code review | CR-02 restante, CR-06 y CR-07 (este último con su cambio de contrato) | 2 |
| | Lo que quedó de R2: filtros, orden y paginación de `GET /parques` en SQL para cumplir RNF-10 | 3 |
| Proceso | Lo que promete la Definition of Done y no existe: CI en GitHub Actions (H2, H7, I2) | 4 |
| | Migraciones con Alembic (H3) | 4 |
| | Ajustar la DoD a las herramientas que sí usamos (dice `ruff`, usamos pylint, flake8 y mypy) | 0.5 |
| **Total** | | **33** |

Las horas son una estimación del equipo y tienen error, pero el orden de magnitud y la distribución son confiables. Una cuarta parte de la deuda (8.5 de 33 horas) está en el proceso: lo acordamos en la Definition of Done y no lo construimos.

### Indicadores

El backend tiene 4,355 líneas en `app/`, 94 % de cobertura y una calificación de pylint de 8.83. Con esos tres números, el proyecto parecía sano. La auditoría encontró un defecto crítico (CR-04: altas válidas rechazadas con 409) y un incumplimiento de un requisito no funcional (CR-03: RNF-10). Ninguna de las cuatro herramientas los reportó: los encontramos leyendo el código contra el SRS y escribiendo pruebas para los casos que las herramientas no ven. La cobertura tampoco ayudaba: el 94 % del total escondía que ocho ramas de la función más compleja nunca se habían ejecutado en una prueba.

Por eso proponemos medir con cinco indicadores:

| Indicador | Herramienta | Hoy | Qué detecta |
|---|---|---|---|
| Horas de corrección pendientes (índice SQALE) | Tabla de arriba, mantenida como issues con etiqueta `deuda-tecnica` | 33 h | El costo total, comparable con la capacidad del sprint |
| Mensajes por severidad (crítico, importante, menor) | `scripts/calidad.sh` y la clasificación | 0 / 22 / 299 al inicio; 314 mensajes en total después de las refactorizaciones (321 antes) | Si la deuda de código crece o baja de un sprint a otro |
| Funciones con complejidad mayor que 10 | flake8 C901 y radon | 4 → 3 | Los puntos donde un cambio es más caro y más riesgoso |
| Errores de mypy | mypy | 30 → 29 | Cuánto código queda fuera de la verificación de tipos |
| Cobertura de las funciones críticas, revisada rama por rama | `pytest --cov` con `--cov-report=term-missing` | 94 % total; 0 % en 8 ramas de `actualizar_parque` antes de esta actividad | Ramas sin prueba en lo que más cambia |

Y un sexto que no sale de ninguna herramienta: cuántos puntos de la Definition of Done se cumplen de verdad en el repositorio. De los cuatro que dependen del CI y de las migraciones (H2, H3, H7 e I2), hoy no se cumple ninguno.

## 2. ¿Qué deuda generamos a propósito y cuál sin darnos cuenta?

Fowler (2009) separa la deuda en deliberada e inadvertida, y cada una en prudente o imprudente. Al clasificar la nuestra así encontramos que la deliberada estaba casi toda documentada y que la inadvertida venía de un mismo hueco en el proceso.

### Deliberada y prudente: documentada y con momento de pago definido

| Decisión | Dónde quedó escrita | Qué nos ahorró | Cuándo se paga |
|---|---|---|---|
| Calcular el atraso de criterios al consultar, porque el worker de revisión diaria no existe | `README.md` ("Decisiones provisionales"); `servicios.py:220-225` | Construir y operar un proceso programado antes de tener funcionalidad que revisar | Cuando entre el worker (RNF-12) |
| Dejar las invitaciones en la tabla `mensaje_correo` sin un proceso que las envíe | `README.md`; `usuarios.py:74-75` | Integrar un proveedor de correo en el sprint de autenticación | Con el mismo worker |
| Cargar el catálogo desde CSV con categoría `seguridad` por omisión y nombres "Estándar N" | `README.md`; `catalogo.py:26-28` | Esperar el catálogo real de AMPIP, que no podemos usar sin autorización | Cuando AMPIP autorice el catálogo 2023 |
| No declarar `relationship()` en el ORM y escribir cada consulta a mano | Docstring de `modelos.py` | Aprender las opciones de carga de SQLAlchemy al mismo tiempo que el dominio | No es deuda mientras alguien revise las consultas en ciclos; ver CR-03 |
| Ordenar y paginar en memoria los listados con campos calculados (`comun.ordenar_lista`, `comun.paginar`) | Docstring de `ordenar_lista` | Escribir en SQL el orden por campos que no son columnas (por ejemplo, `atrasado`) | Antes de la prueba de carga de RNF-10 y RNF-17 |

En estos cinco casos la decisión fue razonable para un equipo de tres personas con 8 a 9 horas por semana, y cada una dice por qué existe. Es la deuda que describe Cunningham (1992) cuando introduce el término: código que se entrega sabiendo que no es el definitivo, con la intención de volver a él.

### Deliberada e imprudente: una fecha de pago que no se cumplió

El caso más claro es la integración continua. El objetivo del Sprint 1 decía que la API debía correr "en las máquinas de los tres integrantes y en GitHub Actions". La Definition of Done promete `ruff` en Actions (H2), migraciones de Alembic que el CI aplica (H3), la suite en verde en Actions (H7, I2), y en su sección 4 dice que la integración continua se construye en la tarea T-06. El repositorio no tiene carpeta `.github/`, ni Alembic, ni configuración de `ruff`.

Lo aplazamos a propósito para avanzar con los endpoints, y la regla temporal ("quien abre el PR corre `uv run pytest` en local y pega la salida") era sensata mientras fuera temporal. El error fue no volver a ella: la tarea T-06 estaba en el tablero del Sprint 1 y el código llegó a la semana 9 sin CI, mientras la DoD seguía describiendo comprobaciones que no existían. Una deuda deliberada necesita dueño y fecha en el tablero, y hay que revisarla cuando esa fecha pasa. Esa es la deuda que más nos costó en esta actividad, porque sin análisis estático en el CI la deuda inadvertida se acumuló sin que nadie la viera.

### Inadvertida: la encontramos en esta auditoría

| Deuda | Cómo entró | Evidencia |
|---|---|---|
| Condición de carrera al crear el desarrollador (CR-04) | Se escribió "buscar y luego insertar", que es la forma obvia y funciona con un solo usuario. El mismo equipo ya había resuelto el problema en el login con `ON CONFLICT`, pero no lo aplicó aquí porque nadie conectó los dos casos. | `servicios.py:77-84` contra `autenticacion.py:78-85` |
| Ocho consultas por parque en el listado (CR-03) | Efecto combinado de dos decisiones deliberadas (sin `relationship()` y armar cada respuesta por separado) que nadie midió juntas. Cada consulta, revisada sola, era correcta. | 643 sentencias con 80 parques |
| Funciones que crecieron sin que nadie midiera su complejidad: `actualizar_parque` D (24), `actualizar_usuario` D (26), `reemplazar_tipo_pi` C (17) | Las correcciones de las revisiones de S05-S06 se aplicaron dentro de las funciones existentes; el código tiene 14 marcas de esas revisiones (`[C-01]`, `[S-01]`, `[D-19]`...). En `reemplazar_tipo_pi`, la regla RD-14 (`[D-19]`) quedó a 40 líneas del inicio de la función. Sin una métrica de complejidad en el proceso, nadie vio cuándo cruzaron el umbral. | radon antes de R3 |
| La misma validación de PATCH en cuatro lugares, con tres textos distintos (CR-02) | Cada endpoint se escribió por separado, sin una función común de la cual partir. | `parques.py`, `usuarios.py`, `configuracion.py`, `plan_trabajo.py` |
| Columnas ENUM tipadas como `str` y 28 funciones con `db` sin tipo | El backend lo generó un agente y lo revisamos contra el SRS (`revision_sql.md`, `revision_seguridad.md`): reglas de negocio, permisos, restricciones. No corrimos mypy: la revisión se centró en qué hacía el código y nadie revisó cómo estaba escrito. | 13 de los 30 errores de mypy |
| Motivo de baja aceptado con solo espacios (CR-07) | `min_length=1` parecía suficiente y nadie probó con un texto en blanco. | Comprobado contra la API: 200 y bitácora vacía |

Las seis tienen la misma causa: no había un paso del proceso que revisara la calidad del código como tal. Las revisiones que sí hicimos (contra el SRS, contra el contrato y de seguridad) encontraron los problemas que buscaban, y ninguna buscaba concurrencia, consultas en ciclo, complejidad ni tipos.

## 3. ¿Cómo integramos el análisis de calidad y la evaluación SOLID en SCRUM?

La propuesta tiene que caber en 8 a 9 horas por persona por semana. Por eso cada punto dice en qué evento de SCRUM ocurre, quién lo hace y cuánto cuesta.

### 3.1 La Definition of Done solo promete lo que el CI comprueba

El primer cambio es corregir la DoD para que no prometa lo que no existe. Proponemos reemplazar H2 y agregar dos puntos:

| # | Punto | Cómo se comprueba |
|---|---|---|
| H2 | `scripts/calidad.sh` no agrega mensajes nuevos de severidad crítica o importante respecto a la línea base del sprint, y ningún error nuevo de mypy. | Job `calidad` en GitHub Actions (abajo). |
| H18 | Ninguna función nueva o modificada en el PR tiene complejidad ciclomática mayor que 10. | flake8 C901 en el mismo job. |
| H19 | Antes de modificar una función sin cobertura, el PR agrega primero pruebas de caracterización de su comportamiento actual, en un commit aparte. | Revisión del PR: el commit de pruebas va antes y pasa sobre el código anterior. |

H19 sale directamente de esta actividad: sin las 7 pruebas de caracterización, R3 habría cambiado el orden de los errores de `PATCH /parques` sin que ninguna prueba lo notara.

### 3.2 Un CI que no deja crecer la deuda (tarea T-06, por fin)

Con 321 mensajes de partida, la regla realista es que no aumenten. El job compara contra una línea base guardada en el repositorio, y la línea base solo puede bajar:

```yaml
# .github/workflows/calidad.yml
name: calidad
on: [pull_request]
jobs:
  calidad:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16
        env: { POSTGRES_HOST_AUTH_METHOD: trust }
        ports: ["5432:5432"]
        options: --health-cmd pg_isready --health-interval 5s --health-retries 10
    defaults: { run: { working-directory: backend } }
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v5
      - run: uv sync
      - run: sudo apt-get install -y postgresql-client
      - run: uv run pytest                         # H7: suite completa contra PostgreSQL 16
      - run: bash scripts/calidad.sh > calidad.txt || true
      - run: uv run python scripts/comparar_linea_base.py calidad.txt calidad_base.json   # H2 y H18
      - uses: actions/upload-artifact@v4
        with: { name: calidad, path: backend/calidad.txt }
```

`comparar_linea_base.py` cuenta los mensajes por grupo de la clasificación y falla si algún grupo crítico o importante sube, o si la calificación de pylint baja de la base (hoy 8.87). Cuando un PR baja un número, el mismo PR actualiza `calidad_base.json`. Estimamos 4 horas para el workflow y el script, que es la partida de proceso más cara de la tabla de la sección 1.

### 3.3 La evaluación SOLID entra en la revisión del PR

Los hallazgos de esta auditoría se convierten en preguntas de la plantilla de PR, que el revisor (H15, otro integrante) contesta antes de aprobar:

- **SRP.** ¿La función nueva o modificada tiene una sola razón para cambiar? Si el PR agrega una regla de negocio a una función que ya tiene otra, ¿se extrajo? (CR-01, CR-05)
- **OCP.** ¿El cambio agregó un `if/elif` por rol, por tipo o por estado? ¿Podía ser una entrada en un mapa, como `PERMISOS`? (`perfiles_en_parque`)
- **ISP.** ¿La función pide un objeto completo del ORM cuando usa uno o dos atributos? (`registrar_bitacora`)
- **DIP.** ¿El código abre su propia sesión de base de datos o lee la configuración global, en lugar de recibirla como dependencia? (`/salud`)
- **DRY.** ¿Esta validación, consulta o mensaje ya existe en otro router? (CR-02 y la consulta de asignación vigente)
- **Consultas.** ¿Hay una consulta dentro de un ciclo? (CR-03)
- **Concurrencia.** ¿Hay un "buscar y luego insertar" sobre una columna única? (CR-04)

LSP no entra en la lista: con la poca herencia que usamos, una pregunta por PR sería ruido. Lo revisamos en la retrospectiva si alguien introduce una jerarquía nueva.

### 3.4 La deuda vive en el backlog y tiene capacidad reservada

| Evento | Qué pasa con la deuda | Quién |
|---|---|---|
| Durante el sprint | Quien toma un atajo a propósito abre en ese momento un issue `deuda-tecnica` con el hallazgo, la estimación en horas y el sprint en que se paga. Si no tiene fecha, no se acepta el atajo. Es la regla que nos faltó con el CI. | Developer |
| Refinamiento | Los issues de deuda se estiman igual que las historias. Si una historia toca una función con C901 mayor que 10, la historia incluye su tarea de refactorización. | Equipo; prioriza el PO |
| Sprint Planning | Se reservan 6 horas de las 42.75 netas (14 %) para deuda. Con 33 horas pendientes, el saldo actual se paga en seis sprints sin dejar de entregar funcionalidad. El PO puede subir la reserva cuando la deuda bloquea un requisito, como RNF-10 hoy. | PO y Scrum Master |
| Sprint Review | Junto al incremento se muestran los cinco indicadores de la sección 1 y su tendencia. AMPIP no necesita ver mensajes de pylint, pero sí que la vista de cartera cumple RNF-10. | Scrum Master |
| Retrospectiva | Se revisa cada deuda deliberada abierta en el sprint: ¿sigue teniendo sentido?, ¿se mantiene la fecha? Una deuda deliberada que pasa dos retrospectivas sin pagarse sube de prioridad. | Equipo |

### 3.5 Lo que entra en el siguiente sprint

Con la reserva de 6 horas más la prioridad que le damos como PO a lo que afecta requisitos, el siguiente sprint lleva:

| Tarea | Horas | Por qué primero |
|---|---|---|
| T-06: workflow de calidad y línea base (3.2) | 4 | Sin esto, todo lo demás vuelve a crecer sin que lo veamos. |
| Filtros y paginación de `GET /parques` en SQL | 3 | Es lo único que falta para cumplir RNF-10, y la vista de cartera es la pantalla principal de AMPIP. |
| CR-07: motivo con `strip_whitespace` y longitud máxima, y el cambio al contrato | 1 | Es la integridad de la bitácora (RNF-03). |
| Actualizar la DoD (3.1) | 0.5 | Que diga lo que se comprueba. |
| **Total** | **8.5** | 6 de la reserva más 2.5 que el PO toma de la capacidad de historias. |

## Referencias

Cunningham, W. (1992). The WyCash portfolio management system. En *Addendum to the Proceedings on Object-Oriented Programming Systems, Languages, and Applications (OOPSLA '92)* (pp. 29-30). ACM. https://doi.org/10.1145/157709.157715

Fowler, M. (2009, 14 de octubre). *Technical debt quadrant*. martinfowler.com. https://martinfowler.com/bliki/TechnicalDebtQuadrant.html

Letouzey, J.-L. (2012). The SQALE method for evaluating technical debt. En *2012 Third International Workshop on Managing Technical Debt (MTD)* (pp. 31-36). IEEE. https://doi.org/10.1109/MTD.2012.6225997
