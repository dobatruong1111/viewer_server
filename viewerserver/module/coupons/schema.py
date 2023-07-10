from typing import Optional, Any, Dict
from uuid import UUID

from pydantic import validator

from ...db.schema import BaseSchema

class CouponSchemaBase(BaseSchema):
    code: str
    init_count: int

class InCouponSchema(CouponSchemaBase):
    remaining_count: Optional[int]

    @validator("remaining_count", always=True)
    def remaining_count_update(
        cls, value: Optional[int], values: Dict[Any, Any], **kwargs
    ):
        return value or values["init_count"]

class CouponSchema(CouponSchemaBase):
    id: UUID
    remaining_count: int

class OutCouponSchema(CouponSchema):
    ...