from datetime import date, datetime, timedelta
from enum import Enum
from random import randint
from typing import List, Optional
from uuid import UUID, uuid4

from flask_login import UserMixin
from pydantic import BaseModel as PyBaseModel
from pydantic import Field

DATETIME_FORMAT = "%H:%M %d-%m-%Y"


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
    is_busy = "Занят"
    is_candidate = "Кандидат"
    is_waiting = "Свободен"


class DriverQualification(str, Enum):
    low = "Низкая"
    below_average = "Ниже среднего"
    above_average = "Выше среднего"
    high = "Высокая"


class Driver(Person):
    qualification: DriverQualification
    _qualification_rate_map: dict[DriverQualification:float] = {
        DriverQualification.low.value: 0.25,
        DriverQualification.below_average.value: 0.5,
        DriverQualification.above_average.value: 0.75,
        DriverQualification.high.value: 1.0,
    }
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
    casual = "Обычный"
    corruptible = "Портящийся"
    fragile = "Хрупкий"
    dangerous = "Опасный"


class Cargo(BaseModel):
    cargo_type: CargoType
    _cargo_type_rate_map: dict[CargoType:float] = {
        CargoType.casual.value: 0.25,
        CargoType.corruptible.value: 0.5,
        CargoType.fragile.value: 0.75,
        CargoType.dangerous.value: 1.0,
    }
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
    wait_decision = "Ждёт выбора решения"
    wait_contract_signing = "Ждёт подписания договора"
    wait_payments = "Ждёт оплаты"
    in_progress = "Выполняется"
    wait_confirmation = "Ждёт подтверждения выполнения"
    ready = "Выполнен"


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
    expected_date: Optional[datetime] = None
    ready_date: Optional[datetime] = None

    class Config:
        use_enum_values = True
        allow_mutation = True

    def update_status(self, status: OrderStatuses) -> None:
        self.status = status
        if status == OrderStatuses.in_progress:
            self.expected_date = datetime.now() + timedelta(hours=self.time)
        if status == OrderStatuses.ready:
            self.ready_date = datetime.now()

    def set_solution_params(self, driver: Driver, cost: float, time: int):
        self.driver = driver
        self.cost = cost
        self.time = time

    def get_expectation(self) -> str:
        expectation = abs(self.ready_date - self.expected_date)
        if self.ready_date < self.expected_date:
            return f"Заказ был выполнен раньше на " \
                   f"{expectation.seconds // 3600} часов" \
                   f" и {(expectation.seconds // 60) % 60} минут"
        return f"Мы опоздали на " \
               f"{expectation.seconds // 3600} часов и " \
               f"{(expectation.seconds // 60) % 60} минут :("

    def get_expected_readable_date(self) -> str:
        return self.expected_date.strftime(DATETIME_FORMAT)

    def get_ready_readable_date(self) -> str:
        return self.ready_date.strftime(DATETIME_FORMAT)


class Customer(Person, UserMixin):
    email: str
    phone: str
    password: str
    orders: Optional[List[Order]] = []


class Solution(BaseModel):
    order: Order
    driver: Driver
    cost: float
    time: int = randint(1, 48)
