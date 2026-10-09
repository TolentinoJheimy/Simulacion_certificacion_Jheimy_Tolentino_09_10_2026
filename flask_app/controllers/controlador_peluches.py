from flask import abort, flash, g, redirect, render_template, request, url_for

from flask_app import app
from flask_app.controllers.controlador_usuarios import login_required
from flask_app.models.modelo_peluche import Peluche


@app.get('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', plushies=Peluche.listar())


def get_plushie(plushie_id):
    plushie = Peluche.buscar_por_id(plushie_id)

    if plushie is None:
        abort(404)

    return plushie


def donation_form(plushie=None):
    values = dict(plushie) if plushie else {'name': '', 'description': ''}
    errors = []

    if request.method == 'POST':
        values = {
            key: request.form.get(key, '').strip()
            for key in ('name', 'description')
        }
        errors = Peluche.validar(
            values,
            excluir_id=plushie['id'] if plushie else None,
        )

        if not errors:
            donation = {**values, 'name_key': values['name'].casefold()}

            try:
                if plushie:
                    Peluche.actualizar(plushie['id'], donation)
                else:
                    Peluche.crear(donation, g.user['id'])
            except ValueError as error:
                errors.append(str(error))
            else:
                flash('Donación guardada correctamente.', 'success')
                return redirect(url_for('dashboard'))

    template = 'editar_donacion.html' if plushie else 'nueva_donacion.html'

    return (
        render_template(
            template,
            values=values,
            errors=errors,
            editing=plushie is not None,
        ),
        422 if errors else 200,
    )


@app.route('/nueva', methods=['GET', 'POST'])
@login_required
def create():
    return donation_form()


@app.route('/editar/<int:plushie_id>', methods=['GET', 'POST'])
@login_required
def edit(plushie_id):
    plushie = get_plushie(plushie_id)

    if plushie['donor_id'] != g.user['id']:
        abort(403)

    return donation_form(plushie)


@app.post('/borrar/<int:plushie_id>')
@login_required
def delete(plushie_id):
    plushie = get_plushie(plushie_id)

    if plushie['donor_id'] != g.user['id']:
        abort(403)

    Peluche.borrar(plushie_id)
    flash('Donación eliminada.', 'success')
    return redirect(url_for('dashboard'))


@app.post('/adoptar/<int:plushie_id>')
@login_required
def adopt(plushie_id):
    plushie = get_plushie(plushie_id)

    if plushie['donor_id'] == g.user['id']:
        abort(403)

    adopted = Peluche.adoptar(plushie_id, g.user['id'])
    flash(
        '¡Peluche adoptado!' if adopted else 'Este peluche ya fue adoptado.',
        'success' if adopted else 'error',
    )
    return redirect(url_for('dashboard'))


@app.get('/ver/<int:plushie_id>')
@login_required
def detail(plushie_id):
    get_plushie(plushie_id)
    Peluche.sumar_visita(plushie_id)
    return render_template('ver_donacion.html', plushie=get_plushie(plushie_id))
