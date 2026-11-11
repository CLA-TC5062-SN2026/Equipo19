# Code review y evaluación SOLID

**Actividad:** S09_A1, Auditoría de calidad de código
**Proyecto:** SGPIS (AMPIP)
**Equipo 19:** Ángel Sebastián Kociankowski Montelongo · Leonardo Cossío Dinorín · Erick Noé Ramírez Olvera
**Curso:** TC5062, Análisis, diseño y construcción de software (Gpo 10)
**Agente utilizado:** Claude (Anthropic), como revisor técnico automatizado

Los números de línea corresponden al código original de `main`, antes de las refactorizaciones, que es el código que revisamos. Los hallazgos CR-01 a CR-04 ya están corregidos; su antes y después completo, con las pruebas, está en `refactorizacion.md`.

## 1. Archivo revisado: `backend/app/routers/parques.py`

Elegimos `parques.py` porque el parque es el recurso principal de SGPIS: cada expediente, criterio, evidencia y dictamen cuelga de él. Las métricas del análisis estático apuntan al mismo archivo:

| Métrica | `parques.py` | Comparación |
|---|---|---|
| Índice de mantenibilidad (radon) | 31.6 | El más bajo de los 30 módulos de `app/` |
| Funciones con complejidad C o peor (radon) | 3: `actualizar_parque` D (24), `reemplazar_tipo_pi` C (17), `listar_parques` C (11) | Le sigue `permisos.py` con 2; los demás tienen 1 o ninguna |
| Líneas | 306 | El router más largo; le sigue `usuarios.py` con 263 |
| Reglas del SRS que implementa | RF-02, RF-11, RF-29, RF-30, RF-31 | Alta, baja, tipo de PI, fechas del programa, parques históricos |

Revisamos también las funciones de `servicios.py` que `parques.py` llama y que definen su comportamiento (`parque_a_esquema`, `obtener_o_crear_desarrollador`), porque varios hallazgos del archivo nacen ahí.

## 2. Resumen de hallazgos

| ID | Tipo | Ubicación | Severidad | Estado |
|---|---|---|---|---|
| CR-01 | Función con múltiples responsabilidades (SRP) | `parques.py:120-179` | Importante | Corregido (R3) |
| CR-02 | Código duplicado (DRY) | `parques.py:123-130`, `usuarios.py:177-182`, `configuracion.py:40-44`, `plan_trabajo.py:134-138` | Importante | Corregido en parques y usuarios (R3); propuesto en los otros dos |
| CR-03 | Consultas dentro de un ciclo (N+1) y función con dos responsabilidades | `parques.py:57` y `servicios.py:131-173` | Importante | Corregido (R2) |
| CR-04 | Manejo inadecuado de excepciones bajo concurrencia | `parques.py:90`, `:151` y `servicios.py:77-84` | Crítico | Corregido (R1) |
| CR-05 | Función demasiado larga (SRP) y conversión duplicada | `parques.py:182-255` | Importante | Propuesto |
| CR-06 | Error ignorado en silencio y bitácora incorrecta | `parques.py:156-161` | Importante | Propuesto |
| CR-07 | Validación insuficiente de un dato de auditoría | `parques.py:135` y `esquemas.py:143` | Importante | Propuesto |
| CR-08 | Nombres poco descriptivos o fuera de convención | `parques.py:10`, `:116`, `:269-293`, `:223-241` | Menor | Propuesto |

La sección 3.9 registra lo que revisamos de seguridad sin encontrar problema, con la evidencia de cada revisión.

## 3. Hallazgos

### CR-01. `actualizar_parque` hace cinco cosas distintas

**Dónde:** `parques.py:120-179`. Complejidad ciclomática 20 según flake8 y 24 según radon; 20 ramas según pylint.

**Problema.** El endpoint de `PATCH /parques/{parqueId}` hace todo en una sola función de 60 líneas:

1. valida el cuerpo: que traiga algún campo y que no haya nulos prohibidos (líneas 123-130);
2. valida la baja: no se da de baja un parque histórico y la baja exige motivo (132-136);
3. decide si necesita el expediente y lo busca (138-144);
4. aplica cinco cambios posibles a dos tablas distintas, `parque` y `expediente` (146-164);
5. registra la baja y los cambios en la bitácora (165-177).

**Por qué es un problema.** Cada responsabilidad tiene un motivo de cambio diferente. Si AMPIP cambia la regla de la baja (RF-29), hay que modificar una función que también decide fechas del programa (RF-30) y parques históricos (RF-31), y el riesgo de romper una regla al tocar otra es real porque las ramas se cruzan: `exp` se calcula en la línea 144 y se usa en las líneas 157 y 162 con significados distintos según el tipo de registro del parque. Además, el orden de los errores importa (un histórico sin motivo debe dar 409 y no 422) y en la función ese orden no se ve: hay que deducirlo leyendo las ramas. Antes de esta auditoría, ocho de esas ramas no tenían ninguna prueba (líneas 125, 127, 130, 134, 141-142, 151-152, 154-155 y 159-160 sin cobertura).

