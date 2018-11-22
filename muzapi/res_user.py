from flask import request, jsonify
from flask_restful import Resource, fields, marshal, marshal_with, abort
from flask_security import current_user, roles_accepted, login_required
from mongoengine.queryset import DoesNotExist
from mongoengine.errors import ValidationError, FieldDoesNotExist

from datetime import datetime

from muzapi.util import stringRestricted, listRestricted
from muzapi.models import *


class User_res(Resource):

    user_fields = {
        'id': fields.String,
        'bio': fields.String(attribute=lambda x: x.profile.bio),
        'username': fields.String(attribute=lambda x: x.profile.username),
        'color': fields.String(attribute=lambda x: x.profile.color),
        'avatar': fields.String(attribute=lambda x: x.profile.avatar),
        'thumb': fields.String(attribute=lambda x: x.profile.thumb),

        'email': stringRestricted(),
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
        if (_id):
            if _id == 'me':
                return marshal({'profile': current_user}, self.user_render)
            else:
                user = User.objects.get(id=_id)
                return marshal({'profile': user}, self.user_render)
        else:
            if current_user.has_role:
                users = User.objects()
            return marshal({'profiles': users}, self.users_render)
        return

    @login_required
    @roles_accepted('logger', 'admin')
    def put(self, _id=None):
        '''
        Update Users

        :param_id: The _id of an User object
        '''
        if (_id):
            if _id == str(current_user.id) or \
               current_user.has_role('admin'):
                user = User.objects.get(id=_id)
            else:
                abort(403)
        else:
            user = current_user

        content = request.get_json()

        if not user:
            abort(404)

        if not content:
            abort(400)

        del content['id']
        del content['roles']

        try:
            for key, value in content.items():
                setattr(user.profile, key, value)
            user.save()
        except (ValidationError, FieldDoesNotExist) as e:
            abort(406)
        except Exception as e:
            abort(e)

        return marshal({'profile': user}, self.user_render)
