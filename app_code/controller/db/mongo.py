import os
from os.path import join, dirname
from typing import List, Union, Type

from dotenv import load_dotenv
from orjson import orjson
from pymongo import MongoClient
from pymongo.errors import OperationFailure
from pymongo.results import DeleteResult, InsertOneResult, UpdateResult, InsertManyResult

from app_code.models.entities import Order, Driver, Solution, Customer, BaseModel, DriverStatuses

dotenv_path = join(dirname(__file__), 'envs.env')
load_dotenv(dotenv_path)


class CustomerExistsException(Exception):
    pass


class MongoBase:
    client = MongoClient('mongodb://%s:%s@localhost:27017/' % (os.environ.get('MONGO_USER'),
                                                               os.environ.get('MONGO_PASSWORD')))

    DATABASE_NAME = 'barathrum'

    def upload_entity(self, entity: BaseModel) -> InsertOneResult:
        try:
            entity_dict = orjson.loads(entity.json())
            collection_name = entity.__class__.__name__.lower()
            result = self.client[self.DATABASE_NAME][collection_name].insert_one(entity_dict)
        except OperationFailure as e:
            raise e
        return result

    def upload_entities(self, entities: List[BaseModel]) -> InsertManyResult:
        try:
            entity_dict = [orjson.loads(entity.json()) for entity in entities]
            collection_name = entities.__class__.__name__.lower()
            result = self.client[self.DATABASE_NAME][collection_name].insert_many(entity_dict)
        except OperationFailure as e:
            raise e
        return result

    def delete_entity(self, entity: BaseModel) -> DeleteResult:
        try:
            entity_dict = orjson.loads(entity.json())
            entity_id = str(entity_dict['id'])
            collection_name = entity.__class__.__name__.lower()
            result = self.client[self.DATABASE_NAME][collection_name].delete_one({'id': entity_id})
        except OperationFailure as e:
            raise e
        return result

    def get_one_result_by_field(self, entity: Type[BaseModel], field: str,
                                value: Union[str, float, int]) -> dict:
        try:
            result = self.client[self.DATABASE_NAME][entity.__name__.lower()].find_one({field: f"{value}"})
        except OperationFailure as e:
            raise e
        return result

    def get_results_by_field(self, entity: Type[BaseModel], field: str,
                             value: Union[str, float, int]) -> List[dict]:
        result = []
        try:
            cursor = self.client[self.DATABASE_NAME][entity.__name__.lower()].find({field: f"{value}"})
        except OperationFailure as e:
            raise e
        for record in cursor:
            result.append(record)
        return result

    def get_results_by_field_query_or(self, entity: Type[BaseModel], field: str,
                                      values: List[Union[str, float, int]]) -> List[dict]:
        result = []
        query = [{f"{field}": value} for value in values]
        try:
            cursor = self.client[self.DATABASE_NAME][entity.__name__.lower()].find({"$or": query})
        except OperationFailure as e:
            raise e
        for record in cursor:
            result.append(record)
        return result

    def update_entity(self, entity: BaseModel, field: str,
                      value: Union[str, float, int, List]) -> UpdateResult:
        try:
            result = self.client[self.DATABASE_NAME][entity.__class__.__name__.lower()].update_one(
                {"id": str(entity.id)},
                {"$set": {f"{field}": value}})
        except OperationFailure as e:
            raise e
        return result

    def upload_order_for_customer(self, customer: Customer, order: Order) -> UpdateResult:
        orders = self.get_orders_by_customer(customer)
        orders.append(orjson.loads(order.json()))
        return self.update_entity(customer, 'orders', orders)

    def delete_order(self, order: Order) -> DeleteResult:
        return self.delete_entity(order)

    def get_order_by_id(self, order_id: str) -> Union[Order, None]:
        result = self.get_one_result_by_field(Order, 'id', order_id)
        if result is None:
            return result
        return Order(**result)

    def get_orders_by_customer(self, customer) -> List[Order]:
        result = self.get_one_result_by_field(Customer, 'id', customer.id)['orders']
        orders = []
        try:
            for order in result:
                orders.append(Order(**order))
        except Exception as e:
            raise e
        return orders

    def upload_customer(self, customer: Customer) -> InsertOneResult:
        if self.get_customer_by_email(customer.email) is not None and self.get_customer_by_phone(
                customer.phone) is not None:
            raise CustomerExistsException
        return self.upload_entity(customer)

    def get_customer_by_email(self, email: str) -> Union[Customer, None]:
        result = self.get_one_result_by_field(Customer, 'email', email)
        if result is None:
            return None
        return Customer(**result)

    def get_customer_by_phone(self, phone: str) -> Union[Customer, None]:
        result = self.get_one_result_by_field(Customer, 'phone', phone)
        if result is None:
            return None
        return Customer(**result)

    def delete_customer(self, customer: Customer) -> DeleteResult:
        return self.delete_entity(customer)

    def get_customer_by_id(self, user_id: str):
        result = self.get_one_result_by_field(Customer, 'id', user_id)
        if result is None:
            return None
        return Customer(**result)

    def update_order_status(self, order: Order) -> UpdateResult:
        return self.update_entity(order, 'status', order.status.value)

    def get_vacant_drivers(self) -> List[Driver]:
        results = self.get_results_by_field_query_or(Driver, 'status', [DriverStatuses.is_waiting.value,
                                                                        DriverStatuses.is_candidate.value])
        drivers = []
        for result in results:
            drivers.append(Driver(**result))
        return drivers

    def upload_solutions(self, solutions: List[Solution]) -> InsertManyResult:
        return self.upload_entities(solutions)
