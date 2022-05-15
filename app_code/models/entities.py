from pydantic import BaseModel as PyBaseModel, Field
from typing import Optional, List
from enum import Enum
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


class DriverStatuses(str, Enum):
    is_busy = 'Занят'
    is_candidate = 'Кандидат'
    is_waiting = 'Свободен'


class DriverQualification(str, Enum):
    low = 'Низкая'
    below_average = 'Ниже среднего'
    above_average = 'Выше среднего'
    high = 'Высокая'


class Driver(Person):
    qualification: DriverQualification
    _qualification_rate_map: dict[DriverQualification: float] = {DriverQualification.low.value: 0.25,
                                                                 DriverQualification.below_average.value: 0.5,
                                                                 DriverQualification.above_average.value: 0.75,
                                                                 DriverQualification.high.value: 1.0}
    experience: int = Field(ge=2, le=60)
    status: DriverStatuses = DriverStatuses.is_waiting

    class Config:
        use_enum_values = True
        allow_mutation = True

    def get_qualification_rate(self) -> float:
        return self._qualification_rate_map[self.qualification]

    def update_status(self, status: DriverStatuses):
        self.status = status


class CargoType(str, Enum):
    casual = 'Обычный'
    corruptible = 'Портящийся'
    fragile = 'Хрупкий'
    dangerous = 'Опасный'


class Cargo(BaseModel):
    cargo_type: CargoType
    _cargo_type_rate_map: dict[CargoType: float] = {CargoType.casual.value: 0.25,
                                                    CargoType.corruptible.value: 0.5,
                                                    CargoType.fragile.value: 0.75,
                                                    CargoType.dangerous.value: 1.0}
    width: float
    length: float
    height: float
    weight: float

    class Config:
        use_enum_values = True

    def get_cargo_type_rate(self):
        return self._cargo_type_rate_map[self.cargo_type]


class OrderStatuses(str, Enum):
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
    status: OrderStatuses = OrderStatuses.in_process
    end_date: Optional[date] = None
    cost: Optional[float] = None
    time: Optional[int] = None

    class Config:
        use_enum_values = True
        allow_mutation = True

    def update_status(self, status: OrderStatuses) -> None:
        self.status = status

    def set_solution_params(self, driver: Driver, cost: float, time: int):
        self.driver = driver
        self.cost = cost
        self.time = time


class Customer(Person, UserMixin):
    email: str
    phone: str
    password: str
    orders: Optional[List[Order]] = []


class Solution(BaseModel):
    order: Order
    driver: Driver
    cost: float
    time: int = 0
