import pytest
import json

from muzapi.models import User, Role

from utils_faker import *
from utils_auth import *


@pytest.fixture
def users():
    yield {'user_1': make_user(),
           'user_2': make_user(),
           'user_3': make_user(),
           'logger': make_user(role='logger'),
           'admin': make_user(role='admin')}


@pytest.fixture
def roles():
    rs = {}
    for role in Role.objects():
        rs[role.name] = role

    yield rs


def test_get_roles(client, users):
    auth(client, users['logger'])
    assert client.get('api/role').status_code == 403

    auth(client, users['user_1'])
    assert client.get('api/role').status_code == 403

    auth(client, users['admin'])
    r = client.get('api/role')
    data = json.loads(r.data.decode())
    assert r.status_code == 200
    assert len(data['roles']) == 2


def test_add_role_to_user(client, users, roles):
    auth(client, users['logger'])
    assert client.post('api/role').status_code == 403

    auth(client, users['user_1'])
    assert client.post('api/role').status_code == 403

    auth(client, users['admin'])

    # test 404 error
    payload = json.dumps({'id': str(users['user_1'].id), 'role': 'patate'})
    assert client.post('api/role', data=payload).status_code == 404
    payload = json.dumps({'id': '000000000000000000000000', 'role': 'logger'})
    assert client.post('api/role', data=payload).status_code == 404

    # give logger perm
    payload = json.dumps({'id': str(users['user_1'].id), 'role': 'logger'})
    r = client.post('api/role', data=payload)
    assert r.status_code == 200

    # test response
    data = json.loads(r.data.decode())
    assert len(data['profile']['roles']) == 1
    assert data['profile']['id'] == str(users['user_1'].id)
    assert data['profile']['roles'][0] == 'logger'

    # test db
    u1 = User.objects.get(id=users['user_1'].id)
    assert roles['logger'] in u1.roles
    assert roles['admin'] not in u1.roles

    # give admin perm
    payload = json.dumps({'id': str(users['user_2'].id), 'role': 'admin'})
    r = client.post('api/role', data=payload)
    assert r.status_code == 200
    data = json.loads(r.data.decode())
    assert len(data['profile']['roles']) == 1
    assert data['profile']['id'] == str(users['user_2'].id)
    assert data['profile']['roles'][0] == 'admin'


def test_remove_role_to_user(client, users, roles):

    users['user_3'].roles.append(roles['admin'])
    users['user_3'].save()

    auth(client, users['logger'])
    assert client.put('api/role').status_code == 403

    auth(client, users['user_1'])
    assert client.put('api/role').status_code == 403

    auth(client, users['admin'])

    # test required inputs
    payload = json.dumps({})
    assert client.put('api/role', data=payload).status_code == 400

    # test 404 error
    payload = json.dumps({'id': str(users['user_1'].id), 'role': 'patate'})
    assert client.put('api/role', data=payload).status_code == 404

    payload = json.dumps({'id': '000000000000000000000000', 'role': 'logger'})
    assert client.put('api/role', data=payload).status_code == 404

    # test removing admin to yourself
    payload = json.dumps({'id': str(users['admin'].id), 'role': 'admin'})
    assert client.put('api/role', data=payload).status_code == 400

    # remove logger perm
    payload = json.dumps({'id': str(users['logger'].id), 'role': 'logger'})
    r = client.put('api/role', data=payload)
    assert r.status_code == 200

    # test response
    data = json.loads(r.data.decode())
    assert len(data['profile']['roles']) == 0
    assert data['profile']['id'] == str(users['logger'].id)

    # test db
    logger = User.objects.get(id=users['logger'].id)
    assert roles['logger'] not in logger.roles
    assert roles['admin'] not in logger.roles

    # remove admin perm
    payload = json.dumps({'id': str(users['user_3'].id), 'role': 'admin'})
    r = client.put('api/role', data=payload)
    assert r.status_code == 200
    data = json.loads(r.data.decode())
    assert len(data['profile']['roles']) == 0
    assert data['profile']['id'] == str(users['user_3'].id)
