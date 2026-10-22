"""Configuración leída de variables de entorno (o de un archivo .env)."""

from functools import lru_cache

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = "postgresql+psycopg://sgpis:sgpis@localhost:5432/sgpis"

    # Autenticación (S05-S06-A2). JWT_SECRET firma el token HS256 (mínimo 32 bytes) y JWT_EXPIRATION es la
    # vida absoluta del token en SEGUNDOS (entero, de 60 a 86400). No tienen valor por omisión: si faltan, la
    # API arranca pero /auth/login y la validación de tokens responden 500 (fallan cerrado).
    jwt_secret: SecretStr | None = None
    jwt_expiration: int | None = Field(default=None, ge=60, le=86400)

    # Transitorio hasta que las rutas CRUD exijan token: las escrituras hechas SIN encabezado Authorization
    # se atribuyen a este usuario técnico, que se crea solo la primera vez que se necesita.
    usuario_sistema_correo: str = "sistema@sgpis.local"
    usuario_sistema_nombre: str = "Usuario de sistema (sin autenticación)"

    # Invitación de alta de usuario (RF-03-AC-1).
    invitacion_vigencia_horas: int = 72
    url_spa: str = "http://localhost:5173"

    zona_horaria: str = "America/Mexico_City"

    @property
    def url_sqlalchemy(self) -> str:
        """Fuerza el driver psycopg 3 aunque la URL venga como postgresql://."""
        url = self.database_url
        if url.startswith("postgres://"):
            url = "postgresql://" + url[len("postgres://"):]
        if url.startswith("postgresql://"):
            url = "postgresql+psycopg://" + url[len("postgresql://"):]
        return url


@lru_cache
def get_settings() -> Settings:
    return Settings()
