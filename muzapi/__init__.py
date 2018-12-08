from flask import Flask
from flask_restplus import Api
from flask_mongoengine import MongoEngine
from flask_security import Security, MongoEngineUserDatastore, \
    auth_token_required
from flask_mail import Mail
from flask_cors import CORS

db = MongoEngine()

from muzapi.models import User, Role

from muzapi.bp_site import muzlog_site
from muzapi.bp_api import muzlog_api
from muzapi.bp_cms import muzlog_cms


def create_app(config):
    app = Flask(__name__,
                template_folder='../muzsite/templates',
                static_folder='../muzsite/static')

    app.config.from_object(config)
    app.url_map.strict_slashes = False

    app.register_blueprint(muzlog_site)
    app.register_blueprint(muzlog_cms)
    app.register_blueprint(muzlog_api)

    user_datastore = MongoEngineUserDatastore(db, User, Role)
    security = Security(app, user_datastore)
    mail = Mail(app)
    db.init_app(app)

    CORS(app)
    return app
