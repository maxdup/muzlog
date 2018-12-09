from flask import Blueprint
from flask_restplus import Api

from muzapi.res_roles import role_api
from muzapi.res_log import log_api
from muzapi.res_user import user_api
from muzapi.res_album import album_api
from muzapi.render import render_api

muzlog_api = Blueprint('muzlog_api', __name__)

api = Api(muzlog_api,
          title="Muzlog API",
          version='1.0',
          description='The muzlog.com api',
          prefix='/api',
          doc='/doc/')


api.add_namespace(render_api)
api.add_namespace(album_api)
api.add_namespace(log_api)
api.add_namespace(user_api)
api.add_namespace(role_api)
