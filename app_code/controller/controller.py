from app_code.models.entities import Customer, Order, Cargo, Solution, Driver, OrderStatuses, DriverStatuses
from app_code.controller.db.mongo import MongoBase, CustomerExistsException
from typing import List
from bcrypt import hashpw, checkpw, gensalt


class Controller:

    def make_solutions_by_order(self, customer: Customer, data: dict) -> None:
        cargo = Cargo(**data)
        order = Order(cargo=cargo, **data)
        db = MongoBase()
        db.upload_order_for_customer(customer, order)
        self._create_solutions(order)

    def _create_solutions(self, order: Order) -> None:
        db = MongoBase()
        drivers = db.get_vacant_drivers()
        solutions = []
        if not drivers:
            return
        for driver in drivers:
            solutions.append(Solution(
                order=order,
                driver=driver,
                cost=self.calculate_cost(driver, order.cargo)
            ))
            if driver.status != DriverStatuses.is_candidate:
                driver.update_status(DriverStatuses.is_candidate)
                db.update_driver_status(driver)
        db.upload_solutions(solutions)
        order.update_status(OrderStatuses.wait_decision)
        db.update_order_status(order)

    def calculate_cost(self, driver: Driver, cargo: Cargo) -> float:
        base_cost = 400
        qualification_base = 300
        cargo_base = 300
        return base_cost + qualification_base * driver.get_qualification_rate() + cargo_base * cargo.get_cargo_type_rate()

    def extract_solutions_from_bd(self, order_id: str) -> List[dict]:
        db = MongoBase()
        solutions = db.get_solutions_by_order_id(order_id)
        return solutions

    def sign_up_user(self, data: dict) -> bool:
        data['password'] = hashpw(data['password'], gensalt())
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
            customer = db.get_customer_by_email(data['email'])
            if checkpw(data['password'], customer.password):
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

    def get_orders_by_user(self, customer: Customer) -> List[dict]:
        db = MongoBase()
        orders = db.get_orders_by_customer(customer)
        return orders
