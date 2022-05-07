from enum import Enum
from pydantic import BaseModel as PyBaseModel, Field
from typing import Optional
from uuid import UUID, uuid4
from datetime import datetime, date


class BaseModel(PyBaseModel):
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=datetime.now)

    class Config:
        allow_mutation = False


class Person(BaseModel):
    name: str
    second_name: str
    middle_name: Optional[str] = None


class Customer(Person):
    email: str
    phone: str


class Driver(Person):
    qualification: str
    experience: int = Field(ge=2, le=60)


class Cargo(BaseModel):
    cargo_type: str
    width: float
    length: float
    height: float
    weight: float


class Statuses(Enum):
    in_process = "В обработке"
    wait_decision = 'Ждёт выбора решения'
    wait_contract_signing = 'Ждёт подписания договора'
    wait_payments = 'Ждёт оплаты'
    in_progress = 'Выполняется'
    wait_confirmation = 'Ждёт подтверждения выполнения'
    ready = 'Выполнен'


class Order(BaseModel):
    customer: Customer
    cargo: Cargo
    driver: Optional[Driver] = None
    # TODO: Мб сделать классы адресов, который легко парсится
    address_from: str
    address_to: str
    status: Statuses = Statuses.in_progress
    end_date: Optional[date] = None


class Solution(BaseModel):
    order: Order
    driver: Driver
    cost: float
    time: int
