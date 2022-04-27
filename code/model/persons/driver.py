from enum import Enum
from person import Person
from pydantic import Field
from typing import Optional


class DriverQualification(Enum):
    A = 'High'
    B = 'Middle'
    C = 'Low'


class Driver(Person):
    qualification: DriverQualification
    experience: int = Field(ge=2, le=60)

    def __init__(self, name: str, second_name: str, qualification: DriverQualification, experience: int,
                 middle_name: Optional[str] = None):
        super().__init__(name, second_name, middle_name)
        self.qualification = qualification
        self.experience = experience
