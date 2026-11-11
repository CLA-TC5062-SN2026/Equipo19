# Refactorización guiada

**Actividad:** S09_A1, Auditoría de calidad de código
**Proyecto:** SGPIS (AMPIP)
**Equipo 19:** Ángel Sebastián Kociankowski Montelongo · Leonardo Cossío Dinorín · Erick Noé Ramírez Olvera
**Curso:** TC5062, Análisis, diseño y construcción de software (Gpo 10)
**Agente utilizado:** Claude (Anthropic), como revisor técnico automatizado

## 1. Qué refactorizamos y por qué esos tres

De los ocho hallazgos del code review y de las violaciones de la evaluación SOLID elegimos los tres que, con el código como está hoy, más afectan a un usuario de SGPIS o al equipo que lo mantiene:

| # | Hallazgo | Por qué está entre los tres primeros |
|---|---|---|
| R1 | CR-04: condición de carrera al crear el desarrollador | Es el único defecto crítico de la auditoría: una solicitud válida recibe 409. |
| R2 | CR-03: ocho consultas por parque en `GET /parques` | Incumple RNF-10 (degradación máxima de 20 % de 41 a 80 parques) y está en la pantalla que AMPIP más va a usar, la vista de cartera. |
| R3 | CR-01 y CR-02: `actualizar_parque` con cinco responsabilidades y la validación del PATCH duplicada | La función más compleja del archivo más complejo, y la violación de SRP más clara de la tabla SOLID. Unimos los dos hallazgos porque la corrección de CR-02 sale del mismo corte. |

Dejamos fuera CR-05 (`reemplazar_tipo_pi`) porque tres de sus ramas no tienen pruebas y no queríamos mover código sin red. CR-06 y CR-07 cambian el comportamiento visible de la API y uno de ellos requiere cambiar el contrato, así que primero los acordamos como equipo.

## 2. Cómo trabajamos

Una refactorización no cambia lo que hace el código, y para demostrarlo hacen falta pruebas que pasen antes y después. La suite del equipo tenía 82 pruebas y 94 % de cobertura, pero al revisar la cobertura de las funciones que íbamos a tocar encontramos huecos justo ahí: los filtros `generacionId` y `atrasado` del listado y ocho ramas de `actualizar_parque` no tenían ninguna prueba. Por eso el orden fue este:

1. Pruebas de caracterización (`tests/test_caracterizacion_s09.py`, 7 pruebas). Fijan lo que el código hace hoy en las ramas sin cobertura, incluido un comportamiento que consideramos incorrecto (CR-06), para que la refactorización no lo cambie sin que nadie se entere. Es la técnica de Feathers (2004) para modificar código que no tiene pruebas suficientes. Las 7 pasan sobre el código original.
2. Pruebas que reproducen los defectos (`tests/test_refactorizacion_s09.py`, 2 pruebas). Sobre el código original fallan: R1 con `UniqueViolation` y R2 con "19 consultas con 2 parques y 99 con 12".
3. Un commit por refactorización, con la suite completa corriendo después de cada uno.

| Paso | Mensaje del commit | Pruebas |
|---|---|---|
| 1 | S09_A1: configura pylint, flake8, mypy y bandit para el backend | 82 pasan |
| 2 | S09_A1: pruebas de caracterización y pruebas que reproducen CR-03 y CR-04 | 89 pasan, 2 fallan (las de R1 y R2, a propósito) |
| 3 | R1 (CR-04): obtener_o_crear_desarrollador con INSERT ... ON CONFLICT DO NOTHING | 90 pasan, 1 falla (la de R2) |
| 4 | R2 (CR-03): parques_a_esquema arma el listado con consultas fijas | 91 pasan |
| 5 | R3 (CR-01, CR-02): actualizar_parque dividido por responsabilidad; exigir_campos compartido | 91 pasan |
| 6 | R2: separa la carga (_cargar_datos_de_parques) del armado (_armar_parque) | 91 pasan |
| 7 | S09_A1: medición del listado con 21 llamadas por tamaño | 91 pasan |

Los mensajes de la tabla están abreviados; los completos, con el hash de cada commit en el repositorio donde trabajamos, están en `evidencia/commits.txt`. Al subir los cambios a GitHub con los parches (`git am`), cada paso conserva su mensaje, pero el hash cambia.

Al final corrimos aparte solo las 82 pruebas originales sobre el código refactorizado y pasan las 82 (`evidencia/pruebas_originales_despues.txt`), igual que sobre el código original (`evidencia/pruebas_codigo_original.txt`). Las salidas completas de pytest están en `evidencia/pruebas_antes.txt` (paso 2, con las dos pruebas de los defectos fallando) y `evidencia/pruebas_despues.txt` (código final), y el diff de `app/` en `evidencia/refactorizacion.diff`. El código de las pruebas nuevas está en `evidencia/pruebas_nuevas/`.

