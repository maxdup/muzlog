from flask import current_app as app, Blueprint, request, jsonify
from flask_restful import Resource, fields, marshal, marshal_with, abort
from flask_security import current_user, roles_accepted
from mongoengine.queryset import DoesNotExist

import os
import uuid
import requests
import urllib.request
from datetime import datetime

from muzapi.util import DictDiffer
from muzapi.models import *
from muzapi.log import Log_res

muzlog_upload = Blueprint('muzlog_upload', __name__)


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
        Get Ablums

        :param_id: The _id of an Album object
        '''
        if (_id):
            album = Album.objects(id=_id)
            return marshal({'album': album[0]}, self.album_render)
        else:
            albums = Album.objects(deleted=False)
            return marshal({'albums': albums}, self.albums_render)

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

        # Manually update release date
        if 'release_date' in delta:
            date = datetime.strptime(content['release_date'], "%d/%m/%Y")
            content['release_date'] = date
            content['release_year'] = date.year

        # Automatically save everything else
        album.modify(**content)
        album.save()

        return marshal({'album': album}, self.album_render)

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


def downloadBrainzCover(mbid):
    thumb_url = 'http://coverartarchive.org/release/' + mbid + '/front-250.jpg'
    cover_url = 'http://coverartarchive.org/release/' + mbid + '/front-1200.jpg'
    thumb_filename = mbid + '-thumb.jpg'
    cover_filename = mbid + '-cover.jpg'
    r = requests.get(thumb_url)
    urllib.request.urlretrieve(
        thumb_url, app.config['UPLOAD_FOLDER'] + thumb_filename)
    urllib.request.urlretrieve(
        cover_url, app.config['UPLOAD_FOLDER'] + cover_filename)

    return {'thumb': thumb_filename, 'cover': cover_filename}


@muzlog_upload.route('/upload_album_cover/<_id>', methods=['POST'])
# @auth_required
def upload_cover(_id=None):
    '''
    Upload an Album cover

    :param_id: The _id of an Album object to add a cover to
    '''
    if (_id):
        album = Album.objects.get(id=_id)
        if not album:
            abort(404)
    else:
        abort(400)

    if 'file' not in request.files:
        return 406

    cover = request.files['file']
    if cover.filename == '':
        return 406

    file_id = str(uuid.uuid4())
    cover_filename = file_id + '-cover.jpg'

    # Save file locally
    try:
        cover.save(os.path.join(app.config['UPLOAD_FOLDER'], cover_filename))
        cover.stream.seek(0)

        album.cover = cover_filename
        # todo: thumbnail resize
        album.thumb = cover_filename

        album.save()
    except Exception as e:
        print(e)
        abort(500)

    return (cover_filename, 200)
