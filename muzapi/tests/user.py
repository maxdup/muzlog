import os
from muzapi import db
import unittest
import requests
import json

from muzapi.models import User, Role
from muzapi.res_roles import ensure_roles
from muzapi import create_app

from muzapi.util_fakedata import fake_user


class UsersTestCase(unittest.TestCase):

    def setUp(self):
        app = create_app('config_test')

        with app.app_context():
            db.connection.drop_database(app.config['MONGODB_DB'])
            ensure_roles()

            self.client = app.test_client()

            self.r_admin = Role.objects.get(name="admin")
            self.r_logger = Role.objects.get(name="logger")

            self.u_admin = fake_user()
            self.u_admin.roles.append(self.r_admin)
            self.u_admin.save()

            self.u_logger1 = fake_user()
            self.u_logger1.roles.append(self.r_logger)
            self.u_logger1.save()

            self.u_logger2 = fake_user()
            self.u_logger2.roles.append(self.r_logger)
            self.u_logger2.save()

            self.u_1 = fake_user()
            self.u_1.save()

    def tearDown(self):
        return

    def test_get_users(self):

        with self.client.session_transaction() as sess:
            sess['user_id'] = str(self.u_1.id)
            sess['_fresh'] = True

        # test /me
        r = self.client.get('api/profile/me')
        self.assertEqual(r.status_code, 200)
        data = json.loads(r.data.decode())
        self.assertEqual(data['profile']['id'], str(self.u_1.id))

        # test by id
        r = self.client.get('api/profile/' + str(self.u_admin.id))
        self.assertEqual(r.status_code, 200)
        data = json.loads(r.data.decode())
        self.assertEqual(data['profile']['id'], str(self.u_admin.id))

        # test by bad id
        r = self.client.get('api/profile/000000000000000000000000')
        self.assertEqual(r.status_code, 404)

        # test no args as user
        r = self.client.get('api/profile')
        self.assertEqual(r.status_code, 200)
        data = json.loads(r.data.decode())
        self.assertEqual(len(data['profiles']), 2)

        with self.client.session_transaction() as sess:
            sess['user_id'] = str(self.u_admin.id)
            sess['_fresh'] = True

        # test no args as admin
        r = self.client.get('api/profile')
        self.assertEqual(r.status_code, 200)
        data = json.loads(r.data.decode())
        self.assertEqual(len(data['profiles']), 4)

    def test_put_users(self):

        # test user role fail
        with self.client.session_transaction() as sess:
            sess['user_id'] = str(self.u_1.id)
            sess['_fresh'] = True
        r = self.client.put('api/profile/' + str(self.u_1.id),
                            content_type='application/json',
                            data=json.dumps({'id': str(self.u_1.id),
                                             'bio': 'im me',
                                             'color': '#333',
                                             'username': 'me'}))
        self.assertEqual(r.status_code, 302)

        # test logger role pass on themself
        with self.client.session_transaction() as sess:
            sess['user_id'] = str(self.u_logger1.id)
            sess['_fresh'] = True
        r = self.client.put('api/profile',
                            content_type='application/json',
                            data=json.dumps({'id': str(self.u_logger1.id),
                                             'bio': 'im me',
                                             'color': '#333',
                                             'username': 'me'}))
        self.assertEqual(r.status_code, 200)
        data = json.loads(r.data.decode())
        self.assertEqual(data['profile']['id'], str(self.u_logger1.id))
        self.assertEqual(data['profile']['bio'], 'im me')
        self.assertEqual(data['profile']['color'], '#333')
        self.assertEqual(data['profile']['username'], 'me')

        # test color regex
        r = self.client.put('api/profile',
                            content_type='application/json',
                            data=json.dumps({'id': str(self.u_logger1.id),
                                             'color': '#3333'}))
        self.assertEqual(r.status_code, 406)

        # test logger role fail on others
        with self.client.session_transaction() as sess:
            sess['user_id'] = str(self.u_logger1.id)
            sess['_fresh'] = True
        r = self.client.put('api/profile',
                            content_type='application/json',
                            data=json.dumps({'id': str(self.u_1.id),
                                             'bio': 'im me'}))
        self.assertEqual(r.status_code, 403)

        # test admin role works on others
        with self.client.session_transaction() as sess:
            sess['user_id'] = str(self.u_admin.id)
            sess['_fresh'] = True
        r = self.client.put('api/profile',
                            content_type='application/json',
                            data=json.dumps({'id': str(self.u_1.id),
                                             'bio': 'im not you',
                                             'color': '#555555'}))
        self.assertEqual(r.status_code, 200)
        data = json.loads(r.data.decode())
        self.assertEqual(data['profile']['id'], str(self.u_1.id))
        self.assertEqual(data['profile']['bio'], 'im not you')
        self.assertEqual(data['profile']['color'], '#555555')

        user = User.objects.get(id=self.u_1.id)
        self.assertEqual(str(user.id), str(self.u_1.id))
        self.assertEqual(user.bio, 'im not you')
        self.assertEqual(user.color, '#555555')

        # test by bad id
        r = self.client.put('api/profile',
                            content_type='application/json',
                            data=json.dumps({'id': '000000000000000000000000'}))
        self.assertEqual(r.status_code, 404)
