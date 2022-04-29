from base import BaseModel


class Cargo(BaseModel):
    cargo_type: str
    width: float
    length: float
    height: float
    weight: float

    def __init__(self, cargo_type: str, width: float, length: float, height: float, weight: float):
        super().__init__()
        self.cargo_type = cargo_type
        self.width = width
        self.length = length
        self.height = height
        self.weight = weight
