from flask import current_app as app
from flask_restplus import Resource, fields, marshal, marshal_with, abort, Namespace
from flask_security import current_user, roles_accepted, login_required
from mongoengine.queryset import DoesNotExist
from mongoengine.errors import ValidationError

from datetime import datetime
import re

from muzapi.util_brainz import *
from muzapi.util_rest import parse_request
from muzapi.models import *
from muzapi.render import *

album_api = Namespace('Albums', path='/album',
                      description="Album resource")


@album_api.route('/', '/<string:_id>')
class Album_res(Resource):

    def get(self, _id=None):
        '''
        Get Albums

        :param_id: The _id of an Album object
        '''
        if (_id):
            try:
                album = Album.objects.get(id=_id)
            except (DoesNotExist, ValidationError):
                abort(404)
            return marshal(album, album_fields, envelope='album')
        else:
            albums = Album.objects(deleted=False)
            return marshal({'albums': albums}, albums_render)

    @login_required
    @roles_accepted('admin', 'logger')
    @marshal_with(album_fields, envelope="album")
    def post(self, _id=None):
        '''
        Create an Album

        :param_id: (ignored)
        '''

        post_args = {
            'title': {}, 'artist': {}, 'country': {}, 'country_code': {},
            'release_type': {}, 'release_date': {}, 'label': {}, 'mbrgid': {}
        }

        content = parse_request(post_args)

        if 'mbrgid' in content:
            album = album_from_mb_release_group(content['mbrgid'])
            if album.deleted:
                album.deleted = False
        else:
            album = Album(**content)

        try:
            album.save()
            album.reload()
        except ValidationError:
            abort(406)

        return album

    @login_required
    @roles_accepted('admin', 'logger')
    @marshal_with(album_fields, envelope="album")
    def put(self, _id=None):

        # Update an Album
        put_args = {
            'id': {'required': True, 'help': "Album id is required"},
            'title': {}, 'artist': {}, 'country': {}, 'country_code': {},
            'release_type': {}, 'release_date': {}, 'label': {}, 'mbrgid': {}
        }

        content = parse_request(put_args)
        try:
            album = Album.objects.get(id=content['id'])
        except (DoesNotExist, ValidationError):
            abort(404)

        if 'mbrgid' in content and content['mbrgid'] and content['mbrgid'] != album.mbrgid:
            album = album_from_mb_release_group(content['mbrgid'], album)
            album.save()
            album.reload()
        else:
            album.modify(**content)

        return album

    @login_required
    @roles_accepted('admin', 'logger')
    def delete(self, _id=None):
        '''
        Delete an Album

        :param_id: The id of an Album object to delete
        '''
        try:
            album = Album.objects.get(id=_id)
        except (DoesNotExist, ValidationError):
            abort(404)

        if len(album.logs) > 0:
            abort(400)

        album.modify(**{'deleted': True})
        return ('', 204)
