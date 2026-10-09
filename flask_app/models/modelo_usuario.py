import re

from pymysql.err import IntegrityError

from flask_app.config.mysql_connection import connectToMySQL


class Usuario:
    @staticmethod
    def buscar_por_id(user_id):
        if user_id is None:
            return None

        rows = connectToMySQL().query_db(
            'SELECT * FROM users WHERE id = %s',
            (user_id,),
        )
        return rows[0] if rows else None

    @staticmethod
    def buscar_por_email(email):
        rows = connectToMySQL().query_db(
            'SELECT * FROM users WHERE email = %s',
            (email,),
        )
        return rows[0] if rows else None

    @staticmethod
    def crear(values):
        try:
            return connectToMySQL().query_db(
                'INSERT INTO users(first_name,last_name,email,password_hash) VALUES(%s,%s,%s,%s)',
                (
                    values['first_name'],
                    values['last_name'],
                    values['email'],
                    values['password_hash'],
                ),
            )
        except IntegrityError as error:
            if error.args[0] == 1062:
                raise ValueError('El e-mail ya está registrado.') from error
            raise

    @staticmethod
    def validar_registro(values, password, confirmation):
        errors = []

        if len(values['first_name']) < 2:
            errors.append('El nombre debe tener al menos 2 caracteres.')
        if len(values['last_name']) < 2:
            errors.append('El apellido debe tener al menos 2 caracteres.')
        if not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+', values['email']):
            errors.append('Ingresa un e-mail válido.')
        if not password.strip():
            errors.append('La contraseña no puede estar vacía.')
        if password != confirmation:
            errors.append('La contraseña y su confirmación deben ser iguales.')
        if len(values['first_name']) > 255 or len(values['last_name']) > 255:
            errors.append(
                'El nombre y apellido deben tener como máximo 255 caracteres.'
            )
        if len(values['email']) > 254:
            errors.append('El e-mail debe tener como máximo 254 caracteres.')
        if Usuario.buscar_por_email(values['email']):
            errors.append('El e-mail ya está registrado.')

        return errors
