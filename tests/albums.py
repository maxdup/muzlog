import pytest
import json

from muzapi.models import *

from utils_faker import *
from utils_auth import *


@pytest.fixture
def setup():
    album_logged = make_album()
    log = make_log(album=album_logged)
    album_logged.logs.append(log)
    album_logged.save()
    album_logged.reload()

    yield {
        'user_1': make_user(username="user1", role='logger'),
        'user_2': make_user(),
        'album': make_album(),
        'album_deleted': make_album(deleted=True),
        'album_logged': album_logged,
        'log': log}


def test_get_albums(client, setup):
    r = client.get('api/album')
    data = json.loads(r.data.decode())
    assert len(data['albums']) == 2
    assert r.status_code == 200

    r = client.get('api/album/' + str(setup['album'].id))

    data = json.loads(r.data.decode())
    assert data['album']['title'] == setup['album'].title
    assert r.status_code == 200

    r = client.get('api/album/000000000000000000000000' +
                   str(setup['album'].id))
    assert r.status_code == 404


def test_post_album(client, setup):
    auth(client, setup['user_2'])
    r = client.post('api/album')
    assert r.status_code == 403

    auth(client, setup['user_1'])

    # Test insuficient post
    r = client.post('api/album', data=json.dumps({}))
    assert r.status_code == 406

    # Test minimal post
    r = client.post('api/album', data=json.dumps({'title': 'album title',
                                                  'artist': 'some artist'}))
    assert r.status_code == 200

    # assert response
    data = json.loads(r.data.decode())
    assert data['album']['id']
    assert data['album']['title'] == 'album title'
    assert data['album']['artist'] == 'some artist'

    # assert db
    album = Album.objects.get(id=data['album']['id'])
    assert album.title == 'album title'
    assert album.artist == 'some artist'

    # Test Full post
    r = client.post('api/album', data=json.dumps({'title': 'nother title',
                                                  'artist': 'other artist',
                                                  'country': 'canada',
                                                  'country_code': 'CA',
                                                  'release_type': 'EP',
                                                  'release_date': '20/11/2018',
                                                  'label': 'label obscura'}))
    assert r.status_code == 200

    # assert response
    data = json.loads(r.data.decode())
    assert data['album']['id']
    assert data['album']['title'] == 'nother title'
    assert data['album']['artist'] == 'other artist'
    assert data['album']['country'] == 'canada'
    assert data['album']['country_code'] == 'CA'
    assert data['album']['release_type'] == 'EP'
    assert data['album']['release_date'] == '2018-11-20'
    assert data['album']['label'] == 'label obscura'

    # assert db
    album = Album.objects.get(id=data['album']['id'])
    assert album.title == 'nother title'
    assert album.artist == 'other artist'
    assert album.country == 'canada'
    assert album.country_code == 'CA'
    assert album.release_type == 'EP'
    assert album.label == 'label obscura'

    # Test mbrgid non existing mbrgid
    r = client.post(
        'api/album', data=json.dumps({'mbrgid': '00000000-7add-3911-0000-9062e28e4c37'}))
    assert r.status_code == 404

    # Test mbrgid post
    r = client.post(
        'api/album', data=json.dumps({'mbrgid': 'f32fab67-77dd-3937-addc-9062e28e4c37'}))
    assert r.status_code == 200

    # assert response
    data = json.loads(r.data.decode())['album']
    assert data['title'] == 'Thriller'
    assert data['artist'] == 'Michael Jackson'
    assert data['country']
    assert data['country_code']
    assert data['release_type'] == 'Album'
    assert data['release_date']
    assert data['label']

    # assert db
    album = Album.objects.get(id=data['id'])
    assert album.title == 'Thriller'
    assert album.artist == 'Michael Jackson'
    assert album.country
    assert album.country_code
    assert album.release_type == 'Album'
    assert album.release_date
    assert album.label

    # Test mbrgid undelete
    r = client.post(
        'api/album', data=json.dumps({'mbrgid': 'f32fab67-77dd-3937-addc-9062e28e4c37'}))
    assert r.status_code == 200
    data = json.loads(r.data.decode())['album']
    deleted_id = data['id']
    r = client.delete('api/album/' + deleted_id)
    album = Album.objects.get(id=deleted_id)
    assert album.deleted
    assert r.status_code == 204
    r = client.post(
        'api/album', data=json.dumps({'mbrgid': 'f32fab67-77dd-3937-addc-9062e28e4c37'}))
    assert r.status_code == 200
    data = json.loads(r.data.decode())['album']
    assert data['id'] == deleted_id
    album = Album.objects.get(id=deleted_id)
    assert not album.deleted