**Código corregido** (implementado en R3; versión completa en `refactorizacion.md`):

```python
def _validar_actualizacion(parque: Parque, cuerpo: e.ParqueUpdate) -> set[str]:
    """Reglas que no consultan la base. Devuelve los campos enviados."""
    campos = exigir_campos(
        cuerpo, ("estado", "nombre", "desarrollador", "region"), {"estado": "El único estado admitido es inactivo"}
    )
    if cuerpo.estado == "inactivo":
        if parque.estado == "historico":
            raise ErrorAPI(409, "transicion_invalida", "Un parque histórico no se puede dar de baja")
        if not cuerpo.motivo:
            raise ErrorAPI(422, "motivo_requerido", "Indique el motivo de la baja del parque")
    return campos

# _expediente_para_fechas, _aplicar_datos_generales, _aplicar_fechas_programa y _dar_de_baja: una regla cada una

@router.patch("/parques/{parqueId}", response_model=e.Parque)
def actualizar_parque(parqueId: uuid.UUID, cuerpo: e.ParqueUpdate, db: DB, actor: Actor):
    parque = obtener_parque(db, parqueId)
    campos = _validar_actualizacion(parque, cuerpo)
    exp = _expediente_para_fechas(db, parque, campos)
    cambios = _aplicar_datos_generales(db, parque, cuerpo) + _aplicar_fechas_programa(parque, exp, cuerpo, campos)
    if cuerpo.estado == "inactivo":
        _dar_de_baja(db, actor, parque, cuerpo.motivo)
    if cambios:
        registrar_bitacora(db, actor, "actualizar_parque", recurso_tipo="parque", recurso_id=parque.id,
                           parque_id=parque.id, detalle=", ".join(cambios))
    db.commit()
    return parque_a_esquema(db, parque)
```

El endpoint queda en complejidad 3, ninguna función auxiliar pasa de 6 y el orden de las reglas se lee de arriba abajo.

### CR-02. La misma validación de PATCH está copiada en cuatro endpoints

**Dónde:** `parques.py:123-130`, `usuarios.py:177-182`, `configuracion.py:40-44` y `plan_trabajo.py:134-138`.

En parques y en usuarios el bloque es idéntico salvo la lista de campos:

```python
# parques.py:123-130 (usuarios.py:177-182 cambia solo la tupla por ("nombre", "rol", "estado"))
campos = cuerpo.model_fields_set
if not campos:
    raise ErrorAPI(422, "datos_invalidos", "Indique al menos un campo a actualizar")
...
for campo in ("nombre", "desarrollador", "region"):
    if campo in campos and getattr(cuerpo, campo) is None:
        raise ErrorAPI(422, "datos_invalidos", f"El campo {campo} no admite nulo")
```

En `configuracion.py` y `plan_trabajo.py` es la misma regla escrita otra vez, con otro texto:

```python
# configuracion.py:40-44
if not campos:
    raise ErrorAPI(422, "datos_invalidos", "Indique al menos un parámetro a cambiar")
if any(getattr(cuerpo, c) is None for c in campos):
    raise ErrorAPI(422, "datos_invalidos", "Los parámetros no admiten nulo")

# plan_trabajo.py:134-138
if not campos:
    raise ErrorAPI(422, "datos_invalidos", "Indique el responsable o la fecha comprometida")
if any(getattr(cuerpo, c) is None for c in campos):
    raise ErrorAPI(422, "datos_invalidos", "Los campos del renglón no admiten nulo")
```

**Por qué es un problema.** Es la misma regla en todos los PATCH del API: cuerpo vacío o nulo en un campo obligatorio responde 422 `datos_invalidos`. Está escrita cuatro veces y con tres redacciones distintas, así que el frontend recibe un mensaje diferente para el mismo error según el recurso. Ninguno de esos textos lo fija el SRS ni el contrato (los buscamos en `SRS_equipo.md` y en `openapi_equipo.yaml`): las diferencias son accidentales. Cada PATCH nuevo vuelve a copiar la regla, y un cambio, por ejemplo agregar el nombre del campo en `detalles`, hay que hacerlo en cuatro lugares. pylint no detectó ninguna de las copias porque ninguna llega a las cuatro líneas idénticas seguidas que su detector exige.

**Código corregido.** En R3 creamos `exigir_campos` en `comun.py` y la usan los dos endpoints que tenían el bloque idéntico:

