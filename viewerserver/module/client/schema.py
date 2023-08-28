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

class APIResponseHeader:
    def __init__(self, code: int, message: str) -> None:
        self.code = code
        self.message = message

    def get_header(self) -> dict:
        return {
            "code": self.code,
            "message": self.message
        }

class APIResponse:
    def __init__(self, header: APIResponseHeader, body: str) -> None:
        self.header = header
        self.body = body

    def get_response(self) -> dict:
        return {
            "header": self.header.get_header(),
            "body": self.body
        }