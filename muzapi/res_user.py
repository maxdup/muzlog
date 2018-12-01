from flask_restplus import Resource, fields, marshal, marshal_with, abort
from flask_security import current_user, roles_accepted, login_required
from mongoengine.queryset import DoesNotExist
from mongoengine.errors import ValidationError

from datetime import datetime

from muzapi.util_rest import *
from muzapi.models import *


class User_res(Resource):

    user_fields = {
        'id': fields.String,
        'email': stringRestricted,

        'bio': fields.String,
        'username': fields.String,
        'color': fields.String,

        'avatar': fields.String,
        'thumb': fields.String,

        'roles': listRestricted(fields.String()),
    }
    users_render = {
        'profiles': fields.List(fields.Nested(user_fields))
    }

    def get(self, _id=None):
        '''
        Get Users

        :param_id: The _id of an User object
        '''
        if _id == 'me':
            return marshal(current_user, self.user_fields, envelope='profile')
        elif _id:
            try:
                user = User.objects.get(id=_id)
            except (DoesNotExist, ValidationError):
                abort(404)
            return marshal(user, self.user_fields, envelope='profile')
        elif current_user.has_role('admin'):
            users = User.objects()
        else:
            log_role = Role.objects.get(name="logger")
            users = User.objects.filter(roles__contains=log_role)

        return marshal({'profiles': users}, self.users_render)

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
            user.save()
        except ValidationError:
            abort(406)

        return user