```python
def exigir_campos(cuerpo: BaseModel, no_nulos: Sequence[str], mensajes: Mapping[str, str] | None = None) -> set[str]:
    campos = set(cuerpo.model_fields_set)
    if not campos:
        raise ErrorAPI(422, "datos_invalidos", "Indique al menos un campo a actualizar")
    for campo in no_nulos:
        if campo in campos and getattr(cuerpo, campo) is None:
            mensaje = (mensajes or {}).get(campo, f"El campo {campo} no admite nulo")
            raise ErrorAPI(422, "datos_invalidos", mensaje)
    return campos

# usuarios.py
campos = exigir_campos(cuerpo, ("nombre", "rol", "estado"))
```

El parámetro `mensajes` existe porque en parques el nulo en `estado` tiene un texto propio, y `no_nulos` se revisa en orden para conservar exactamente qué error sale primero cuando vienen varios nulos. Configuración y plan de trabajo no los migramos todavía: pasarlos a `exigir_campos` cambia el texto que hoy ve el frontend, y esa decisión la tomamos como equipo (propuesta: un solo texto, "Indique al menos un campo a actualizar", y el nombre del campo en `detalles`).

### CR-03. El listado de parques hace ocho consultas por parque

**Dónde:** `parques.py:57` llama a `parque_a_esquema` (`servicios.py:131-173`) una vez por cada parque.

```python
# parques.py:57
items = [parque_a_esquema(db, parque) for parque in db.scalars(q)]

# servicios.py:131-173, por cada parque:
exp = expediente_actual(db, parque.id)                       # 1
desarrollador=nombre_desarrollador(db, parque.desarrollador_id)   # 2
tipo_pi=tipo_vigente(db, parque.id)                          # 3
gen = generacion_de(db, exp)                                 # 4
version = db.get(VersionCatalogo, gen.version_catalogo_id)   # 5
asignacion = db.scalars(select(AsignacionConsultor)...)      # 6
ultima = db.scalar(select(func.max(ActualizacionAnual.fecha))...)  # 7
fase=fase_actual(db, exp)                                    # 8
```

**Por qué es un problema.** Es el patrón N+1: el número de consultas crece con el número de parques. Lo medimos contra PostgreSQL 16 con el listado completo (promedio de tres corridas; cada tiempo es la mediana de 21 llamadas):

| Parques | Sentencias SQL | Tiempo |
|---|---|---|
| 10 | 83 | 93.4 ms |
| 41 | 331 | 283.0 ms |
| 80 | 643 | 503.1 ms |

RNF-10 pide que la vista de cartera con 80 parques no tarde más de 20 % que con 41. Con el código original tardaba 78 % más, y eso con la base en la misma máquina. Con la base en otro servidor, cada una de las 643 consultas paga además la latencia de red. Hay un segundo problema de diseño: `parque_a_esquema` mezcla dos responsabilidades, consultar y armar la respuesta, y por eso no hay forma de reutilizar el armado con datos que ya se tienen.

**Código corregido** (R2). La carga y el armado quedan en funciones separadas: `_cargar_datos_de_parques` hace siete consultas para todos los parques a la vez y `_armar_parque` construye cada respuesta sin tocar la base. `parque_a_esquema` reutiliza el listado con un solo parque, así el detalle y el listado no pueden dar respuestas distintas.

```python
def _cargar_datos_de_parques(db: Session, parques: Sequence[Parque]) -> _DatosDeParques:
    """Siete consultas en total, sin importar cuántos parques sean."""
    ids = [p.id for p in parques]
    expedientes = {
        exp.parque_id: (exp, gen)
        for exp, gen in db.execute(
            select(Expediente, Generacion)
            .join(Generacion, Generacion.id == Expediente.generacion_id)
            .where(Expediente.parque_id.in_(ids))
            .order_by(Expediente.parque_id, Generacion.fecha_inicio.desc(), Generacion.nombre.desc())
            .distinct(Expediente.parque_id)      # DISTINCT ON: el expediente de la generación más reciente
        ).tuples()
    }
    # ... una consulta con IN para desarrolladores, tipos de PI, versiones, consultores, actualizaciones y fases


def parques_a_esquema(db: Session, parques: Sequence[Parque]) -> list[e.Parque]:
    if not parques:
        return []
    datos = _cargar_datos_de_parques(db, parques)
    fecha_hoy = hoy()
    return [_armar_parque(parque, datos, fecha_hoy) for parque in parques]


def parque_a_esquema(db: Session, parque: Parque) -> e.Parque:
    return parques_a_esquema(db, [parque])[0]

# parques.py
items = parques_a_esquema(db, db.scalars(q).all())
```

Resultado: 10 sentencias para cualquier número de parques (3 de autenticación y 7 de datos), y 46 ms con 80 parques en lugar de 503. El crecimiento de 41 a 80 parques bajó de 78 % a 42 % en promedio. Todavía no cumple el 20 % de RNF-10: lo que queda viene de filtrar, ordenar y paginar en memoria (`parques.py:58-69`). Eso queda como siguiente paso en `deuda_tecnica.md`.

