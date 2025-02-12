import os
from typing import List, Tuple, Dict

from psycopg2 import sql, connect
from psycopg2.extras import RealDictCursor
import json

from utils import Singleton


class Connection(Singleton):
    _connection = None

    def __init__(self):
        dbname = os.environ.get('POSTGRES_DB', 'postgresDB')
        user = os.environ.get('POSTGRES_USER', 'postgresUser')
        password = os.environ.get('POSTGRES_PASSWORD', 'postgresPW')
        host = os.environ.get('POSTGRES_HOST', 'localhost')
        port = os.environ.get('POSTGRES_PORT', 5455)
        try:
            self._connection = connect(
                dbname=dbname,
                user=user,
                host=host,
                password=password,
                port=port
            )
            print('Connected to DB')
        except Exception as err:
            print('Error connection to db: ', err)


class BasicDao:
    _connection = Connection()

    def __init__(self, table : str, schema: str = 'public'):
        self.table = table
        self.schema = schema

    # Execute sql query
    def execute_sql(self, sql: str):
        if not self._connection:
            return None
        try:
            cursor = self._connection.cursor()
            cursor.execute(sql)
            return cursor
        except Exception as err:
            print('Error occurred when executing sql: ', err)
            return None

    def format_sql(self, columns: List[str] = None, distinct: bool = False, where: Dict[str, str] = None, order_by: str = None):
        columns_formatted = '*' if not columns else f'''({",".join(columns)})'''
        select = 'SELECT DISTINCT' if distinct else 'SELECT'
        sql = f'''{select} {columns_formatted} FROM "{self.schema}"."{self.table}"'''
        if where:
            where_formatted = ' AND '.join([f'''"{k}"="{v}"''' for k, v in where.items()])
            sql += f' WHERE {where_formatted}'
        if order_by:
            sql += f''' ORDER BY "{order_by}"'''

        sql += ';'
        return sql

    def fetch_all(self):
        pass

    def fetch_many(self):
        pass

    def fetch_one(self):
        pass


