from flask import request, jsonify
from flask_restful import Resource, fields, marshal, marshal_with, abort, reqparse
from flask_security import current_user, roles_accepted, login_required
from mongoengine.queryset import DoesNotExist

from muzapi.models import User, Role
from muzapi.res_user import User_res


class Role_res(Resource):

    roles_fields = {
        'roles': fields.List(fields.String()),
    }

    parser = reqparse.RequestParser()
    parser.add_argument('id', required=True, help="role id is required")
    parser.add_argument('role', required=True, help="role is required")

    @login_required
    @roles_accepted('admin')
    def get(self):

        # Get All Roles

        return marshal({'roles': Role.objects()}, self.roles_fields)

    @login_required
    @roles_accepted('admin')
    def post(self):

        # Add a role

        content = self.parser.parse_args()
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

        content = self.parser.parse_args()
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