### CR-04. Dos altas simultáneas con un desarrollador nuevo responden 409

**Dónde:** `parques.py:90` (alta) y `:151` (cambio de desarrollador) llaman a `obtener_o_crear_desarrollador`, en `servicios.py:77-84`:

```python
def obtener_o_crear_desarrollador(db: Session, nombre: str) -> Desarrollador:
    nombre = nombre.strip()
    des = db.scalars(select(Desarrollador).where(Desarrollador.nombre == nombre)).first()
    if des is None:
        des = Desarrollador(nombre=nombre)
        db.add(des)
        db.flush()
    return des
```

**Problema.** La función primero busca y después inserta. Si Coordinación AMPIP da de alta al mismo tiempo dos parques de un desarrollador que todavía no existe (por ejemplo, desde dos pestañas, al capturar la generación nueva), las dos transacciones buscan, ninguna encuentra nada y las dos insertan. La segunda choca con `uq_desarrollador_nombre` (`esquema_bd.sql:46`), SQLAlchemy lanza `IntegrityError` y el handler global (`errores.py:160-171`) responde 409 con el mensaje "La operación entra en conflicto con el estado actual del recurso".

**Por qué es un problema.** La solicitud era válida y la API la rechaza con un mensaje que el usuario no puede entender ni corregir: no hay ningún conflicto que resolver, basta con reintentar. El manejo de errores convierte una condición de carrera interna en un error de cliente. Lo reprodujimos con dos sesiones de base de datos reales (`tests/test_refactorizacion_s09.py::test_R1_...`):

```
AssertionError: la segunda alta falló: IntegrityError('(psycopg.errors.UniqueViolation) duplicate key value
violates unique constraint "uq_desarrollador_nombre"
DETAIL:  Key (nombre)=(Desarrolladora Nueva) already exists.')
```

**Código corregido** (R1). El equipo ya había resuelto el mismo problema en el contador de intentos de login (`autenticacion.py:78-85`) con `INSERT ... ON CONFLICT DO NOTHING`; aplicamos el mismo patrón:

```python
def obtener_o_crear_desarrollador(db: Session, nombre: str) -> Desarrollador:
    nombre = nombre.strip()
    consulta = select(Desarrollador).where(Desarrollador.nombre == nombre)
    des = db.scalars(consulta).first()
    if des is None:
        db.execute(
            pg_insert(Desarrollador)
            .values(nombre=nombre)
            .on_conflict_do_nothing(constraint="uq_desarrollador_nombre")
        )
        des = db.scalars(consulta).one()
    return des
```

Si otra transacción está insertando el mismo nombre, PostgreSQL espera a que confirme, el `INSERT` no hace nada y el `SELECT` siguiente, que en READ COMMITTED toma una vista nueva, ya encuentra la fila. No hace falta capturar `IntegrityError` ni reintentar.

### CR-05. `reemplazar_tipo_pi` mezcla cierre, alta y recálculo

**Dónde:** `parques.py:182-255`. 74 líneas y 19 variables locales (pylint R0914); radon C (17).

**Problema.** La función implementa RF-11 completo en un solo bloque: cierra la clasificación vigente guardando el cumplimiento del momento (196-212), crea la nueva (214-219), recalcula qué criterios dejan de ser NA y los regresa a "pendiente" con historial (221-241) y registra la bitácora (243-246). Dentro de ese bloque, la conversión de porcentaje a `Decimal` está escrita dos veces con la misma forma:

```python
vigente.porcentaje_obligatorios_al_cierre = (
    Decimal(str(total["porcentaje_obligatorios"])) if total["porcentaje_obligatorios"] is not None else None
)
vigente.porcentaje_avance_general_al_cierre = (
    Decimal(str(total["porcentaje_avance_general"])) if total["porcentaje_avance_general"] is not None else None
)
```

y la conversión inversa está escrita otras dos veces en `servicios.py:182-189` y dos más en `historial.py:55-56`.

**Por qué es un problema.** La regla RD-14 (un criterio que vuelve a aplicar regresa a "pendiente" y deja historial) está enterrada en el paso 3, a 40 líneas de la firma de la función. Quien necesite cambiarla tiene que entender primero el cierre de la clasificación, que no tiene relación con esa regla. Las conversiones repetidas son seis lugares donde alguien puede olvidar el caso `None`.

**Código corregido** (propuesto):