Todas las pruebas corren contra PostgreSQL 16 real (una base clonada por prueba) y cada respuesta HTTP se valida contra `openapi_equipo.yaml`. Si una refactorización hubiera cambiado el formato de una respuesta, la prueba habría fallado aunque el código de estado fuera correcto.

## 3. R1: alta del desarrollador sin condición de carrera

R1 corrige CR-04 en `app/servicios.py`. Es la corrección de un defecto, así que sí altera el comportamiento: una solicitud que antes fallaba con 409 ahora responde 201.

### Antes (`servicios.py:77-84`)

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

### Después (`servicios.py:81-99`)

```python
def obtener_o_crear_desarrollador(db: Session, nombre: str) -> Desarrollador:
    """Devuelve el desarrollador con ese nombre y lo crea si no existe.

    [R1, S09_A1] El alta va con INSERT ... ON CONFLICT DO NOTHING, igual que el contador de intentos de login
    (autenticacion._contador). Si otra transacción está creando el mismo nombre, PostgreSQL espera a que confirme y
    el INSERT no hace nada; el SELECT siguiente ya ve la fila confirmada. Antes, buscar y luego insertar dejaba una
    ventana en la que dos altas simultáneas chocaban con uq_desarrollador_nombre y la API respondía 409."""
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

### Alternativas que consideramos

| Opción | Por qué no / por qué sí |
|---|---|
| Capturar `IntegrityError` dentro de un `SAVEPOINT` (`db.begin_nested()`) y volver a buscar | Funciona, pero usa una excepción para el flujo normal y obliga a manejar el savepoint en cada llamada. |
| Subir el aislamiento de la transacción a `SERIALIZABLE` | Cambia el comportamiento de todas las consultas de la solicitud para resolver una sola, y obliga a reintentar transacciones completas. |
| `INSERT ... ON CONFLICT DO NOTHING` y volver a leer | Elegida. Es atómico en PostgreSQL, no lanza excepciones y es el patrón que el equipo ya usa en `autenticacion._contador` para el contador de intentos de login, así que no agrega una forma nueva de resolver lo mismo. |

### Justificación técnica

Con el código original, dos transacciones que crean el mismo desarrollador hacen las dos el `SELECT`, ninguna ve la fila de la otra porque todavía no está confirmada, y las dos hacen `INSERT`. La segunda espera el candado del índice único `uq_desarrollador_nombre` y, cuando la primera confirma, falla con `UniqueViolation`. Con `ON CONFLICT DO NOTHING`, la segunda espera igual, pero al confirmarse la primera su `INSERT` no hace nada y no falla; el `SELECT` siguiente, que en READ COMMITTED toma una vista nueva, encuentra la fila recién confirmada.

Mantuvimos el `SELECT` inicial para que el caso común (el desarrollador ya existe) siga costando una consulta.

### Verificación

`test_R1_dos_altas_simultaneas_con_el_mismo_desarrollador_nuevo` abre dos sesiones reales: la primera crea el desarrollador sin confirmar, la segunda intenta crearlo en otro hilo y la prueba espera hasta ver en `pg_stat_activity` que la segunda quedó bloqueada en el candado. Solo entonces confirma la primera. La espera no depende de tiempos fijos, como pide el punto H8 de la Definition of Done.

| | Antes | Después |
|---|---|---|
| Segunda alta simultánea | `IntegrityError` → 409 | Devuelve el mismo desarrollador |
| Filas en `desarrollador` con ese nombre | 1 | 1 |

## 4. R2: listado de parques con consultas fijas

R2 corrige CR-03 en `app/servicios.py` y `app/routers/parques.py`. Es una refactorización de rendimiento y las respuestas de la API no cambian.

### Antes (`servicios.py:117-173` y `parques.py:57`)

```python
def fase_actual(db: Session, exp: Expediente) -> str | None:
    filas = db.execute(
        select(FaseExpediente.fase, FaseExpediente.estado, CatalogoFase.orden)
        .join(CatalogoFase, CatalogoFase.clave == FaseExpediente.fase)
        .where(FaseExpediente.expediente_id == exp.id)
        .order_by(CatalogoFase.orden)
    ).all()
    for fase, estado, _ in filas:
        if estado == "en_proceso":
            return fase
    iniciadas = [f for f, estado, _ in filas if estado != "pendiente"]
    return iniciadas[-1] if iniciadas else None


