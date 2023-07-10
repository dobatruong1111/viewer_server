import logging
import os
from enum import Enum
from functools import lru_cache
from typing import Optional

from pydantic import BaseSettings, PostgresDsn

logger = logging.getLogger(__name__)

class EnvironmentEnum(str, Enum):
    PRODUCTION = "production"
    LOCAL = "local"


class GlobalConfig(BaseSettings):
    TITLE: str = "Tutorial"
    DESCRIPTION: str = "This is a tutorial project for my blog"

    ENVIRONMENT: EnvironmentEnum
    DEBUG: bool = False
    TESTING: bool = False
    TIMEZONE: str = "UTC"

    DATABASE_URL: Optional[
        PostgresDsn
    ] = "postgresql://postgres:dbroothp2022@192.168.1.32:6632/fastapi"

    DB_ECHO_LOG: bool = False

    @property
    def async_database_url(self) -> Optional[str]:
        if self.ENVIRONMENT == EnvironmentEnum.LOCAL:
            # return "sqlite+aiosqlite:///:memory:"
            return "sqlite+aiosqlite:///./sql_app.db"

        return (
            self.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
            if self.DATABASE_URL
            else self.DATABASE_URL
        )
    
    WADO_URL = "http://192.168.1.32:8042/wado-rs"
    WADO_USER = "orthanc"
    WADO_PASSWORD = "orthanc"

    # Api V1 prefix
    API_V1_STR = "/v1"

    class Config:
        case_sensitive = True


class LocalConfig(GlobalConfig):
    """Local configurations."""

    DEBUG: bool = True
    ENVIRONMENT: EnvironmentEnum = EnvironmentEnum.LOCAL


class ProdConfig(GlobalConfig):
    """Production configurations."""

    DEBUG: bool = False
    ENVIRONMENT: EnvironmentEnum = EnvironmentEnum.PRODUCTION


class FactoryConfig:
    def __init__(self, environment: Optional[str]):
        self.environment = environment

    def __call__(self) -> GlobalConfig:
        if self.environment == EnvironmentEnum.PRODUCTION.value:
            return ProdConfig()
        return LocalConfig()

@lru_cache()
def get_configuration() -> GlobalConfig:
    return FactoryConfig(os.environ.get("ENVIRONMENT"))()


settings = get_configuration()