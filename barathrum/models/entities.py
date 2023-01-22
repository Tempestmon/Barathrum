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
    IS_BUSY = "Занят"
    IS_CANDIDATE = "Кандидат"
    IS_WAITING = "Свободен"


class DriverQualification(str, Enum):
    LOW = "Низкая"
    BELOW_AVERAGE = "Ниже среднего"
    ABOVE_AVERAGE = "Выше среднего"
    HIGH = "Высокая"


class Driver(Person):
    qualification: DriverQualification
    _qualification_rate_map: dict[DriverQualification:float] = {
        DriverQualification.LOW.value: 0.25,
        DriverQualification.BELOW_AVERAGE.value: 0.5,
        DriverQualification.ABOVE_AVERAGE.value: 0.75,
        DriverQualification.HIGH.value: 1.0,
    }
    experience: int = Field(ge=2, le=60)
    status: DriverStatuses = DriverStatuses.IS_WAITING

    class Config:
        use_enum_values = True
        allow_mutation = True

    def get_qualification_rate(self) -> float:
        return self._qualification_rate_map[self.qualification]

    def update_status(self, status: DriverStatuses):
        self.status = status


class CargoType(str, Enum):
    CASUAL = "Обычный"
    CORRUPTIBLE = "Портящийся"
    FRAGILE = "Хрупкий"
    DANGEROUS = "Опасный"


class Cargo(BaseModel):
    cargo_type: CargoType
    _cargo_type_rate_map: dict[CargoType:float] = {
        CargoType.CASUAL.value: 0.25,
        CargoType.CORRUPTIBLE.value: 0.5,
        CargoType.FRAGILE.value: 0.75,
        CargoType.DANGEROUS.value: 1.0,
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
    IN_PROCESS = "В обработке"
    WAIT_DECISION = "Ждёт выбора решения"
    WAIT_CONTRACT_SIGNING = "Ждёт подписания договора"
    WAIT_PAYMENTS = "Ждёт оплаты"
    IN_PROGRESS = "Выполняется"
    WAIT_CONFIRMATION = "Ждёт подтверждения выполнения"
    READY = "Выполнен"


class Order(BaseModel):
    cargo: Cargo
    driver: Optional[Driver] = None
    # TODO: Мб сделать классы адресов, который легко парсится
    address_from: str
    address_to: str
    status: OrderStatuses = OrderStatuses.IN_PROCESS
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
        if status == OrderStatuses.IN_PROGRESS:
            self.expected_date = datetime.now() + timedelta(hours=self.time)
        if status == OrderStatuses.READY:
            self.ready_date = datetime.now()

    def set_solution_params(self, driver: Driver, cost: float, time: int):
        self.driver = driver
        self.cost = cost
        self.time = time

    def get_expectation(self) -> str:
        expectation = abs(self.ready_date - self.expected_date)
        if self.ready_date < self.expected_date:
            return (
                f"Заказ был выполнен раньше на "
                f"{expectation.seconds // 3600} часов"
                f" и {(expectation.seconds // 60) % 60} минут"
            )
        return (
            f"Мы опоздали на "
            f"{expectation.seconds // 3600} часов и "
            f"{(expectation.seconds // 60) % 60} минут :("
        )

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