```python
def _a_decimal(valor: float | None) -> Decimal | None:
    return Decimal(str(valor)) if valor is not None else None


def _cerrar_clasificacion(db: Session, exp: Expediente, vigente: ClasificacionTipoPI,
                          fecha: date) -> dict[uuid.UUID, str | None]:
    """RF-11-AC-1: cierra la vigente con el cumplimiento del momento. Devuelve la marca que tenía cada criterio."""
    if fecha < vigente.fecha_desde:
        raise ErrorAPI(422, "fecha_cambio_invalida",
                       "La fecha de cambio no puede ser anterior al inicio de la clasificación vigente")
    total, _ = calcular_cumplimiento(db, exp, vigente.tipo_pi)
    marcas = {f.cp.criterio_id: f.marca for f in filas_criterios(db, exp, vigente.tipo_pi)}
    vigente.fecha_hasta = fecha
    vigente.porcentaje_obligatorios_al_cierre = _a_decimal(total["porcentaje_obligatorios"])
    vigente.porcentaje_avance_general_al_cierre = _a_decimal(total["porcentaje_avance_general"])
    db.flush()  # libera el índice único de clasificación vigente
    return marcas


def _recalcular_aplicabilidad(db: Session, exp: Expediente, tipo: str, marcas_antes: dict[uuid.UUID, str | None],
                              actor: Usuario) -> tuple[list[uuid.UUID], list[uuid.UUID]]:
    """RF-11-AC-4 y RD-14: lo que deja de ser NA regresa a pendiente con historial; lo que pasa a NA se reporta."""
    dejan_na, pasan_na = [], []
    momento = ahora()
    for fila in filas_criterios(db, exp, tipo):
        aplicaba = marcas_antes.get(fila.cp.criterio_id) in ("O", "R")
        aplica = fila.marca in ("O", "R")
        if aplica and not aplicaba:
            dejan_na.append(fila.cp.criterio_id)
            _regresar_a_pendiente(db, fila.cp, tipo, actor, momento)
        elif aplicaba and not aplica:
            pasan_na.append(fila.cp.criterio_id)
    return dejan_na, pasan_na
```

`reemplazar_tipo_pi` queda en unas 20 líneas que llaman a estas dos funciones en orden. La condición `vigente is not None` de la línea 227 se resuelve llamando a `_recalcular_aplicabilidad` solo cuando había clasificación anterior. No la implementamos en esta iteración porque tres ramas de la función no tienen prueba (líneas 189, 198 y 241: cambio al mismo tipo, fecha anterior a la vigente y criterios que pasan a NA). Primero escribimos esas pruebas de caracterización, como hicimos con `actualizar_parque`, y después movemos el código.

### CR-06. Un `null` se ignora en silencio y la bitácora registra un cambio que no hubo

**Dónde:** `parques.py:156-161`.

```python
if "fecha_termino_programa" in campos:
    if exp is not None:
        exp.fecha_termino_programa = cuerpo.fecha_termino_programa
    elif cuerpo.fecha_termino_programa is not None:
        parque.fecha_termino_historico = cuerpo.fecha_termino_programa
    cambios.append("fechaTerminoPrograma")
```

**Problema.** En un parque histórico `exp` es `None`. Si el cliente manda `{"fechaTerminoPrograma": null}`, ninguna de las dos asignaciones ocurre (la base no lo permitiría: `ck_parque_historico_datos` exige la fecha), la API responde 200 con la fecha anterior y, aun así, la línea 161 agrega `fechaTerminoPrograma` a los cambios y la bitácora queda con un registro `actualizar_parque` que dice que la fecha cambió.

**Por qué es un problema.** Es un error tragado: el cliente pidió algo imposible y recibió un 200. Y la bitácora, que según RNF-03 es la fuente de verdad de quién cambió qué, contiene un cambio falso. La prueba de caracterización `test_patch_parque_historico` documenta hoy ese comportamiento para que nadie lo cambie sin darse cuenta; esa prueba se ajusta al corregir.

**Código corregido** (propuesto), en `_aplicar_fechas_programa` después de R3:

```python
if "fecha_termino_programa" in campos:
    if exp is not None:
        exp.fecha_termino_programa = cuerpo.fecha_termino_programa
    elif cuerpo.fecha_termino_programa is None:
        raise ErrorAPI(422, "datos_invalidos",
                       "La fecha de término de un parque histórico no admite nulo")
    else:
        parque.fecha_termino_historico = cuerpo.fecha_termino_programa
    cambios.append("fechaTerminoPrograma")
```

El 422 ya está declarado en el contrato para esta operación, así que la corrección no cambia el contrato.

### CR-07. La baja acepta un motivo hecho solo de espacios

**Dónde:** `parques.py:135` (`if not cuerpo.motivo`) y `esquemas.py:143` (`motivo: str | None = Field(default=None, min_length=1)`).

**Problema.** `min_length=1` cuenta los espacios, y `not "   "` es `False`. Lo comprobamos contra la API:

```
PATCH /api/parques/{id}  {"estado": "inactivo", "motivo": "   "}
-> 200, motivoBaja = '   '
-> registro_bitacora.detalle = '   '
```

