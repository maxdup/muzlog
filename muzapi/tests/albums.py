import os
from muzapi import db, User
import unittest
import requests
import json

from muzapi import User, Role
from muzapi import create_app

from muzapi.fake_data import fake_user, fake_album, fake_log, fake_comment

from datetime import datetime


class AlbumsTestCase(unittest.TestCase):

    def setUp(self):
        app = create_app('config_test')
        with app.app_context():
            db.connection.drop_database(app.config['MONGODB_DB'])
            self.client = app.test_client

            self.user1 = fake_user()
            self.user1.save()

            self.album = fake_album(self.user1)
            self.album.save()

    def tearDown(self):
        return

    def test_get_albums(self):
        r = self.client().get('api/albums',
                              headers={'content-type': 'application/json'})
        data = json.loads(r.data.decode())
        self.assertEqual(len(data['albums']), 1)
        self.assertEqual(r.status_code, 200)
