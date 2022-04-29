from person import Person
from pydantic import Field
from typing import Optional


class Driver(Person):
    qualification: str
    experience: int = Field(ge=2, le=60)

    def __init__(self, name: str, second_name: str, qualification: str, experience: int,
                 middle_name: Optional[str] = None):
        super().__init__(name, second_name, middle_name)
        self.qualification = qualification
        self.experience = experience
