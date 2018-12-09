from flask_restplus import Resource, fields, marshal_with, abort, Namespace, reqparse
from flask_security import current_user, roles_accepted, login_required
from mongoengine.queryset import DoesNotExist
from mongoengine.errors import ValidationError

from datetime import datetime


from muzapi.util_rest import RequestParser
from muzapi.models import User, Role
from muzapi.util_rest import *
from muzapi.render import user_render, users_render


user_api = Namespace('Profiles', path='/profile',
                     description="User resource")

parser_args = {'bio': {}, 'color': {}, 'username': {}}
parser = RequestParser(arguments=parser_args)


@user_api.route('/')
class Users_res(Resource):

    @user_api.marshal_with(users_render)
    def get(self):
        '''Get a list of Users'''
        if current_user.has_role('admin'):
            users = User.objects()
        else:
            log_role = Role.objects.get(name="logger")
            users = User.objects.filter(roles__contains=log_role)

        return {'profiles': users}


@user_api.route('/<string:_id>')
class User_res(Resource):

    @user_api.marshal_with(user_render)
    def get(self, _id=None):
        '''Get a specific User'''
        if _id == 'me':
            user = current_user
        else:
            try:
                user = User.objects.get(id=_id)
            except (DoesNotExist, ValidationError):
                abort(404)

        return {'profile': user}

    @login_required
    @roles_accepted('admin', 'logger')
    @user_api.expect(parser)
    @user_api.marshal_with(user_render)
    def put(self, _id=None):
        '''Update specific User'''
        content = parser.parse_args()

        if _id == str(current_user.id):
            user = current_user
        elif current_user.has_role('admin'):
            try:
                user = User.objects.get(id=_id)
            except (DoesNotExist, ValidationError):
                abort(404)
        else:
            abort(403)
        try:
            user.modify(**content)
        except ValidationError:
            abort(406)

        return {'profile': user}
