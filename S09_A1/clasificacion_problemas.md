# Clasificación de problemas del análisis estático

**Actividad:** S09_A1, Auditoría de calidad de código
**Proyecto:** SGPIS (AMPIP), backend en `backend/app/`
**Equipo 19:** Ángel Sebastián Kociankowski Montelongo · Leonardo Cossío Dinorín · Erick Noé Ramírez Olvera
**Curso:** TC5062, Análisis, diseño y construcción de software (Gpo 10)
**Agente utilizado:** Claude (Anthropic), como revisor técnico automatizado
**Insumo:** `output_linter.txt`, generado sobre el código de `main` tal como estaba en GitHub el 11 de noviembre de 2026, con la configuración de las herramientas ya agregada (paso 1 de `refactorizacion.md`; la cabecera del archivo muestra el hash de ese commit en el repositorio de trabajo)

## 1. Herramientas y configuración

El backend es Python 3.12 con FastAPI, SQLAlchemy 2.0 y Pydantic v2. Corrimos las tres herramientas que pide la actividad para Python y agregamos bandit para cubrir seguridad, que pylint y flake8 casi no revisan.

| Herramienta | Qué revisa | Configuración |
|---|---|---|
| pylint 4.1.3 | Convenciones, diseño (complejidad, duplicación, número de argumentos), errores probables | `[tool.pylint]` en `pyproject.toml` |
| flake8 7.5.0 | PEP 8, imports sin uso, complejidad ciclomática (mccabe) | `.flake8` |
| mypy 2.4.1 | Tipos estáticos, con el plugin de Pydantic | `[tool.mypy]` y `[tool.pydantic-mypy]` en `pyproject.toml` |
| bandit 1.9.4 | Patrones inseguros conocidos (complemento) | Sin configuración; reglas por omisión |

Para reproducir el análisis completo: `cd backend && bash scripts/calidad.sh`. El script corre las cuatro herramientas aunque alguna encuentre problemas. Copias de la configuración y del script están en `evidencia/configuracion/`.

Tomamos tres decisiones de configuración:

1. Longitud de línea de 120, igual en pylint y en flake8. Con los valores por omisión (79 en flake8, 100 en pylint), flake8 reportó 639 líneas largas y pylint 229. El equipo escribe con nombres en español, que son largos (`fecha_proxima_actualizacion`, `porcentaje_avance_general_al_cierre`), y el código ya seguía de hecho un límite cercano a 120: el percentil 99 de longitud de línea es 116. Dejar 79 habría escondido los hallazgos útiles entre cientos de avisos de formato. Con 120 quedan 13 líneas que sí rompen la convención del propio proyecto.
2. Desactivamos `too-few-public-methods`. La regla marcaba las 89 clases de `esquemas.py` (Pydantic) y `modelos.py` (SQLAlchemy). Son contenedores de datos y no deben tener métodos públicos, así que para este tipo de código la regla da un falso positivo.
3. Corrimos mypy con el plugin `pydantic.mypy` y con opciones más estrictas que las de omisión (`check_untyped_defs`, `warn_return_any`, `strict_equality`, `warn_unreachable`). Sin el plugin, mypy reportaba como error cada esquema construido con nombres de campo en snake_case (`tipo_pi=...`), porque no entiende el `alias_generator` de Pydantic. Esos 7 errores eran falsos. Con el plugin desaparecen, y las opciones estrictas reportan funciones que devuelven `Any` y valores `str` donde el esquema pide un `Literal`.

El alcance es `app/`, que es el código de la API. Dejamos fuera `tests/`.

## 2. Números del análisis

| Herramienta | Mensajes | Calificación |
|---|---|---|
| pylint | 271 | 8.83 / 10 |
| flake8 | 19 | |
| mypy | 30 errores en 12 archivos | |
| bandit | 1 (severidad baja) | |
| **Total de mensajes** | **321** | |

