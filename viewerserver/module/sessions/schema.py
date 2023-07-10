from typing import Optional, Any, Dict
from uuid import UUID

from datetime import datetime

from ...db.schema import BaseSchema

class SessionSchemaBase(BaseSchema):

    user_id : str
    
    session : str

    owner_session : str

    owner_user_id : str
    
    store_authentication : str
    
    store_url : str
    
    study_iuid : str
    
    expired_time : datetime

class InSessionSchema(SessionSchemaBase):
    id: str

class SessionSchema(SessionSchemaBase):
    id: str

class OutSessionSchema(SessionSchema):
    ...