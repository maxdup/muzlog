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
from muzapi.bp_cms import muzlog_cms
from muzapi.res_album import Album_res
from muzapi.res_roles import Role_res
from muzapi.res_user import User_res
from muzapi.res_log import Log_res


def create_app(config):
    app = Flask(__name__,
                template_folder='../muzsite/templates',
                static_folder='../muzsite/static')

    app.config.from_object(config)
    app.url_map.strict_slashes = False

    app.register_blueprint(muzlog_site)
    app.register_blueprint(muzlog_cms)

    user_datastore = MongoEngineUserDatastore(db, User, Role)
    security = Security(app, user_datastore)
    mail = Mail(app)
    db.init_app(app)

    api = Api(app, doc='/doc/', prefix='/api/')

    api.add_resource(Log_res, "log", "log/<string:_id>")
    api.add_resource(Role_res, "role")
    api.add_resource(User_res, "profile", "profile/<string:_id>")
    api.add_resource(Album_res, "album", "album/<string:_id>")

    CORS(app)
    return app
