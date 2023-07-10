from sqlalchemy import Column, Integer, String

from ...db.model.base_model import BaseModel

class Coupon(BaseModel):
    __tablename__ = "coupon"

    code = Column(String, nullable=False, unique=True)

    init_count = Column(Integer, nullable=False)

    remaining_count = Column(Integer, nullable=False)