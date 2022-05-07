import pytest
from pydantic import ValidationError
from app.controller.controller import Controller


@pytest.fixture()
def wrong_naming_data():
    return {
        "address_from": "2",
        "address_to": "2",
        "cargo_type": "casual",
        "email": "kekus@mail.ru",
        "height": "2",
        "length": "2",
        "weight": "2",
        "width": "2",
        "mname": "Иванович",
        "name": "Иван",
        "sname": "Иванов",
        "phone": "88005553535"
    }


def test_controller_order_creation(wrong_naming_data):
    controller = Controller()
    with pytest.raises(ValidationError):
        controller.make_solutions_by_order(wrong_naming_data)


def test_controller_order_creation_in_db(right_order_data):
    pass

