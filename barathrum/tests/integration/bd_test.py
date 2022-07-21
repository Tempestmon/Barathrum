import random
import string
import time
from typing import Tuple

import pytest
from bcrypt import gensalt, hashpw

from barathrum.controller.db.mongo import CustomerExistsException, MongoBase
from barathrum.models.entities import Cargo, Customer, Order, OrderStatuses


@pytest.fixture()
def right_customer_data():
    return {
        "middle_name": "Иванович",
        "name": "Иван",
        "second_name": "Иванов",
        "phone": "88001111111",
        "email": "kekus@mail.ru",
        "password": hashpw("sets4be4wtest43".encode('utf-8'), gensalt()),
    }


@pytest.fixture()
def get_db_customer_order_by_right_data(
    right_customer_data, right_order_data
) -> Tuple[MongoBase, Customer, Order]:
    customer = Customer(**right_customer_data)
    cargo = Cargo(**right_order_data)
    order = Order(customer=customer, cargo=cargo, **right_order_data)
    db = MongoBase()
    return db, customer, order


@pytest.fixture()
def get_customer_update_from_bd(
    get_db_customer_order_by_right_data,
) -> Tuple[Customer, Customer]:
    db, customer, _ = get_db_customer_order_by_right_data
    db.upload_customer(customer)
    customer_from_bd = db.get_customer_by_email("kekus@mail.ru")
    db.delete_customer(customer)
    return customer_from_bd, customer


class TestDataBase:
    def test_db_upload_and_delete_order(self, get_db_customer_order_by_right_data):
        db, customer, order = get_db_customer_order_by_right_data
        db.upload_customer(customer)
        db.upload_order_for_customer(customer, order)
        db.delete_customer(customer)

    def test_db_upload_and_find_order(self, get_db_customer_order_by_right_data):
        db, customer, order = get_db_customer_order_by_right_data
        db.upload_customer(customer)
        db.upload_order_for_customer(customer, order)
        db.get_order_by_id(customer, str(order.id))
        db.delete_customer(customer)

    def test_db_order_insert_with_same_email_or_phone(
        self, get_db_customer_order_by_right_data
    ):
        db, customer, order = get_db_customer_order_by_right_data
        db.upload_customer(customer)
        with pytest.raises(CustomerExistsException):
            db.upload_customer(customer)
        db.delete_customer(customer)

    def test_db_order_update_status(self, get_db_customer_order_by_right_data):
        db, customer, order = get_db_customer_order_by_right_data
        db.upload_customer(customer)
        db.upload_order_for_customer(customer, order)
        order.update_status(OrderStatuses.ready)
        db.update_order_status(customer, order)
        db_order = db.get_order_by_id(customer, str(order.id))
        db.delete_customer(customer)
        assert db_order["status"] == order.status.value

    def test_db_customer_find_by_email(self, get_customer_update_from_bd):
        customer_from_bd, customer = get_customer_update_from_bd
        assert customer.id == customer_from_bd.id


class TestPassword:
    def test_check_hashed_pwd(self, get_customer_update_from_bd):
        customer_from_bd, customer = get_customer_update_from_bd
        assert customer.password == customer_from_bd.password


class TestPerformance:
    def test_insert_get_orders_performance(self, get_db_customer_order_by_right_data):
        db, customer, _ = get_db_customer_order_by_right_data
        db.upload_customer(customer)
        orders = []
        random_orders = []
        letters = string.ascii_lowercase
        for i in range(5000):
            random_order = {
                "address_from": "".join(random.choice(letters) for j in range(10)),
                "address_to": "".join(random.choice(letters) for j in range(10)),
                "cargo_type": "Обычный",
                "height": random.randrange(10),
                "length": random.randrange(10),
                "weight": random.randrange(10),
                "width": random.randrange(10),
            }
            cargo = Cargo(**random_order)
            order = Order(customer=customer, cargo=cargo, **random_order)
            orders.append(order)
            random_orders.append(random_order)
        insert_start = time.time()
        # db.upload_orders_for_customer(customer, orders)
        db.upload_orders_for_customer_json(customer, random_orders)
        insert_end = time.time()
        print(f"Insert time: {(insert_end - insert_start) * 1000}")
        get_start = time.time()
        db.get_orders_by_customer(customer)
        get_end = time.time()
        print(f"Get time: {(get_end - get_start) * 1000}")