def parque_a_esquema(db: Session, parque: Parque) -> e.Parque:
    exp = expediente_actual(db, parque.id)
    datos: dict = dict(
        id=parque.id,
        tipo_registro=parque.tipo_registro,
        nombre=parque.nombre,
        desarrollador=nombre_desarrollador(db, parque.desarrollador_id),
        tipo_pi=tipo_vigente(db, parque.id),
        region=parque.region,
        estado=parque.estado,
        fecha_alta=parque.fecha_alta,
        fecha_ultimo_dictamen=parque.fecha_ultimo_dictamen,
        motivo_baja=parque.motivo_baja,
        contacto_principal_id=parque.contacto_principal_id,
        fecha_termino_programa=parque.fecha_termino_historico,
        atrasado_actualizacion=False,
    )
    if exp is not None:
        gen = generacion_de(db, exp)
        version = db.get(VersionCatalogo, gen.version_catalogo_id)
        asignacion = db.scalars(
            select(AsignacionConsultor).where(
                AsignacionConsultor.expediente_id == exp.id, AsignacionConsultor.vigente_hasta.is_(None)
            )
        ).first()
        ultima = db.scalar(
            select(func.max(ActualizacionAnual.fecha))
            .join(Expediente, Expediente.id == ActualizacionAnual.expediente_id)
            .where(Expediente.parque_id == parque.id)
        )
        datos.update(
            generacion_id=gen.id,
            fase=fase_actual(db, exp),
            version_catalogo=version.nombre if version else None,
            consultor_asignado_id=asignacion.consultor_id if asignacion else None,
            fecha_termino_programa=exp.fecha_termino_programa,
            fecha_proxima_actualizacion=exp.fecha_proxima_actualizacion,
            fecha_ultima_actualizacion=ultima,
            atrasado_actualizacion=bool(
                exp.fecha_proxima_actualizacion and exp.fecha_proxima_actualizacion < hoy()
            ),
        )
    return e.Parque(**datos)
```

```python
# parques.py:57
items = [parque_a_esquema(db, parque) for parque in db.scalars(q)]
```

### Después (`servicios.py:131-256` y `parques.py:71`)

```python
def _fase_actual_de(fases: Sequence[tuple[str, str]]) -> str | None:
    """Fase en proceso; si ninguna lo está, la última iniciada. `fases` = [(fase, estado)] en el orden del catálogo."""
    for fase, estado in fases:
        if estado == "en_proceso":
            return fase
    iniciadas = [fase for fase, estado in fases if estado != "pendiente"]
    return iniciadas[-1] if iniciadas else None


@dataclass
class _DatosDeParques:
    """Lo necesario para armar la respuesta de varios parques, cargado con una consulta por dato."""

    expedientes: dict[uuid.UUID, tuple[Expediente, Generacion]]  # por parque: expediente vigente y su generación
    desarrolladores: dict[uuid.UUID, str]  # por desarrollador
    tipos: dict[uuid.UUID, str]  # por parque: tipo de PI vigente
    versiones: dict[uuid.UUID, str]  # por versión del catálogo
    consultores: dict[uuid.UUID, uuid.UUID]  # por expediente: consultor con asignación vigente
    ultimas: dict[uuid.UUID, date]  # por parque: fecha de la última actualización anual
    fases: dict[uuid.UUID, list[tuple[str, str]]]  # por expediente: [(fase, estado)] en orden del catálogo


