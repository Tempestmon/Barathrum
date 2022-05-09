import os
from os.path import join, dirname
from typing import List, Union, Type

from dotenv import load_dotenv
from orjson import orjson
from pydantic import BaseModel
from pymongo import MongoClient
from pymongo.errors import OperationFailure
from pymongo.results import DeleteResult, InsertOneResult, UpdateResult, InsertManyResult

from app_code.models.entities import Order, Driver, Solution, Customer

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

    def delete_entity(self, entity: BaseModel) -> DeleteResult:
        try:
            entity_dict = orjson.loads(entity.json())
            entity_id = str(entity_dict['id'])
            collection_name = entity.__class__.__name__.lower()
            result = self.client[self.DATABASE_NAME][collection_name].delete_one({'id': entity_id})
        except OperationFailure as e:
            raise e
        return result

    def get_query_result_by_field(self, entity: Type[Union[Order, Driver, Solution, Customer]], field: str,
                                  value: Union[str, float, int]) -> dict:
        try:
            result = self.client[self.DATABASE_NAME][entity.__name__.lower()].find_one({field: f"{value}"})
        except Exception as e:
            raise e
        return result

    def upload_order(self, order: Order) -> InsertOneResult:
        return self.upload_entity(order)

    def delete_order(self, order: Order) -> DeleteResult:
        return self.delete_entity(order)

    def get_order_by_id(self, order_id: str) -> Union[Order, None]:
        result = self.get_query_result_by_field(Order, 'id', order_id)
        if result is None:
            return result
        return Order(**result)

    def upload_customer(self, customer: Customer) -> InsertOneResult:
        if self.get_customer_by_email(customer.email) is not None:
            raise CustomerExistsException
        return self.upload_entity(customer)

    def get_customer_by_email(self, email: str) -> Union[Customer, None]:
        result = self.get_query_result_by_field(Customer, 'email', email)
        if result is None:
            return None
        return Customer(**result)

    def update_order_status(self, order: Order) -> UpdateResult:
        pass

    def get_vacant_driver(self, order: Order) -> List[Driver]:
        pass

    def upload_solutions(self, solutions: List[Solution]) -> InsertManyResult:
        pass

    def delete_customer(self, customer) -> DeleteResult:
        return self.delete_entity(customer)

    def get_customer_by_id(self, user_id: str):
        result = self.get_query_result_by_field(Customer, 'id', user_id)
        if result is None:
            return None
        return Customer(**result)
