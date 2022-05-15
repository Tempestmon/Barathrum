from typing import Tuple

import pytest
from bcrypt import hashpw, gensalt

from app_code.controller.db.mongo import MongoBase, CustomerExistsException
from app_code.models.entities import Order, Cargo, Customer, OrderStatuses


@pytest.fixture()
def right_order_data():
    return {
        "address_from": "2",
        "address_to": "2",
        "cargo_type": "Обычный",
        "height": "2",
        "length": "2",
        "weight": "2",
        "width": "2",
    }


@pytest.fixture()
def right_customer_data():
    return {
        "middle_name": "Иванович",
        "name": "Иван",
        "second_name": "Иванов",
        "phone": "88001111111",
        "email": "kekus@mail.ru",
        "password": hashpw("sets4be4wtest43", gensalt())
    }


@pytest.fixture()
def get_db_customer_order_by_right_data(right_customer_data, right_order_data) -> Tuple[MongoBase, Customer, Order]:
    customer = Customer(**right_customer_data)
    cargo = Cargo(**right_order_data)
    order = Order(customer=customer, cargo=cargo, **right_order_data)
    db = MongoBase()
    return db, customer, order


@pytest.fixture()
def get_customer_update_from_bd(get_db_customer_order_by_right_data) -> Tuple[Customer, Customer]:
    db, customer, _ = get_db_customer_order_by_right_data
    db.upload_customer(customer)
    customer_from_bd = db.get_customer_by_email('kekus@mail.ru')
    db.delete_customer(customer)
    return customer_from_bd, customer


def test_db_upload_and_delete_order(get_db_customer_order_by_right_data):
    db, customer, order = get_db_customer_order_by_right_data
    db.upload_customer(customer)
    db.upload_order_for_customer(customer, order)
    db.delete_customer(customer)


def test_db_upload_and_find_order(get_db_customer_order_by_right_data):
    db, customer, order = get_db_customer_order_by_right_data
    db.upload_customer(customer)
    db.upload_order_for_customer(customer, order)
    db.get_order_by_id(customer, str(order.id))
    db.delete_customer(customer)


def test_db_order_insert_with_same_email_or_phone(get_db_customer_order_by_right_data):
    db, customer, order = get_db_customer_order_by_right_data
    db.upload_customer(customer)
    with pytest.raises(CustomerExistsException):
        db.upload_customer(customer)
    db.delete_customer(customer)


def test_db_order_update_status(get_db_customer_order_by_right_data):
    db, customer, order = get_db_customer_order_by_right_data
    db.upload_customer(customer)
    db.upload_order_for_customer(customer, order)
    order.update_status(OrderStatuses.ready)
    db.update_order_status(customer, order)
    db_order = db.get_order_by_id(customer, str(order.id))
    db.delete_customer(customer)
    assert db_order['status'] == order.status.value


def test_db_customer_find_by_email(get_customer_update_from_bd):
    customer_from_bd, customer = get_customer_update_from_bd
    assert customer.id == customer_from_bd.id


def test_check_hashed_pwd(get_customer_update_from_bd):
    customer_from_bd, customer = get_customer_update_from_bd
    assert customer.password == customer_from_bd.password
