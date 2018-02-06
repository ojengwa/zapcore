from flask import current_app as app
from flask import flash
from flask import redirect
from flask import render_template
from flask import url_for
from flask_login import current_user
from flask_login import login_required

from . import main
from .forms import SearchForm

from ..api.utils import _search


@main.route('/', methods=['GET', 'POST'])
def index():
    if current_user.is_anonymous:
        return redirect(url_for('auth.login'))
    else:
        return redirect(url_for('main.dashboard'))


@main.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    bio = app.db.bios.count()
    payroll = app.db.payrolls.count()
    work = app.db.work_histories.count()

    context = {
        'counter': {
            'bio': bio,
            'pay_histories': payroll,
            'work_histories': work,
            'mortgages': 0,
            'rents': 0,
            'utilities': 0,
            'loans': 0,
            'education_histories': 0
        },
        'total_records': bio + payroll + work
    }

    return render_template('index.html', **context)


@main.route('/search', methods=['GET', 'POST'])
def search():
    context = {}
    form = SearchForm()

    if form.validate_on_submit():
        bvn = form.bvn.data

        context.update(bvn=form.bvn.data)
        result = _search(bvn, app)

        if result.get('status') == 'error':
            flash(result.get('message'), 'error')
        context.update(enrollee=result)
    else:
        for error in form.errors.values():
            if isinstance(error, list):
                for e in error:
                    flash(e, 'error')
            else:
                flash(error, 'error')
    return render_template('search/results.html', **context)
