from flask_restplus import Resource, fields, marshal, marshal_with, abort
from flask_security import current_user, roles_accepted, login_required
from mongoengine.queryset import DoesNotExist
from mongoengine.errors import ValidationError

from datetime import datetime


from muzapi.util_rest import parse_request
from muzapi.models import *
from muzapi.render import *


class User_res(Resource):

    def get(self, _id=None):
        '''
        Get Users

        :param_id: The _id of an User object
        '''
        if _id == 'me':
            return marshal(current_user, user_fields, envelope='profile')
        elif _id:
            try:
                user = User.objects.get(id=_id)
            except (DoesNotExist, ValidationError):
                abort(404)
            return marshal(user, user_fields, envelope='profile')
        elif current_user.has_role('admin'):
            users = User.objects()
        else:
            log_role = Role.objects.get(name="logger")
            users = User.objects.filter(roles__contains=log_role)

        return marshal({'profiles': users}, users_render)

    @login_required
    @roles_accepted('admin', 'logger')
    @marshal_with(user_fields, envelope='profile')
    def put(self, _id=None):

        # Update User

        args = {'id': {'required': True, 'help': 'User id is required'},
                'bio': {}, 'color': {}, 'username': {}}
        content = parse_request(args)

        if content['id'] == str(current_user.id):
            user = current_user
        elif current_user.has_role('admin'):
            try:
                user = User.objects.get(id=content['id'])
            except (DoesNotExist, ValidationError):
                abort(404)
        else:
            abort(403)
        try:
            user.modify(**content)
        except ValidationError:
            abort(406)

        return user
