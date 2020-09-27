import pytest
import json

from muzapi.models import User, Role

from utils_faker import *
from utils_auth import *


@pytest.fixture
def users():
    yield {'user_1': make_user(),
           'admin': make_user(role='admin'),
           'logger_1': make_user(role='logger'),
           'logger_2': make_user(role='logger')}


def test_get_users(client, users):

    auth(client, users['user_1'])

    # test /me
    r = client.get('api/profile/me')
    assert r.status_code == 200
    data = json.loads(r.data.decode())
    assert data['profile']['id'] == str(users['user_1'].id)

    # test by id
    r = client.get('api/profile/' + str(users['admin'].id))
    assert r.status_code == 200
    data = json.loads(r.data.decode())
    assert data['profile']['id'] == str(users['admin'].id)

    # test by bad id
    r = client.get('api/profile/000000000000000000000000')
    assert r.status_code == 404

    # test no args as user
    r = client.get('api/profile')
    assert r.status_code == 200
    data = json.loads(r.data.decode())
    assert len(data['profiles']) == 2

    auth(client, users['admin'])

    # test no args as admin
    r = client.get('api/profile')
    assert r.status_code == 200
    data = json.loads(r.data.decode())
    assert len(data['profiles']) == 4


def test_put_users(client, users):

    # test user role fail
    auth(client, users['user_1'])
    r = client.put('api/profile/' + str(users['user_1'].id),
                   data=json.dumps({'bio': 'im me',
                                    'color': '#333',
                                    'username': 'me'}))
    assert r.status_code == 403

    # test logger role pass on themself
    auth(client, users['logger_1'])
    r = client.put('api/profile/' + str(users['logger_1'].id),
                   data=json.dumps({'id': str(users['logger_1'].id),
                                    'bio': 'im me',
                                    'color': '#333',
                                    'username': 'me'}))
    assert r.status_code == 200
    data = json.loads(r.data.decode())
    assert data['profile']['id'] == str(users['logger_1'].id)
    assert data['profile']['bio'] == 'im me'
    assert data['profile']['color'] == '#333'
    assert data['profile']['username'] == 'me'

    # test color regex
    r = client.put('api/profile/' + str(users['logger_1'].id),
                   data=json.dumps({'color': '#55555'}))
    assert r.status_code == 406

    # test logger role fail on others
    auth(client, users['logger_1'])
    r = client.put('api/profile/' + str(users['user_1'].id),
                   data=json.dumps({'bio': 'im me'}))
    assert r.status_code == 403

    # test admin role works on others
    auth(client, users['admin'])
    r = client.put('api/profile/' + str(users['user_1'].id),
                   data=json.dumps({'bio': 'im not you',
                                    'color': '#555555'}))
    assert r.status_code == 200
    data = json.loads(r.data.decode())
    assert data['profile']['id'] == str(users['user_1'].id)
    assert data['profile']['bio'] == 'im not you'
    assert data['profile']['color'] == '#555555'

    user = User.objects.get(id=users['user_1'].id)
    assert str(user.id) == str(users['user_1'].id)
    assert user.bio == 'im not you'
    assert user.color == '#555555'

    # test fictive user
    r = client.put('api/profile/000000000000000000000000',
                   data=json.dumps({'bio': 'im not you',
                                    'color': '#555555'}))
    assert r.status_code == 404

    # test by bad id
    r = client.put('api/profile/000000000000000000000000')
    assert r.status_code == 400
