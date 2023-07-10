from typing import Optional, Dict
from ...db.schema import BaseSchema


class StoreRequestDTOCreate(BaseSchema):
    url: str
    
    authentication: str


class ViewerRequestDTOCreate(BaseSchema):
    user_id : Optional[str]

    expire_in : int

    study_uids : Dict[str, StoreRequestDTOCreate]


class ViewerShareDTOCreate(BaseSchema):
    expire_in : Optional[int]

    type: Optional[str] = None

    anonymize : Optional[bool] = None
