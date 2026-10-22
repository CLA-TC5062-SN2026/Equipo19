"""Configuración leída de variables de entorno (o de un archivo .env)."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = "postgresql+psycopg://sgpis:sgpis@localhost:5432/sgpis"

    # Mientras no exista autenticación (S05-S06-A2), toda escritura se atribuye a este usuario
    # técnico. Se crea solo la primera vez que se necesita.
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