Hay 17 mensajes repetidos entre herramientas: las 13 líneas largas salen en pylint (C0301) y en flake8 (E501), el import sin uso sale en los dos (W0611 y F401), y tres funciones aparecen a la vez como `too-many-branches` en pylint y como C901 en flake8. Quitando esos repetidos quedan 304 hallazgos distintos.

## 3. Criterio de clasificación

No usamos la etiqueta de cada herramienta como severidad. mypy llama "error" a todo lo que reporta, y algunos de esos errores no pueden ocurrir en ejecución. pylint pone en la misma categoría "C" una línea de 121 caracteres y una función de 20 ramas. Por eso clasificamos cada grupo por su efecto en SGPIS:

- **Crítico:** puede producir un resultado incorrecto, un error 500 o un problema de seguridad con el código como está hoy.
- **Importante:** no rompe nada hoy, pero encarece los cambios (mantenibilidad), degrada el rendimiento o deja sin protección del verificador de tipos una parte del código.
- **Menor:** estilo, nombres, documentación, o falsos positivos ya verificados.

Antes de bajar de severidad cualquier "error" de mypy, revisamos en el código si el caso que reporta puede ocurrir. La justificación de cada grupo dice qué revisamos.

## 4. Clasificación

### 4.1 Críticos: 0 de las herramientas

Ningún mensaje del análisis estático resultó crítico después de revisarlo. Cuatro candidatos parecían serlo; los revisamos uno por uno y los bajamos de nivel:

| Candidato | Por qué parecía crítico | Qué revisamos | Quedó en |
|---|---|---|---|
| `servicios.py:256`, mypy arg-type: `marca` es `str \| None` y el esquema `CriterioParque` pide `Literal['O','R']` | Si llega un criterio NA, Pydantic lanza ValidationError y la respuesta es 500 | Las dos funciones que llaman a `criterios_parque_a_esquema` (`criterios_parque.py:28` y `:57`) filtran antes `f.marca in ("O", "R")`. Hoy no puede llegar un NA | I-4 (defecto latente: la función no protege su propia precondición) |
| `operacion.py:29`, pylint W0718: `except Exception` en `/salud` | Se traga cualquier excepción | No afecta a usuarios: el endpoint responde 503 "degradado" | I-3 (afecta el monitoreo; los usuarios no lo notan) |
| `permisos.py:312`, mypy union-attr: `ruta.methods` puede ser `None` | Está dentro de `verificar_mapa`, el control que impide arrancar la API con rutas sin permisos | FastAPI asigna `{"GET"}` a toda `APIRoute` sin métodos; el `None` no ocurre en ejecución | M-9 |
| `autoevaluacion.py:97-110`, mypy union-attr (6): `a` puede ser `None` | Acceso a atributos de un objeto posiblemente nulo | `a` se crea en la línea 94 justo cuando es `None`; mypy pierde el estrechamiento porque la condición se guarda en la variable `creada` | M-9 |

Los dos defectos con más impacto de la auditoría (CR-04, crítico, y CR-03, de rendimiento) no los reportó ninguna herramienta; están en la sección 5.

### 4.2 Importantes: 22 mensajes en 5 grupos

