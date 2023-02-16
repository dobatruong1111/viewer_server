from sanic import Sanic
from sanic_ext import Extend

from routes import api

from db import db

from settings.config import db_config

app = Sanic(__name__)
app.config.update(db_config)
Extend(app)

db.init_app(app)

app.blueprint(api)