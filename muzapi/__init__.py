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

    api = Api(app, doc='/doc/')

    api.add_resource(Album_res, "/api/album", endpoint="albums")
    api.add_resource(Album_res, "/api/album/<string:_id>", endpoint="album")
    api.add_resource(Log_res, "/api/log", endpoint="logs")
    api.add_resource(Log_res, "/api/log/<string:_id>", endpoint="log")
    api.add_resource(User_res, "/api/profile", endpoint="profiles")
    api.add_resource(User_res, "/api/profile/<string:_id>", endpoint="profile")
    api.add_resource(Role_res, "/api/role", endpoint="roles")

    CORS(app)
    return app