| ID | Herramienta y regla | Mensajes | Ubicación | Justificación |
|---|---|---|---|---|
| I-1 | flake8 C901, pylint R0912 y R0914 | 7 | `routers/parques.py:121` `actualizar_parque` (C901 = 20); `routers/usuarios.py:175` `actualizar_usuario` (16); `routers/catalogo.py:49` `_leer_csv` (18); `routers/parques.py:183` `reemplazar_tipo_pi` (19 variables locales) | Son las funciones con más reglas de negocio del sistema: baja de parque (RF-29), cambio de tipo de PI (RF-11), carga del catálogo (RF-01). Con 16 a 20 caminos, cada regla nueva obliga a leer la función completa y las pruebas tienen que cubrir combinaciones que nadie enumera. radon confirma el diagnóstico: `actualizar_usuario` D (26), `actualizar_parque` D (24), `_leer_csv` D (23). `actualizar_parque` se corrigió en R3. |
| I-2 | pylint R0801 duplicate-code | 1 | `permisos.py:142-152` y `routers/usuarios.py:48-59` | Las dos funciones responden la misma pregunta: ¿el consultor tiene asignación vigente en el parque? Una cuenta filas y la otra usa `limit(1)`. La de `permisos.py` decide el acceso a la información de un parque (RNF-01). Si la regla de "asignación vigente" cambia, hay que cambiarla en dos lugares, y si solo se cambia uno, la API autoriza con una regla y valida roles incompatibles con otra. |
| I-3 | pylint W0718 broad-exception-caught | 1 | `routers/operacion.py:29` | `/salud` es lo que consulta el monitoreo externo (RNF-08). Cualquier excepción se reporta como `baseDatos: "sin_respuesta"`, sin escribir nada en el log. Un error de programación en la consulta del worker se ve igual que una caída de PostgreSQL, y quien atiende la alerta no tiene cómo distinguirlos. |
| I-4 | mypy arg-type contra `Literal` | 6 | `servicios.py:256`; `routers/historial.py:53`, `:65` (2); `routers/catalogo.py:45`; `routers/operacion.py:35` | La causa es una sola: `modelos.py` mapea las columnas ENUM de PostgreSQL como `Mapped[str]`. Los esquemas de respuesta sí usan `Literal`, así que en cada conversión ORM → esquema mypy no puede comprobar el valor. Hoy los CHECK y los ENUM de la base garantizan valores válidos, pero el verificador de tipos no protege ninguna de esas conversiones. `servicios.py:256` es además un defecto latente (sección 4.1). |
| I-5 | mypy no-any-return | 7 | `servicios.py:126`; `routers/configuracion.py:19`; `routers/usuarios.py:36`, `:45`; `routers/plan_trabajo.py:26`; `routers/autenticacion.py:85`; `routers/analisis_riesgos.py:24` | Los siete casos vienen de lo mismo: 28 funciones auxiliares reciben `db` sin anotación de tipo (`def _obtener_usuario(db, usuario_id)`), así que para mypy `db` es `Any` y todo lo que devuelve también. En esas 28 funciones el verificador de tipos no revisa nada. Las funciones que declaran `db: Session` o `db: DB` sí quedan verificadas. |

### 4.3 Menores: 299 mensajes en 10 grupos

