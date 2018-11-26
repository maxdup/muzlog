from flask import current_app as app, request
from flask_restful import Resource, fields, marshal, marshal_with, abort, reqparse
from flask_security import current_user, roles_accepted, login_required
from mongoengine.queryset import DoesNotExist
from mongoengine.errors import ValidationError

from datetime import datetime
import re

from muzapi.util import DictDiffer
from muzapi.util_brainz import downloadBrainzCover
from muzapi.models import *
from muzapi.res_log import Log_res


class Album_res(Resource):

    album_fields_base = {
        'id': fields.String,
        'artist': fields.String,
        'title': fields.String,
        'release_year': fields.String(attribute=lambda x: x.release_date.year
                                      if x.release_date else ''),
        'published': fields.Boolean,
        'published_date': fields.DateTime(dt_format='iso8601'),
        'published_by_username': fields.String(
            attribute=lambda x: x.published_by.username
            if x.published_by and 'username' in x.published_by else ''),
        'cover': fields.String,
        'thumb': fields.String,
    }

    album_fields = {
        'mbid': fields.String,
        'asin': fields.String,
        'label': fields.String,
        'country': fields.String,
        'release_date': fields.DateTime(dt_format='iso8601'),
        'logs': fields.List(fields.Nested(Log_res.log_fields)),
    }
    album_fields.update(album_fields_base)

    album_render = {
        'album': fields.Nested(album_fields)
    }
    albums_render = {
        'albums': fields.List(fields.Nested(album_fields_base))
    }

    # POST parser
    post_parser = reqparse.RequestParser()
    post_parser.add_argument('mbid')
    post_parser.add_argument('asin')
    post_parser.add_argument('title')
    post_parser.add_argument('artist')
    post_parser.add_argument('country')
    post_parser.add_argument('label')
    post_parser.add_argument('release_date')
    post_parser.add_argument('release_year')

    post_parser.add_argument('date')
    post_parser.add_argument('label-info', default=[])
    post_parser.add_argument('artist-credit', default=[])

    # PUT parser
    put_parser = post_parser.copy()
    put_parser.remove_argument('date')
    put_parser.remove_argument('label-info')
    put_parser.remove_argument('artist-credit')
    put_parser.add_argument('id', required=True,
                            help="album id is required")

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
            return marshal({'album': album}, self.album_render)
        else:
            albums = Album.objects(deleted=False).order_by(
                'published', '-published_date')
            return marshal({'albums': albums}, self.albums_render)

    @login_required
    @roles_accepted('admin', 'logger')
    def post(self, _id=None):
        '''
        Create an Album

        :param_id: (ignored)
        '''

        content = self.post_parser.parse_args()

        album = Album(artist=content['artist'],
                      title=content['title'],
                      label=content['label'],
                      country=content['country'],
                      release_date=content['release_date'])

        if content['asin']:
            try:
                asin_album = Album.objects.get(asin=content['asin'])
                return marshal({'album', asin_album}, self.album_render)
            except (DoesNotExist, ValidationError):
                album.asin = content['asin']

        if content['mbid']:
            try:
                mbid_album = Album.objects.get(mbid=content['mbid'])
                return marshal({'album', mbid_album}, self.album_render)
            except (DoesNotExist, ValidationError):
                album.mbid = content['mbid']
                covers = downloadBrainzCover(album.mbid)
                album.cover = covers['cover']
                album.thumb = covers['thumb']

        if content['date']:
            year_re = re.compile('^[0-9]{4}$')
            date_re = re.compile('^[0-9]{4}-[0-9]{2}-[0-9]{2}$')

            if year_re.match(content['date']):
                album.release_year = content['date']
            elif date_re.match(content['date']):
                date = datetime.strptime(content['date'], "%Y-%m-%d")
                album.release_date = date

        if album.release_date:
            album.release_year = album.release_date.year
        elif content['release_year'] and \
                year_re.match(content['release_year']):
            album.release_year = content['release_year']

        if content['artist-credit']:
            if 'artist' in content['artist-credit'][0] and \
               'name' in content['artist-credit'][0]['artist']:
                album.artist = content['artist-credit'][0]['artist']['name']

        if content['label-info']:
            if 'label' in content['label-info'][0] and \
               'name' in content['label-info'][0]['label']:
                album.label = content['label-info'][0]['label']['name']

        album.save()
        return marshal({'album': album}, self.album_render)

    @login_required
    @roles_accepted('admin', 'logger')
    def put(self, _id=None):

        # Update an Album

        content = self.put_parser.parse_args()

        try:
            album = Album.objects.get(id=content['id'])
        except DoesNotExist:
            abort(404)

        # don't interfere with 'sparse' fields
        if not content['mbid']:
            del content['mbid']
        if not content['asin']:
            del content['asin']

        delta = DictDiffer(content, album.to_mongo()).changed()

        album.modify(**content)

        if 'release_date' in delta and content['release_date']:
            album.release_year = album.release_date.year

        album.save()

        return marshal({'album': album}, self.album_render)

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

        album.deleted = True
        album.save()
        return (204)
