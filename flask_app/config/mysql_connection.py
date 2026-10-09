import pymysql
from flask import current_app


class MySQLConnection:
    def __init__(self, database):
        self.database = database

    def query_db(self, query, data=None):
        config = current_app.config
        connection = pymysql.connect(
            host=config['MYSQL_HOST'],
            port=config['MYSQL_PORT'],
            user=config['MYSQL_USER'],
            password=config['MYSQL_PASSWORD'],
            database=self.database,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor,
        )

        try:
            with connection.cursor() as cursor:
                cursor.execute(query, data)

                if cursor.description is not None:
                    result = cursor.fetchall()
                elif query.lstrip().upper().startswith('INSERT'):
                    result = cursor.lastrowid
                else:
                    result = cursor.rowcount

            connection.commit()
            return result
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()


def connectToMySQL(database=None):
    return MySQLConnection(database or current_app.config['MYSQL_DATABASE'])
