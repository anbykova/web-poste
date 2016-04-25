import os
from flask import Flask
from flask.ext.login import LoginManager
from config import basedir
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.openid import OpenID
from momentjs import momentjs


app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)

lm = LoginManager()
lm.init_app(app)
app.jinja_env.globals['momentjs'] = momentjs

from app import views, models
