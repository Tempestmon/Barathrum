from datetime import date
from base import BaseModel
from persons import Customer, Driver
from cargo import Cargo


class Order(BaseModel):
    order_id: int
    customer: Customer
    cargo: Cargo
    driver: Driver
    address_from: str
    address_to: str
    status: str
    creation_date: date
    end_date: date

    def __init__(self, order_id: int, customer: Customer, cargo: Cargo, driver: Driver, address_from: str,
                 address_to: str, status: str):
        super().__init__()
