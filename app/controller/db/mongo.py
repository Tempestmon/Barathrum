from pymongo import MongoClient
from pymongo.errors import OperationFailure
from pymongo.results import DeleteResult, InsertOneResult, UpdateResult, InsertManyResult
from os import getenv
from orjson import orjson
from app.models.entities import Order, Driver, Solution
from typing import List


class MongoBase:
    client = MongoClient('mongodb://%s:%s@localhost:27017/' % (getenv('MONGO_USER', 'barathrum_admin'),
                         getenv('MONGO_PASSWORD', 'iogaeS0JaeThee0aibah')))

    DATABASE_NAME = 'barathrum'
    ORDER_COLLECTION_NAME = 'orders'
    DRIVER_COLLECTION_NAME = 'drivers'
    SOLUTION_COLLECTION_NAME = 'solutions'

    BARATHRUM_ORDER_COLLECTION = client[DATABASE_NAME][ORDER_COLLECTION_NAME]

    def upload_order(self, order: Order) -> InsertOneResult:
        try:
            order_dict = orjson.loads(order.json())
            result = self.BARATHRUM_ORDER_COLLECTION.insert_one(order_dict)
        except OperationFailure as e:
            raise e
        return result

    def delete_order(self, order: Order) -> DeleteResult:
        try:
            order_id = str(order.id)
            result = self.BARATHRUM_ORDER_COLLECTION.delete_one({'id': order_id})
        except OperationFailure as e:
            raise e
        return result

    def get_order_by_id(self, order_id: str) -> Order:
        try:
            result = self.BARATHRUM_ORDER_COLLECTION.find_one({'id': order_id})
        except OperationFailure as e:
            raise e
        return Order(**result)

    def update_order_status(self, order: Order) -> UpdateResult:
        pass

    def get_vacant_driver(self, order: Order) -> List[Driver]:
        pass

    def upload_solutions(self, solutions: List[Solution]) -> InsertManyResult:
        pass
