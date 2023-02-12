from sqlalchemy import create_engine


class SQLiteBase:
    def __init__(self):
        engine = create_engine("sqlite://", echo=True)

    # TODO: Декоратор для транзакций
    # TODO: Описать все кейсы как в mongo.py
    # TODO: Не забыть пресоздать нужные таблицы
