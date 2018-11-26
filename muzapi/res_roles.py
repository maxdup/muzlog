from flask import request, jsonify
from flask_restful import Resource, fields, marshal, marshal_with, abort
from flask_security import current_user, roles_accepted, login_required
from mongoengine.queryset import DoesNotExist

from muzapi.util import parse_request
from muzapi.models import User, Role
from muzapi.res_user import User_res


class Role_res(Resource):

    roles_fields = {
        'roles': fields.List(fields.String()),
    }

    args = {'id': {'required': True, 'help': "user id is required"},
            'role': {'required': True, 'help': "role is required"}}

    @login_required
    @roles_accepted('admin')
    def get(self):

        # Get All Roles

        return marshal({'roles': Role.objects()}, self.roles_fields)

    @login_required
    @roles_accepted('admin')
    def post(self):

        # Add a role
        content = parse_request(request, self.args)

        try:
            user = User.objects.get(id=content['id'])
            role = Role.objects.get(name=content['role'])
        except DoesNotExist:
            abort(404)

        if (role not in user.roles):
            user.roles.append(role)
            user.save()

        return marshal({'profile': user}, User_res.user_render)

    @login_required
    @roles_accepted('admin')
    def put(self):

        # Revoke a role

        content = parse_request(request, self.args)

        try:
            user = User.objects.get(id=content['id'])
            role = Role.objects.get(name=content['role'])
        except DoesNotExist:
            abort(404)

        if current_user.id == user.id and role.name == 'admin':
            abort(400)

        if (role in user.roles):
            user.roles = [x for x in user.roles if x.id != role.id]
            user.save()

        return marshal({'profile': user}, User_res.user_render)
