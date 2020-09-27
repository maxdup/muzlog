from flask import Flask, Config
from flask_restx import Api
from flask_mongoengine import MongoEngine
from flask_security import Security, MongoEngineUserDatastore, \
    auth_token_required
from flask_mail import Mail
from flask_cors import CORS

db = MongoEngine()  # NOQA: E402
mail = Mail()  # NOQA: E402
security = Security()  # NOQA: E402

from muzapi.models import User, Role  # NOQA: E402

user_datastore = MongoEngineUserDatastore(db, User, Role)  # NOQA: E402

from muzapi.bp_site import muzlog_site  # NOQA: E402
from muzapi.bp_api import muzlog_api  # NOQA: E402
from muzapi.bp_cms import muzlog_cms  # NOQA: E402

configuration = Config('/')
configuration.from_object('config.config')


def create_app(overrides={}):
    app = Flask(__name__,
                template_folder='../muzsite/templates',
                static_folder='../muzsite/static')

    configuration.update(overrides)
    app.config.update(configuration)

    app.url_map.strict_slashes = False

    db.init_app(app)
    mail = Mail(app)

    security.init_app(app, user_datastore)

    app.register_blueprint(muzlog_site)
    app.register_blueprint(muzlog_cms)
    app.register_blueprint(muzlog_api)

    CORS(app)
    return app
