import pytest
import json

from muzapi.models import *

from utils_faker import *
from utils_auth import *


@pytest.fixture
def setup():

    logger_1 = make_user(role='logger')
    logger_2 = make_user(role='logger')

    album_logged_1 = make_album()
    log_1 = make_log(author=logger_1.id,
                     album=album_logged_1,
                     published=True)
    album_logged_1.logs = [log_1]
    album_logged_1.save()
    album_logged_2 = make_album()
    log_2 = make_log(author=logger_1.id,
                     album=album_logged_2,
                     published=False)
    log_3 = make_log(author=logger_2.id,
                     album=album_logged_2,
                     published=True)
    album_logged_2.logs = [log_2, log_3]
    album_logged_2.recommended_by = log_3.author
    album_logged_2.published_by = log_3
    album_logged_2.save()
    yield {
        'user_1': make_user(),
        'admin_1': make_user(role='admin'),
        'logger_1': logger_1,
        'logger_2': logger_2,
        'album_1': make_album(),
        'album_logged_1': album_logged_1,
        'album_logged_2': album_logged_2,
        'log_1': log_1,
        'log_2': log_2,
        'log_3': log_3,
    }


def test_get_logs(client, setup):

    # test /log/ no auth
    r = client.get('api/log/')
    assert r.status_code == 200
    data = json.loads(r.data.decode())
    assert len(data['logs']) == 2

    # test /log/me 403
    r = client.get('api/log/me')
    assert r.status_code == 302

    # test /log/me
    auth(client, setup['logger_1'])
    r = client.get('api/log/me')
    assert r.status_code == 200
    data = json.loads(r.data.decode())
    assert len(data['logs']) == 2

    auth(client, setup['logger_2'])
    r = client.get('api/log/me')
    assert r.status_code == 200
    data = json.loads(r.data.decode())
    assert len(data['logs']) == 1

    # test /log/id
    r = client.get('api/log/' + str(setup['log_2'].id))
    assert r.status_code == 200
    data = json.loads(r.data.decode())['log']
    assert data['id'] == str(setup['log_2'].id)

    # test /log/id
    r = client.get('api/log/' + str(setup['log_1'].id))
    assert r.status_code == 200
    data = json.loads(r.data.decode())['log']
    assert data['id'] == str(setup['log_1'].id)

    # test /log/id
    r = client.get('api/log/' + '000000000000000000000000')
    assert r.status_code == 404


def test_post_logs(client, setup):
    # test role /log/
    r = client.post('api/log',
                    data=json.dumps({'message': 'a message',
                                     'album': str(setup['album_1'].id)}))
    assert r.status_code == 302

    auth(client, setup['logger_1'])

    # test incomplete /log/
    r = client.post('api/log',
                    data=json.dumps({'message': 'a message'}))
    assert r.status_code == 400
    r = client.post('api/log',
                    data=json.dumps({'album': str(setup['album_1'].id)}))
    assert r.status_code == 400

    # test wrong album id /log/
    r = client.post('api/log',
                    data=json.dumps({'message': 'a message',
                                     'album': '000000000000000000000000'}))
    assert r.status_code == 404

    # test partial /log/
    r = client.post('api/log',
                    data=json.dumps({'message': 'a message',
                                     'album': str(setup['album_1'].id)}))
    # test response
    assert r.status_code == 200
    data = json.loads(r.data.decode())['log']
    assert data['id']
    assert data['message'] == 'a message'
    assert data['recommended'] == False
    assert data['published'] == False
    assert data['album']['id'] == str(setup['album_1'].id)

    # test db
    log = Log.objects.get(id=data['id'])
    assert log.message == 'a message'
    assert log.recommended == False
    assert log.published == False
    assert log.album == setup['album_1']

    # test complete /log/
    r = client.post('api/log',
                    data=json.dumps({'message': 'another message',
                                     'album': str(setup['album_1'].id),
                                     'published': True,
                                     'published_date': '2020-10-15',
                                     'recommended': True}))
    # test response
    assert r.status_code == 200
    data = json.loads(r.data.decode())['log']
    assert data['id']
    assert data['message'] == 'another message'
    assert data['recommended'] == True
    assert data['published'] == True
    assert data['published_date'] == '2020-10-15'
    assert data['album']['id'] == str(setup['album_1'].id)
    # test db
    log = Log.objects.get(id=data['id'])
    assert log.message == 'another message'
    assert log.recommended == True
    assert log.published == True
    assert log.published_date.year == 2020
    assert log.published_date.month == 10
    assert log.published_date.day == 15
    assert log.album == setup['album_1']


