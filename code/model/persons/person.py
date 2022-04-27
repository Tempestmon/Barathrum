from typing import Optional
from ..base import BaseModel


class Person(BaseModel):
    name: str
    second_name: str
    middle_name: Optional[str]

    def __init__(self, name: str, second_name: str, middle_name: Optional[str] = None):
        super().__init__()
        self.name = name
        self.second_name = second_name
        self.middle_name = middle_name
