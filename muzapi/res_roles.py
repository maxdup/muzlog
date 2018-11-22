from flask import request, jsonify
from flask_restful import Resource, fields, marshal, marshal_with, abort
from flask_security import current_user, roles_accepted, login_required
from mongoengine.queryset import DoesNotExist
from mongoengine.errors import ValidationError, FieldDoesNotExist

from muzapi.models import User, Role
from muzapi.res_user import User_res


class Role_res(Resource):

    roles_fields = {
        'roles': fields.List(fields.String()),
    }

    @login_required
    @roles_accepted('admin')
    def get(self, _id=None):
        '''
        Get Roles

        :param_id: The _id of an User object
        '''
        roles = Role.objects()
        return marshal({'roles': roles}, self.roles_fields)

    @login_required
    @roles_accepted('admin')
    def post(self, _id=None):
        '''
        Add a role

        :param_id: The _id of an User object
        '''
        if (_id):
            user = User.objects.get(id=_id)
        else:
            abort(404)

        content = request.get_json()

        if not user:
            abort(404)

        if not content or 'role' not in content:
            abort(400)

        try:
            role = Role.objects.get(name=content['role'])
            if (role and role not in user.roles):
                user.roles.append(role)
                user.save()
        except (ValidationError, FieldDoesNotExist) as e:
            abort(406)
        except Exception as e:
            abort(e)

        return marshal({'profile': user}, User_res.user_render)

    @login_required
    @roles_accepted('admin')
    def put(self, _id=None):
        '''
        Revoke a role

        :param_id: The _id of an User object
        '''
        if (_id):
            user = User.objects.get(id=_id)
        else:
            abort(404)

        content = request.get_json()

        if not user:
            abort(404)

        if not content or 'role' not in content:
            abort(400)

        try:
            role = Role.objects.get(name=content['role'])

            if (role and role in user.roles):
                if current_user.id == user.id and \
                   role.name == 'admin':
                    abort(400)
                else:
                    user.roles = [x for x in user.roles if x.id != role.id]
                    user.save()

        except (ValidationError, FieldDoesNotExist) as e:
            abort(406)
        except Exception as e:
            abort(e)

        return marshal({'profile': user}, User_res.user_render)
