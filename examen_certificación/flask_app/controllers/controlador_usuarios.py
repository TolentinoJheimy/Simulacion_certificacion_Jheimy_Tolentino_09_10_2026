import secrets
from functools import wraps

from flask import (
    abort,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug.security import check_password_hash

from flask_app import app, bcrypt
from flask_app.models.modelo_usuario import Usuario


@app.before_request
def cargar_usuario_y_csrf():
    usuario_id = session.get('usuario_id')
    g.usuario = Usuario.buscar_por_id(usuario_id) if usuario_id is not None else None

    if 'csrf' not in session:
        session['csrf'] = secrets.token_hex(32)

    if request.method == 'POST' and not secrets.compare_digest(
        request.form.get('csrf', '').encode('utf-8'),
        session['csrf'].encode('utf-8'),
    ):
        abort(400, 'Formulario vencido. Recarga la página e inténtalo nuevamente.')


def sesion_requerida(vista):
    @wraps(vista)
    def vista_protegida(*argumentos, **argumentos_nombrados):
        if not g.usuario:
            flash('Inicia sesión para acceder a esta página.', 'error')
            return redirect(url_for('inicio'))
        return vista(*argumentos, **argumentos_nombrados)

    return vista_protegida


@app.get('/')
def inicio():
    if g.usuario:
        return redirect(url_for('principal'))

    return render_template('inicio.html', errores=[], datos={}, tipo_formulario='')


@app.post('/registro')
def registrar():
    datos = {
        campo: request.form.get(campo, '').strip()
        for campo in ('nombre', 'apellido', 'correo')
    }
    datos['correo'] = datos['correo'].casefold()
    contrasena = request.form.get('contrasena', '')
    errores = Usuario.validar_registro(
        datos,
        contrasena,
        request.form.get('confirmacion', ''),
    )

    if not errores:
        try:
            usuario_id = Usuario.crear(
                {
                    **datos,
                    'contrasena_hash': bcrypt.generate_password_hash(contrasena).decode(
                        'utf-8'
                    ),
                }
            )
        except ValueError as error:
            errores.append(str(error))
        else:
            session.clear()
            session['usuario_id'] = usuario_id
            return redirect(url_for('principal'))

    return (
        render_template(
            'inicio.html',
            errores=errores,
            datos=datos,
            tipo_formulario='registrar',
        ),
        422,
    )


def verificar_contrasena(usuario, contrasena):
    contrasena_hash = usuario['contrasena_hash']

    if contrasena_hash.startswith(('scrypt:', 'pbkdf2:')):
        correcta = check_password_hash(contrasena_hash, contrasena)
        if correcta and len(contrasena.encode('utf-8')) <= 72:
            nuevo_hash = bcrypt.generate_password_hash(contrasena).decode('utf-8')
            Usuario.actualizar_contrasena(usuario['id'], nuevo_hash)
        return correcta

    if len(contrasena.encode('utf-8')) > 72:
        return False
    try:
        return bcrypt.check_password_hash(contrasena_hash, contrasena)
    except ValueError:
        return False


@app.post('/iniciar_sesion')
def iniciar_sesion():
    correo = request.form.get('correo', '').strip().casefold()
    usuario = Usuario.buscar_por_correo(correo)

    if usuario and verificar_contrasena(
        usuario,
        request.form.get('contrasena', ''),
    ):
        session.clear()
        session['usuario_id'] = usuario['id']
        return redirect(url_for('principal'))

    return (
        render_template(
            'inicio.html',
            errores=['E-mail o contraseña incorrectos.'],
            datos={'correo': correo},
            tipo_formulario='iniciar_sesion',
        ),
        422,
    )


@app.post('/cerrar_sesion')
def cerrar_sesion():
    session.clear()
    return redirect(url_for('inicio'))


@app.errorhandler(403)
@app.errorhandler(404)
@app.errorhandler(400)
def pagina_error(error):
    mensajes = {
        403: 'No tienes permiso para realizar esta acción.',
        404: 'No encontramos este recurso.',
        400: 'Formulario vencido o inválido. Recarga la página.',
    }
    return render_template('error.html', mensaje=mensajes[error.code]), error.code
