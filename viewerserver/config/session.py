from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from .settings import settings

engine = create_async_engine(
    settings.async_database_url,
    echo=settings.DB_ECHO_LOG,
    poolclass=StaticPool
)

async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)