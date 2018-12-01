from flask import request, jsonify
from flask_restplus import Resource, fields, marshal, marshal_with, abort
from flask_security import current_user, roles_accepted, login_required
from mongoengine.queryset import DoesNotExist
from mongoengine.errors import ValidationError

from datetime import datetime

from muzapi.util import DictDiffer
from muzapi.util_rest import parse_request
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
        'published_date': fields.String,

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
    log_album_render = {
        'log': fields.Nested(log_album_fields)
    }
    logs_album_render = {
        'logs': fields.List(fields.Nested(log_album_fields))
    }

    def get(self, _id=None):
        '''
        Get a specific log

        :param_id: The _id of a Log object to get
        '''
        if (_id):
            try:
                log = Log.objects(id=_id)
            except (DoesNotExist, ValidationError):
                abort(404)
            return marshal({'log': log[0]}, self.log_render)
        else:
            logs = Log.objects(author=current_user.id)
            return marshal({'logs': logs}, self.logs_album_render)

    @login_required
    @roles_accepted('admin', 'logger')
    def post(self):

        # Create an album log

        post_args = {
            'album': {'required': True, 'help': "album is required"},
            'message': {'required': True, 'help': "message is required"},
            'published': {'type': bool, 'init': True}, 'published_date': {},
            'recommended': {'type': bool, 'init': True}}

        content = parse_request(request, post_args)

        try:
            content['album'] = Album.objects.get(id=content['album'])
            content['author'] = current_user.id

        except (DoesNotExist, ValidationError):
            abort(404)
        except:
            abort(406)

        log = Log(**content)
        log.save()
        log.reload()

        if log.published and not log.album.published_by:
            log.album.published_by = log
            log.album.published_date = log.published_date

        if log.recommended and not log.album.recommended_by:
            log.album.recommended_by = log.author

        log.album.logs.append(log)
        log.album.save()

        return marshal({'log': log}, self.log_album_render)

    @login_required
    @roles_accepted('admin', 'logger')
    def put(self, _id=None):
        '''
        Update an album log

        :param_id: The _id of a Log object to update
        '''

        put_args = {
            'id': {'required': True, 'help': 'album is is require'},
            'published': {'type': bool}, 'published_date': {},
            'recommended': {'type': bool}, 'message': {}}

        content = parse_request(request, put_args)

        try:
            log = Log.objects.get(id=content['id'])
        except (DoesNotExist, ValidationError):
            abort(404)

        if not current_user.has_role('admin'):
            if log.author.id != current_user.id:
                abort(403)

        delta = DictDiffer(content, log.to_mongo()).changed()

        log.modify(**content)
        log.save()
        log.reload()

        if 'published' in delta:
            if log.published:
                if not log.album.published_by or \
                   log.album.published_by == log:
                    log.album.published_by = log
                    log.album.published_date = log.published_date
            elif log.album.published_by == log:
                log.album.published_by = None
                log.album.published_date = None
                for l in log.album.logs:
                    if l.published:
                        log.album.published_by = l
                        log.album.published_date = l.published_date
                        break

        if 'published_date' in delta and log.album.published_by == log:
            log.album.published_date = log.published_date

        if 'recommended' in delta:
            if log.recommended:
                if not log.album.recommended_by:
                    log.album.recommended_by = log.author
            elif log.album.recommended_by == log:
                log.album.recommended_by = None
                for l in log.album.logs:
                    if l.recommended:
                        log.album.recommended_by = l.author
                        break

        log.album.save()
        return marshal({'log': log}, self.log_album_render)

    @login_required
    @roles_accepted('admin', 'logger')
    def delete(self, _id=None):  # delete room
        '''
        Delete an ablum log

        :param_id: The _id of a Log object to delete
        '''
        try:
            log = Log.objects.get(id=_id)
        except (DoesNotExist, ValidationError):
            abort(404)

        if log.published:
            abort(400)

        log.album.logs = [l for l in log.album.logs if l.id != log.id]

        log.album.save()
        log.delete()

        return (204)
