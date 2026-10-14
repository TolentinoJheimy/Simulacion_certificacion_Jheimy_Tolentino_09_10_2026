from datetime import date

from pymysql.err import IntegrityError
from flask_app.config.conexion_mysql import conectar_mysql


class Pelicula:
    @staticmethod
    def listar():
        return conectar_mysql().consultar('SELECT * FROM peliculas ORDER BY id DESC')

    @staticmethod
    def buscar_por_id(pelicula_id):
        filas = conectar_mysql().consultar(
            '''
            SELECT m.*, u.nombre AS creador_nombre, u.apellido AS creador_apellido
            FROM peliculas m JOIN usuarios u ON u.id=m.creador_id WHERE m.id=%s
        ''',
            (pelicula_id,),
        )
        return filas[0] if filas else None

    @staticmethod
    def validar(datos, excluir_id=None):
        errores = []
        for campo, etiqueta in [
            ('nombre', 'El nombre'),
            ('director', 'El director'),
            ('sinopsis', 'La sinopsis'),
        ]:
            if len(datos[campo].strip()) < 3:
                errores.append(f'{etiqueta} debe tener al menos 3 caracteres.')
        if len(datos['nombre']) > 255 or len(datos['director']) > 255:
            errores.append(
                'El nombre y director deben tener como máximo 255 caracteres.'
            )
        if len(datos['sinopsis']) > 300:
            errores.append('La sinopsis debe tener como máximo 300 caracteres.')
        try:
            fecha_estreno = date.fromisoformat(datos['fecha_estreno'])
            if fecha_estreno > date.today():
                errores.append('La fecha de estreno no puede ser posterior a hoy.')
        except ValueError:
            errores.append('Ingresa una fecha de estreno válida.')
        filas = conectar_mysql().consultar(
            'SELECT id FROM peliculas WHERE nombre_normalizado=%s AND id != %s',
            (datos['nombre'].strip().casefold(), excluir_id or -1),
        )
        if filas:
            errores.append('Ya existe una película con ese nombre.')
        return errores

    @staticmethod
    def guardar(datos, creador_id, pelicula_id=None):
        parametros = (
            datos['nombre'],
            datos['nombre'].casefold(),
            datos['director'],
            datos['fecha_estreno'],
            datos['sinopsis'],
        )
        try:
            if pelicula_id is not None:
                return conectar_mysql().consultar(
                    'UPDATE peliculas SET nombre=%s,nombre_normalizado=%s,director=%s,fecha_estreno=%s,sinopsis=%s WHERE id=%s',
                    (*parametros, pelicula_id),
                )
            return conectar_mysql().consultar(
                'INSERT INTO peliculas(nombre,nombre_normalizado,director,fecha_estreno,sinopsis,creador_id) VALUES(%s,%s,%s,%s,%s,%s)',
                (*parametros, creador_id),
            )
        except IntegrityError as error:
            if error.args[0] == 1062:
                raise ValueError('Ya existe una película con ese nombre.') from error
            raise

    @staticmethod
    def borrar(pelicula_id):
        return conectar_mysql().consultar(
            'DELETE FROM peliculas WHERE id=%s', (pelicula_id,)
        )
