from datetime import date
from typing import List, Optional

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    id: Mapped[str] = mapped_column(primary_key=True)


class Person(Base):
    name: Mapped[str] = mapped_column(String(30))
    middle_name: Mapped[Optional[str]] = mapped_column(String(30))
    second_name: Mapped[str] = mapped_column(String(30))


class User(Person):
    __tablename__ = "user"
    mail: Mapped[str]
    password: Mapped[str]
    phone: Mapped[str]
    orders: Mapped[List["Order"]] = relationship("Order")


class Driver(Person):
    __tablename__ = "driver"
    status_id = mapped_column(ForeignKey("driver_status.id"))
    status: Mapped["DriverStatus"] = relationship("DriverStatus")
    qualification: Mapped[str]
    experience: Mapped[int]


class DriverStatus(Base):
    __tablename__ = "driver_status"
    id: Mapped[int] = mapped_column(primary_key=True)
    status: Mapped[str]


class Cargo(Base):
    __tablename__ = "cargo"
    type_id = mapped_column(ForeignKey("cargo_type.id"))
    type: Mapped["CargoType"] = relationship("CargoType")
    width: Mapped[float]
    length: Mapped[float]
    height: Mapped[float]
    weight: Mapped[float]


class CargoType(Base):
    __tablename__ = "cargo_type"
    id: Mapped[int] = mapped_column(primary_key=True)
    type: Mapped[str]


class Order(Base):
    __tablename__ = "order"
    status_id = mapped_column(ForeignKey("order_status.id"))
    status: Mapped["OrderStatus"] = relationship("OrderStatus")
    cargo_id: Mapped[str] = mapped_column(ForeignKey("cargo.id"))
    cargo: Mapped["Cargo"] = relationship("Cargo")
    driver_id: Mapped[str] = mapped_column(ForeignKey("driver.id"))
    driver: Mapped["Driver"] = relationship("Driver")
    address_from: Mapped[str]
    address_to: Mapped[str]
    end_date: Mapped[date]
    cost: Mapped[float]
    time: Mapped[int]
    expected_date: Mapped[date]
    ready_date: Mapped[date]


class OrderStatus(Base):
    __tablename__ = "order_status"
    id: Mapped[int] = mapped_column(primary_key=True)
    status: Mapped[str]