def _cargar_datos_de_parques(db: Session, parques: Sequence[Parque]) -> _DatosDeParques:
    """Siete consultas en total, sin importar cuántos parques sean."""
    ids = [p.id for p in parques]
    # Expediente vigente de cada parque: el de la generación más reciente (mismo criterio que expediente_actual).
    expedientes = {
        exp.parque_id: (exp, gen)
        for exp, gen in db.execute(
            select(Expediente, Generacion)
            .join(Generacion, Generacion.id == Expediente.generacion_id)
            .where(Expediente.parque_id.in_(ids))
            .order_by(Expediente.parque_id, Generacion.fecha_inicio.desc(), Generacion.nombre.desc())
            .distinct(Expediente.parque_id)
        ).tuples()
    }
    ids_exp = [exp.id for exp, _ in expedientes.values()]
    fases: dict[uuid.UUID, list[tuple[str, str]]] = defaultdict(list)
    for exp_id, fase, estado in db.execute(
        select(FaseExpediente.expediente_id, FaseExpediente.fase, FaseExpediente.estado)
        .join(CatalogoFase, CatalogoFase.clave == FaseExpediente.fase)
        .where(FaseExpediente.expediente_id.in_(ids_exp))
        .order_by(FaseExpediente.expediente_id, CatalogoFase.orden)
    ).tuples():
        fases[exp_id].append((fase, estado))
    return _DatosDeParques(
        expedientes=expedientes,
        desarrolladores=dict(db.execute(
            select(Desarrollador.id, Desarrollador.nombre)
            .where(Desarrollador.id.in_({p.desarrollador_id for p in parques if p.desarrollador_id}))
        ).tuples().all()),
        tipos=dict(db.execute(
            select(ClasificacionTipoPI.parque_id, ClasificacionTipoPI.tipo_pi)
            .where(ClasificacionTipoPI.parque_id.in_(ids), ClasificacionTipoPI.fecha_hasta.is_(None))
        ).tuples().all()),
        versiones=dict(db.execute(
            select(VersionCatalogo.id, VersionCatalogo.nombre)
            .where(VersionCatalogo.id.in_({gen.version_catalogo_id for _, gen in expedientes.values()}))
        ).tuples().all()),
        consultores=dict(db.execute(
            select(AsignacionConsultor.expediente_id, AsignacionConsultor.consultor_id)
            .where(AsignacionConsultor.expediente_id.in_(ids_exp), AsignacionConsultor.vigente_hasta.is_(None))
        ).tuples().all()),
        ultimas=dict(db.execute(
            select(Expediente.parque_id, func.max(ActualizacionAnual.fecha))
            .join(Expediente, Expediente.id == ActualizacionAnual.expediente_id)
            .where(Expediente.parque_id.in_(ids))
            .group_by(Expediente.parque_id)
        ).tuples().all()),
        fases=fases,
    )


def _armar_parque(parque: Parque, datos: _DatosDeParques, fecha_hoy: date) -> e.Parque:
    """Respuesta de un parque a partir de datos ya cargados; no consulta la base."""
    # dict[str, Any] como en la versión anterior: los modelos ORM tipan las columnas ENUM como str y mypy no
    # aceptaría str donde el esquema pide Literal (ver clasificacion_problemas.md, grupo I-4).
    campos: dict[str, Any] = {
        "id": parque.id,
        "tipo_registro": parque.tipo_registro,
        "nombre": parque.nombre,
        "desarrollador": datos.desarrolladores.get(parque.desarrollador_id) if parque.desarrollador_id else None,
        "tipo_pi": datos.tipos.get(parque.id),
        "region": parque.region,
        "estado": parque.estado,
        "fecha_alta": parque.fecha_alta,
        "fecha_ultimo_dictamen": parque.fecha_ultimo_dictamen,
        "motivo_baja": parque.motivo_baja,
        "contacto_principal_id": parque.contacto_principal_id,
        "fecha_termino_programa": parque.fecha_termino_historico,
        "atrasado_actualizacion": False,
    }
    if parque.id in datos.expedientes:
        exp, gen = datos.expedientes[parque.id]
        campos.update({
            "generacion_id": gen.id,
            "fase": _fase_actual_de(datos.fases[exp.id]),
            "version_catalogo": datos.versiones.get(gen.version_catalogo_id),
            "consultor_asignado_id": datos.consultores.get(exp.id),
            "fecha_termino_programa": exp.fecha_termino_programa,
            "fecha_proxima_actualizacion": exp.fecha_proxima_actualizacion,
            "fecha_ultima_actualizacion": datos.ultimas.get(parque.id),
            "atrasado_actualizacion": bool(
                exp.fecha_proxima_actualizacion and exp.fecha_proxima_actualizacion < fecha_hoy
            ),
        })
    return e.Parque(**campos)


def parques_a_esquema(db: Session, parques: Sequence[Parque]) -> list[e.Parque]:
    """Respuesta de varios parques con un número fijo de consultas.

    [R2, S09_A1] Antes cada parque costaba ocho consultas (expediente, desarrollador, tipo de PI, generación,
    versión, asignación, última actualización y fases): GET /parques con 80 parques ejecutaba 643 sentencias.
    Ahora la carga (_cargar_datos_de_parques) y el armado (_armar_parque) están separados: siete consultas para
    todos los parques y el armado en memoria."""
    if not parques:
        return []
    datos = _cargar_datos_de_parques(db, parques)
    fecha_hoy = hoy()
    return [_armar_parque(parque, datos, fecha_hoy) for parque in parques]


def parque_a_esquema(db: Session, parque: Parque) -> e.Parque:
    """Un solo parque: misma construcción que el listado, así las dos respuestas no pueden divergir."""
    return parques_a_esquema(db, [parque])[0]
