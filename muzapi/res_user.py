from flask import request, jsonify
from flask_restful import Resource, fields, marshal, marshal_with, abort
from flask_security import current_user, roles_accepted, login_required
from mongoengine.queryset import DoesNotExist
from mongoengine.errors import ValidationError

from datetime import datetime

from muzapi.util import stringRestricted, listRestricted, parse_request
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
    user_render = {
        'profile': fields.Nested(user_fields)
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
            return marshal({'profile': current_user}, self.user_render)
        elif _id:
            try:
                user = User.objects.get(id=_id)
            except (DoesNotExist, ValidationError):
                abort(404)
            return marshal({'profile': user}, self.user_render)
        elif current_user.has_role('admin'):
            users = User.objects()
        else:
            log_role = Role.objects.get(name="logger")
            users = User.objects.filter(roles__contains=log_role)

        return marshal({'profiles': users}, self.users_render)

    @login_required
    @roles_accepted('admin', 'logger')
    def put(self, _id=None):

        # Update User

        args = {'id': {}, 'bio': {}, 'color': {}, 'username': {}}
        content = parse_request(request, args)

        if 'id' in content:
            if content['id'] == str(current_user.id):
                user = current_user
            elif current_user.has_role('admin'):
                try:
                    user = User.objects.get(id=content['id'])
                except (DoesNotExist, ValidationError):
                    abort(404)
            else:
                abort(403)
        else:
            user = current_user

        user.modify(**content)
        user.save()

        return marshal({'profile': user}, self.user_render)
