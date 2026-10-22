"""Catálogo: versiones cargadas desde CSV y criterios con su evidencia suficiente (RF-01, RF-24, RF-25)."""

import csv
import io
import uuid
from typing import Annotated

from fastapi import APIRouter, File, Form, Response, UploadFile
from sqlalchemy import func, select

from app import esquemas as e
from app.comun import DB, Actor, registrar_bitacora
from app.errores import ErrorAPI, no_encontrado
from app.modelos import Criterio, Estandar, MarcaPorTipo, Subestandar, VersionCatalogo

router = APIRouter(tags=["Catálogo"])

COLUMNAS_MARCA = {
    "marca_construccion_abierto": "construccion_abierto",
    "marca_construccion_cerrado": "construccion_cerrado",
    "marca_operacion_abierto": "operacion_abierto",
    "marca_operacion_cerrado": "operacion_cerrado",
}
COLUMNAS = ["estandar", "subestandar", "criterio", "metodo_verificacion", *COLUMNAS_MARCA]
# El CSV del contrato no trae categoría de evidencia; se asume la más restrictiva (RF-07:
# Coordinación AMPIP no abre evidencias de seguridad). Se corrige después en el catálogo.
CATEGORIA_POR_DEFECTO = "seguridad"


def _version_a_esquema(db, v: VersionCatalogo) -> e.VersionCatalogo:
    total = db.scalar(
        select(func.count(Criterio.id))
        .join(Subestandar, Subestandar.id == Criterio.subestandar_id)
        .join(Estandar, Estandar.id == Subestandar.estandar_id)
        .where(Estandar.version_catalogo_id == v.id)
    )
    return e.VersionCatalogo(
        id=v.id,
        nombre=v.nombre,
        vigente=v.estado == "activa",
        total_criterios=total or 0,
        fecha_carga=v.fecha_carga,
        cargado_por=v.cargado_por,
        estado=v.estado,
    )


def _leer_csv(contenido: bytes) -> list[dict]:
    """Valida el archivo completo; ante cualquier error lo rechaza listando cada problema."""
    try:
        texto = contenido.decode("utf-8-sig")
    except UnicodeDecodeError:
        raise ErrorAPI(422, "catalogo_invalido", "El archivo no está codificado en UTF-8")
    lector = csv.DictReader(io.StringIO(texto))
    encabezado = [c.strip() for c in (lector.fieldnames or [])]
    lector.fieldnames = encabezado

    errores: list[tuple[int, str, str]] = []  # (fila, columna, problema)
    for col in COLUMNAS:
        if col not in encabezado:
            errores.append((1, col, "falta la columna"))
    if errores:
        _rechazar(errores)

    filas = []
    for i, fila in enumerate(lector, start=2):
        valores = {c: (fila.get(c) or "").strip() for c in COLUMNAS}
        if not any(valores.values()):
            continue  # renglón vacío
        est = valores["estandar"]
        if not est.isdigit() or not 1 <= int(est) <= 10:
            errores.append((i, "estandar", f'el valor "{est}" no es un estándar del 1 al 10'))
        sub = valores["subestandar"]
        if not sub:
            errores.append((i, "subestandar", "valor vacío"))
        elif est.isdigit() and not sub.startswith(f"{int(est)}."):
            errores.append((i, "subestandar", f'el subestándar "{sub}" no pertenece al estándar {est}'))
        elif len(sub) > 16:
            errores.append((i, "subestandar", f'el subestándar "{sub}" es demasiado largo'))
        for col in ("criterio", "metodo_verificacion"):
            if not valores[col]:
                errores.append((i, col, "valor vacío"))
        for col in COLUMNAS_MARCA:
            if valores[col] not in ("O", "R", "NA"):
                errores.append((i, col, f'el valor "{valores[col]}" no es O, R ni NA'))
        filas.append(valores)

    if errores:
        _rechazar(errores)
    if not filas:
        raise ErrorAPI(422, "catalogo_invalido", "El archivo no contiene criterios")
    return filas


def _rechazar(errores: list[tuple[int, str, str]]) -> None:
    fila, col, problema = errores[0]
    raise ErrorAPI(
        422,
        "catalogo_invalido",
        f"Fila {fila}, columna {col}: {problema}",
        [{"campo": c, "problema": f"Fila {f}: {p}"} for f, c, p in errores],
    )


@router.get("/versiones-catalogo", response_model=list[e.VersionCatalogo])
def listar_versiones_catalogo(db: DB):
    versiones = db.scalars(select(VersionCatalogo).order_by(VersionCatalogo.fecha_carga.desc())).all()
    return [_version_a_esquema(db, v) for v in versiones]


