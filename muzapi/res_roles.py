from flask_restplus import Resource, fields, marshal, marshal_with, abort, Namespace
from flask_security import current_user, roles_accepted, login_required
from mongoengine.queryset import DoesNotExist

from muzapi.util_rest import RequestParser
from muzapi.models import User, Role
from muzapi.render import base_user, user_render

role_api = Namespace('Roles', path='/role',
                     description="Role resource")

parser_args = {'id': {'required': True, 'help': "User id is required"},
               'role': {'required': True, 'help': "Role name is required"}}
parser = RequestParser(arguments=parser_args)


@role_api.route('/')
class Role_res(Resource):

    @login_required
    @roles_accepted('admin')
    @role_api.marshal_with(base_user, skip_none=True)
    def get(self):
        '''Get All Roles'''
        return {'roles': Role.objects()}

    @login_required
    @roles_accepted('admin')
    @role_api.expect(parser)
    @role_api.marshal_with(user_render)
    def post(self):
        '''Grant a role to a User'''
        content = parser.parse_args()

        try:
            user = User.objects.get(id=content['id'])
            role = Role.objects.get(name=content['role'])
        except DoesNotExist:
            abort(404)

        if (role not in user.roles):
            user.roles.append(role)
            user.save()

        return {'profile': user}

    @login_required
    @roles_accepted('admin')
    @role_api.expect(parser)
    @role_api.marshal_with(user_render)
    def put(self):
        '''Revoke a role from a User'''
        content = parser.parse_args()

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

        return {'profile': user}


def ensure_roles():
    if not Role.objects(name="admin"):
        role_admin = Role(name="admin",
                          description="includes all permissions")
        role_admin.save()

    if not Role.objects(name="logger"):
        role_logger = Role(name="logger",
                           description="common poster")
        role_logger.save()