```

```python
# parques.py:71
items = parques_a_esquema(db, db.scalars(q).all())  # [R2] consultas fijas, no por parque
```

### Alternativas que consideramos

| Opción | Por qué no / por qué sí |
|---|---|
| Declarar `relationship()` en los modelos y usar `selectinload` | `modelos.py` dice explícitamente que no se definen relaciones y que las consultas se escriben a mano. Cambiar esa decisión afecta a los 36 modelos para resolver un problema de una función. |
| Una sola consulta grande con `JOIN` y subconsultas laterales | Es la opción con menos viajes a la base, pero junta siete reglas distintas (expediente vigente, asignación vigente, fase actual...) en un SQL difícil de leer y de probar por partes. |
| Una consulta por dato para todos los parques (`IN`) y armado en memoria | Elegida. Siete consultas sin importar el número de parques, cada una equivalente a la que ya existía, así que la regla de cada dato se reconoce comparando con el código anterior. |

### Justificación técnica

La primera versión de R2 (paso 4) metía las siete consultas y el armado en una sola función de 20 variables locales, y pylint la marcó con `too-many-locals` cuando corrimos `scripts/calidad.sh` sobre el código ya refactorizado. Era el mismo problema que CR-03 le señalaba a `parque_a_esquema`: consultar y armar en el mismo lugar. La segunda versión (paso 6) lo separa en `_cargar_datos_de_parques`, que hace las siete consultas y devuelve un `_DatosDeParques`, y `_armar_parque`, que construye la respuesta de un parque sin tocar la base.

El expediente vigente se resuelve con `DISTINCT ON (expediente.parque_id)` ordenado por `fecha_inicio` y `nombre` de la generación en forma descendente, que es exactamente el criterio de `expediente_actual` (`servicios.py:45-53`). La fase actual pasó a una función pura, `_fase_actual_de`, con la misma lógica que tenía `fase_actual`. `parque_a_esquema` ahora llama a `parques_a_esquema` con un solo parque: el detalle y el listado salen del mismo código y no pueden dar respuestas distintas. Una de las pruebas de caracterización compara cada elemento del listado contra `GET /parques/{id}` para comprobarlo.

Dejamos el diccionario `campos` de `_armar_parque` anotado como `dict[str, Any]`, igual que en la versión anterior (`datos: dict`). Con un tipo más estricto, mypy marca 8 errores nuevos; la causa está en `modelos.py`, que tipa las columnas ENUM como `str` (grupo I-4 de la clasificación).

### Verificación

`test_R2_el_listado_de_parques_no_hace_consultas_por_parque` cuenta las sentencias SQL de una llamada con 2 y con 12 parques y exige que sean iguales. Antes: 19 y 99. Después: 10 y 10.

Medición con `tests/medicion_s09.py` (listado completo contra PostgreSQL 16 local). Corrimos la medición tres veces antes y tres después; cada tiempo es la mediana de 21 llamadas y la tabla muestra el promedio de las tres corridas (los valores de cada corrida están en `evidencia/medicion_antes.txt` y `evidencia/medicion_despues.txt`):

| Parques | Sentencias antes | Sentencias después | Tiempo antes | Tiempo después |
|---|---|---|---|---|
| 10 | 83 | 10 | 93.4 ms | 23.3 ms |
| 41 | 331 | 10 | 283.0 ms | 32.5 ms |
| 80 | 643 | 10 | 503.1 ms | 46.1 ms |
| Crecimiento de 41 a 80 | | | **+78 %** (corridas: +74 % a +81 %) | **+42 %** (corridas: +21 % a +59 %) |

RNF-10 todavía no se cumple: el tiempo crece en promedio 42 % y el límite es 20 %. La medición después de R2 varía mucho entre corridas porque la diferencia entre 41 y 80 parques ya es de solo 10 a 20 ms, pero ninguna corrida bajó del 20 %. Lo que queda es lineal y está en `listar_parques`: filtra por `generacionId` y `atrasado`, ordena y pagina en memoria después de armar todos los parques. La corrección es aplicar esos filtros y la paginación en SQL y armar solo la página pedida; la registramos como deuda en `deuda_tecnica.md`. La base estaba en la misma máquina que la API; con la base en otro servidor, la diferencia entre 643 y 10 viajes de red pesa mucho más que en esta medición.

## 5. R3: `actualizar_parque` por responsabilidades y validación compartida

R3 corrige CR-01 y CR-02 en `app/routers/parques.py`, `app/routers/usuarios.py` y `app/comun.py`. Es una refactorización de estructura: el comportamiento no cambia, incluido el orden de los errores y el de los registros de bitácora.

### Antes (`parques.py:120-179`)

```python
@router.patch("/parques/{parqueId}", response_model=e.Parque)
def actualizar_parque(parqueId: uuid.UUID, cuerpo: e.ParqueUpdate, db: DB, actor: Actor):
    parque = obtener_parque(db, parqueId)
    campos = cuerpo.model_fields_set
    if not campos:
        raise ErrorAPI(422, "datos_invalidos", "Indique al menos un campo a actualizar")
    if "estado" in campos and cuerpo.estado is None:
        raise ErrorAPI(422, "datos_invalidos", "El único estado admitido es inactivo")
    for campo in ("nombre", "desarrollador", "region"):
        if campo in campos and getattr(cuerpo, campo) is None:
            raise ErrorAPI(422, "datos_invalidos", f"El campo {campo} no admite nulo")

    if cuerpo.estado == "inactivo":
        if parque.estado == "historico":
            raise ErrorAPI(409, "transicion_invalida", "Un parque histórico no se puede dar de baja")
        if not cuerpo.motivo:
            raise ErrorAPI(422, "motivo_requerido", "Indique el motivo de la baja del parque")

    exp = None
    if campos & {"fecha_termino_programa", "fecha_proxima_actualizacion"}:
        if parque.tipo_registro == "historico":
            if "fecha_proxima_actualizacion" in campos:
                raise ErrorAPI(422, "parque_historico", "Un parque histórico no tiene actualización anual")
        else:
            exp = exigir_expediente(db, parque)

    cambios = []
    if cuerpo.nombre is not None:
        parque.nombre = cuerpo.nombre.strip()
        cambios.append("nombre")
    if cuerpo.desarrollador is not None:
        parque.desarrollador_id = obtener_o_crear_desarrollador(db, cuerpo.desarrollador).id
        cambios.append("desarrollador")
    if cuerpo.region is not None:
        parque.region = cuerpo.region
        cambios.append("region")
    if "fecha_termino_programa" in campos:
        if exp is not None:
            exp.fecha_termino_programa = cuerpo.fecha_termino_programa
        elif cuerpo.fecha_termino_programa is not None:
            parque.fecha_termino_historico = cuerpo.fecha_termino_programa
        cambios.append("fechaTerminoPrograma")
    if "fecha_proxima_actualizacion" in campos and exp is not None:
        exp.fecha_proxima_actualizacion = cuerpo.fecha_proxima_actualizacion
        cambios.append("fechaProximaActualizacion")
    # Repetir la baja de un parque ya inactivo no tiene efectos.
    if cuerpo.estado == "inactivo" and parque.estado != "inactivo":
        parque.estado = "inactivo"
        parque.motivo_baja = cuerpo.motivo
        registrar_bitacora(
            db, actor, "baja_parque", recurso_tipo="parque", recurso_id=parque.id, parque_id=parque.id,
            detalle=cuerpo.motivo,
        )
    if cambios:
        registrar_bitacora(
            db, actor, "actualizar_parque", recurso_tipo="parque", recurso_id=parque.id, parque_id=parque.id,
            detalle=", ".join(cambios),
        )
    db.commit()
    return parque_a_esquema(db, parque)
