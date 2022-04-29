from typing import Optional
from person import Person


class Customer(Person):
    def __init__(self, name: str, second_name: str, middle_name: Optional[str] = None):
        super().__init__(name, second_name, middle_name)
