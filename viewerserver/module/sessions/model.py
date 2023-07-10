from sqlalchemy import Column, DateTime, String

from ...db.model.base_model import BaseModel

class Session(BaseModel):

    __tablename__ = "viewer_session"

    user_id = Column(String)

    session = Column(String)

    owner_session = Column(String)

    owner_user_id = Column(String)
    
    store_authentication = Column(String)
    
    store_url = Column(String)
    
    study_iuid = Column(String)
    
    expired_time = Column(DateTime)
