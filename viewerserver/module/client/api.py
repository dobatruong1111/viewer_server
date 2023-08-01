from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

import requests
import os
from dotenv import load_dotenv
load_dotenv(verbose=True)

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
) -> OutSessionSchema:
    return await SessionsRepository(db).get_by_id(session)

@router.post("/client/session3d/viewer")
async def get_ws_link_3d(
    payload: Viewer3DRequestGetWebSocketLink
) -> dict:
    host = os.getenv('HOST') if os.getenv('HOST')[-1] != '\r' else os.getenv('HOST')[:-1]
    port = os.getenv('PORT_APACHE') if os.getenv('PORT_APACHE')[-1] != '\r' else os.getenv('PORT_APACHE')[:-1]
    launcher_url = f"http://{host}:{port}/viewer"
    try:
        response = requests.post(
            launcher_url,
            json = payload.dict()
        )
        return response.json()
    except Exception as e:
        return {"Error": e}