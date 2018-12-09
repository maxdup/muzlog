import os
from muzapi import db, User
import unittest
import requests
import json

from muzapi.models import *
from muzapi.res_roles import ensure_roles
from muzapi import create_app

from muzapi.util_fakedata import fake_user, fake_album, fake_log

from datetime import datetime


class AlbumsTestCase(unittest.TestCase):

    def setUp(self):
        app = create_app('config_test')
        with app.app_context():
            db.connection.drop_database(app.config['MONGODB_DB'])
            ensure_roles()

            self.client = app.test_client()

            self.r_logger = Role.objects.get(name="logger")

            self.u_1 = fake_user()
            self.u_1.roles.append(self.r_logger)
            self.u_1.save()

            self.u_2 = fake_user()
            self.u_2.save()

            self.album = fake_album()
            self.album.save()
            self.album.reload()

            self.album_logged = fake_album()
            self.album_logged.save()
            self.album_logged.reload()

            log = Log(message="hi",
                      album=self.album_logged)
            log.save()
            self.album_logged.logs = [log]
            self.album_logged.save()

            self.deleted_album = fake_album()
            self.deleted_album.deleted = True
            self.deleted_album.save()
            self.deleted_album.reload()

    def tearDown(self):
        return

    def test_get_albums(self):
        r = self.client.get('api/album',
                            headers={'content-type': 'application/json'})
        data = json.loads(r.data.decode())
        self.assertEqual(len(data['albums']), 2)
        self.assertEqual(r.status_code, 200)

        r = self.client.get('api/album/' + str(self.album.id),
                            headers={'content-type': 'application/json'})

        data = json.loads(r.data.decode())
        self.assertEqual(data['album']['title'], self.album.title)
        self.assertEqual(r.status_code, 200)

        r = self.client.get('api/album/000000000000000000000000' + str(self.album.id),
                            headers={'content-type': 'application/json'})
        self.assertEqual(r.status_code, 404)

    def test_post_album(self):
        with self.client.session_transaction() as sess:
            sess['user_id'] = str(self.u_2.id)
            sess['_fresh'] = True
        r = self.client.post('api/album')
        self.assertEqual(r.status_code, 302)

        with self.client.session_transaction() as sess:
            sess['user_id'] = str(self.u_1.id)
            sess['_fresh'] = True

        # Test insuficient post
        r = self.client.post('api/album', content_type='application/json',
                             data=json.dumps({}))
        self.assertEqual(r.status_code, 406)

        # Test minimal post
        r = self.client.post('api/album', content_type='application/json',
                             data=json.dumps({'title': 'album title',
                                              'artist': 'some artist'}))
        self.assertEqual(r.status_code, 200)

        # assert response
        data = json.loads(r.data.decode())
        self.assertTrue(data['album']['id'])
        self.assertEqual(data['album']['title'], 'album title')
        self.assertEqual(data['album']['artist'], 'some artist')

        # assert db
        album = Album.objects.get(id=data['album']['id'])
        self.assertEqual(album.title, 'album title')
        self.assertEqual(album.artist, 'some artist')

        # Test Full post
        r = self.client.post('api/album', content_type='application/json',
                             data=json.dumps({'title': 'nother title',
                                              'artist': 'other artist',
                                              'country': 'canada',
                                              'country_code': 'CA',
                                              'release_type': 'EP',
                                              'release_date': '20/11/2018',
                                              'label': 'label obscura'}))
        self.assertEqual(r.status_code, 200)

        # assert response
        data = json.loads(r.data.decode())
        self.assertTrue(data['album']['id'])
        self.assertEqual(data['album']['title'], 'nother title')
        self.assertEqual(data['album']['artist'], 'other artist')
        self.assertEqual(data['album']['country'], 'canada')
        self.assertEqual(data['album']['country_code'], 'CA')
        self.assertEqual(data['album']['release_type'], 'EP')
        self.assertEqual(data['album']['release_date'], '2018-11-20')
        self.assertEqual(data['album']['label'], 'label obscura')

        # assert db
        album = Album.objects.get(id=data['album']['id'])
        self.assertEqual(album.title, 'nother title')
        self.assertEqual(album.artist, 'other artist')
        self.assertEqual(album.country, 'canada')
        self.assertEqual(album.country_code, 'CA')
        self.assertEqual(album.release_type, 'EP')
        self.assertEqual(album.label, 'label obscura')

        # Test mbrgid non existing mbrgid
        r = self.client.post('api/album', content_type='application/json',
                             data=json.dumps({'mbrgid': '00000000-7add-3911-0000-9062e28e4c37'}))
        self.assertEqual(r.status_code, 404)

        # Test mbrgid post
        r = self.client.post('api/album', content_type='application/json',
                             data=json.dumps({'mbrgid': 'f32fab67-77dd-3937-addc-9062e28e4c37'}))
        self.assertEqual(r.status_code, 200)

        # assert response
        data = json.loads(r.data.decode())['album']
        self.assertEqual(data['title'], 'Thriller')
        self.assertEqual(data['artist'], 'Michael Jackson')
        self.assertTrue(data['country'])
        self.assertTrue(data['country_code'])
        self.assertEqual(data['release_type'], 'Album')
        self.assertTrue(data['release_date'])
        self.assertTrue(data['label'])

        # assert db
        album = Album.objects.get(id=data['id'])
        self.assertEqual(album.title, 'Thriller')
        self.assertEqual(album.artist, 'Michael Jackson')
        self.assertTrue(album.country)
        self.assertTrue(album.country_code)
        self.assertEqual(album.release_type, 'Album')
        self.assertTrue(album.release_date)
        self.assertTrue(album.label)

        # Test mbrgid undelete
        r = self.client.post('api/album', content_type='application/json',
                             data=json.dumps({'mbrgid': 'f32fab67-77dd-3937-addc-9062e28e4c37'}))
        self.assertEqual(r.status_code, 200)
        data = json.loads(r.data.decode())['album']
        deleted_id = data['id']
        r = self.client.delete('api/album/' + deleted_id,
                               content_type='application/json')
        album = Album.objects.get(id=deleted_id)
        self.assertTrue(album.deleted)
        self.assertEqual(r.status_code, 204)
        r = self.client.post('api/album', content_type='application/json',
                             data=json.dumps({'mbrgid': 'f32fab67-77dd-3937-addc-9062e28e4c37'}))
        self.assertEqual(r.status_code, 200)
        data = json.loads(r.data.decode())['album']
        self.assertEqual(data['id'], deleted_id)
        album = Album.objects.get(id=deleted_id)
        self.assertFalse(album.deleted)

    def test_put_album(self):
        with self.client.session_transaction() as sess:
            sess['user_id'] = str(self.u_2.id)
            sess['_fresh'] = True
        r = self.client.put('api/album')
        self.assertEqual(r.status_code, 405)

        with self.client.session_transaction() as sess:
            sess['user_id'] = str(self.u_1.id)
            sess['_fresh'] = True

        # Test insufficient put
        r = self.client.put('api/album', content_type='application/json',
                            data=json.dumps({}))
        self.assertEqual(r.status_code, 405)

        # Test not found put
        r = self.client.put('api/album/000000000000000000000000',
                            content_type='application/json',
                            data=json.dumps({}))
        self.assertEqual(r.status_code, 404)

        # Test minimal put
        r = self.client.put('api/album/' + str(self.album.id),
                            content_type='application/json',
                            data=json.dumps({'artist': 'new artist'}))
        self.assertEqual(r.status_code, 200)

        # assert response
        data = json.loads(r.data.decode())
        self.assertEqual(data['album']['id'], str(self.album.id))
        self.assertEqual(data['album']['artist'], 'new artist')
        self.assertEqual(data['album']['title'], self.album.title)

        # assert db
        album = Album.objects.get(id=data['album']['id'])
        self.assertEqual(album.artist, 'new artist')
        self.assertEqual(album.title, self.album.title)

        # Test Full put
        r = self.client.put('api/album/' + str(self.album.id),
                            content_type='application/json',
                            data=json.dumps({'title': 'nother title',
                                             'artist': 'newer artist',
                                             'country': 'canada',
                                             'country_code': 'CA',
                                             'release_type': 'EP',
                                             'release_date': '20/11/2018',
                                             'label': 'label obscura'}))
        self.assertEqual(r.status_code, 200)

        # assert response
        data = json.loads(r.data.decode())
        self.assertEqual(data['album']['id'], str(self.album.id))
        self.assertEqual(data['album']['title'], 'nother title')
        self.assertEqual(data['album']['artist'], 'newer artist')
        self.assertEqual(data['album']['country'], 'canada')
        self.assertEqual(data['album']['country_code'], 'CA')
        self.assertEqual(data['album']['release_type'], 'EP')
        self.assertEqual(data['album']['release_date'], '2018-11-20')
        self.assertEqual(data['album']['label'], 'label obscura')

        # assert db
        album = Album.objects.get(id=data['album']['id'])
        self.assertEqual(album.title, 'nother title')
        self.assertEqual(album.artist, 'newer artist')
        self.assertEqual(album.country, 'canada')
        self.assertEqual(album.country_code, 'CA')
        self.assertEqual(album.release_type, 'EP')
        self.assertEqual(album.label, 'label obscura')

        # Test mbrgid put
        r = self.client.put('api/album/' + str(self.album.id),
                            content_type='application/json',
                            data=json.dumps({'mbrgid': 'f32fab67-77dd-3937-addc-9062e28e4c37'}))
        self.assertEqual(r.status_code, 200)
        data = json.loads(r.data.decode())['album']
        self.assertEqual(data['mbrgid'],
                         'f32fab67-77dd-3937-addc-9062e28e4c37')
        self.assertEqual(data['artist'], 'Michael Jackson')

    def test_delete_album(self):
        with self.client.session_transaction() as sess:
            sess['user_id'] = str(self.u_2.id)
            sess['_fresh'] = True
        r = self.client.put('api/album')
        self.assertEqual(r.status_code, 405)

        with self.client.session_transaction() as sess:
            sess['user_id'] = str(self.u_1.id)
            sess['_fresh'] = True

        # Test delete fictive album
        r = self.client.delete('api/album/000000000000000000000000',
                               content_type='application/json',
                               data=json.dumps({}))
        self.assertEqual(r.status_code, 404)

        # Test insufficient delete
        r = self.client.delete('api/album', content_type='application/json',
                               data=json.dumps({}))
        self.assertEqual(r.status_code, 405)

        # Test failed delete for logged albums
        r = self.client.delete('api/album/'+str(self.album_logged.id),
                               content_type='application/json')
        self.assertEqual(r.status_code, 400)

        # Test complete delete
        r = self.client.delete('api/album/'+str(self.album.id),
                               content_type='application/json')
        self.assertEqual(r.status_code, 204)

        # Assert db
        album = Album.objects.get(id=self.album.id)
        self.assertTrue(album.deleted)
