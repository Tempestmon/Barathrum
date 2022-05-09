import os
from os.path import join, dirname
from pymongo import MongoClient
from pymongo.errors import OperationFailure
from pymongo.results import DeleteResult, InsertOneResult, UpdateResult, InsertManyResult
from orjson import orjson
from app_code.models.entities import Order, Driver, Solution, Customer
from typing import List, Union
from dotenv import load_dotenv
from pydantic import BaseModel

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

    def upload_order(self, order: Order) -> InsertOneResult:
        return self.upload_entity(order)

    def delete_order(self, order: Order) -> DeleteResult:
        return self.delete_entity(order)

    def get_order_by_id(self, order_id: str) -> Order:
        try:
            result = self.client[self.DATABASE_NAME]['order'].find_one({'id': order_id})
        except OperationFailure as e:
            raise e
        return Order(**result)

    def upload_customer(self, customer: Customer) -> InsertOneResult:
        if self.get_customer_by_email(customer.email) is not None:
            raise CustomerExistsException
        return self.upload_entity(customer)

    def get_customer_by_email(self, email: str) -> Union[Customer, None]:
        try:
            result = self.client[self.DATABASE_NAME]['customer'].find_one({'email': email})
        except OperationFailure as e:
            raise e
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
        try:
            result = self.client[self.DATABASE_NAME]['customer'].find_one({'id': user_id})
        except OperationFailure as e:
            raise e
        if result is None:
            return None
        return Customer(**result)
