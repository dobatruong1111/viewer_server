import asyncio

from ...db.db import get_db
from .repository import SessionsRepository

async def remove_expired_sessions():
    while True:
        # test
        # await asyncio.sleep(3)
        # sleep for 60 seconds after running above code
        await asyncio.sleep(60)
        async for db in get_db():
            await SessionsRepository(db).remove_expired_2dviewer_session()