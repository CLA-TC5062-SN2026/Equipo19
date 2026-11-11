"""Usuarios: alta, cambio de rol, baja y contacto principal de la APPI (RF-03, RF-29, RF-34)."""

import hashlib
import secrets
import uuid
from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Query, Response
from sqlalchemy import func, select, update

from app import esquemas as e
from app.comun import DB, Actor, Paginacion, ahora, exigir_campos, orden_sql, registrar_bitacora
from app.config import get_settings
from app.errores import ErrorAPI, no_encontrado
from app.modelos import (
    AsignacionConsultor,
    EnlaceUnSoloUso,
    Expediente,
    MensajeCorreo,
    Parque,
    Sesion,
    Usuario,
)
from app.servicios import obtener_o_crear_desarrollador, obtener_parque, usuario_a_esquema

router = APIRouter(tags=["Usuarios"])

ROLES_INCOMPATIBLES = ("roles_incompatibles", "Un usuario no puede ser APPI y Consultor del mismo parque")


def _obtener_usuario(db, usuario_id: uuid.UUID) -> Usuario:
    u = db.get(Usuario, usuario_id)
    if u is None:
        raise no_encontrado("usuario")
    return u


def _parque_para_appi(db, parque_id: uuid.UUID | None) -> Parque:
    if parque_id is None:
        raise ErrorAPI(422, "parque_requerido", "Indique el parque del usuario APPI")
    parque = db.get(Parque, parque_id)
    if parque is None:
        raise ErrorAPI(422, "parque_no_existe", "El parque indicado no existe")
    return parque


def _tiene_asignacion_vigente_en(db, usuario_id: uuid.UUID, parque_id: uuid.UUID) -> bool:
    return bool(
        db.scalar(
            select(func.count(AsignacionConsultor.id))
            .join(Expediente, Expediente.id == AsignacionConsultor.expediente_id)
            .where(
                AsignacionConsultor.consultor_id == usuario_id,
                AsignacionConsultor.vigente_hasta.is_(None),
                Expediente.parque_id == parque_id,
            )
        )
    )


def _cerrar_asignaciones(db, usuario_id: uuid.UUID) -> None:
    db.execute(
        update(AsignacionConsultor)
        .where(AsignacionConsultor.consultor_id == usuario_id, AsignacionConsultor.vigente_hasta.is_(None))
        .values(vigente_hasta=ahora())
    )


def _quitar_contacto_principal(db, usuario_id: uuid.UUID) -> None:
    db.execute(update(Parque).where(Parque.contacto_principal_id == usuario_id).values(contacto_principal_id=None))


def _encolar_invitacion(db, u: Usuario) -> None:
    """Enlace de un solo uso y correo en el outbox (RF-03-AC-1, RNF-12); lo envía el worker."""
    s = get_settings()
    token = secrets.token_urlsafe(32)
    db.add(
        EnlaceUnSoloUso(
            usuario_id=u.id,
            token_hash=hashlib.sha256(token.encode()).hexdigest(),
            tipo="invitacion",
            expira_en=ahora() + timedelta(hours=s.invitacion_vigencia_horas),
        )
    )
    db.add(
        MensajeCorreo(
            usuario_id=u.id,
            tipo="invitacion",
            destinatario=u.correo,
            asunto="Invitación a SGPIS",
            cuerpo=(
                f"Hola {u.nombre}:\n\nSe creó tu cuenta en SGPIS. Para activarla y definir tu contraseña "
                f"entra a {s.url_spa}/registro?token={token}\n\nEl enlace vence en "
                f"{s.invitacion_vigencia_horas} horas y solo se puede usar una vez."
            ),
        )
    )


@router.get("/usuarios", response_model=e.Pagina[e.Usuario])
def listar_usuarios(
    db: DB,
    p: Paginacion,
    rol: Annotated[e.Rol | None, Query()] = None,
    parque_id: Annotated[uuid.UUID | None, Query(alias="parqueId")] = None,
    estado: Annotated[e.EstadoUsuario | None, Query()] = None,
):
    q = select(Usuario)
    if rol:
        q = q.where(Usuario.rol == rol)
    if parque_id:
        q = q.where(Usuario.rol == "appi", Usuario.parque_id == parque_id)
    if estado:
        q = q.where(Usuario.estado == estado)
    total = db.scalar(select(func.count()).select_from(q.subquery()))
    q = q.order_by(
        *orden_sql(
            p.orden,
            {"nombre": Usuario.nombre, "correo": Usuario.correo, "fechaAlta": Usuario.fecha_alta},
            "nombre",
            Usuario.id,
        )
    )
    usuarios = db.scalars(q.offset(p.offset).limit(p.tamano_pagina)).all()
    return {
        "pagina": p.pagina,
        "tamanoPagina": p.tamano_pagina,
        "total": total,
        "items": [usuario_a_esquema(db, u) for u in usuarios],
    }


@router.post("/usuarios", response_model=e.Usuario, status_code=201)
def crear_usuario(cuerpo: e.UsuarioCreate, db: DB, actor: Actor, response: Response):
    correo = cuerpo.correo.strip().lower()
    if db.scalar(select(Usuario.id).where(func.lower(Usuario.correo) == correo)):
        raise ErrorAPI(409, "correo_duplicado", "Ya existe un usuario con ese correo")

    parque_id = None
    desarrollador_id = None
    if cuerpo.rol == "appi":
        parque_id = _parque_para_appi(db, cuerpo.parque_id).id
    elif cuerpo.rol == "gerente_corporativo":
        if not cuerpo.desarrollador or not cuerpo.desarrollador.strip():
            raise ErrorAPI(422, "desarrollador_requerido", "Indique el desarrollador del gerente corporativo")
        desarrollador_id = obtener_o_crear_desarrollador(db, cuerpo.desarrollador).id

    u = Usuario(
        nombre=cuerpo.nombre.strip(),
        correo=correo,
        rol=cuerpo.rol,
        estado="pendiente_activacion",
        parque_id=parque_id,
        desarrollador_id=desarrollador_id,
    )
    db.add(u)
    db.flush()
    _encolar_invitacion(db, u)
    registrar_bitacora(
        db, actor, "crear_usuario", recurso_tipo="usuario", recurso_id=u.id, parque_id=parque_id,
        detalle=f"rol={u.rol}",
    )
    db.commit()
    response.headers["Location"] = f"/api/usuarios/{u.id}"
    return usuario_a_esquema(db, u)


