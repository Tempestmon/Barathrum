import logging
from barathrum.config import LOGGING_CONFIG
from typing import List

from bcrypt import checkpw, gensalt, hashpw

from barathrum.controller.db.mongo import CustomerExistsException, MongoBase
from barathrum.models.entities import (
    Cargo,
    Customer,
    Driver,
    DriverStatuses,
    Order,
    OrderStatuses,
    Solution,
)

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger('barathrum')


class WrongPasswordException(Exception):
    pass


class Controller:
    database: MongoBase

    def __init__(self, database: MongoBase):
        self.database = database

    @staticmethod
    def _calculate_cost(driver: Driver, cargo: Cargo) -> float:
        base_cost = 400
        qualification_base = 300
        cargo_base = 300
        logger.info("Calculated driver cost with ")
        cost = (
            base_cost
            + qualification_base * driver.get_qualification_rate()
            + cargo_base * cargo.get_cargo_type_rate()
        )
        return cost

    def create_order(self, customer: Customer, data: dict) -> None:
        cargo = Cargo(**data)
        order = Order(cargo=cargo, **data)
        order.update_status(OrderStatuses.WAIT_DECISION)
        self.database.upload_order_for_customer(customer, order)

    def make_solutions_by_order_id(self, customer: Customer, order_id: str) -> None:
        drivers = self.database.get_vacant_drivers()
        order_db = self.database.get_order_by_id(customer, order_id)
        order = Order(**order_db)
        solutions = []
        if not drivers:
            logger.info("Did not find any drivers")
            return
        for driver in drivers:
            solutions.append(
                Solution(
                    order=order,
                    driver=driver,
                    cost=self._calculate_cost(driver, order.cargo),
                )
            )
            if driver.status != DriverStatuses.IS_CANDIDATE:
                logger.info(f"Setting driver with id={driver.id} as candidate")
                driver.update_status(DriverStatuses.IS_CANDIDATE)
                self.database.update_driver_status(driver)
        self.database.upload_solutions(solutions)
        order.update_status(OrderStatuses.WAIT_DECISION)
        self.database.update_order_status(customer, order)

    def extract_solutions_from_bd(self, order_id: str) -> List[dict]:
        solutions = self.database.get_solutions_by_order_id(order_id)
        return solutions

    def sign_up_user(self, data: dict) -> bool:
        data["password"] = hashpw(data["password"].encode("utf-8"), gensalt())
        customer = Customer(**data)
        try:
            self.database.upload_customer(customer)
        except CustomerExistsException:
            logger.info(f"User with {customer} already exists")
            return False
        logger.info(f"User {customer} does not exists in db")
        return True

    def login_user(self, data: dict) -> Customer:
        customer = self.database.get_customer_by_email(data["email"])
        if checkpw(
            data["password"].encode("utf-8"), customer.password.encode("utf-8")
        ):
            logger.info(f"{customer} is authenticated")
            return customer
        raise WrongPasswordException

    def get_user_by_id(self, user_id: str) -> Customer:
        customer = self.database.get_customer_by_id(user_id)
        logger.info(f"Found user {customer}")
        return customer

    def get_orders_by_user(self, customer: Customer) -> List[Order]:
        orders = []
        orders_db = self.database.get_orders_by_customer(customer)
        for order in orders_db:
            logger.info(f"Found order {order} for customer {customer}")
            orders.append(Order(**order))
        return orders

    def confirm_solution(
        self, customer: Customer, order_id: str, solution_id: str
    ) -> None:
        order_db = self.database.get_order_by_id(customer, order_id)
        order = Order(**order_db)
        solution_bd = self.database.get_solution_by_id(solution_id)
        solution_bd.pop("order")
        solution = Solution(order=order, **solution_bd)
        order.set_solution_params(
            driver=solution.driver, cost=solution.cost, time=solution.time
        )
        order.update_status(OrderStatuses.WAIT_CONTRACT_SIGNING)
        order.driver.update_status(DriverStatuses.IS_BUSY)
        self.database.update_driver_status(order.driver)
        self.database.update_order_status(customer, order)
        self.database.update_order_solution_params(customer, order)
        self.database.delete_solutions_by_order(order)
        logger.info(f"{customer} confirmed {solution}")

    def create_agreement(self, customer: Customer, order_id: str) -> str:
        order_db = self.database.get_order_by_id(customer, order_id)
        order = Order(**order_db)
        agreement_text = (
            f"Я, {customer.name} "
            f"{customer.middle_name} "
            f"{customer.second_name}, "
            f"согласен с условиями {order.id}"
        )
        logger.info(f"Created agreement for {customer}")
        return agreement_text

    def confirm_agreement(self, customer: Customer, order_id: str) -> None:
        order_db = self.database.get_order_by_id(customer, order_id)
        order = Order(**order_db)
        order.update_status(OrderStatuses.WAIT_PAYMENTS)
        self.database.update_order_status(customer, order)
        logger.info(f"{customer} confirmed agreement order_id={order_id}")

    def show_payments(self, customer: Customer, order_id: str) -> str:
        order_db = self.database.get_order_by_id(customer, order_id)
        order = Order(**order_db)
        return f"Оплатить заказ с номером {order.id} за {order.cost} рублей?"

    def confirm_payments(self, customer: Customer, order_id: str) -> None:
        order_db = self.database.get_order_by_id(customer, order_id)
        order = Order(**order_db)
        order.update_status(OrderStatuses.IN_PROGRESS)
        self.database.update_order_status(customer, order)
        self.database.update_order_expected_date(customer, order)

    def accomplish_order(self, customer: Customer, order_id: str) -> None:
        order_db = self.database.get_order_by_id(customer, order_id)
        order = Order(**order_db)
        order.update_status(OrderStatuses.READY)
        order.driver.update_status(DriverStatuses.IS_WAITING)
        self.database.update_order_status(customer, order)
        self.database.update_ready_date(customer, order)
        self.database.update_driver_status(order.driver)
