import pymysql
from flask import current_app


class ConexionMySQL:
    def __init__(self, base_datos):
        self.base_datos = base_datos

    def consultar(self, consulta, datos=None):
        configuracion = current_app.config
        conexion = pymysql.connect(
            host=configuracion['MYSQL_HOST'],
            port=configuracion['MYSQL_PORT'],
            user=configuracion['MYSQL_USER'],
            password=configuracion['MYSQL_PASSWORD'],
            database=self.base_datos,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor,
        )

        try:
            with conexion.cursor() as cursor:
                cursor.execute(consulta, datos)
                if cursor.description is not None:
                    resultado = cursor.fetchall()
                elif consulta.lstrip().upper().startswith('INSERT'):
                    resultado = cursor.lastrowid
                else:
                    resultado = cursor.rowcount
            conexion.commit()
            return resultado
        except Exception:
            conexion.rollback()
            raise
        finally:
            conexion.close()


def conectar_mysql(base_datos=None):
    return ConexionMySQL(base_datos or current_app.config['MYSQL_DATABASE'])
