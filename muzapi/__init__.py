#import os

from flask import Flask
from flask_restful import Api
from flask_mongoengine import MongoEngine
from flask_security import Security, MongoEngineUserDatastore, \
    auth_token_required
from flask_mail import Mail
from flask_cors import CORS
import jinja2

db = MongoEngine()

from muzapi.models import User, Role
from muzapi.albums import Album_res
from muzapi.pages import *


def create_app(config):
    app = Flask(__name__, static_folder='../muzsite/static')
    api = Api(app)

    app.config.from_object(config)

    my_loader = jinja2.ChoiceLoader([
        app.jinja_loader,
        jinja2.FileSystemLoader('muzsite/templates'),
    ])
    app.jinja_loader = my_loader

    app.url_map.strict_slashes = True

    user_datastore = MongoEngineUserDatastore(db, User, Role)
    security = Security(app, user_datastore)
    mail = Mail(app)
    db.init_app(app)

    api.add_resource(Album_res, "/api/albums", endpoint="albums")
    api.add_resource(Album_res, "/api/albums/<string:_id>", endpoint="album")

    app.register_blueprint(muzlog_pages)

    CORS(app)
    return app
