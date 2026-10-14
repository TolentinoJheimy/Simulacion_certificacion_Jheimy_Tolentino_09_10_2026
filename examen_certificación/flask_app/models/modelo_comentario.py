from flask_app.config.conexion_mysql import conectar_mysql


class Comentario:
    @staticmethod
    def listar(pelicula_id):
        return conectar_mysql().consultar(
            '''
            SELECT c.*, u.nombre AS autor_nombre FROM comentarios c
            JOIN usuarios u ON u.id=c.usuario_id WHERE c.pelicula_id=%s
            ORDER BY c.creado_en DESC, c.id DESC
        ''',
            (pelicula_id,),
        )

    @staticmethod
    def crear(pelicula_id, usuario_id, contenido):
        return conectar_mysql().consultar(
            'INSERT INTO comentarios(pelicula_id,usuario_id,contenido) VALUES(%s,%s,%s)',
            (pelicula_id, usuario_id, contenido),
        )

    @staticmethod
    def buscar_por_id(comentario_id):
        filas = conectar_mysql().consultar(
            'SELECT * FROM comentarios WHERE id=%s', (comentario_id,)
        )
        return filas[0] if filas else None

    @staticmethod
    def borrar(comentario_id, usuario_id):
        return conectar_mysql().consultar(
            'DELETE FROM comentarios WHERE id=%s AND usuario_id=%s',
            (comentario_id, usuario_id),
        )