@router.get("/usuarios/{usuarioId}", response_model=e.Usuario)
def obtener_usuario(usuarioId: uuid.UUID, db: DB):
    return usuario_a_esquema(db, _obtener_usuario(db, usuarioId))


@router.patch("/usuarios/{usuarioId}", response_model=e.Usuario)
def actualizar_usuario(usuarioId: uuid.UUID, cuerpo: e.UsuarioUpdate, db: DB, actor: Actor):
    u = _obtener_usuario(db, usuarioId)
    campos = exigir_campos(cuerpo, ("nombre", "rol", "estado"))  # [R3] regla compartida con PATCH /parques
    baja = cuerpo.estado == "inactivo" and u.estado != "inactivo"
    if baja and not cuerpo.motivo:
        raise ErrorAPI(422, "motivo_requerido", "Indique el motivo de la baja del usuario")

    rol_nuevo = cuerpo.rol or u.rol
    parque_nuevo = None
    desarrollador_nuevo = None
    if rol_nuevo == "appi":
        parque_nuevo = _parque_para_appi(db, cuerpo.parque_id if "parque_id" in campos else u.parque_id).id
        if _tiene_asignacion_vigente_en(db, u.id, parque_nuevo):
            raise ErrorAPI(422, *ROLES_INCOMPATIBLES)
    if rol_nuevo == "gerente_corporativo":
        if "desarrollador" in campos:
            if not cuerpo.desarrollador or not cuerpo.desarrollador.strip():
                raise ErrorAPI(422, "desarrollador_requerido", "Indique el desarrollador del gerente corporativo")
            desarrollador_nuevo = obtener_o_crear_desarrollador(db, cuerpo.desarrollador).id
        elif u.desarrollador_id is None:
            raise ErrorAPI(422, "desarrollador_requerido", "Indique el desarrollador del gerente corporativo")
        else:
            desarrollador_nuevo = u.desarrollador_id

    # La FK compuesta del contacto principal exige soltar la marca antes de mover al usuario.
    if baja or parque_nuevo != u.parque_id:
        _quitar_contacto_principal(db, u.id)
        db.flush()
    # Un usuario que deja de ser consultor (o se da de baja) pierde sus asignaciones vigentes.
    if baja or (u.rol == "consultor" and rol_nuevo != "consultor"):
        _cerrar_asignaciones(db, u.id)

    rol_anterior = u.rol
    if cuerpo.nombre is not None:
        u.nombre = cuerpo.nombre.strip()
    u.rol = rol_nuevo
    u.parque_id = parque_nuevo
    u.desarrollador_id = desarrollador_nuevo
    if baja:
        u.estado = "inactivo"
        u.motivo_baja = cuerpo.motivo
        db.execute(
            update(Sesion).where(Sesion.usuario_id == u.id, Sesion.revocada_en.is_(None)).values(revocada_en=ahora())
        )
        registrar_bitacora(db, actor, "baja_usuario", recurso_tipo="usuario", recurso_id=u.id, detalle=cuerpo.motivo)
    if campos - {"estado", "motivo"}:
        registrar_bitacora(
            db, actor, "actualizar_usuario", recurso_tipo="usuario", recurso_id=u.id,
            detalle=f"rol {rol_anterior} -> {rol_nuevo}" if rol_anterior != rol_nuevo else None,
        )
    db.commit()
    return usuario_a_esquema(db, u)


# ------------------------------------------------------------------ usuarios APPI del parque
def _usuario_parque(db, u: Usuario, parque: Parque) -> e.UsuarioParque:
    base = usuario_a_esquema(db, u)
    return e.UsuarioParque(**base.model_dump(), contacto_principal=parque.contacto_principal_id == u.id)


@router.get("/parques/{parqueId}/usuarios", response_model=list[e.UsuarioParque])
def listar_usuarios_parque(parqueId: uuid.UUID, db: DB):
    parque = obtener_parque(db, parqueId)
    usuarios = db.scalars(
        select(Usuario).where(Usuario.rol == "appi", Usuario.parque_id == parque.id).order_by(Usuario.nombre, Usuario.id)
    )
    return [_usuario_parque(db, u, parque) for u in usuarios]


@router.put("/parques/{parqueId}/contacto-principal", response_model=e.UsuarioParque)
def fijar_contacto_principal(parqueId: uuid.UUID, cuerpo: e.ContactoPrincipalUpdate, db: DB, actor: Actor):
    parque = obtener_parque(db, parqueId)
    u = db.get(Usuario, cuerpo.usuario_id)
    if u is None or u.rol != "appi" or u.estado != "activo" or u.parque_id != parque.id:
        raise ErrorAPI(
            422, "contacto_no_appi_del_parque", "El contacto principal debe ser un usuario APPI activo de este parque"
        )
    if parque.contacto_principal_id != u.id:
        parque.contacto_principal_id = u.id
        registrar_bitacora(
            db, actor, "designar_contacto_principal", recurso_tipo="usuario", recurso_id=u.id, parque_id=parque.id
        )
        db.commit()
    return _usuario_parque(db, u, parque)
