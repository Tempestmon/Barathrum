from app.models.entities import Customer, Order, Cargo, Solution
from app.controller.db.mongo import MongoBase
from typing import List


class Controller:

    def make_solutions_by_order(self, data: dict) -> None:
        customer = Customer(**data)
        cargo = Cargo(**data)
        order = Order(customer=customer, cargo=cargo, **data)
        db = MongoBase()
        db.upload_order(order)
        self._create_soutions(order)

    def _create_soutions(self, order: Order) -> List[Solution]:
        db = MongoBase()
        drivers = db.get_vacant_driver(order)
        solutions = []
        if not drivers:
            return solutions
        # TODO: получать по квалификации и типу груза их коэффициенты (мб сделать методы классов)
        for driver in drivers:
            solutions.append(Solution(
                order=order,
                driver=driver,
                cost=self._calculate_cost(driver.qualification, order.cargo)
            ))
        db.upload_solutions(solutions)
        db.update_order_status(order)
        return solutions

    # TODO: мб вынести куда-то
    @staticmethod
    def _calculate_cost(qualification_rate: float, cargo_type_rate: float) -> float:
        base_cost = 400
        qualification_base = 300
        cargo_base = 300
        return base_cost + qualification_base * qualification_rate + cargo_base * cargo_type_rate

    def extract_solutions_from_bd(self) -> List[Solution]:
        pass
