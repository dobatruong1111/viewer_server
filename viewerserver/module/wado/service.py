
from typing import Union

import requests

from sqlalchemy.ext.asyncio import AsyncSession

from ...module.sessions.repository import SessionsRepository

from ...module.sessions.schema import OutSessionSchema

class MyAuth(requests.auth.AuthBase):
    def __init__(self, auth):
        self._auth = auth
    def __call__(self, r):
        # Implement my authentication
        r.headers['Authorization'] = self._auth
        return r

class WadoService:

    def __init__(self, db_session: AsyncSession) -> None:
        self._repository = SessionsRepository(db_session)

    async def _get_session(self, sessionID: str, studyIUID: str) -> OutSessionSchema:
        id: str = sessionID + "-" + studyIUID
        return await self._repository.get_by_id(id)

    async def get_study(self, sessionID: str, studyUID: str) -> requests.Response:
        session = await self._get_session(sessionID, studyUID)
        return requests.get(f"{session.store_url}/studies/{studyUID}/series", auth = MyAuth(session.store_authentication))

    async def get_series_metadata(self, sessionID: str, studyUID: str, seriesUID: str) -> requests.Response:
        session = await self._get_session(sessionID, studyUID)
        return requests.get(f"{session.store_url}/studies/{studyUID}/series/{seriesUID}/metadata", auth = MyAuth(session.store_authentication))

    async def get_frame(self, sessionID: str, studyUID: str, seriesUID: str, sopUID: str, frames: str) -> requests.Response:
        session = await self._get_session(sessionID, studyUID)
        return requests.get(f"{session.store_url}/studies/{studyUID}/series/{seriesUID}/instances/{sopUID}/frames/{frames}", auth = MyAuth(session.store_authentication))
        
    async def get_series_thumbnail(self, sessionID: str, studyUID: str, seriesUID: str, q: Union[str, None] = None, viewport: str = "") -> requests.Response:
        session = await self._get_session(sessionID, studyUID)
        return requests.get(f"{session.store_url}/studies/{studyUID}/series/{seriesUID}/thumbnail", auth = MyAuth(session.store_authentication))
        
    async def get_instance_thumbnail(self, sessionID: str, studyUID: str, seriesUID: str, sopUID: str, frames: str, q: Union[str, None] = None, viewport: str = "") -> requests.Response:
        session = await self._get_session(sessionID, studyUID)
        return requests.get(f"{session.store_url}/studies/{studyUID}/series/{seriesUID}/instances/{sopUID}/frames/{frames}/thumbnail", auth = MyAuth(session.store_authentication))
