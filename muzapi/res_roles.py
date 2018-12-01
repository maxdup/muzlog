from flask_restplus import Resource, fields, marshal, marshal_with, abort
from flask_security import current_user, roles_accepted, login_required
from mongoengine.queryset import DoesNotExist

from muzapi.util_rest import *
from muzapi.models import User, Role
from muzapi.res_user import User_res


class Role_res(Resource):

    args = {'id': {'required': True, 'help': "user id is required"},
            'role': {'required': True, 'help': "role is required"}}

    @login_required
    @roles_accepted('admin')
    @marshal_with(User_res.user_fields, skip_none=True)
    def get(self):
        # Get All Roles
        return {'roles': Role.objects()}

    @login_required
    @roles_accepted('admin')
    @marshal_with(User_res.user_fields, envelope="profile")
    def post(self):

        # Add a role
        content = parse_request(self.args)

        try:
            user = User.objects.get(id=content['id'])
            role = Role.objects.get(name=content['role'])
        except DoesNotExist:
            abort(404)

        if (role not in user.roles):
            user.roles.append(role)
            user.save()

        return user

    @login_required
    @roles_accepted('admin')
    @marshal_with(User_res.user_fields, envelope="profile")
    def put(self):

        # Revoke a role

        content = parse_request(self.args)

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

        return user
