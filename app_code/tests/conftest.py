import pytest


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
