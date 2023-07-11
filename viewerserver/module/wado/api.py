from typing import Union

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse, Response
from sqlalchemy.ext.asyncio import AsyncSession

from ...db.db import get_db

from .service import WadoService

router = APIRouter(prefix="/ws/rest/wado-rs", tags=['wado-rs'])

@router.get("/{sessionID}/studies/{studyUID}/series")
async def get_study(sessionID: str, studyUID: str, db: AsyncSession = Depends(get_db)) -> Response:
    resp = await WadoService(db).get_study(sessionID, studyUID)
    return JSONResponse(resp.json())

@router.get("/{sessionID}/studies/{studyUID}/series/{seriesUID}/metadata")
async def get_series_metadata(sessionID: str, studyUID: str, seriesUID: str, db: AsyncSession = Depends(get_db)) -> Response:
    resp = await WadoService(db).get_series_metadata(sessionID, studyUID, seriesUID)
    return Response(content = resp.content, media_type="application/octet-stream")

@router.get("/{sessionID}/studies/{studyUID}/series/{seriesUID}/instances/{sopUID}/frames/{frames}")
async def get_frame(sessionID: str, studyUID: str, seriesUID: str, sopUID: str, frames: str, db: AsyncSession = Depends(get_db)) -> Response:
    resp = await WadoService(db).get_frame(sessionID, studyUID, seriesUID, sopUID, frames)
    return Response(content = resp.content, media_type="application/octet-stream")

@router.get("/{sessionID}/studies/{studyUID}/series/{seriesUID}/thumbnail")
async def get_series_thumbnail(sessionID: str, studyUID: str, seriesUID: str, q: Union[str, None] = None, viewport: str = "", db: AsyncSession = Depends(get_db)) -> Response:
    resp = await WadoService(db).get_series_thumbnail(sessionID, studyUID, seriesUID, q, viewport)
    return Response(content = resp.content, media_type="application/octet-stream")