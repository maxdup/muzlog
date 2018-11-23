from flask import request, jsonify
from flask_restful import Resource, fields, marshal, marshal_with, abort
from flask_security import current_user, roles_accepted, login_required
from mongoengine.queryset import DoesNotExist

from datetime import datetime

from muzapi.util import DictDiffer
from muzapi.models import *
from muzapi.res_user import User_res


class Log_res(Resource):

    comment_fields = {
        'id': fields.String,
        'author': fields.Nested(User_res.user_fields),
        'message': fields.String,
        'creation_time': fields.DateTime(dt_format='iso8601'),

        'username': db.StringField(),
    }

    log_fields = {
        'id': fields.String,
        'author': fields.Nested(User_res.user_fields),
        'message': fields.String,
        'published': fields.Boolean,
        'published_date': fields.DateTime(dt_format='iso8601'),

        'recommended': fields.Boolean,
        'comments': fields.List(fields.Nested(comment_fields)),
    }

    log_render = {
        'log': fields.Nested(log_fields)
    }
    logs_render = {
        'logs': fields.List(fields.Nested(log_fields))
    }
    album_summary = {
        'id': fields.String,
        'artist': fields.String,
        'title': fields.String,
        'release_year': fields.Integer,
        'cover': fields.String,
        'thumb': fields.String,
    }
    log_album_fields = {
        'album': fields.Nested(album_summary)
    }
    log_album_fields.update(log_fields)
    logs_album_render = {
        'logs': fields.List(fields.Nested(log_album_fields))
    }

    def get(self, _id=None):
        '''
        Get a specific log

        :param_id: The _id of a Log object to get
        '''
        if (_id):
            log = Log.objects(id=_id)
            return marshal({'log': log[0]}, self.log_render)
        else:
            logs = Log.objects(author=current_user.id)
            return marshal({'logs': logs}, self.logs_album_render)

    @login_required
    @roles_accepted('admin', 'logger')
    def post(self, _id=None):
        '''
        Create an ablum log

        :param_id: (ignored)
        '''
        try:
            x = request.get_json()
            log = Log()

            log.author = current_user.id

            if 'message' in x and x['message'] != '':
                log.message = x['message']

            if 'recommended' in x and x['recommended'] != '':
                log.recommended = x['recommended']

            if 'published' in x and x['published'] != '':
                log.published = x['published']

            if 'published_date' in x and x['published_date'] != '':
                date = datetime.strptime(x['published_date'], "%d/%m/%Y")
                log.published_date = date
            else:
                log.published_date = datetime.now()

            if 'album_id' in x and x['album_id'] != '':
                album = Album.objects.get(id=x['album_id'])
                if album:
                    log.album = album
                    log.save()
                    log.reload()
                    album.logs.append(log)
                else:
                    abort(404)

                if not album.recommended and log.recommended:
                    album.recommended = log.recommended
                    album.recommended_by = log.author

                if not album.published and log.published:
                    album.published = True
                    album.published_by = log.author
                    album.published_date = log.published_date

                album.save()

            return marshal({'log': log}, self.log_render)

        except Exception as e:
            print(e)
            abort(400)

    @login_required
    @roles_accepted('admin', 'logger')
    def put(self, _id=None):
        '''
        Update an album log

        :param_id: The _id of a Log object to update
        '''
        if (_id):
            log = Log.objects.get(id=_id)
            if not log:
                abort(404)
        else:
            abort(400)

        content = request.get_json()

        if 'author' in content:
            del content['author']
        if 'comments' in content:
            del content['comments']

        delta = DictDiffer(content, log.to_mongo()).changed()

        log.modify(**content)

        if 'published' in delta or \
           'recommended' in delta:
            album = Album.objects.get(id=log.album_id)
            if not album:
                abort(400)

        if 'published' in delta:
            still_published = False
            for l in album.logs:
                if l.published == True:
                    still_published = True
                    album.published = True
                    album.published_by = l.author
                    album.published_date = datetime.now()
                    break
            if not still_published:
                album.published = False
                album.published_by = None
                album.published_date = None
            album.save()

        if 'recommended' in delta:
            still_recommended = False
            for l in album.logs:
                if l.recommended:
                    still_recommended = True
                    album.recommended = True
                    album.recommended_by = l.author
                    break

            if not still_recommended:
                album.recommended = False
                album.recommended_by = None
            album.save()

        log.save()

        return marshal({'log': log}, self.log_render)

    @login_required
    @roles_accepted('admin', 'logger')
    def delete(self, _id=None):  # delete room
        '''
        Delete an ablum log

        :param_id: The _id of a Log object to delete
        '''
        if (_id):
            log = Log.objects.get(id=_id)
            album = Album.objects.get(id=log.album_id)
            if not log or not album:
                abort(400)
        else:
            abort(400)

        if log.published:
            abort(400)

        album.logs = [l for l in album.logs if l.id != log.id]

        album.save()
        log.delete()

        return (204)
