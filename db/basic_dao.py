import os
from psycopg2 import sql, connect
from psycopg2.extras import RealDictCursor
import json

from utils import Singleton


class DbInstance(Singleton):
    def __init__(self):
        self.dbname = os.environ.get('POSTGRES_DB', 'postgresDB')
        self.user = os.environ.get('POSTGRES_USER', 'postgresUser')
        self.password = os.environ.get('POSTGRES_PASSWORD', 'postgresPW')
        self.host = os.environ.get('POSTGRES_HOST', 'localhost')
        self.port = os.environ.get('POSTGRES_PORT', 5455)


class BasicDao:
    _connection = None
    _db_instance = DbInstance()

    def __init__(self, table):
        if not self._connection:
           self.connect()
        self.table = table

    def connect(self) -> bool:
        try:
            self._connection = connect(
                dbname=self._db_instance.dbname,
                user=self._db_instance.user,
                host=self._db_instance.host,
                password=self._db_instance.password
            )
            return True
        except Exception as err:
            print('Error connection to db: ', err)
        return False

    # Execute sql query
    def execute_sql(self, sql):
        if not self._connection:
            return None
        try:
            cursor = self._connection.cursor()
            cursor.execute(sql)
            return cursor
        except Exception as err:
            print('Error occurred when executing sql: ', err)
            return None

    def fetch_all(self):



    def get_numeric_column_names(self, table: str):
        columns = list()
        try:
            conn = self.connect_db()
            if conn == None:
                return ("Error in database connection")
            with conn.cursor() as col_cursor:
                col_names_str = """
                                SELECT col.column_name FROM INFORMATION_SCHEMA.COLUMNS as col 
                                WHERE table_name = '{}' 
                                    AND col.data_type in ('smallint', 'integer', 'bigint', 'decimal', 'numeric', 'real', 'double precision', 'smallserial', 'serial', 'bigserial', 'money');
                                """.format(table)

                sql_object = sql.SQL(col_names_str).format(
                    sql.Identifier(table))
                col_cursor.execute(sql_object)
                col_names = col_cursor.fetchall()
                for tup in col_names:
                    columns += [tup[0]]
                conn.close()
                return columns
        except Exception as e:
            conn.rollback()
            conn.close()
            return ("get_numeric_column_names ERROR:", e)

    # get all the values from specific column
    def get_values_from_column(self, column, table, schema, distinct=True):
        values = []
        try:
            conn = self.connect_db()
            if conn == None:
                return ("Error in database connection")
            with conn.cursor() as col_cursor:
                if distinct:
                    all_values_str = '''SELECT DISTINCT "{0}" FROM "{2}"."{1}" ORDER BY "{0}";'''.format(
                        column, table, schema)
                else:
                    all_values_str = '''SELECT "{0}" FROM "{2}"."{1}" ORDER BY "{0}";'''.format(
                        column, table, schema)

                sql_object = sql.SQL(all_values_str).format(
                    sql.Identifier(column), sql.Identifier(table))

                col_cursor.execute(sql_object, (column))
                values_name = (col_cursor.fetchall())
                for tup in values_name:
                    values += [tup[0]]
                conn.close()
                return values
        except Exception as e:
            conn.rollback()
            conn.close()
            return {"error": str(e)}
            # return ("get_numeric_column_names ERROR:", e)

    # create the schema based on the given name
    def create_schema(self, name):
        n = name.split(' ')
        if len(n) > 0:
            name = name.replace(' ', '_')
        try:
            conn = self.connect_db()
            if conn == None:
                return ("Error in database connection")
            with conn.cursor() as cursor:
                sql = f'''CREATE SCHEMA IF NOT EXISTS {name}'''
                self.execute_sql(cursor, sql)
                conn.commit()
                conn.close()
                return ('Schema create successfully')
        except Exception as e:
            conn.rollback()
            conn.close()
            return ("create_schema ERROR:", e)

    # delete the schema based on the given name
    def delete_schema(self, name):
        try:
            conn = self.connect_db()
            if conn == None:
                return (False, "Error in database connection")
            with conn.cursor() as cursor:
                sql = f'''DROP SCHEMA IF EXISTS {name} CASCADE'''
                self.execute_sql(cursor, sql)
                conn.commit()
                conn.close()
                return (True, 'Schema deleted successfully')
        except Exception as e:
            conn.rollback()
            conn.close()
            return (False, str(e))

    # create new column in table
    def create_column(self, column, table, schema='public', col_datatype='varchar'):
        try:
            conn = self.connect_db()
            if conn == None:
                return ("Error in database connection")
            with conn.cursor() as cursor:
                sql = '''ALTER TABLE "{3}"."{0}" ADD IF NOT EXISTS "{1}" {2}'''.format(
                    table, column, col_datatype, schema)
                self.execute_sql(cursor, sql)
                conn.commit()
                conn.close()
                return ('create column successful')
        except Exception as e:
            conn.rollback()
            conn.close()
            return ("create_column ERROR:", e)

    # update column
    def update_column(self, column, value, table, schema, where_column, where_value):
        try:
            conn = self.connect_db()
            if conn == None:
                return ("Error in database connection")
            with conn.cursor() as cursor:
                sql = '''
                    UPDATE "{0}"."{1}" SET "{2}"='{3}' WHERE "{4}"='{5}'
                    '''.format(
                    schema, table, column, value, where_column, where_value)
                self.execute_sql(cursor, sql)
                conn.commit()
                conn.close()
                return ('update table successful')
        except Exception as e:
            conn.rollback()
            conn.close()
            return ("update_column ERROR:", e)

    # delete column in table
    def delete_column(self, column, table, schema='public', col_datatype='varchar'):
        try:
            conn = self.connect_db()
            if conn == None:
                return ("Error in database connection")
            with conn.cursor() as cursor:
                sql = '''ALTER TABLE "{3}"."{0}" DELETE IF EXISTS "{1}" {2}'''.format(
                    table, column, col_datatype, schema)
                self.execute_sql(cursor, sql)
                conn.commit()
                conn.close()
                return ({"detail": 'delete column successful'})
        except Exception as e:
            conn.rollback()
            conn.close()
            return ({'error': str(e)})

    def run_sql(self, sql):
        try:
            conn = self.connect_db()
            if conn == None:
                return ("Error in database connection")
            with conn.cursor() as cursor:
                self.execute_sql(cursor, sql)
                conn.commit()
                conn.close()
                return ('Your sql run successfully')
        except Exception as e:
            conn.rollback()
            conn.close()
            return ("run_sql ERROR:", e)

    # get all values
    def get_all_values(self, table, schema, where_col=None, where_val=None):
        try:
            conn = self.connect_db()
            if conn == None:
                return ("Error in database connection")
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                if where_col:
                    sql = '''SELECT * FROM "{}"."{}" WHERE "{}"='{}';'''.format(
                        schema, table, where_col, where_val)
                else:
                    sql = '''SELECT * FROM "{}"."{}";'''.format(
                        schema, table)

                cursor.execute(sql)
                rows = cursor.fetchall()
                conn.close()
                return json.dumps(rows, default=json_util.default)
        except Exception as e:
            conn.rollback()
            conn.close()
            return ("get_all_values ERROR:", e)

    # delete table
    def delete_table(self, name, schema):
        try:
            conn = self.connect_db()
            if conn == None:
                return ("Error in database connection")
            with conn.cursor() as cursor:
                sql = '''DROP TABLE IF EXISTS "{}"."{}" CASCADE;'''.format(
                    schema, name)
                self.execute_sql(cursor, sql)
                conn.commit()
                conn.close()
                return ('{} table dropped successfully.'.format(name))
        except Exception as e:
            conn.rollback()
            conn.close()
            return ("delete_table ERROR:", e)

    # Delete values
    def delete_values(self, table_name, schema, condition):
        try:
            conn = self.connect_db()
            if conn == None:
                return ("Error in database connection")
            with conn.cursor() as cursor:
                sql = '''DELETE FROM "{}"."{}" WHERE {}'''.format(
                    schema, table_name, condition)
                self.execute_sql(cursor, sql)
                conn.commit()
                conn.close()
                return ('Values dropped successfully.')
        except Exception as e:
            conn.rollback()
            conn.close()
            return ("delete_values ERROR:", e)

    # Get all the table names
    def get_table_names(self, schema):
        values = []
        try:
            conn = self.connect_db()
            if conn == None:
                return ("Error in database connection")
            with conn.cursor() as cursor:
                sql = """SELECT table_name FROM information_schema.tables WHERE table_schema='{0}'""".format(
                    schema)
                cursor.execute(sql)
                rows = cursor.fetchall()
                for tup in rows:
                    values += [tup[0]]
                conn.close()
                return values
        except Exception as e:
            conn.rollback()
            conn.close()
            return ("get_table_names ERROR:", e)

    # get vuln connection
    def clone_table(self, from_schema, to_schema, from_table, to_table):
        try:
            conn = self.connect_db()
            if conn == None:
                return ("Error in database connection")
            with conn.cursor() as cursor:
                # CREATE TABLE schema2.mytable AS SELECT * FROM schema1.mytable WHERE 1=2;
                sql1 = '''CREATE TABLE "{}"."{}" AS SELECT * FROM "{}"."{}" WHERE 1=2;'''.format(
                    to_schema, to_table, from_schema, from_table)
                cursor.execute(sql1)
                sql2 = '''INSERT INTO "{}"."{}" SELECT * FROM "{}"."{}";'''.format(
                    to_schema, to_table, from_schema, from_table)
                cursor.execute(sql2)
                conn.commit()
                conn.close()
                return "table cloned successfully"
        except Exception as e:
            conn.rollback()
            conn.close()
            return ("clone table ERROR:", e)