```

```python
# usuarios.py:174-182
@router.patch("/usuarios/{usuarioId}", response_model=e.Usuario)
def actualizar_usuario(usuarioId: uuid.UUID, cuerpo: e.UsuarioUpdate, db: DB, actor: Actor):
    u = _obtener_usuario(db, usuarioId)
    campos = cuerpo.model_fields_set
    if not campos:
        raise ErrorAPI(422, "datos_invalidos", "Indique al menos un campo a actualizar")
    for campo in ("nombre", "rol", "estado"):
        if campo in campos and getattr(cuerpo, campo) is None:
            raise ErrorAPI(422, "datos_invalidos", f"El campo {campo} no admite nulo")
```

### Después (`parques.py:134-218`)

```python
# ------------------------------------------------------------------ PATCH /parques/{parqueId}
# [R3, S09_A1] actualizar_parque tenía complejidad ciclomática 20 y hacía cinco cosas: validar el cuerpo, validar la
# baja, ubicar el expediente, aplicar los cambios y registrar la bitácora. Cada paso es ahora una función; el orden
# de los errores y de los registros de bitácora es el mismo (tests/test_caracterizacion_s09.py).
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


def _expediente_para_fechas(db: Session, parque: Parque, campos: set[str]) -> Expediente | None:
    """Las fechas del programa viven en el expediente. El histórico no tiene expediente ni actualización anual."""
    if not campos & {"fecha_termino_programa", "fecha_proxima_actualizacion"}:
        return None
    if parque.tipo_registro == "historico":
        if "fecha_proxima_actualizacion" in campos:
            raise ErrorAPI(422, "parque_historico", "Un parque histórico no tiene actualización anual")
        return None
    return exigir_expediente(db, parque)


