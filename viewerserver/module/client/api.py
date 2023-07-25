from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
import requests

from ...db.db import get_db

from ...module.sessions.repository import SessionsRepository

from ...module.sessions.schema import OutSessionSchema

from .schema import ViewerRequestDTOCreate, ViewerShareDTOCreate, Viewer3DRequestGetWebSocketLink

router = APIRouter(prefix="/ws/rest", tags=['client-api'])

from .service import RequestService

@router.post("/client/getlink", status_code=status.HTTP_201_CREATED)
async def get_link(
    payload: ViewerRequestDTOCreate, db: AsyncSession = Depends(get_db)
) -> str:
    return await RequestService(db).get_new_viewer_url(payload)

@router.post("/session/{sessionID}/share", status_code=status.HTTP_201_CREATED)
async def get_link(
    sessionID: str,
    payload: ViewerShareDTOCreate,
    db: AsyncSession = Depends(get_db)
) -> str:
    return await  RequestService(db).get_shared_viewer_url(sessionID, payload)

@router.get("/session/{session}/", status_code=status.HTTP_201_CREATED)
async def get_link(
    session: str, db: AsyncSession = Depends(get_db)
) -> list[OutSessionSchema]:
    return await SessionsRepository(db).get_all_by_session(session)

@router.post("/client/session3d/viewer")
async def get_ws_link_3d(
    payload: Viewer3DRequestGetWebSocketLink
) -> dict:
    apache_url = "http://localhost:8081/viewer"
    try:
        response = requests.post(
            apache_url,
            json = payload.dict()
        )
        return response.json()
    except Exception as e:
        return {"Error": e}