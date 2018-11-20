from flask import request, jsonify
from flask_restful import Resource, fields, marshal, marshal_with, abort
from flask_security import current_user, roles_accepted
from mongoengine.queryset import DoesNotExist

from datetime import datetime

from muzapi.models import *


class Album_res(Resource):

    user_fields = {
        'id': fields.String,
        'username': fields.String,
        'avatar': fields.String,
    }

    comment_fields = {
        'id': fields.String,
        'author': fields.Nested(user_fields),
        'message': fields.String,
        'creation_time': fields.DateTime(dt_format='iso8601'),

        'username': db.StringField(),
    }

    log_fields = {
        'id': fields.String,
        'author': fields.Nested(user_fields),
        'message': fields.String,
        'creation_time': fields.DateTime(dt_format='iso8601'),

        'recommended': fields.Boolean,
        'comments': fields.List(fields.Nested(comment_fields)),
    }

    album_base = {
        'id': fields.String,
        'artist': fields.String,
        'title': fields.String,
        'release_year': fields.Integer,
        'cover': fields.String
    }
    album = {
        'mbid': fields.String,
        'asin': fields.String,
        'label': fields.String,
        'release_date': fields.DateTime(dt_format='iso8601'),
        'logs': fields.List(fields.Nested(log_fields))
    }
    album.update(album_base)

    album_fields = {
        'album': fields.Nested(album)
    }
    albums_fields = {
        'albums': fields.List(fields.Nested(album_base))
    }

    def get(self, _id=None):
        '''
        Get ablum reviews

        :param_id: The _id of an Album object
        '''
        if (_id):
            album = Album.objects(id=_id)
            return marshal({'album': album[0]}, self.album_fields)
        else:
            albums = Album.objects()
            return marshal({'albums': albums}, self.albums_fields)

    def post(self, _id=None):
        try:
            x = request.get_json()
            album = Album()

            if 'mbid' in x and x['mbid'] != '':
                mbid_album = Album.objects(mbid=x['mbid'])
                if mbid_album:
                    return marshal({'album', mbid_album[0]}, self.album_fields)
                else:
                    album.mbid = x['mbid']

            if 'asin' in x and x['asin'] != '':
                asin_album = Album.objects(asin=x['asin'])
                if asin_album:
                    return marshal({'album': asin_album[0]}, self.album_fields)
                else:
                    album.asin = x['asin']

            if 'artist' in x and x['artist'] != '':
                album.artist = x['artist']
            elif 'artist-credit' in x:
                album.artist = 'Unknown'
                if len(x['artist-credit']) > 0:
                    if 'artist' in x['artist-credit'][0] and \
                       'name' in x['artist-credit'][0]['artist']:
                        album.artist = x['artist-credit'][0]['artist']['name']

            if 'label' in x and x['label'] != '':
                album.label = x['label']
            elif 'label-info' in x and len(x['label-info']) > 0:
                if 'label' in x['label-info'][0] and \
                   'name' in x['label-info'][0]['label']:
                    album.label = x['label-info'][0]['label']['name']

            if 'country' in x and x['country'] != '':
                album.country = x['country']

            if 'title' in x and x['title'] != '':
                album.title = x['title']

            if 'date' in x:
                date = datetime.strptime(x['date'], "%Y-%m-%d")
                album.release_date = date
                album.release_year = date.year
            elif 'release_date' in x and x['release_date'] != '':
                date = datetime.strptime(x['release_date'], "%d/%m/%Y")
                album.release_date = date
                album.release_year = date.year
            elif 'release_year' in x and x['release_year'] != '':
                album.release_year = x['release_year']

            album.save()

            return marshal({'album': album}, self.album_fields)

        except Exception as e:
            print(e)
            abort(400)