@router.post("/versiones-catalogo", response_model=e.VersionCatalogo, status_code=201)
def crear_version_catalogo(
    db: DB,
    actor: Actor,
    response: Response,
    archivo: Annotated[UploadFile, File()],
    nombre_version: Annotated[str, Form(alias="nombreVersion", min_length=1, max_length=100)],
):
    nombre_version = nombre_version.strip()
    if db.scalar(select(VersionCatalogo.id).where(VersionCatalogo.nombre == nombre_version)):
        raise ErrorAPI(409, "version_catalogo_duplicada", f"Ya existe una versión del catálogo llamada {nombre_version}")
    filas = _leer_csv(archivo.file.read())

    # Una sola versión vigente: la anterior pasa a solo lectura.
    for anterior in db.scalars(select(VersionCatalogo).where(VersionCatalogo.estado == "activa")):
        anterior.estado = "solo_lectura"
    db.flush()

    version = VersionCatalogo(nombre=nombre_version, estado="activa", cargado_por=actor.id)
    db.add(version)
    db.flush()

    estandares: dict[int, Estandar] = {}
    subestandares: dict[str, Subestandar] = {}
    consecutivo: dict[str, int] = {}
    for f in filas:
        num = int(f["estandar"])
        if num not in estandares:
            estandares[num] = Estandar(version_catalogo_id=version.id, numero=num, nombre=f"Estándar {num}")
            db.add(estandares[num])
            db.flush()
        sub = f["subestandar"]
        if sub not in subestandares:
            subestandares[sub] = Subestandar(estandar_id=estandares[num].id, numero=sub, nombre=f"Subestándar {sub}")
            db.add(subestandares[sub])
            db.flush()
        consecutivo[sub] = consecutivo.get(sub, 0) + 1
        criterio = Criterio(
            subestandar_id=subestandares[sub].id,
            clave=f"{sub}.{consecutivo[sub]}",
            texto=f["criterio"],
            metodo_verificacion=f["metodo_verificacion"],
            categoria_evidencia=CATEGORIA_POR_DEFECTO,
        )
        db.add(criterio)
        db.flush()
        db.add_all(
            MarcaPorTipo(criterio_id=criterio.id, tipo_pi=tipo, marca=f[col]) for col, tipo in COLUMNAS_MARCA.items()
        )
    registrar_bitacora(
        db, actor, "cargar_version_catalogo", recurso_tipo="version_catalogo", recurso_id=version.id,
        detalle=f"{len(filas)} criterios",
    )
    db.commit()
    response.headers["Location"] = f"/api/versiones-catalogo/{version.id}"
    return _version_a_esquema(db, version)


@router.get("/versiones-catalogo/{versionId}", response_model=e.VersionCatalogo)
def obtener_version_catalogo(versionId: uuid.UUID, db: DB):
    v = db.get(VersionCatalogo, versionId)
    if v is None:
        raise no_encontrado("versión del catálogo")
    return _version_a_esquema(db, v)


def _criterio_a_esquema(db, criterio: Criterio) -> e.Criterio:
    sub = db.get(Subestandar, criterio.subestandar_id)
    est = db.get(Estandar, sub.estandar_id)
    marcas = {
        m.tipo_pi: m.marca
        for m in db.scalars(select(MarcaPorTipo).where(MarcaPorTipo.criterio_id == criterio.id))
    }
    # Sin autenticación toda consulta se trata como de Coordinación AMPIP, que ve las cuatro marcas.
    return e.Criterio(
        id=criterio.id,
        version_catalogo_id=est.version_catalogo_id,
        estandar=est.numero,
        subestandar=sub.numero,
        clave=criterio.clave,
        texto=criterio.texto,
        metodo_verificacion=criterio.metodo_verificacion,
        categoria_evidencia=criterio.categoria_evidencia,
        evidencia_suficiente=criterio.evidencia_suficiente,
        marcas=e.MarcasPorTipo(**marcas) if len(marcas) == 4 else None,
    )


@router.get("/criterios/{criterioId}", response_model=e.Criterio, response_model_exclude_none=False)
def obtener_criterio(criterioId: uuid.UUID, db: DB):
    criterio = db.get(Criterio, criterioId)
    if criterio is None:
        raise no_encontrado("criterio")
    return _criterio_a_esquema(db, criterio)


@router.patch("/criterios/{criterioId}", response_model=e.Criterio)
def actualizar_criterio(criterioId: uuid.UUID, cuerpo: e.CriterioUpdate, db: DB, actor: Actor):
    criterio = db.get(Criterio, criterioId)
    if criterio is None:
        raise no_encontrado("criterio")
    criterio.evidencia_suficiente = cuerpo.evidencia_suficiente
    registrar_bitacora(db, actor, "definir_evidencia_suficiente", recurso_tipo="criterio", recurso_id=criterio.id)
    db.commit()
    return _criterio_a_esquema(db, criterio)
