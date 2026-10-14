from flask import abort, flash, g, redirect, render_template, request, url_for
from flask_app import app
from flask_app.controllers.controlador_usuarios import sesion_requerida
from flask_app.models.modelo_pelicula import Pelicula
from flask_app.models.modelo_comentario import Comentario


@app.get('/cine')
@sesion_requerida
def principal():
    return render_template('principal.html', peliculas=Pelicula.listar())


def obtener_pelicula(pelicula_id):
    pelicula = Pelicula.buscar_por_id(pelicula_id)
    if pelicula is None:
        abort(404)
    return pelicula


def formulario_pelicula(pelicula=None):
    campos = ('nombre', 'director', 'fecha_estreno', 'sinopsis')
    datos = dict(pelicula) if pelicula else dict.fromkeys(campos, '')
    errores = []
    if request.method == 'POST':
        datos = {campo: request.form.get(campo, '').strip() for campo in campos}
        errores = Pelicula.validar(datos, pelicula['id'] if pelicula else None)
        if not errores:
            try:
                Pelicula.guardar(
                    datos, g.usuario['id'], pelicula['id'] if pelicula else None
                )
            except ValueError as error:
                errores.append(str(error))
            else:
                flash('Película guardada correctamente.', 'exito')
                return redirect(url_for('principal'))
    return render_template(
        'editar_pelicula.html' if pelicula else 'nueva_pelicula.html',
        datos=datos,
        errores=errores,
    ), (422 if errores else 200)


@app.route('/cine/nueva', methods=['GET', 'POST'])
@sesion_requerida
def crear_pelicula():
    return formulario_pelicula()


@app.route('/cine/editar/<int:pelicula_id>', methods=['GET', 'POST'])
@sesion_requerida
def editar_pelicula(pelicula_id):
    pelicula = obtener_pelicula(pelicula_id)
    if pelicula['creador_id'] != g.usuario['id']:
        abort(403)
    return formulario_pelicula(pelicula)


@app.post('/cine/borrar/<int:pelicula_id>')
@sesion_requerida
def borrar_pelicula(pelicula_id):
    pelicula = obtener_pelicula(pelicula_id)
    if pelicula['creador_id'] != g.usuario['id']:
        abort(403)
    Pelicula.borrar(pelicula_id)
    return redirect(url_for('principal'))


@app.get('/cine/<int:pelicula_id>')
@sesion_requerida
def ver_pelicula(pelicula_id):
    return render_template(
        'ver_pelicula.html',
        pelicula=obtener_pelicula(pelicula_id),
        comentarios=Comentario.listar(pelicula_id),
        errores=[],
        contenido='',
    )


@app.post('/cine/<int:pelicula_id>/comentarios')
@sesion_requerida
def crear_comentario(pelicula_id):
    pelicula = obtener_pelicula(pelicula_id)
    if pelicula['creador_id'] == g.usuario['id']:
        abort(403)
    contenido = request.form.get('contenido', '').strip()
    if not contenido:
        return (
            render_template(
                'ver_pelicula.html',
                pelicula=pelicula,
                comentarios=Comentario.listar(pelicula_id),
                errores=['El comentario no puede estar vacío.'],
                contenido=contenido,
            ),
            422,
        )
    Comentario.crear(pelicula_id, g.usuario['id'], contenido)
    return redirect(url_for('ver_pelicula', pelicula_id=pelicula_id))


@app.post('/cine/comentarios/<int:comentario_id>/borrar')
@sesion_requerida
def borrar_comentario(comentario_id):
    elemento = Comentario.buscar_por_id(comentario_id)
    if elemento is None:
        abort(404)
    if elemento['usuario_id'] != g.usuario['id']:
        abort(403)
    Comentario.borrar(comentario_id, g.usuario['id'])
    return redirect(url_for('ver_pelicula', pelicula_id=elemento['pelicula_id']))
