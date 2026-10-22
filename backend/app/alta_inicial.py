"""Alta de la primera cuenta de Coordinación AMPIP. [P-02]

Con todas las rutas protegidas, POST /usuarios exige una sesión de Coordinación AMPIP; sin este comando no habría
forma de crear la primera. Corre en el servidor (fuera de la API, con acceso a la base) y no recibe contraseñas:
crea la cuenta en "pendiente de activación" con su invitación y muestra el token una sola vez. La contraseña la fija
la persona con POST /api/auth/register.

Uso: uv run python -m app.alta_inicial --correo coordinacion@ampip.mx --nombre "Coordinación AMPIP"
"""

import argparse
import hashlib
import secrets
import sys
from datetime import timedelta

from sqlalchemy import func, select

from app.comun import ahora
from app.config import get_settings
from app.db import SessionLocal
from app.modelos import EnlaceUnSoloUso, RegistroBitacora, Usuario


def crear_invitacion(db, usuario: Usuario) -> str:
    token = secrets.token_urlsafe(32)
    db.add(EnlaceUnSoloUso(usuario_id=usuario.id, token_hash=hashlib.sha256(token.encode()).hexdigest(),
                           tipo="invitacion",
                           expira_en=ahora() + timedelta(hours=get_settings().invitacion_vigencia_horas)))
    return token


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--correo", required=True)
    p.add_argument("--nombre", required=True)
    args = p.parse_args(argv)
    correo = args.correo.strip().lower()
    with SessionLocal() as db:
        if db.scalar(select(Usuario.id).where(func.lower(Usuario.correo) == correo)):
            print(f"Ya existe una cuenta con el correo {correo}", file=sys.stderr)
            return 1
        u = Usuario(nombre=args.nombre.strip(), correo=correo, rol="coordinacion_ampip", estado="pendiente_activacion")
        db.add(u)
        db.flush()
        token = crear_invitacion(db, u)
        db.add(RegistroBitacora(usuario_id=None, rol=None, accion="alta_inicial_coordinacion", recurso_tipo="usuario",
                                recurso_id=str(u.id), resultado="exitoso", detalle="comando app.alta_inicial"))
        db.commit()
    print(f"Cuenta creada: {correo} (pendiente de activación)")
    print("Token de invitación (se muestra una sola vez):")
    print(token)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
