#import os

from flask import Flask
from flask_restful import Api
from flask_mongoengine import MongoEngine
from flask_security import Security, MongoEngineUserDatastore, \
    auth_token_required
from flask_mail import Mail
from flask_cors import CORS

db = MongoEngine()

from muzapi.models import User, Role
from muzapi.albums import Album_res, muzlog_upload
from muzapi.log import Log_res
from muzapi.pages import *


def create_app(config):
    app = Flask(__name__,
                template_folder='../muzsite/templates',
                static_folder='../muzsite/static')
    api = Api(app)

    app.config.from_object(config)
    app.url_map.strict_slashes = True

    user_datastore = MongoEngineUserDatastore(db, User, Role)
    security = Security(app, user_datastore)
    mail = Mail(app)
    db.init_app(app)

    api.add_resource(Album_res, "/api/album", endpoint="albums")
    api.add_resource(Album_res, "/api/album/<string:_id>", endpoint="album")
    api.add_resource(Log_res, "/api/log", endpoint="logs")
    api.add_resource(Log_res, "/api/log/<string:_id>", endpoint="log")

    app.register_blueprint(muzlog_pages)
    app.register_blueprint(muzlog_upload)

    CORS(app)
    return app
