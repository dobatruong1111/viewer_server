import requests
from sanic import Blueprint
from sanic.response import json, raw

from settings.config import wado_config

bp_wado = Blueprint("wado", url_prefix="/wado-rs")

@bp_wado.get("/studies/<studyUID>/series")
async def get_study(_, studyUID):
    return json(requests.get(f"{wado_config['URL']}/studies/{studyUID}/series",
                auth = (wado_config['USERNAME'], wado_config['PASSWORD'])).json())

@bp_wado.get("/studies/<studyUID>/series/<seriesUID>/metadata")
async def get_series_metadata(_, studyUID, seriesUID):
    return raw(requests.get(f"{wado_config['URL']}/studies/{studyUID}/series/{seriesUID}/metadata",
                auth = (wado_config['USERNAME'], wado_config['PASSWORD'])).content)

@bp_wado.get("/studies/<studyUID>/series/<seriesUID>/instances/<sopUID>/frames/<frames>")
async def get_frame(_, studyUID: str, seriesUID: str, sopUID: str, frames: str):
    return raw(requests.get(f"{wado_config['URL']}/studies/{studyUID}/series/{seriesUID}/instances/{sopUID}/frames/{frames}",
                 auth = (wado_config['USERNAME'], wado_config['PASSWORD'])).content)

@bp_wado.get("/studies/<studyUID>/series/<seriesUID>/thumbnail")
async def get_series_thumbnail(request, studyUID, seriesUID):
    return raw(requests.get(f"{wado_config['URL']}/studies/{studyUID}/series/{seriesUID}/thumbnail",
                params=request.query_string,
                auth = (wado_config['USERNAME'], wado_config['PASSWORD'])).content,
                content_type = "image/jpeg")

@bp_wado.get("/studies/<studyUID>/series/<seriesUID>/instances/<sopUID>/frames/<frames>/thumbnail")
async def get_frame_thumbnail(request, studyUID, seriesUID, sopUID, frames):
    return raw(requests.get(f"{wado_config['URL']}/studies/{studyUID}/series/{seriesUID}/instances/{sopUID}/frames/{frames}/thumbnail",
        params=request.query_string,
        auth = (wado_config['USERNAME'], wado_config['PASSWORD'])).content,
        content_type = "image/jpeg")