def test_put_album(client, setup):

    auth(client, setup['user_2'])
    r = client.put('api/album')
    assert r.status_code == 405

    auth(client, setup['user_1'])

    # Test insufficient put
    r = client.put('api/album', data=json.dumps({}))
    assert r.status_code == 405

    # Test not found put
    r = client.put('api/album/000000000000000000000000', data=json.dumps({}))
    assert r.status_code == 404

    # Test minimal put
    r = client.put('api/album/' + str(setup['album'].id),
                   data=json.dumps({'artist': 'new artist'}))
    assert r.status_code == 200

    # assert response
    data = json.loads(r.data.decode())
    assert data['album']['id'] == str(setup['album'].id)
    assert data['album']['artist'] == 'new artist'
    assert data['album']['title'] == setup['album'].title

    # assert db
    album = Album.objects.get(id=data['album']['id'])
    assert album.artist == 'new artist'
    assert album.title == setup['album'].title

    # Test Full put
    r = client.put('api/album/' + str(setup['album'].id),
                   data=json.dumps({'title': 'nother title',
                                    'artist': 'newer artist',
                                    'country': 'canada',
                                    'country_code': 'CA',
                                    'release_type': 'EP',
                                    'release_date': '20/11/2018',
                                    'label': 'label obscura'}))
    assert r.status_code == 200

    # assert response
    data = json.loads(r.data.decode())
    assert data['album']['id'] == str(setup['album'].id)
    assert data['album']['title'] == 'nother title'
    assert data['album']['artist'] == 'newer artist'
    assert data['album']['country'] == 'canada'
    assert data['album']['country_code'] == 'CA'
    assert data['album']['release_type'] == 'EP'
    assert data['album']['release_date'] == '2018-11-20'
    assert data['album']['label'] == 'label obscura'

    # assert db
    album = Album.objects.get(id=data['album']['id'])
    assert album.title == 'nother title'
    assert album.artist == 'newer artist'
    assert album.country == 'canada'
    assert album.country_code == 'CA'
    assert album.release_type == 'EP'
    assert album.label == 'label obscura'

    # Test mbrgid put
    r = client.put('api/album/' + str(setup['album'].id),
                   data=json.dumps({'mbrgid': 'f32fab67-77dd-3937-addc-9062e28e4c37'}))
    assert r.status_code == 200
    data = json.loads(r.data.decode())['album']
    assert data['mbrgid'] == 'f32fab67-77dd-3937-addc-9062e28e4c37'
    assert data['artist'] == 'Michael Jackson'


def test_delete_album(client, setup):
    auth(client, setup['user_2'])
    r = client.put('api/album')
    assert r.status_code == 405

    auth(client, setup['user_1'])

    # Test delete fictive album
    r = client.delete('api/album/000000000000000000000000', data=json.dumps({}))
    assert r.status_code == 404

    # Test insufficient delete
    r = client.delete('api/album', data=json.dumps({}))
    assert r.status_code == 405

    # Test failed delete for logged albums
    r = client.delete('api/album/'+str(setup['album_logged'].id))
    assert r.status_code == 400

    # Test complete delete
    r = client.delete('api/album/'+str(setup['album'].id))
    assert r.status_code == 204

    # Assert db
    album = Album.objects.get(id=setup['album'].id)
    assert album.deleted
