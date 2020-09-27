from flask import current_app as app
from flask_restx import Resource, fields, marshal, marshal_with, abort, Namespace
from flask_security import current_user, roles_accepted, login_required
from mongoengine.queryset import DoesNotExist
from mongoengine.errors import ValidationError

from datetime import datetime
import re

from muzapi.utils_brainz import *
from muzapi.utils_rest import RequestParser
from muzapi.models import *
from muzapi.render import *

album_api = Namespace('Albums', path='/album',
                      description="Album resource")

args = {
    'title': {}, 'artist': {}, 'country': {}, 'country_code': {},
    'release_type': {}, 'release_date': {}, 'label': {}, 'mbrgid': {}}
request_parser = RequestParser(arguments=args)


@album_api.route('/')
class Albums_res(Resource):

    @album_api.marshal_with(albums_render)
    def get(self, _id=None):
        '''Get Albums'''
        return {'albums': Album.objects(deleted=False)}

    @login_required
    @roles_accepted('admin', 'logger')
    @album_api.expect(request_parser)
    @album_api.marshal_with(album_render)
    def post(self, _id=None):
        '''Create an Album'''

        content = request_parser.parse_args()

        mbrgid = content.pop('mbrgid', None)
        if mbrgid:
            album = album_from_mb_release_group(mbrgid)
            if album.deleted:
                album.deleted = False
        else:
            album = Album(**content)

        try:
            album.save()
            album.reload()
        except ValidationError:
            abort(406)

        return {'album': album}


@album_api.route('/<string:_id>')
class Album_res(Resource):

    @album_api.marshal_with(album_render)
    def get(self, _id=None):
        '''Get a specific Album'''
        try:
            return {'album': Album.objects.get(id=_id)}
        except (DoesNotExist, ValidationError):
            abort(404)

    @login_required
    @roles_accepted('admin', 'logger')
    @album_api.expect(request_parser)
    @album_api.marshal_with(album_render)
    def put(self, _id=None):
        '''Update an Album'''

        content = request_parser.parse_args()

        try:
            album = Album.objects.get(id=_id)
        except (DoesNotExist, ValidationError):
            abort(404)

        mbrgid = content.pop('mbrgid', None)
        if mbrgid and mbrgid != album.mbrgid:
            album = album_from_mb_release_group(mbrgid, album)
            album.save()
            album.reload()
        elif content:
            try:
                album.modify(**content)
            except ValidationError:
                abort(406)

        return {'album': album}

    @login_required
    @roles_accepted('admin', 'logger')
    def delete(self, _id=None):
        '''Delete an Album'''

        try:
            album = Album.objects.get(id=_id)
        except (DoesNotExist, ValidationError):
            abort(404)

        if len(album.logs) > 0:
            abort(400)

        album.modify(**{'deleted': True})
        return ('', 204)
