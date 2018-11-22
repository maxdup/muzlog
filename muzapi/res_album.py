from flask import current_app as app, request
from flask_restful import Resource, fields, marshal, marshal_with, abort
from flask_security import current_user, roles_accepted, login_required
from mongoengine.queryset import DoesNotExist

from datetime import datetime
import re

from muzapi.util import DictDiffer
from muzapi.bp_files import downloadBrainzCover
from muzapi.models import *
from muzapi.res_log import Log_res


class Album_res(Resource):

    album_fields_base = {
        'id': fields.String,
        'artist': fields.String,
        'title': fields.String,
        'release_year': fields.Integer,
        'cover': fields.String,
        'thumb': fields.String,
    }

    album_fields = {
        'mbid': fields.String,
        'asin': fields.String,
        'label': fields.String,
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

    def get(self, _id=None):
        '''
        Get Albums

        :param_id: The _id of an Album object
        '''
        if (_id):
            album = Album.objects.get(id=_id)
            return marshal({'album': album}, self.album_render)
        else:
            albums = Album.objects(deleted=False)
            return marshal({'albums': albums}, self.albums_render)

    @login_required
    @roles_accepted('logger', 'admin')
    def post(self, _id=None):
        '''
        Create an Album

        :param_id: (ignored)
        '''
        try:
            x = request.get_json()
            album = Album()

            if 'mbid' in x and x['mbid']:
                mbid_album = Album.objects(mbid=x['mbid'])
                if mbid_album:
                    return marshal({'album', mbid_album[0]}, self.album_render)
                else:
                    album.mbid = x['mbid']

            if 'asin' in x and x['asin']:
                asin_album = Album.objects(asin=x['asin'])
                if asin_album:
                    return marshal({'album': asin_album[0]}, self.album_render)
                else:
                    album.asin = x['asin']

            if 'artist' in x and x['artist']:
                album.artist = x['artist']
            elif 'artist-credit' in x:
                album.artist = 'Unknown'
                if len(x['artist-credit']) > 0:
                    if 'artist' in x['artist-credit'][0] and \
                       'name' in x['artist-credit'][0]['artist']:
                        album.artist = x['artist-credit'][0]['artist']['name']

            if 'label' in x and x['label']:
                album.label = x['label']
            elif 'label-info' in x and len(x['label-info']) > 0:
                if 'label' in x['label-info'][0] and \
                   'name' in x['label-info'][0]['label']:
                    album.label = x['label-info'][0]['label']['name']

            if 'country' in x and x['country']:
                album.country = x['country']

            if 'title' in x and x['title']:
                album.title = x['title']

            if 'date' in x:
                year_re = re.compile('^[0-9]{4}$')
                date_re = re.compile('^[0-9]{4}-[0-9]{2}-[0-9]{2}$')

                if year_re.match(x['date']):
                    album.release_year = x['date']
                elif date_re.match(x['date']):
                    date = datetime.strptime(x['date'], "%Y-%m-%d")
                    album.release_date = date
                    album.release_year = date.year

            elif 'release_date' in x and x['release_date']:
                date = datetime.strptime(x['release_date'], "%d/%m/%Y")
                album.release_date = date
                album.release_year = date.year
            elif 'release_year' in x and x['release_year']:
                album.release_year = x['release_year']

            if album.mbid:
                covers = downloadBrainzCover(album.mbid)
                album.cover = covers['cover']
                album.thumb = covers['thumb']

            album.save()
            return marshal({'album': album}, self.album_render)

        except Exception as e:
            print(e)
            abort(400)

    @login_required
    @roles_accepted('logger', 'admin')
    def put(self, _id=None):
        '''
        Update an Album

        :param_id: The _id of an Album object to update
        '''
        if (_id):
            album = Album.objects.get(id=_id)
            if not album:
                abort(404)
        else:
            abort(400)

        content = request.get_json()

        # Don't interfere with reference fields
        if 'logs' in content:
            del content['logs']
        if 'recommended' in content:
            del content['recommended']
        if 'recommended_by' in content:
            del content['recommended_by']
        if 'published' in content:
            del content['published']
        if 'published_by' in content:
            del content['published_by']
        if 'published_date' in content:
            del content['published_date']
        if 'mbid' in content and not content['mbid']:
            del content['mbid']
        if 'asin' in content and not content['asin']:
            del content['asin']

        delta = DictDiffer(content, album.to_mongo()).changed()

        # Automatically save every other fields
        album.modify(**content)

        # Manually update release year if needed
        if 'release_date' in delta and content['release_date']:
            album.release_year = album.release_date.year

        album.save()

        return marshal({'album': album}, self.album_render)

    @login_required
    @roles_accepted('logger', 'admin')
    def delete(self, _id=None):
        '''
        Update an Album

        :param_id: The _id of an Album object to update
        '''
        if (_id):
            album = Album.objects.get(id=_id)
            if not album:
                abort(404)
        else:
            abort(400)

        album.deleted = True
        album.save()
        return (204)