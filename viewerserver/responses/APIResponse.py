from collections.abc import Iterable
from .BaseAPIResponse import BaseAPIResponseHeader, BaseAPIResponse

from typing import TypeVar

T = TypeVar('T')

class APIResponseHeader(BaseAPIResponseHeader):

    def __init__(self, code: int, message: str) -> None:
        self.code: int = code
        self.message: str = message

    def get_code(self) -> int:
        return self.code
    
    def set_code(self, code) -> None:
        self.code = code

    def get_message(self) -> str:
        return self.message
    
    def set_message(self, message) -> None:
        self.message = message


class APIResponse(BaseAPIResponse):

    def __init__(self, header: APIResponseHeader, body: T) -> None:
        self.header: dict = vars(header)
        self.body: T = body

    def get_header(self) -> dict:
        return self.header
    
    def set_header(self, header) -> None:
        self.header = header

    def get_body(self) -> T:
        return self.body
    
    def set_body(self, body) -> None:
        self.body = body
