import uuid
import pytest
from app_code.models.entities import Cargo, Customer, Order
from app_code.tests.integration.bd_test import right_customer_data, right_order_data


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


def test_cargo_creation():
    data = {'cargo_type': 'Обычный', 'width': '20', 'length': '20', 'height': '20', 'weight': '40',
            'address_from': '20', 'address_to': '20'}
    cargo = Cargo(**data)
    print(cargo)
