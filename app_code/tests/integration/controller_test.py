import pytest
from pydantic import ValidationError
from app_code.controller.controller import Controller


@pytest.fixture()
def user_data():
    return {
        "email": "kekus@mail.ru",
        "middle_name": "Иванович",
        "name": "Иван",
        "second_name": "Иванов",
        "phone": "88005553535"
    }


def test_create_order():
    pass


def test_make_solutions_by_order_id():
    pass


def test_calculate_cost():
    pass


def test_extract_solutions_from_bd():
    pass


def test_sign_up_user():
    pass


def test_login_user():
    pass


def test_get_user_by_id():
    pass


def test_get_orders_by_user():
    pass


def test_confirm_solution():
    pass


def test_create_agreement():
    pass


def test_confirm_agreement():
    pass


def test_show_payments():
    pass


def test_confirm_payments():
    pass


def test_accomplish_order():
    pass
