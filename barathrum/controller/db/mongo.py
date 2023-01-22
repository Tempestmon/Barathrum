import os
from os.path import dirname, join
from typing import List, Type, Union

from dotenv import load_dotenv
from orjson import orjson
from pymongo import MongoClient
from pymongo.errors import OperationFailure
from pymongo.results import (
    DeleteResult,
    InsertManyResult,
    InsertOneResult,
    UpdateResult,
)

from barathrum.models.entities import (
    BaseModel,
    Customer,
    Driver,
    DriverStatuses,
    Order,
    Solution,
)

dotenv_path = join(dirname(__file__), "envs.env")
load_dotenv(dotenv_path)


# TODO: Надо сделать операции с БД транзакционными


class CustomerExistsException(Exception):
    pass


class MongoBase:
    client = MongoClient(
        f"mongodb://{os.environ.get('MONGO_USER')}:"
        f"{os.environ.get('MONGO_PASSWORD')}"
        f"@{os.environ.get('MONGO_HOST')}:27017/"
    )

    DATABASE_NAME = "barathrum"

    def upload_entity(self, entity: BaseModel) -> InsertOneResult:
        try:
            entity_dict = orjson.loads(entity.json())
            collection_name = entity.__class__.__name__.lower()
            result = self.client[self.DATABASE_NAME][collection_name].insert_one(
                entity_dict
            )
        except OperationFailure as e:
            raise e
        return result

    def upload_entities(self, entities: List[BaseModel]) -> InsertManyResult:
        try:
            entity_dict = [orjson.loads(entity.json()) for entity in entities]
            for entity in entity_dict:
                entity["order"] = entity["order"]["id"]
            collection_name = entities[0].__class__.__name__.lower()
            result = self.client[self.DATABASE_NAME][collection_name].insert_many(
                entity_dict
            )
        except OperationFailure as e:
            raise e
        return result

    def delete_entity(self, entity: BaseModel) -> DeleteResult:
        try:
            entity_dict = orjson.loads(entity.json())
            entity_id = str(entity_dict["id"])
            collection_name = entity.__class__.__name__.lower()
            result = self.client[self.DATABASE_NAME][collection_name].delete_one(
                {"id": entity_id}
            )
        except OperationFailure as e:
            raise e
        return result

    def get_one_result_by_field(
        self, entity: Type[BaseModel], field: str, value: Union[str, float, int]
    ) -> dict:
        try:
            result = self.client[self.DATABASE_NAME][entity.__name__.lower()].find_one(
                {field: f"{value}"}
            )
        except OperationFailure as e:
            raise e
        return result

    def get_results_by_field(
        self, entity: Type[BaseModel], field: str, value: Union[str, float, int]
    ) -> List[dict]:
        result = []
        try:
            cursor = self.client[self.DATABASE_NAME][entity.__name__.lower()].find(
                {field: f"{value}"}
            )
        except OperationFailure as e:
            raise e
        for record in cursor:
            result.append(record)
        return result

    def get_results_by_field_query_or(
        self,
        entity: Type[BaseModel],
        field: str,
        values: List[Union[str, float, int]],
        limit: int = None,
    ) -> List[dict]:
        result = []
        query = [{f"{field}": value} for value in values]
        try:
            if limit is None:
                cursor = self.client[self.DATABASE_NAME][entity.__name__.lower()].find(
                    {"$or": query}
                )
            else:
                cursor = (
                    self.client[self.DATABASE_NAME][entity.__name__.lower()]
                    .find({"$or": query})
                    .limit(limit)
                )
        except OperationFailure as e:
            raise e
        for record in cursor:
            result.append(record)
        return result

    def update_entity(
        self, entity: BaseModel, field: str, value: Union[str, float, int, List]
    ) -> UpdateResult:
        try:
            result = self.client[self.DATABASE_NAME][
                entity.__class__.__name__.lower()
            ].update_one({"id": str(entity.id)}, {"$set": {f"{field}": value}})
        except OperationFailure as e:
            raise e
        return result

    def upload_order_for_customer(
        self, customer: Customer, order: Order
    ) -> UpdateResult:
        orders = self.get_orders_by_customer(customer)
        orders.append(orjson.loads(order.json()))
        return self.update_entity(customer, "orders", orders)

    def upload_orders_for_customer(
        self, customer: Customer, orders: List[Order]
    ) -> UpdateResult:
        orders_to_db = [orjson.loads(obj.json()) for obj in orders]
        return self.update_entity(customer, "orders", orders_to_db)

    def upload_orders_for_customer_json(
        self, customer: Customer, orders: List
    ) -> UpdateResult:
        return self.update_entity(customer, "orders", orders)

    def delete_order(self, order: Order) -> DeleteResult:
        return self.delete_entity(order)

    def get_order_by_id(self, customer: Customer, order_id: str) -> Union[dict, None]:
        result = None
        orders_db = self.get_orders_by_customer(customer)
        for order in orders_db:
            if order["id"] == order_id:
                result = order
        if result is None:
            return result
        return result

    def get_orders_by_customer(self, customer) -> List[dict]:
        result = self.get_one_result_by_field(Customer, "id", customer.id)
        orders_db = result["orders"]
        orders = []
        if not orders_db:
            return orders
        try:
            for order in orders_db:
                orders.append(order)
        except Exception as e:
            raise e
        return orders

    def upload_customer(self, customer: Customer) -> InsertOneResult:
        if (
            self.get_customer_by_email(customer.email) is not None
            or self.get_customer_by_phone(customer.phone) is not None
        ):
            raise CustomerExistsException
        return self.upload_entity(customer)

    def get_customer_by_email(self, email: str) -> Union[Customer, None]:
        result = self.get_one_result_by_field(Customer, "email", email)
        if result is None:
            return None
        return Customer(**result)

    def get_customer_by_phone(self, phone: str) -> Union[Customer, None]:
        result = self.get_one_result_by_field(Customer, "phone", phone)
        if result is None:
            return None
        return Customer(**result)

    def delete_customer(self, customer: Customer) -> DeleteResult:
        return self.delete_entity(customer)

    def get_customer_by_id(self, user_id: str):
        result = self.get_one_result_by_field(Customer, "id", user_id)
        if result is None:
            return None
        return Customer(**result)

    def update_order_status(self, customer: Customer, order: Order) -> UpdateResult:
        orders = self.get_orders_by_customer(customer)
        for order_db in orders:
            if order_db["id"] == str(order.id):
                order_db["status"] = order.status.value
        return self.update_entity(customer, "orders", orders)

    def get_vacant_drivers(self) -> List[Driver]:
        results = self.get_results_by_field_query_or(
            Driver,
            "status",
            [DriverStatuses.IS_WAITING.value, DriverStatuses.IS_CANDIDATE.value],
            10,
        )
        drivers = []
        for result in results:
            drivers.append(Driver(**result))
        return drivers

    def upload_solutions(self, solutions: List[Solution]) -> InsertManyResult:
        return self.upload_entities(solutions)

    def update_driver_status(self, driver: Driver) -> UpdateResult:
        return self.update_entity(driver, "status", driver.status.value)

    def get_solutions_by_order_id(self, order_id: str) -> List[dict]:
        return self.get_results_by_field(Solution, "order", order_id)

    def get_solution_by_id(self, solution_id: str) -> dict:
        return self.get_one_result_by_field(Solution, "id", solution_id)

    def get_driver_by_id(self, driver_id: str) -> dict:
        return self.get_one_result_by_field(Driver, "id", driver_id)

    def update_order_solution_params(
        self, customer: Customer, order: Order
    ) -> UpdateResult:
        orders = self.get_orders_by_customer(customer)
        for order_db in orders:
            if order_db["id"] == str(order.id):
                order_db["driver"] = self.get_driver_by_id(str(order.driver.id))
                order_db["cost"] = order.cost
                order_db["time"] = order.time
        return self.update_entity(customer, "orders", orders)

    def delete_solutions_by_order(self, order: Order) -> DeleteResult:
        try:
            result = self.client[self.DATABASE_NAME][
                Solution.__name__.lower()
            ].delete_many({"order": str(order.id)})
        except OperationFailure as e:
            raise e
        return result

    def update_order_expected_date(self, customer, order) -> UpdateResult:
        orders = self.get_orders_by_customer(customer)
        for order_db in orders:
            if order_db["id"] == str(order.id):
                order_db["expected_date"] = order.expected_date
        return self.update_entity(customer, "orders", orders)

    def update_ready_date(self, customer, order) -> UpdateResult:
        orders = self.get_orders_by_customer(customer)
        for order_db in orders:
            if order_db["id"] == str(order.id):
                order_db["ready_date"] = order.ready_date
        return self.update_entity(customer, "orders", orders)
