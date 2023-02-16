from sanic import Blueprint

from .wado import bp_wado
from .admin import bp_admin

api = Blueprint.group(bp_wado, bp_admin)