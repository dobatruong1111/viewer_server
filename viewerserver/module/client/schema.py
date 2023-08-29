from typing import Optional, Dict
from ...db.schema import BaseSchema


class StoreRequestDTOCreate(BaseSchema):
    url: str
    
    authentication: str


class ViewerRequestDTOCreate(BaseSchema):
    userID : Optional[str]

    expireIn : int

    studyUIDs : Dict[str, StoreRequestDTOCreate]


class ViewerShareDTOCreate(BaseSchema):
    expiredIn : Optional[int]

    type: Optional[str] = None

    anonymize : Optional[bool] = None


class Viewer3DRequestGetWebSocketLink(BaseSchema):
    application: str = "viewer"

    useUrl: bool

    studyUUID: str

    seriesUUID: str

    session2D: str