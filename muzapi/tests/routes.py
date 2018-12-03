from muzapi import db, User
import unittest

from muzapi.util_fakedata import fake_user, fake_album
from muzapi.models import User, Role
from muzapi import create_app


class RoutesTestCase(unittest.TestCase):

    def setUp(self):
        app = create_app('config_test')

        with app.app_context():
            self.client = app.test_client()

            self.user = fake_user()
            self.user.save()
            self.user.reload()

            self.album = fake_album()
            self.album.save()
            self.album.reload()

    def tearDown(self):
        return

    def test_get_root_page(self):

        with self.client.session_transaction() as sess:
            sess['user_id'] = str(self.user.id)
            sess['_fresh'] = True

        r = self.client.get('')
        self.assertEqual(r.status_code, 200)

    def test_get_album_page(self):

        with self.client.session_transaction() as sess:
            sess['user_id'] = str(self.user.id)
            sess['_fresh'] = True

        r = self.client.get('album/' + str(self.album.id))
        self.assertEqual(r.status_code, 200)
