from __future__ import absolute_import

from flask import Blueprint
from flask_cors import CORS

main = Blueprint(
    'main',
    __name__
)

# add CORS support
CORS(main)

from . import views
