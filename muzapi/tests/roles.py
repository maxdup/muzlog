from muzapi import db, User
import unittest
import requests
import json

from muzapi.models import User, Role
from muzapi.res_roles import ensure_roles
from muzapi import create_app

from muzapi.util_fakedata import fake_user, fake_album, fake_log


class RolesTestCase(unittest.TestCase):

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

            self.u_logger = fake_user()
            self.u_logger.roles.append(self.r_logger)
            self.u_logger.save()

            self.u_1 = fake_user()
            self.u_1.save()

            self.u_2 = fake_user()
            self.u_2.save()

            self.u_3 = fake_user()
            self.u_3.save()

    def tearDown(self):
        return

    def test_get_roles(self):
        with self.client.session_transaction() as sess:
            sess['user_id'] = str(self.u_logger.id)
            sess['_fresh'] = True
        r = self.client.get('api/role')
        self.assertEqual(r.status_code, 302)

        with self.client.session_transaction() as sess:
            sess['user_id'] = str(self.u_1.id)
            sess['_fresh'] = True
        r = self.client.get('api/role')
        self.assertEqual(r.status_code, 302)

        with self.client.session_transaction() as sess:
            sess['user_id'] = str(self.u_admin.id)
            sess['_fresh'] = True
        r = self.client.get('api/role')
        self.assertEqual(r.status_code, 200)
        data = json.loads(r.data.decode())
        self.assertTrue(len(data['roles']) == 2)

    def test_add_role_to_user(self):
        with self.client.session_transaction() as sess:
            sess['user_id'] = str(self.u_logger.id)
            sess['_fresh'] = True
        r = self.client.post('api/role')
        self.assertEqual(r.status_code, 302)

        with self.client.session_transaction() as sess:
            sess['user_id'] = str(self.u_1.id)
            sess['_fresh'] = True
        r = self.client.post('api/role')
        self.assertEqual(r.status_code, 302)

        with self.client.session_transaction() as sess:
            sess['user_id'] = str(self.u_admin.id)
            sess['_fresh'] = True

        # test 404 error
        r = self.client.post('api/role', content_type='application/json',
                             data=json.dumps({'id': str(self.u_1.id),
                                              'role': 'patate'}))
        self.assertEqual(r.status_code, 404)

        r = self.client.post('api/role', content_type='application/json',
                             data=json.dumps({'id': '000000000000000000000000',
                                              'role': 'logger'}))
        self.assertEqual(r.status_code, 404)

        # give logger perm
        r = self.client.post('api/role', content_type='application/json',
                             data=json.dumps({'id': str(self.u_1.id),
                                              'role': 'logger'}))
        self.assertEqual(r.status_code, 200)

        # test response
        data = json.loads(r.data.decode())
        self.assertTrue(len(data['profile']['roles']) == 1)
        self.assertEqual(data['profile']['id'], str(self.u_1.id))
        self.assertEqual(data['profile']['roles'][0], 'logger')

        # test db
        u1 = User.objects.get(id=self.u_1.id)
        self.assertTrue(self.r_logger in u1.roles)
        self.assertTrue(self.r_admin not in u1.roles)

        # give admin perm
        r = self.client.post('api/role', content_type='application/json',
                             data=json.dumps({'id': str(self.u_2.id),
                                              'role': 'admin'}))
        self.assertEqual(r.status_code, 200)
        data = json.loads(r.data.decode())
        self.assertTrue(len(data['profile']['roles']) == 1)
        self.assertEqual(data['profile']['id'], str(self.u_2.id))
        self.assertEqual(data['profile']['roles'][0], 'admin')

    def test_remove_role_to_user(self):

        self.u_3.roles.append(self.r_admin)
        self.u_3.save()

        with self.client.session_transaction() as sess:
            sess['user_id'] = str(self.u_logger.id)
            sess['_fresh'] = True
        r = self.client.put('api/role')
        self.assertEqual(r.status_code, 302)

        with self.client.session_transaction() as sess:
            sess['user_id'] = str(self.u_1.id)
            sess['_fresh'] = True
        r = self.client.put('api/role')
        self.assertEqual(r.status_code, 302)

        with self.client.session_transaction() as sess:
            sess['user_id'] = str(self.u_admin.id)
            sess['_fresh'] = True

        # test required inputs
        r = self.client.put('api/role', content_type='application/json',
                            data=json.dumps({}))
        self.assertEqual(r.status_code, 400)

        # test 404 error
        r = self.client.put('api/role', content_type='application/json',
                            data=json.dumps({'id': str(self.u_1.id),
                                             'role': 'patate'}))
        self.assertEqual(r.status_code, 404)

        r = self.client.put('api/role', content_type='application/json',
                            data=json.dumps({'id': '000000000000000000000000',
                                             'role': 'logger'}))
        self.assertEqual(r.status_code, 404)

        # test removing admin to yourself
        r = self.client.put('api/role', content_type='application/json',
                            data=json.dumps({'id': str(self.u_admin.id),
                                             'role': 'admin'}))
        self.assertEqual(r.status_code, 400)

        # remove logger perm
        r = self.client.put('api/role', content_type='application/json',
                            data=json.dumps({'id': str(self.u_logger.id),
                                             'role': 'logger'}))
        self.assertEqual(r.status_code, 200)

        # test response
        data = json.loads(r.data.decode())
        self.assertTrue(len(data['profile']['roles']) == 0)
        self.assertEqual(data['profile']['id'], str(self.u_logger.id))

        # test db
        logger = User.objects.get(id=self.u_logger.id)
        self.assertTrue(self.r_logger not in logger.roles)
        self.assertTrue(self.r_admin not in logger.roles)

        # remove admin perm
        r = self.client.put('api/role', content_type='application/json',
                            data=json.dumps({'id': str(self.u_3.id),
                                             'role': 'admin'}))
        self.assertEqual(r.status_code, 200)
        data = json.loads(r.data.decode())
        self.assertTrue(len(data['profile']['roles']) == 0)
        self.assertEqual(data['profile']['id'], str(self.u_3.id))