Lo mismo pasa con el motivo de cambio de tipo de PI (`esquemas.py:171`). Además, el campo no tiene longitud máxima ni en el esquema ni en el contrato.

**Por qué es un problema.** RF-29 exige el motivo de la baja precisamente para que AMPIP sepa por qué un parque salió del programa, y la restricción `ck_parque_baja_con_motivo` de la base solo comprueba que no sea `NULL`. Un motivo vacío cumple la letra de las dos validaciones y vacía de contenido la bitácora (RNF-03), que es justo el registro que se revisa cuando hay una disputa sobre una baja. La falta de longitud máxima permite guardar textos de cualquier tamaño en `parque.motivo_baja` y en `registro_bitacora.detalle`, que son `text`.

**Código corregido** (propuesto), en `esquemas.py`:

```python
from pydantic import StringConstraints

Motivo = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=500)]


class ParqueUpdate(Esquema):
    ...
    motivo: Motivo | None = None


class CambioTipoPI(Esquema):
    ...
    motivo: Motivo
```

y en `errores.py`, para que el 422 diga lo mismo que dice hoy la validación manual:

```python
("PATCH", "/api/parques/{parqueId}"): {
    "region": _REGION,
    "motivo": ("motivo_requerido", "Indique el motivo de la baja del parque"),
},
```

Comprobamos en el entorno del proyecto que `strip_whitespace=True` con `min_length=1` rechaza `"   "`. El `max_length=500` es un cambio al contrato (hoy `motivo` solo declara `minLength: 1`) y lo tenemos que acordar como equipo antes de aplicarlo.

### CR-08. Nombres que no dicen qué contienen o rompen la convención

**Dónde:**

- `parques.py:10`: `from app import esquemas as e`. En Python, `e` es por costumbre la variable de una excepción (`except ValueError as e`). En este archivo `e.Parque` es un esquema, y en `tests/test_parques.py` la variable `e` es el escenario de prueba: la misma letra significa tres cosas en el proyecto.
- `parques.py:116`, `:121`, `:183`, `:259`, `:278`, `:297`: parámetros `parqueId` y `actualizacionId` en camelCase. pylint los reporta como `invalid-name` (44 casos en todo el backend).
- `parques.py:269-293`: `a` para una `ActualizacionAnual`; `parques.py:223-241`: `f` para una fila de criterio y `cp` para un `CriterioParque`; `parques.py:65`: `lambda x:` para un parque.

**Por qué es un problema.** Los parámetros en camelCase son una decisión entendible (copian el `{parqueId}` del contrato), pero mezclan dos convenciones dentro de la misma firma: `parqueId` junto a `generacion_id` en la línea 43. Los nombres de una letra obligan a leer la asignación para saber qué hay en la variable. En `reemplazar_tipo_pi`, `f.cp.criterio_id` aparece cuatro veces y hay que recordar qué es `f` y qué es `cp` en cada una.

**Código corregido** (propuesto). Comprobamos que FastAPI acepta el alias y que el OpenAPI generado sigue publicando el parámetro como `parqueId`, así que el contrato no cambia:

```python
from fastapi import Path
from app import esquemas as esq

ParqueId = Annotated[uuid.UUID, Path(alias="parqueId")]


@router.get("/parques/{parqueId}", response_model=esq.Parque)
def obtener_parque_endpoint(parque_id: ParqueId, db: DB):
    return parque_a_esquema(db, obtener_parque(db, parque_id))


def _actualizacion_a_esquema(actualizacion: ActualizacionAnual, parque_id: uuid.UUID) -> esq.ActualizacionAnual:
    ...

for fila in filas_criterios(db, exp, cuerpo.tipo_pi):
    criterio_parque = fila.cp
    ...
```

`permisos.py` lee `request.path_params["parqueId"]`, que sale de la plantilla de la ruta y no del nombre del parámetro de Python, así que el cambio no afecta los permisos.

### 3.9 Seguridad: lo que revisamos sin encontrar problema

- Inyección SQL. Todas las consultas de `parques.py` y de las funciones de `servicios.py` que usa se construyen con expresiones de SQLAlchemy (`select(...).where(Parque.id == ...)`), que envían los valores como parámetros. No hay SQL armado con f-strings ni `text()` con datos del usuario. El parámetro `orden`, que termina en un `sorted`, se valida dos veces: con la expresión regular de `comun.py:60` y contra la lista de campos permitidos en `comun.py:83`.
- Acceso a parques ajenos (IDOR). `obtener_actualizacion_anual` (`parques.py:299-303`) busca la actualización filtrando también por `Expediente.parque_id == parqueId`, así que no se puede leer la actualización de otro parque cambiando el id en la URL. Los permisos por rol y parque se aplican antes de entrar al endpoint (`main.py:58`, `permisos.py:241`), y `verificar_mapa` impide arrancar la API si una ruta de este router no tiene entrada en `PERMISOS`.
- Exposición de datos. La respuesta `Parque` incluye `motivoBaja`. Revisamos quién la puede ver: los parques inactivos quedan fuera del listado para los roles con alcance por parque (`permisos.py:195`) y `perfiles_en_parque` no da acceso a un parque inactivo (`permisos.py:171-172`). Solo Coordinación AMPIP y el Director General ven el motivo de una baja.

