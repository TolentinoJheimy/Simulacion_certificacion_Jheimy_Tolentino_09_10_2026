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
from werkzeug.security import check_password_hash, generate_password_hash

from flask_app import app
from flask_app.models.modelo_usuario import Usuario


@app.before_request
def load_user_and_csrf():
    user_id = session.get('user_id')
    g.user = Usuario.buscar_por_id(user_id) if user_id is not None else None

    if 'csrf' not in session:
        session['csrf'] = secrets.token_hex(32)

    if request.method == 'POST' and not secrets.compare_digest(
        request.form.get('csrf', '').encode('utf-8'),
        session['csrf'].encode('utf-8'),
    ):
        abort(400, 'Formulario vencido. Recarga la página e inténtalo nuevamente.')


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not g.user:
            flash('Inicia sesión para acceder a esta página.', 'error')
            return redirect(url_for('index'))
        return view(*args, **kwargs)

    return wrapped


@app.get('/')
def index():
    if g.user:
        return redirect(url_for('dashboard'))

    return render_template('index.html', errors=[], values={}, form='')


@app.post('/registro')
def register():
    values = {
        key: request.form.get(key, '').strip()
        for key in ('first_name', 'last_name', 'email')
    }
    values['email'] = values['email'].casefold()
    password = request.form.get('password', '')
    errors = Usuario.validar_registro(
        values,
        password,
        request.form.get('confirmation', ''),
    )

    if not errors:
        try:
            user_id = Usuario.crear(
                {
                    **values,
                    'password_hash': generate_password_hash(password),
                }
            )
        except ValueError as error:
            errors.append(str(error))
        else:
            session.clear()
            session['user_id'] = user_id
            return redirect(url_for('dashboard'))

    return (
        render_template(
            'index.html',
            errors=errors,
            values=values,
            form='register',
        ),
        422,
    )


@app.post('/login')
def login():
    email = request.form.get('email', '').strip().casefold()
    user = Usuario.buscar_por_email(email)

    if user and check_password_hash(
        user['password_hash'],
        request.form.get('password', ''),
    ):
        session.clear()
        session['user_id'] = user['id']
        return redirect(url_for('dashboard'))

    return (
        render_template(
            'index.html',
            errors=['E-mail o contraseña incorrectos.'],
            values={'email': email},
            form='login',
        ),
        422,
    )


@app.post('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


@app.errorhandler(403)
@app.errorhandler(404)
@app.errorhandler(400)
def error_page(error):
    messages = {
        403: 'No tienes permiso para realizar esta acción.',
        404: 'No encontramos este peluche.',
        400: 'Formulario vencido o inválido. Recarga la página.',
    }
    return render_template('error.html', message=messages[error.code]), error.code
