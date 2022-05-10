from aenum import MultiValueEnum
from enum import Enum
from pydantic import BaseModel as PyBaseModel, Field
from typing import Optional, List
from uuid import UUID, uuid4
from datetime import datetime, date
from flask_login import UserMixin


class BaseModel(PyBaseModel):
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=datetime.now)

    class Config:
        allow_mutation = False


class Person(BaseModel):
    name: str
    second_name: str
    middle_name: Optional[str] = None


class DriverStatuses(Enum):
    is_busy = 'Занят'
    is_candidate = 'Кандидат'
    is_waiting = 'Свободен'


class DriverQualification(MultiValueEnum):
    low = 'Низкая'
    below_average = 'Ниже среднего'
    above_average = 'Выше среднего'
    high = 'Высокая'


class Driver(Person):
    qualification: DriverQualification
    _qualification_rate_map: dict[DriverQualification: float] = {DriverQualification.low: 0.25,
                                                                 DriverQualification.below_average: 0.5,
                                                                 DriverQualification.above_average: 0.75,
                                                                 DriverQualification.high: 1.0}
    experience: int = Field(ge=2, le=60)
    is_busy: DriverStatuses = DriverStatuses.is_waiting

    def get_qualification_rate(self) -> float:
        return self._qualification_rate_map[self.qualification]


class CargoType(Enum):
    casual = 'Обычный'
    corruptible = 'Портящийся'
    fragile = 'Хрупкий'
    dangerous = 'Опасный'


class Cargo(BaseModel):
    cargo_type: CargoType
    _cargo_type_rate_map: dict[CargoType: float] = {CargoType.casual: 0.25,
                                                    CargoType.corruptible: 0.5,
                                                    CargoType.fragile: 0.75,
                                                    CargoType.dangerous: 1.0}
    width: float
    length: float
    height: float
    weight: float

    def get_cargo_type_rate(self):
        return self._cargo_type_rate_map[self.cargo_type]


class OrderStatuses(Enum):
    in_process = "В обработке"
    wait_decision = 'Ждёт выбора решения'
    wait_contract_signing = 'Ждёт подписания договора'
    wait_payments = 'Ждёт оплаты'
    in_progress = 'Выполняется'
    wait_confirmation = 'Ждёт подтверждения выполнения'
    ready = 'Выполнен'


class Order(BaseModel):
    cargo: Cargo
    driver: Optional[Driver] = None
    # TODO: Мб сделать классы адресов, который легко парсится
    address_from: str
    address_to: str
    status: OrderStatuses = OrderStatuses.in_progress
    end_date: Optional[date] = None

    def update_status(self, status: OrderStatuses) -> None:
        self.status = status


class Customer(Person, UserMixin):
    email: str
    phone: str
    password: str
    orders: Optional[List[Order]] = []


class Solution(BaseModel):
    order: Order
    driver: Driver
    cost: float
    time: int
