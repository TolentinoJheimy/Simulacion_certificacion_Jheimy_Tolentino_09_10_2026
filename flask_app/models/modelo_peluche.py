from pymysql.err import IntegrityError

from flask_app.config.mysql_connection import connectToMySQL


class Peluche:
    @staticmethod
    def listar():
        return connectToMySQL().query_db('''
            SELECT p.*, u.first_name AS donor FROM plushies p
            JOIN users u ON u.id = p.donor_id ORDER BY p.id DESC
        ''')

    @staticmethod
    def buscar_por_id(plushie_id):
        rows = connectToMySQL().query_db('''
            SELECT p.*, u.first_name AS donor, u.last_name AS donor_last,
                   a.first_name AS adopter, a.last_name AS adopter_last
            FROM plushies p JOIN users u ON u.id = p.donor_id
            LEFT JOIN users a ON a.id = p.adopter_id WHERE p.id = %s
        ''', (plushie_id,))
        return rows[0] if rows else None

    @staticmethod
    def nombre_existe(name_key, excluir_id=None):
        rows = connectToMySQL().query_db(
            'SELECT id FROM plushies WHERE name_key = %s AND id != %s',
            (name_key, excluir_id if excluir_id is not None else -1),
        )
        return bool(rows)

    @staticmethod
    def validar(values, excluir_id=None):
        errors = []
        name_key = values['name'].strip().casefold()

        if not name_key:
            errors.append('El nombre no puede estar vacío.')
        if not values['description'].strip():
            errors.append('La descripción no puede estar vacía.')
        if len(values['name']) > 255 or len(name_key) > 512:
            errors.append('El nombre debe tener como máximo 255 caracteres.')
        if Peluche.nombre_existe(name_key, excluir_id):
            errors.append('Ya existe un peluche con ese nombre.')

        return errors

    @staticmethod
    def crear(values, donor_id):
        try:
            return connectToMySQL().query_db(
                'INSERT INTO plushies(name,name_key,description,donor_id) VALUES(%s,%s,%s,%s)',
                (
                    values['name'],
                    values['name_key'],
                    values['description'],
                    donor_id,
                ),
            )
        except IntegrityError as error:
            if error.args[0] == 1062:
                raise ValueError('Ya existe un peluche con ese nombre.') from error
            raise

    @staticmethod
    def actualizar(plushie_id, values):
        try:
            return connectToMySQL().query_db(
                'UPDATE plushies SET name=%s,name_key=%s,description=%s WHERE id=%s',
                (
                    values['name'],
                    values['name_key'],
                    values['description'],
                    plushie_id,
                ),
            )
        except IntegrityError as error:
            if error.args[0] == 1062:
                raise ValueError('Ya existe un peluche con ese nombre.') from error
            raise

    @staticmethod
    def borrar(plushie_id):
        return connectToMySQL().query_db(
            'DELETE FROM plushies WHERE id=%s',
            (plushie_id,),
        )

    @staticmethod
    def adoptar(plushie_id, user_id):
        affected = connectToMySQL().query_db(
            'UPDATE plushies SET adopter_id=%s WHERE id=%s AND adopter_id IS NULL AND donor_id != %s',
            (user_id, plushie_id, user_id),
        )
        return affected == 1

    @staticmethod
    def sumar_visita(plushie_id):
        return connectToMySQL().query_db(
            'UPDATE plushies SET views=views+1 WHERE id=%s',
            (plushie_id,),
        )
