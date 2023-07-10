
from typing import Union

import httpx

from sqlalchemy.ext.asyncio import AsyncSession

from ...module.sessions.repository import SessionsRepository

from ...module.sessions.schema import OutSessionSchema

# Customize httpx Auth
# Refer to https://github.com/encode/httpx/blob/master/httpx/_auth.py
def get_auth(auth) -> httpx.Auth:
    def _inner_func(request: httpx._models.Request) -> httpx._models.Request:
        request.headers["Authorization"] = auth
        return request
    return httpx._auth.FunctionAuth(_inner_func)

class WadoService:

    def __init__(self, db_session: AsyncSession) -> None:
        self._repository = SessionsRepository(db_session)

    async def _get_session(self, sessionID: str, studyIUID: str) -> OutSessionSchema:
        id: str = sessionID + "-" + studyIUID
        return await self._repository.get_by_id(id)

    async def get_study(self, sessionID: str, studyUID: str) -> httpx.Response:
        session = await self._get_session(sessionID, studyUID)
        async with httpx.AsyncClient() as client:
            return await client.get(f"{session.store_url}/studies/{studyUID}/series", auth = get_auth(session.store_authentication))

    async def get_series_metadata(self, sessionID: str, studyUID: str, seriesUID: str) -> httpx.Response:
        session = await self._get_session(sessionID, studyUID)
        async with httpx.AsyncClient() as client:
            return await client.get(f"{session.store_url}/studies/{studyUID}/series/{seriesUID}/metadata", auth = get_auth(session.store_authentication))

    async def get_frame(self, sessionID: str, studyUID: str, seriesUID: str, sopUID: str, frames: str) -> httpx.Response:
        session = await self._get_session(sessionID, studyUID)
        async with httpx.AsyncClient() as client:
            return await client.get(f"{session.store_url}/studies/{studyUID}/series/{seriesUID}/instances/{sopUID}/frames/{frames}", auth = get_auth(session.store_authentication))
        
    async def get_series_thumbnail(self, sessionID: str, studyUID: str, seriesUID: str, q: Union[str, None] = None, viewport: str = "") -> httpx.Response:
        session = await self._get_session(sessionID, studyUID)
        async with httpx.AsyncClient() as client:
            return await client.get(f"{session.store_url}/studies/{studyUID}/series/{seriesUID}/thumbnail", auth = get_auth(session.store_authentication))
        
    async def get_instance_thumbnail(self, sessionID: str, studyUID: str, seriesUID: str, sopUID: str, frames: str, q: Union[str, None] = None, viewport: str = "") -> httpx.Response:
        session = await self._get_session(sessionID, studyUID)
        async with httpx.AsyncClient() as client:
            return await client.get(f"{session.store_url}/studies/{studyUID}/series/{seriesUID}/instances/{sopUID}/frames/{frames}/thumbnail", auth = get_auth(session.store_authentication))
