import pytest
from typing import Tuple
from app_code.controller.db.mongo import MongoBase
from app_code.models.entities import Order, Cargo, Customer
from pymongo.errors import DuplicateKeyError


@pytest.fixture()
def right_order_data():
    return {
        "address_from": "2",
        "address_to": "2",
        "cargo_type": "casual",
        "email": "kekus@mail.ru",
        "height": "2",
        "length": "2",
        "weight": "2",
        "width": "2",
        "middle_name": "Иванович",
        "name": "Иван",
        "second_name": "Иванов",
        "phone": "88005553535"
    }


@pytest.fixture()
def get_order_and_db_by_right_data(right_order_data) -> Tuple[MongoBase, Order]:
    customer = Customer(**right_order_data)
    cargo = Cargo(**right_order_data)
    order = Order(customer=customer, cargo=cargo, **right_order_data)
    db = MongoBase()
    return db, order


def test_db_upload_and_delete_order(get_order_and_db_by_right_data):
    db, order = get_order_and_db_by_right_data
    db.upload_order(order)
    db.delete_order(order)


def test_db_upload_and_find_order(get_order_and_db_by_right_data):
    db, order = get_order_and_db_by_right_data
    db.upload_order(order)
    db.get_order_by_id(str(order.id))
    db.delete_order(order)


def test_db_order_insert_with_same_id(get_order_and_db_by_right_data):
    db, order = get_order_and_db_by_right_data
    db.upload_order(order)
    with pytest.raises(DuplicateKeyError):
        db.upload_order(order)
        db.delete_order(order)
    db.delete_order(order)


def test_db_order_update_status(get_order_and_db_by_right_data):
    pass
