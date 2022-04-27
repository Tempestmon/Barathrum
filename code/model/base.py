from uuid import uuid4 as generate_uuid, UUID
from pydantic import BaseModel as PyBaseModel


class BaseModel(PyBaseModel):
    model_id: UUID

    def __init__(self):
        self.model_id = generate_uuid()