def _aplicar_datos_generales(db: Session, parque: Parque, cuerpo: e.ParqueUpdate) -> list[str]:
    cambios = []
    if cuerpo.nombre is not None:
        parque.nombre = cuerpo.nombre.strip()
        cambios.append("nombre")
    if cuerpo.desarrollador is not None:
        parque.desarrollador_id = obtener_o_crear_desarrollador(db, cuerpo.desarrollador).id
        cambios.append("desarrollador")
    if cuerpo.region is not None:
        parque.region = cuerpo.region
        cambios.append("region")
    return cambios


def _aplicar_fechas_programa(
    parque: Parque, exp: Expediente | None, cuerpo: e.ParqueUpdate, campos: set[str]
) -> list[str]:
    cambios = []
    if "fecha_termino_programa" in campos:
        if exp is not None:
            exp.fecha_termino_programa = cuerpo.fecha_termino_programa
        elif cuerpo.fecha_termino_programa is not None:
            parque.fecha_termino_historico = cuerpo.fecha_termino_programa
        cambios.append("fechaTerminoPrograma")  # CR-06: se anota aunque el null del histórico se ignore
    if "fecha_proxima_actualizacion" in campos and exp is not None:
        exp.fecha_proxima_actualizacion = cuerpo.fecha_proxima_actualizacion
        cambios.append("fechaProximaActualizacion")
    return cambios


def _dar_de_baja(db: Session, actor: Usuario, parque: Parque, motivo: str | None) -> None:
    """Repetir la baja de un parque ya inactivo no tiene efectos."""
    if parque.estado == "inactivo":
        return
    parque.estado = "inactivo"
    parque.motivo_baja = motivo
    registrar_bitacora(
        db, actor, "baja_parque", recurso_tipo="parque", recurso_id=parque.id, parque_id=parque.id, detalle=motivo,
    )


@router.patch("/parques/{parqueId}", response_model=e.Parque)
def actualizar_parque(parqueId: uuid.UUID, cuerpo: e.ParqueUpdate, db: DB, actor: Actor):
    parque = obtener_parque(db, parqueId)
    campos = _validar_actualizacion(parque, cuerpo)
    exp = _expediente_para_fechas(db, parque, campos)
    cambios = _aplicar_datos_generales(db, parque, cuerpo) + _aplicar_fechas_programa(parque, exp, cuerpo, campos)
    if cuerpo.estado == "inactivo":
        _dar_de_baja(db, actor, parque, cuerpo.motivo)
    if cambios:
        registrar_bitacora(
            db, actor, "actualizar_parque", recurso_tipo="parque", recurso_id=parque.id, parque_id=parque.id,
            detalle=", ".join(cambios),
        )
    db.commit()
    return parque_a_esquema(db, parque)
```

```python
# comun.py:125-140
def exigir_campos(cuerpo: BaseModel, no_nulos: Sequence[str], mensajes: Mapping[str, str] | None = None) -> set[str]:
    """Reglas comunes de los PATCH (422 datos_invalidos): el cuerpo trae al menos un campo y ninguno de `no_nulos`
    viene en null. Revisa `no_nulos` en el orden dado; `mensajes` cambia el texto de un campo. Devuelve los campos
    que el cliente envió, aunque sea con null.

    [R3, S09_A1] Antes este bloque estaba copiado en parques.actualizar_parque y usuarios.actualizar_usuario."""
    campos = set(cuerpo.model_fields_set)
    if not campos:
        raise ErrorAPI(422, "datos_invalidos", "Indique al menos un campo a actualizar")
    for campo in no_nulos:
        if campo in campos and getattr(cuerpo, campo) is None:
            mensaje = (mensajes or {}).get(campo, f"El campo {campo} no admite nulo")
            raise ErrorAPI(422, "datos_invalidos", mensaje)
    return campos
```

```python
# usuarios.py:174-178
@router.patch("/usuarios/{usuarioId}", response_model=e.Usuario)
def actualizar_usuario(usuarioId: uuid.UUID, cuerpo: e.UsuarioUpdate, db: DB, actor: Actor):
    u = _obtener_usuario(db, usuarioId)
    campos = exigir_campos(cuerpo, ("nombre", "rol", "estado"))  # [R3] regla compartida con PATCH /parques
    baja = cuerpo.estado == "inactivo" and u.estado != "inactivo"
