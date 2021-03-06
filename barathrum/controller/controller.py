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


class Controller:
    def create_order(self, customer: Customer, data: dict) -> None:
        cargo = Cargo(**data)
        order = Order(cargo=cargo, **data)
        order.update_status(OrderStatuses.wait_decision)
        db = MongoBase()
        db.upload_order_for_customer(customer, order)

    def make_solutions_by_order_id(self, customer: Customer, order_id: str) -> None:
        db = MongoBase()
        drivers = db.get_vacant_drivers()
        order_db = db.get_order_by_id(customer, order_id)
        order = Order(**order_db)
        solutions = []
        if not drivers:
            return
        for driver in drivers:
            solutions.append(
                Solution(
                    order=order,
                    driver=driver,
                    cost=self.calculate_cost(driver, order.cargo),
                )
            )
            if driver.status != DriverStatuses.is_candidate:
                driver.update_status(DriverStatuses.is_candidate)
                db.update_driver_status(driver)
        db.upload_solutions(solutions)
        order.update_status(OrderStatuses.wait_decision)
        db.update_order_status(customer, order)

    def calculate_cost(self, driver: Driver, cargo: Cargo) -> float:
        base_cost = 400
        qualification_base = 300
        cargo_base = 300
        return (
            base_cost
            + qualification_base * driver.get_qualification_rate()
            + cargo_base * cargo.get_cargo_type_rate()
        )

    def extract_solutions_from_bd(self, order_id: str) -> List[dict]:
        db = MongoBase()
        solutions = db.get_solutions_by_order_id(order_id)
        return solutions

    def sign_up_user(self, data: dict) -> bool:
        data["password"] = hashpw(data["password"].encode('utf-8'), gensalt())
        customer = Customer(**data)
        db = MongoBase()
        try:
            db.upload_customer(customer)
        except CustomerExistsException:
            return False
        return True

    def login_user(self, data: dict) -> Customer:
        db = MongoBase()
        try:
            customer = db.get_customer_by_email(data["email"])
            if checkpw(data["password"].encode('utf-8'), customer.password.encode('utf-8')):
                return customer
        except Exception as e:
            raise e

    def get_user_by_id(self, user_id: str) -> Customer:
        db = MongoBase()
        try:
            customer = db.get_customer_by_id(user_id)
            return customer
        except Exception as e:
            raise e

    def get_orders_by_user(self, customer: Customer) -> List[Order]:
        db = MongoBase()
        orders = []
        orders_db = db.get_orders_by_customer(customer)
        for order in orders_db:
            orders.append(Order(**order))
        return orders

    def confirm_solution(
        self, customer: Customer, order_id: str, solution_id: str
    ) -> None:
        db = MongoBase()
        order_db = db.get_order_by_id(customer, order_id)
        order = Order(**order_db)
        solution_bd = db.get_solution_by_id(solution_id)
        solution_bd.pop("order")
        solution = Solution(order=order, **solution_bd)
        order.set_solution_params(
            driver=solution.driver, cost=solution.cost, time=solution.time
        )
        order.update_status(OrderStatuses.wait_contract_signing)
        order.driver.update_status(DriverStatuses.is_busy)
        db.update_driver_status(order.driver)
        db.update_order_status(customer, order)
        db.update_order_solution_params(customer, order)
        db.delete_solutions_by_order(order)

    def create_agreement(self, customer: Customer, order_id: str) -> str:
        db = MongoBase()
        order_db = db.get_order_by_id(customer, order_id)
        order = Order(**order_db)
        agreement_text = f"??, {customer.name} " \
                         f"{customer.middle_name} " \
                         f"{customer.second_name}, " \
                         f"???????????????? ?? ?????????????????? {order.id}"
        return agreement_text

    def confirm_agreement(self, customer: Customer, order_id: str) -> None:
        db = MongoBase()
        order_db = db.get_order_by_id(customer, order_id)
        order = Order(**order_db)
        order.update_status(OrderStatuses.wait_payments)
        db.update_order_status(customer, order)

    def show_payments(self, customer: Customer, order_id: str) -> str:
        db = MongoBase()
        order_db = db.get_order_by_id(customer, order_id)
        order = Order(**order_db)
        return f"???????????????? ?????????? ?? ?????????????? {order.id} ???? {order.cost} ?????????????"

    def confirm_payments(self, customer: Customer, order_id: str) -> None:
        db = MongoBase()
        order_db = db.get_order_by_id(customer, order_id)
        order = Order(**order_db)
        order.update_status(OrderStatuses.in_progress)
        db.update_order_status(customer, order)
        db.update_order_expected_date(customer, order)

    def accomplish_order(self, customer: Customer, order_id: str) -> None:
        db = MongoBase()
        order_db = db.get_order_by_id(customer, order_id)
        order = Order(**order_db)
        order.update_status(OrderStatuses.ready)
        order.driver.update_status(DriverStatuses.is_waiting)
        db.update_order_status(customer, order)
        db.update_ready_date(customer, order)
        db.update_driver_status(order.driver)