| ID | Herramienta y regla | Mensajes | Ubicación | Justificación |
|---|---|---|---|---|
| M-1 | pylint C0115 y C0116 (docstrings) | 174 | 85 de las 89 clases están en `esquemas.py` (50) y `modelos.py` (35). Las funciones sin docstring se concentran en `servicios.py` (14), `parques.py` (8) y `comun.py` (7) | Las clases son esquemas y tablas cuyo significado ya documentan `openapi_equipo.yaml` y `esquema_bd.sql`. En los endpoints, FastAPI toma la descripción del contrato. Sí conviene documentar las funciones auxiliares de `servicios.py`, que concentran reglas de dominio. |
| M-2 | pylint C0103 invalid-name | 59 | 44 parámetros de ruta en camelCase (`parqueId` ×29, `criterioId` ×5, `renglonId` ×3...); 14 constantes `*Enum` en `modelos.py:62-75`; `SessionLocal` en `db.py:11` | Los parámetros copian el nombre del contrato (`/parques/{parqueId}`). Se corrige con `parque_id: Annotated[UUID, Path(alias="parqueId")]` sin cambiar la API (CR-08 del code review). `SessionLocal` es la convención de la documentación de SQLAlchemy. |
| M-3 | pylint C0301, flake8 E501 y E127 | 27 (14 líneas distintas) | 13 líneas de 121 a 144 caracteres, la peor en `historial.py:56`; sangría en `semilla.py:83` | Formato. Lo resuelve un formateador automático en el CI. |
| M-4 | pylint W0611, W0612, W0613; flake8 F401 | 4 (3 distintos) | Import sin uso `generacion_de` en `autoevaluacion.py:13`; variable `cp` sin uso en `plan_trabajo.py:156`; parámetro `db` sin uso en `fases.py:30` | Código muerto. No cambia el comportamiento. |
| M-5 | pylint R1735, R1721, C0207 | 5 | `dict(...)` en lugar de literal en `servicios.py:133`, `:273`, `:304`; comprensión innecesaria en `autoevaluacion.py:50`; `split` sin `maxsplit` en `alta_inicial.py:34` | Idioma de Python. Sin efecto en el resultado. |
| M-6 | pylint R0913, R0917, R0914; flake8 C901 | 11 | Endpoints con 6 a 8 parámetros: `parques.py:39`, `bitacora.py:18`, `criterios_parque.py:17`, `autoevaluacion.py:77`; `comun.py:129`; `semilla.py:50` (18 locales); `errores.py:119` (C901 = 11) | En los endpoints, los parámetros son los filtros de consulta del contrato que FastAPI inyecta. Agruparlos en una clase de dependencia sería cosmético. `registrar_bitacora` (`comun.py:129`) ya obliga a pasar sus argumentos por nombre. `semilla.py` es un script de desarrollo. En `registrar_handlers`, mccabe suma las ramas de cinco handlers anidados que, por separado, son simples. |
| M-7 | pylint W0707 raise-missing-from | 1 | `routers/catalogo.py:54` | Se pierde la excepción original (`UnicodeDecodeError`) en la traza. Al usuario le llega el 422 correcto; solo afecta la depuración. |
| M-8 | mypy var-annotated y arg-type sobre `dict(Row)` | 6 | `servicios.py:232-233`, `:245-246`; `routers/historial.py:44` (2) | mypy no infiere un `dict` a partir de `Sequence[Row]`. En ejecución funciona porque `Row` se comporta como tupla. Se corrige con `.tuples()`, como ya hace `parques_a_esquema` después de R2. |
| M-9 | mypy union-attr y arg-type (posible `None`) | 11 | `autoevaluacion.py:97-110` (6); `analisis_riesgos.py:91` (2); `permisos.py:312`; `semilla.py:85`, `:107` | Revisamos cada uno: el `None` no puede ocurrir. En `analisis_riesgos.py:91` el expediente viene de una FK; en `semilla.py` el usuario se acaba de crear con la API. mypy no logra seguir el estrechamiento de tipo en estos casos. |
| M-10 | bandit B106 | 1 | `routers/autenticacion.py:133` | Falso positivo: `tipo_token="Bearer"` es el tipo de token que fija el contrato, no una contraseña. Bandit lo marca porque el nombre del parámetro contiene "token". |

Comprobación: 0 + 22 + 299 = 321 mensajes.

## 5. Lo que las herramientas no vieron

La revisión manual de `routers/parques.py` (`code_review.md`) encontró tres problemas que ninguna de las cuatro herramientas reportó, y dos de ellos son los más graves de toda la auditoría:

| Hallazgo | Severidad | Por qué no lo detecta el análisis estático | Estado |
|---|---|---|---|
| CR-04: dos altas simultáneas de parques con un desarrollador nuevo chocan con `uq_desarrollador_nombre` y la segunda recibe 409 | Crítico | Es una condición de carrera entre dos transacciones; ninguna herramienta modela la concurrencia ni los índices únicos de la base | Reproducido con `test_R1_...` y corregido en R1 |
| CR-03: `GET /parques` ejecuta 8 consultas por parque (643 sentencias con 80 parques) | Importante (rendimiento, RNF-10) | Cada consulta, vista sola, es correcta; el problema está en llamarlas dentro de un ciclo | Medido y corregido en R2 |
| CR-07: una baja de parque con motivo `"   "` se acepta y queda en la bitácora un motivo vacío | Importante (integridad de la bitácora, RNF-03) | `min_length=1` cuenta los espacios; validar el contenido del texto es una regla de negocio | Propuesto en el code review |

El análisis estático encontró sobre todo deuda de mantenibilidad: complejidad, tipos y duplicación. Los problemas de comportamiento aparecieron al leer el código con el SRS al lado y al escribir pruebas para los casos que las herramientas no pueden ver.
