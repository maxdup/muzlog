from muzapi import db, User
import unittest

from muzapi.util_fakedata import *
from muzapi.models import User, Role
from muzapi import create_app


class FakeTestCase(unittest.TestCase):

    def setUp(self):
        return

    def tearDown(self):
        return

    def test_fake_objects(self):
        app = create_app('config_test')
        with app.app_context():
            self.album = fake_album()
            self.album.save()
            self.album.reload()
            self.assertTrue(self.album.title)
            self.assertTrue(self.album.artist)
            self.assertTrue(self.album.release_date)

            self.user = fake_user()
            self.user.save()
            self.user.reload()
            self.assertTrue(self.user.password)
            self.assertTrue(self.user.username)
            self.assertTrue(self.user.email)
            self.assertTrue(self.user.bio)

            self.log = fake_log(self.user, self.album)
            self.log.save()
            self.log.reload()
            self.assertTrue(self.log.album)
            self.assertTrue(self.log.author)
            self.assertTrue(self.log.message)
            self.assertTrue(self.log.published_date)
