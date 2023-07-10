from sqlalchemy.ext.asyncio import AsyncSession

from ..config.session import async_session

async def get_db() -> AsyncSession:
    """
    Dependency function that yields db sessions
    """
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.commit()
            await session.close()