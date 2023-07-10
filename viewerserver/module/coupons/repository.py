from typing import Type

from ...db.repository.base_repository import BaseRepository
from .model import Coupon
from .schema import InCouponSchema, CouponSchema


class CouponsRepository(BaseRepository[InCouponSchema, CouponSchema, Coupon]):
    @property
    def _in_schema(self) -> Type[InCouponSchema]:
        return InCouponSchema

    @property
    def _schema(self) -> Type[CouponSchema]:
        return CouponSchema

    @property
    def _table(self) -> Type[Coupon]:
        return Coupon