## 4. Sección SOLID

Evaluamos los cinco principios en todo `backend/app/`. Para cada uno buscamos un ejemplo donde se cumple y otro donde no; marcamos un principio como respetado solo después de buscar una violación y no encontrarla.

### 4.1 Tabla de evaluación

| Principio | ¿Se respeta? | Ejemplo en el código | Propuesta de corrección |
|---|---|---|---|
| **Single Responsibility (SRP)** | Parcialmente | Se cumple a nivel de módulo: `seguridad.py` solo autentica, `errores.py` solo traduce errores al schema `Error`, `permisos.py:79-138` solo declara quién puede qué. Se viola a nivel de función: `routers/parques.py:120` (`actualizar_parque`, 5 responsabilidades, CR-01), `routers/parques.py:182` (`reemplazar_tipo_pi`, CR-05), `servicios.py:131` (`parque_a_esquema`, consulta y arma, CR-03) y `routers/usuarios.py:175` (`actualizar_usuario`, complejidad 26) | Separar cada endpoint largo en validación, aplicación y registro. Hecho en `actualizar_parque` (R3) y `parque_a_esquema` (R2); pendiente en `reemplazar_tipo_pi` y `actualizar_usuario`. |
| **Open/Closed (OCP)** | Parcialmente | Se cumple en `permisos.py:79` (`PERMISOS`): proteger una ruta nueva es agregar una entrada al mapa, sin tocar `autorizar`. Lo mismo `errores.py:55` (`TABLA_VALIDACION`). Se viola en `permisos.py:168-187` (`perfiles_en_parque`): una cadena `if/elif` por rol. Cada perfil relativo nuevo (por ejemplo, si AMPIP decidiera dar lectura a un auditor externo) obliga a abrir la función y revisar el orden de las ramas. También en `routers/parques.py:74`: `isinstance` sobre el tipo de alta. | Registro de resolvedores de perfil (sección 4.2). |
| **Liskov Substitution (LSP)** | Sí | La herencia en el backend es poca y respeta el contrato del padre. `esquemas.py:264`: `UsuarioParque(Usuario)` solo agrega `contacto_principal`; `usuarios.py:237` lo arma desde `Usuario.model_dump()` y cualquier código que espera un `Usuario` acepta un `UsuarioParque`. `errores.py:19`: `ErrorAPI(Exception)` llama a `super().__init__(mensaje)`, así que `str(exc)` y el handler genérico de `errores.py:173` funcionan igual que con cualquier `Exception`. Ningún modelo ni esquema sobrescribe métodos de su base. | Sin corrección. Riesgo a vigilar: si `ParqueCreate` y `ParqueHistoricoCreate` (`esquemas.py:116`, `:125`) llegan a heredar de una base común y `parques.py:74` sigue preguntando el tipo con `isinstance`, el código cliente estaría tratando a los subtipos como no intercambiables. |
| **Interface Segregation (ISP)** | Parcialmente | Se cumple en `comun.py:72-73`: `Paginacion` y `PaginacionSinOrden` son dos dependencias distintas, y los endpoints que no ordenan no reciben `orden`. También en `seguridad.py:181-182`: `SesionAutenticada` para `/auth/me` y `/auth/logout`, que necesitan la sesión, y `UsuarioAutenticado` para el resto, que solo necesita al usuario. Se viola en `comun.py:129` (`registrar_bitacora`): exige un `Usuario` completo del ORM y solo usa `actor.id` y `actor.rol` (`comun.py:143-144`). Y en `servicios.py`: un módulo de 357 líneas con cinco temas (búsquedas, armado de respuestas, criterios, cumplimiento, fases) del que 12 módulos importan piezas distintas. | Un `Protocol` con solo lo que la bitácora usa, y dividir `servicios.py` por tema (sección 4.2). |
| **Dependency Inversion (DIP)** | Parcialmente | Se cumple en `comun.py:42`: `DB = Annotated[Session, Depends(get_db)]`; los endpoints reciben la sesión por inyección y no saben cómo se crea. La autenticación (`seguridad.py:170-182`) y la autorización (`main.py:58`) también llegan como dependencias. Se viola en `routers/operacion.py:24`: `/salud` abre `SessionLocal()` directamente y se salta `get_db`, así que `app.dependency_overrides` no lo alcanza en pruebas. Y en `routers/usuarios.py:76` y `seguridad.py:68`, `:76`: llaman a `get_settings()` dentro de la función en lugar de recibir la configuración. | Inyectar `DB` en `/salud` y `Settings` por `Depends` (sección 4.2). Los routers dependen de SQLAlchemy directamente (`parques.py:48`, `select(Parque)`); lo dejamos así a propósito, ver la nota en 4.2. |

