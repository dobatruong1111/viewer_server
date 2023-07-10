from typing import Type

from sqlalchemy import select

from ...db.repository.base_repository import BaseRepository
from .model import Session
from .schema import InSessionSchema, SessionSchema


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
