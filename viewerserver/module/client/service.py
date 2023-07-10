from datetime import datetime, timedelta

from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from ..sessions.schema import InSessionSchema

from ...module.sessions.repository import SessionsRepository

from .schema import ViewerRequestDTOCreate, ViewerShareDTOCreate

class RequestService:

    # TODO: Should be set in environment
    MAX_SHARE_TIME = 129600

    def __init__(self, db_session: AsyncSession) -> None:
        self._repository: AsyncSession = SessionsRepository(db_session)

    async def get_new_viewer_url(self, obj: ViewerRequestDTOCreate) -> str:
        session_id = str(uuid4())
    
        for study_iuid in obj.study_uids:
            store = obj.study_uids[study_iuid]
            json = {
                "id": session_id + "-" + study_iuid,
                "user_id": obj.user_id,
                "owner_session": "",
                "owner_user_id": obj.user_id,
                "session": session_id,
                "store_authentication": store.authentication,
                "store_url": store.url,
                "study_iuid": study_iuid,
                "expired_time": datetime.today() + timedelta(seconds=obj.expire_in * 60)
            }
            session = InSessionSchema(**json)

            print(await self._repository.create(session))

        url = "/viewer/index.html?session=" + session_id + "&studies=" + ",".join(obj.study_uids)
        return url if obj.user_id is None else url + "&userID=" + obj.user_id

    async def get_shared_viewer_url(self, sessionID: str, obj: ViewerShareDTOCreate) -> str:
        sessions =  await self._repository.get_all_by_session(sessionID)

        expireIn = self.MAX_SHARE_TIME
        if obj.expire_in is not None and obj.expire_in > 0:
            expireIn = min(expireIn, obj.expire_in)

        sharedSessionID = str(uuid4())

        sharedStudyIUIDs = []
        for session in sessions:
            json = {
                "id": sharedSessionID + "-" + session.study_iuid,
                "session": sharedSessionID,
                "user_id": session.user_id,
                "owner_session": session.session,
                "owner_user_id": session.owner_user_id,
                "store_authentication": session.store_authentication,
                "store_url": session.store_url,
                "study_iuid": session.study_iuid,
                "expired_time": datetime.today() + timedelta(seconds=expireIn)
            }
            # Create new session
            await self._repository.create(InSessionSchema(**json))

            sharedStudyIUIDs.append(session.study_iuid)

        url = "/viewer/index.html?session=" + sharedSessionID + "&studies=" + ",".join(sharedStudyIUIDs)
        return url if obj.anonymize is None else url + "ano=1"
