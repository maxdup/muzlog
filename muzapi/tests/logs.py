import os
from muzapi import db, User
import unittest
import requests
import json

from muzapi.models import *
from muzapi.util import ensure_roles
from muzapi import create_app

from muzapi.util_fakedata import fake_user, fake_album, fake_log, fake_comment

from datetime import datetime


class LogsTestCase(unittest.TestCase):

    def setUp(self):
        app = create_app('config_test')
        with app.app_context():
            db.connection.drop_database(app.config['MONGODB_DB'])
            ensure_roles()

            self.client = app.test_client()

            self.r_admin = Role.objects.get(name="admin")
            self.r_logger = Role.objects.get(name="logger")

            self.u_admin_1 = fake_user()
            self.u_admin_1.roles.append(self.r_admin)
            self.u_admin_1.save()

            self.u_logger_1 = fake_user()
            self.u_logger_1.roles.append(self.r_logger)
            self.u_logger_1.save()

            self.u_logger_2 = fake_user()
            self.u_logger_2.roles.append(self.r_logger)
            self.u_logger_2.save()

            self.u_1 = fake_user()
            self.u_1.save()

            self.album_1 = fake_album()
            self.album_1.save()
            self.album_1.reload()

            self.album_logged_1 = fake_album()
            self.album_logged_1.save()
            self.album_logged_1.reload()
            self.log_1 = Log(message="hi",
                             author=self.u_logger_1,
                             published=True,
                             album=self.album_logged_1)
            self.log_1.save()
            self.album_logged_1.logs = [self.log_1]
            self.album_logged_1.save()

            self.album_logged_2 = fake_album()
            self.album_logged_2.save()
            self.album_logged_2.reload()
            self.log_2 = Log(message="hi!",
                             author=self.u_logger_1,
                             album=self.album_logged_2)
            self.log_2.save()
            self.album_logged_2.logs = [self.log_2]
            self.album_logged_2.save()

    def tearDown(self):
        return

    def test_get_logs(self):

        # test /log/ 404
        r = self.client.get('api/log/',
                            headers={'content-type': 'application/json'})
        self.assertEqual(r.status_code, 404)

        # test /log/me 403
        r = self.client.get('api/log/me',
                            headers={'content-type': 'application/json'})
        self.assertEqual(r.status_code, 403)

        # test /log/me
        with self.client.session_transaction() as sess:
            sess['user_id'] = str(self.u_logger_1.id)
            sess['_fresh'] = True
        r = self.client.get('api/log/me',
                            headers={'content-type': 'application/json'})
        self.assertEqual(r.status_code, 200)
        data = json.loads(r.data.decode())
        self.assertEqual(len(data['logs']), 2)

        with self.client.session_transaction() as sess:
            sess['user_id'] = str(self.u_logger_2.id)
            sess['_fresh'] = True
        r = self.client.get('api/log/me',
                            headers={'content-type': 'application/json'})
        self.assertEqual(r.status_code, 200)
        data = json.loads(r.data.decode())
        self.assertEqual(len(data['logs']), 0)

        # test /log/id
        r = self.client.get('api/log/' + str(self.log_2.id),
                            headers={'content-type': 'application/json'})
        self.assertEqual(r.status_code, 200)
        data = json.loads(r.data.decode())['log']
        self.assertEqual(data['id'], str(self.log_2.id))

        # test /log/id
        r = self.client.get('api/log/' + str(self.log_1.id),
                            headers={'content-type': 'application/json'})
        self.assertEqual(r.status_code, 200)
        data = json.loads(r.data.decode())['log']
        self.assertEqual(data['id'], str(self.log_1.id))

        # test /log/id
        r = self.client.get('api/log/' + '000000000000000000000000')
        self.assertEqual(r.status_code, 404)

    def test_post_logs(self):
        # test role /log/
        r = self.client.post('api/log', content_type='application/json',
                             data=json.dumps({'message': 'a message',
                                              'album': str(self.album_1.id)}))
        self.assertEqual(r.status_code, 302)

        with self.client.session_transaction() as sess:
            sess['user_id'] = str(self.u_logger_1.id)
            sess['_fresh'] = True

        # test incomplete /log/
        r = self.client.post('api/log', content_type='application/json',
                             data=json.dumps({'message': 'a message'}))
        self.assertEqual(r.status_code, 400)
        r = self.client.post('api/log', content_type='application/json',
                             data=json.dumps({'album': str(self.album_1.id)}))
        self.assertEqual(r.status_code, 400)

        # test wrong album id /log/
        r = self.client.post('api/log', content_type='application/json',
                             data=json.dumps({'message': 'a message',
                                              'album': '000000000000000000000000'}))
        self.assertEqual(r.status_code, 404)

        # test partial /log/
        r = self.client.post('api/log', content_type='application/json',
                             data=json.dumps({'message': 'a message',
                                              'album': str(self.album_1.id)}))
        # test response
        self.assertEqual(r.status_code, 200)
        data = json.loads(r.data.decode())['log']
        self.assertTrue(data['id'])
        self.assertEqual(data['message'], 'a message')
        self.assertEqual(data['recommended'], False)
        self.assertEqual(data['published'], False)
        self.assertEqual(data['album']['id'], str(self.album_1.id))
        # test db
        log = Log.objects.get(id=data['id'])
        self.assertEqual(log.message, 'a message')
        self.assertEqual(log.recommended, False)
        self.assertEqual(log.published, False)
        self.assertEqual(log.album, self.album_1)

        # test complete /log/
        r = self.client.post('api/log', content_type='application/json',
                             data=json.dumps({'message': 'another message',
                                              'album': str(self.album_1.id),
                                              'published': True,
                                              'published_date': '2020-10-15',
                                              'recommended': True}))
        # test response
        self.assertEqual(r.status_code, 200)
        data = json.loads(r.data.decode())['log']
        self.assertTrue(data['id'])
        self.assertEqual(data['message'], 'another message')
        self.assertEqual(data['recommended'], True)
        self.assertEqual(data['published'], True)
        self.assertEqual(data['published_date'], '2020-10-15')
        self.assertEqual(data['album']['id'], str(self.album_1.id))
        # test db
        log = Log.objects.get(id=data['id'])
        self.assertEqual(log.message, 'another message')
        self.assertEqual(log.recommended, True)
        self.assertEqual(log.published, True)
        self.assertEqual(log.published_date.year, 2020)
        self.assertEqual(log.published_date.month, 10)
        self.assertEqual(log.published_date.day, 15)
        self.assertEqual(log.album, self.album_1)

    def test_delete_logs(self):

        # test roles
        r = self.client.delete('api/log/000000000000000000000000')
        self.assertEqual(r.status_code, 302)

        # test /log/ 404
        with self.client.session_transaction() as sess:
            sess['user_id'] = str(self.u_logger_1.id)
            sess['_fresh'] = True
        r = self.client.delete('api/log')
        self.assertEqual(r.status_code, 404)
        r = self.client.delete('api/log/')
        self.assertEqual(r.status_code, 404)

        # test invalid id
        with self.client.session_transaction() as sess:
            sess['user_id'] = str(self.u_logger_1.id)
            sess['_fresh'] = True
        r = self.client.delete('api/log/000000000000000000000000')
        self.assertEqual(r.status_code, 404)

        # test deleting other people's logs
        with self.client.session_transaction() as sess:
            sess['user_id'] = str(self.u_logger_2.id)
            sess['_fresh'] = True
        r = self.client.delete('api/log/' + str(self.log_1.id))
        self.assertEqual(r.status_code, 403)

        # test deleting published logs
        with self.client.session_transaction() as sess:
            sess['user_id'] = str(self.u_admin_1.id)
            sess['_fresh'] = True
        r = self.client.delete('api/log/' + str(self.log_1.id))
        self.assertEqual(r.status_code, 400)

        # test deleting own logs
        with self.client.session_transaction() as sess:
            sess['user_id'] = str(self.u_logger_1.id)
            sess['_fresh'] = True
        r = self.client.delete('api/log/' + str(self.log_2.id))
        self.assertEqual(r.status_code, 204)
