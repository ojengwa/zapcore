import json

from . import api
from .utils import clean, _search
from flask import Response
from flask import current_app as app
from flask import request
from flask_login import login_required


@api.route('/stats')
@login_required
def stats():
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
    return Response(json.dumps(context, indent=4), mimetype='application/json')


@api.route('/search', methods=['GET'])
@login_required
def search():
    bvn = request.args.get('bvn')
    bio = _search(bvn, app)

    return Response(json.dumps(bio, indent=4), mimetype='application/json')
