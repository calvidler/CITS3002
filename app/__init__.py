from flask import Flask
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_pymongo import PyMongo
from flask_wtf import CSRFProtect
from config import Config

# Init flask packages
bootstrap = Bootstrap()
csrf = CSRFProtect()
moment = Moment()
mongo = PyMongo()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    bootstrap.init_app(app)
    csrf.init_app(app)
    moment.init_app(app)
    mongo.init_app(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app