### 4.2 Cambios concretos para la siguiente iteración

**SRP.** Ya separamos `actualizar_parque` (R3) y `parque_a_esquema` (R2). En el siguiente sprint seguimos con `reemplazar_tipo_pi` (propuesta completa en CR-05) y con `actualizar_usuario` (`usuarios.py:175`), que después de R3 sigue en complejidad 22 según radon. Para `actualizar_usuario` el corte es el mismo que en parques: `_validar_cambio_de_rol` (APPI necesita parque, gerente necesita desarrollador, APPI y consultor del mismo parque son incompatibles), `_aplicar_baja` (cierra asignaciones, quita el contacto principal, revoca sesiones) y el registro en bitácora. El criterio de aceptación es que flake8 deje de reportar C901 en las dos funciones y que pasen las pruebas de RF-03, RF-11, RF-29 y RF-34.

**OCP.** Cambiar la cadena `if/elif` de `perfiles_en_parque` por un registro de funciones, una por perfil relativo:

```python
ResolvedorPerfil = Callable[[Session, Usuario, Parque], bool]

RESOLVEDORES: dict[str, ResolvedorPerfil] = {
    APPI_DEL_PARQUE: lambda db, u, p: u.rol == APPI and u.parque_id == p.id,
    CONSULTOR_ASIGNADO: lambda db, u, p: u.rol == CONSULTOR and _tiene_asignacion_vigente(db, u.id, p.id),
    CONSULTOR_COMITE: lambda db, u, p: u.rol == CONSULTOR and _tiene_comite_abierto(db, u.id, p.id),
    GERENTE_DEL_DESARROLLADOR: lambda db, u, p: (
        u.rol == GERENTE and u.desarrollador_id is not None and p.desarrollador_id == u.desarrollador_id),
}


def perfiles_en_parque(db: Session, usuario: Usuario, parque: Parque, buscados: frozenset[str]) -> set[str]:
    if parque.estado == "inactivo":
        return set()
    return {perfil for perfil in buscados & set(RESOLVEDORES) if RESOLVEDORES[perfil](db, usuario, parque)}
```

Un perfil nuevo es una entrada nueva en `RESOLVEDORES` y `autorizar` no cambia. Además, con el parámetro `buscados` solo se evalúan los perfiles que la ruta admite: hoy, para un consultor, se consultan siempre la asignación y el comité aunque la ruta acepte solo uno de los dos.

**ISP.** Que la bitácora pida solo lo que usa:

```python
class ActorBitacora(Protocol):
    id: uuid.UUID
    rol: str


def registrar_bitacora(db: Session, actor: ActorBitacora, accion: str, *, ...) -> None:
```

`Usuario` cumple el protocolo sin cambios, y los scripts (`semilla.py`, `alta_inicial.py`) y un futuro worker pueden registrar con un objeto propio sin cargar un usuario de la base. Por otro lado, `servicios.py` se divide en `servicios/expediente.py` (expediente vigente, tipo de PI, fases), `servicios/cumplimiento.py` (RF-08) y `servicios/respuestas.py` (armado de esquemas), para que `permisos.py` dependa solo de `expediente.py` y no de todo el módulo.

**DIP.** En `/salud`, recibir la sesión como cualquier otro endpoint:

```python
@router.get("/salud", response_model=e.Salud, responses={503: {"model": e.Salud}})
def obtener_salud(db: DB):
    ...
```

con el `try` alrededor de las consultas, para que un fallo de conexión siga respondiendo 503. Y la configuración por dependencia: `Config = Annotated[Settings, Depends(get_settings)]` en `comun.py`, recibida en `_encolar_invitacion` y en las funciones de `seguridad.py` que hoy la leen por su cuenta.

Nota sobre los repositorios: los routers construyen consultas de SQLAlchemy directamente, y un DIP estricto pediría una interfaz de repositorio entre el router y el ORM. No la proponemos. Las pruebas ya corren contra un PostgreSQL real clonado por prueba (`tests/conftest.py`) y el sistema no va a cambiar de motor de base de datos (la decisión de stack fija PostgreSQL 16). Una capa de repositorios duplicaría cada consulta sin ningún beneficio que hoy podamos señalar. La introducimos cuando aparezca una segunda implementación real, por ejemplo, almacenamiento de evidencias en S3 contra almacenamiento local.
