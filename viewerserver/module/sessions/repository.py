from typing import Type

from sqlalchemy import select, delete

from ...db.repository.base_repository import BaseRepository
from .model import Session
from .schema import InSessionSchema, SessionSchema

from datetime import datetime

class SessionsRepository(BaseRepository[InSessionSchema, SessionSchema, Session]):

    @property
    def _in_schema(self) -> Type[InSessionSchema]:
        return InSessionSchema

    @property
    def _schema(self) -> Type[SessionSchema]:
        return SessionSchema

    @property
    def _table(self) -> Type[Session]:
        return Session
    
    async def get_all_by_session(self, session: str) -> list[SessionSchema]:
        statement = select(Session).where(Session.session == session)
        result = await self._db_session.execute(statement)

        entries: list[Session] = result.scalars().all()
        return [self._schema.from_orm(entry) for entry in entries]
    
    async def get_all_2dviewer_session(self) -> list[Session]:
        statement = select(Session)
        result = await self._db_session.execute(statement)

        entries: list[Session] = result.scalars().all()
        result = [self._schema.from_orm(entry) for entry in entries]
        return result

    async def remove_expired_2dviewer_session(self) -> None:
        allViewerSession = await self.get_all_2dviewer_session()
        for record in allViewerSession:
            if (datetime.today() - record.expired_time).total_seconds() >= 0:
                await self.remove_2dviewer_session_by_id(record.id)

    async def remove_2dviewer_session_by_id(self, id: str) -> None:
        statement = (
            delete(Session)
            .where(Session.id == id)
        )
        await self._db_session.execute(statement)