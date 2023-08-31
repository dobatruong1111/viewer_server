from typing import TypeVar

T = TypeVar('T')

class BaseAPIResponseHeader:

    code: int

    message: str


class BaseAPIResponse:

    header: BaseAPIResponseHeader

    body: T
