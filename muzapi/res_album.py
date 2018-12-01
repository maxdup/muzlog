from flask import current_app as app
from flask_restplus import Resource, fields, marshal, marshal_with, abort
from flask_security import current_user, roles_accepted, login_required
from mongoengine.queryset import DoesNotExist
from mongoengine.errors import ValidationError

from datetime import datetime
import re

from muzapi.util import DictDiffer
from muzapi.util_rest import *
from muzapi.util_brainz import *
from muzapi.models import *
from muzapi.res_log import Log_res
from muzapi.res_user import User_res


class Album_res(Resource):

    album_fields_base = {
        'id': fields.String,
        'title': fields.String,
        'artist': fields.String,
        'release_type': fields.String,
        'release_date': fields.String,
        'release_year': fields.String(attribute=lambda x: x.release_date.year
                                      if x.release_date else ''),
        'published': fields.Boolean(attribute=lambda x: True
                                    if x.published_by else False),
        'published_date': fields.String,
        'published_by_username': fields.String(
            attribute=lambda x: x.published_by.author.username
            if x.published_by else ''),
        'recommended_by_username': fields.String(
            attribute=lambda x: x.recommended_by.username
            if x.recommended_by else None),
        'recommended_by_color': fields.String(
            attribute=lambda x: x.recommended_by.color
            if x.recommended_by else None),
        'cover': fields.String,
        'thumb': fields.String,
    }

    album_fields = {
        'mbrgid': fields.String,
        'mbaid': fields.String,
        'label': fields.String,
        'country': fields.String,
        'country_code': fields.String,
        'logs': fields.List(fields.Nested(Log_res.log_fields)),
        'published_by': fields.Nested(Log_res.log_fields),
        'recommended_by': fields.Nested(User_res.user_fields),
    }
    album_fields.update(album_fields_base)

    album_render = {
        'album': fields.Nested(album_fields)
    }
    albums_render = {
        'albums': fields.List(fields.Nested(album_fields_base))
    }

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
            return marshal(album, self.album_fields, envelope='album')
        else:
            albums = Album.objects(deleted=False).order_by('-published_date')
            return marshal({'albums': albums}, self.albums_render)

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

        delta = DictDiffer(content, album.to_mongo()).changed()
        added = DictDiffer(content, album.to_mongo()).added()

        album.modify(**content)

        if 'release_date' in delta and content['release_date']:
            album.release_year = album.release_date.year

        if ('mbrgid' in delta or 'mbrgid' in added) and content['mbrgid']:
            album = album_from_mb_release_group(content['mbrgid'], album)

        album.save()
        album.reload()

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

        album.deleted = True
        album.save()
        return (200)
