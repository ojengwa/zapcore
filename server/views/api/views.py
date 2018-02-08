from flask import jsonify

from server.models.utils import get_types as _get_types
from . import api


@api.route('/types', methods=['GET'])
def get_types():
    sqlalchemy_types = _get_types()

    return jsonify(sqlalchemy_types)