```

### Alternativas que consideramos

| Opción | Por qué no / por qué sí |
|---|---|
| Una clase `ServicioParques` con un método por paso | Mueve el problema a otro archivo sin reducirlo y agrega una capa que el resto de los routers no tiene. |
| Un objeto por tipo de cambio (nombre, desarrollador, región, fechas, baja) con una interfaz común | Sirve cuando los tipos de cambio crecen seguido. Aquí son cinco y estables; sería más código que el que reemplaza. |
| Funciones privadas en el mismo router, una por responsabilidad | Elegida. Es el corte más pequeño que separa las cinco responsabilidades de CR-01, y cada función se puede leer sin las demás. |

### Justificación técnica

Cada función tiene ahora una sola razón para cambiar:

| Función | Responsabilidad | Regla del SRS | Complejidad (radon) |
|---|---|---|---|
| `_validar_actualizacion` | Reglas del cuerpo y de la baja que no consultan la base | RF-29 | 4 |
| `_expediente_para_fechas` | Ubicar el expediente o rechazar fechas en un histórico | RF-30, RF-31 | 4 |
| `_aplicar_datos_generales` | Nombre, desarrollador y región | RF-02 | 4 |
| `_aplicar_fechas_programa` | Fecha de término y próxima actualización | RF-30 | 6 |
| `_dar_de_baja` | Baja idempotente con su registro en bitácora | RF-29, RNF-03 | 2 |
| `actualizar_parque` | Orquestar los pasos y confirmar | | 3 (antes 24) |

Hay dos detalles de equivalencia que cuidamos y que fijan las pruebas de caracterización:

- Orden de los errores. El original revisaba el nulo en `estado` antes que los nulos de `nombre`, `desarrollador` y `region`, y la regla del histórico (409) antes que la del motivo (422). `exigir_campos` revisa `no_nulos` en el orden recibido y `_validar_actualizacion` mantiene el 409 antes que el 422. `test_patch_parque_historico` manda una baja sin motivo a un histórico y exige 409.
- CR-06 queda igual a propósito. `_aplicar_fechas_programa` sigue anotando `fechaTerminoPrograma` aunque el nulo de un histórico se ignore. Corregirlo cambia el comportamiento y no es parte de esta refactorización; el comentario en el código y la prueba `test_patch_parque_historico` lo marcan para el cambio que sí lo corrija.

### Verificación

Las 7 pruebas de caracterización y las 82 originales pasan. Las métricas de la función:

| | Antes | Después |
|---|---|---|
| Complejidad de `actualizar_parque` (flake8 C901) | 20 (reportada) | Ya no se reporta (menor que 10) |
| Complejidad de `actualizar_parque` (radon) | D (24) | A (3) |
| Ramas de `actualizar_parque` (pylint R0912) | 20 | Ya no se reporta |
| Copias de la validación del PATCH | 4 (2 idénticas) | 3 (las 2 idénticas ahora usan `exigir_campos`) |
| Complejidad de `actualizar_usuario` (radon) | D (26) | D (22) |

`actualizar_usuario` bajó solo un poco porque únicamente le quitamos la validación compartida; su división completa está propuesta en la sección 4.2 de `code_review.md`.

## 6. Efecto en el análisis estático

Corrimos `scripts/calidad.sh` sobre el código final (`evidencia/output_linter_despues.txt`):

| Métrica | Antes | Después |
|---|---|---|
| Calificación de pylint | 8.83 / 10 | 8.87 / 10 |
| Mensajes de flake8 | 19 | 18 |
| Errores de mypy | 30 | 29 |
| Funciones con C901 (complejidad > 10) | 4 | 3 |
| Mensajes de las cuatro herramientas | 321 | 314 |
| Pruebas | 82 | 91 (82 originales + 7 de caracterización + 2 de los defectos) |

El cambio en los números del linter es pequeño, y es lo esperado: los dos cambios con más efecto (R1 y R2) corrigen problemas que ninguna de las cuatro herramientas había reportado.

## 7. Cómo reproducirlo

```bash
cd backend
uv sync
uv run pytest                                   # 91 pruebas; necesita PostgreSQL 16 local (README)
uv run pytest tests/medicion_s09.py -s -q       # tabla de sentencias y tiempos del listado
bash scripts/calidad.sh                         # pylint, flake8, mypy y bandit
git log --oneline                               # un commit por refactorización
```

## Referencias

Feathers, M. C. (2004). *Working effectively with legacy code*. Prentice Hall.
