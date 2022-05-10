import uuid
import pytest
from bcrypt import hashpw, gensalt
from app_code.models.entities import Cargo, Customer, Order, OrderStatuses, Driver
from app_code.tests.integration.bd_test import right_customer_data, right_order_data


@pytest.fixture()
def right_driver_data():
    return {
        "middle_name": "Иванович",
        "name": "Иван",
        "second_name": "Иванов",
        "phone": "88005553535",
        "email": "kekus@mail.ru",
        "password": hashpw("sets4be4wtest43", gensalt()),
        "qualification": "Выше среднего",
        "experience": 4
    }


@pytest.fixture()
def order_creation_right_data(right_customer_data, right_order_data):
    cargo = Cargo(**right_order_data)
    customer = Customer(**right_customer_data)
    order = Order(cargo=cargo, customer=customer, **right_order_data)
    return order


def test_mutation(right_order_data, order_creation_right_data):
    order = order_creation_right_data
    with pytest.raises(TypeError):
        order.id = uuid.uuid4()


def test_cargo_creation(right_order_data):
    cargo = Cargo(**right_order_data)
    print(cargo)


def test_right_cargo_type_rate(right_order_data):
    cargo = Cargo(**right_order_data)
    assert cargo.get_cargo_type_rate() == 0.25


def test_right_driver_qualification_rate(right_driver_data):
    driver = Driver(**right_driver_data)
    assert driver.get_qualification_rate() == 0.75


def test_update_order_status(right_order_data):
    cargo = Cargo(**right_order_data)
    order = Order(cargo=cargo, **right_order_data)
    order.update_status(OrderStatuses.wait_decision)
    assert order.status.value == 'Ждёт выбора решения'