def test_put_logs(client, setup):
    # test role /log/
    r = client.put('api/log',
                   data=json.dumps({'id': str(setup['log_1'].id),
                                    'message': 'a message',
                                    'album': str(setup['album_1'].id)}))
    assert r.status_code == 405

    auth(client, setup['logger_1'])

    # test incomplete /log/
    r = client.put('api/log',
                   data=json.dumps({'message': 'a message'}))
    assert r.status_code == 405
    r = client.put('api/log',
                   data=json.dumps({'album': str(setup['album_1'].id)}))
    assert r.status_code == 405

    # test wrong album id /log/
    r = client.put('api/log/000000000000000000000000',
                   data=json.dumps({'message': 'a message'}))
    assert r.status_code == 404

    # test block when not author
    auth(client, setup['logger_2'])

    r = client.put('api/log/' + str(setup['log_1'].id),
                   data=json.dumps({'message': 'a message'}))
    assert r.status_code == 403

    # test partial /log/
    auth(client, setup['logger_1'])
    r = client.put('api/log/' + str(setup['log_2'].id),
                   data=json.dumps({'message': 'an edited message'}))
    assert r.status_code == 200
    data = json.loads(r.data.decode())['log']
    assert data['message'] == 'an edited message'
    assert data['recommended'] == False
    assert data['published'] == False
    assert data['published_date']

    # test full /log/
    auth(client, setup['logger_1'])
    r = client.put('api/log/' + str(setup['log_2'].id),
                   data=json.dumps({'published': True,
                                    'recommended': True,
                                    'message': 'an edited log'}))
    # assert response
    assert r.status_code == 200
    data = json.loads(r.data.decode())['log']
    assert data['message'] == 'an edited log'
    assert data['recommended'] == True
    assert data['published'] == True
    assert data['published_date']
    assert r.status_code == 200

    # assert database
    log = Log.objects.get(id=setup['log_2'].id)
    assert log.message == 'an edited log'
    assert log.recommended == True
    assert log.published == True

    # test unpublish /log/
    auth(client, setup['logger_1'])
    r = client.put('api/log/' + str(setup['log_2'].id),
                   data=json.dumps({'published': False,
                                    'recommended': False,
                                    'message': 'an unpublished log'}))
    assert r.status_code == 200

    # test unpublish /log/
    r = client.put('api/log/' + str(setup['log_1'].id),
                   data=json.dumps({'published': False,
                                    'recommended': False,
                                    'message': 'an unpublished log'}))
    assert r.status_code == 200

    # test empty update
    r = client.put('api/log/' + str(setup['log_1'].id),
                   data=json.dumps({}))
    assert r.status_code == 200


def test_delete_logs(client, setup):

    # test roles
    r = client.delete('api/log/000000000000000000000000')
    assert r.status_code == 302

    # test /log/ 404
    auth(client, setup['logger_1'])
    r = client.delete('api/log')
    assert r.status_code == 405
    r = client.delete('api/log/')
    assert r.status_code == 405

    # test invalid id
    r = client.delete('api/log/000000000000000000000000')
    assert r.status_code == 404

    # test deleting other people's logs
    auth(client, setup['logger_2'])
    r = client.delete('api/log/' + str(setup['log_1'].id))
    assert r.status_code == 403

    # test deleting published logs
    auth(client, setup['admin_1'])
    r = client.delete('api/log/' + str(setup['log_1'].id))
    assert r.status_code == 400

    # test deleting own logs
    auth(client, setup['logger_1'])
    r = client.delete('api/log/' + str(setup['log_2'].id))
    assert r.status_code == 204

    # Assert db
    logs = Log.objects(id=setup['log_2'].id)
    assert len(logs) == 0
