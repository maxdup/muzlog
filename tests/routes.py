import pytest
from muzapi import db
from utils_faker import *
from utils_auth import *


@pytest.fixture
def album():
    album = fake_album()
    album.save()
    album.reload()
    yield album


def test_get_root_page(client):
    assert client.get('').status_code == 200


def test_get_album_page(client, album):
    assert client.get('album/' + str(album.id)).status_code == 200


def test_get_cms_page(client, album):
    assert client.get('cms/' + str(album.id)) == 302
    auth(client, make_user(role='admin'))
    assert client.get('cms/' + str(album.id)) == 200
