from flask import request, jsonify
from flask_restplus import Resource, fields, marshal, marshal_with, abort
from flask_security import current_user, roles_accepted, login_required
from mongoengine.queryset import DoesNotExist
from mongoengine.errors import ValidationError

from datetime import datetime

from muzapi.util_rest import parse_request
from muzapi.models import *
from muzapi.render import *


class Log_res(Resource):

    def get(self, _id=None):
        '''
        Get a specific log

        :param_id: The _id of a Log object to get
        '''
        if _id == 'me':
            if not current_user.has_role('logger') and \
               not current_user.has_role('admin'):
                abort(403)
            logs = Log.objects(author=current_user.id).order_by(
                'published', '-published_date')
            return marshal({'logs': logs}, logs_album_render)
        elif _id:
            try:
                log = Log.objects.get(id=_id)
                return marshal(log, log_album_render, envelope="log")
            except (DoesNotExist, ValidationError):
                abort(404)
        else:
            logs = Log.objects(published=True).order_by('-published_date')
            return marshal({'logs': logs}, logs_album_render)

    @login_required
    @roles_accepted('admin', 'logger')
    @marshal_with(log_album_render, envelope="log")
    def post(self, id=None):

        # Create an album log

        post_args = {
            'album': {'required': True, 'help': "album is required"},
            'message': {'required': True, 'help': "message is required"},
            'published': {'type': bool, 'init': True}, 'published_date': {},
            'recommended': {'type': bool, 'init': True}}

        content = parse_request(post_args)

        try:
            content['album'] = Album.objects.get(id=content['album'])
            content['author'] = current_user.id
        except (DoesNotExist, ValidationError):
            abort(404)

        log = Log(**content)
        log.save()
        log.reload()

        return log

    @login_required
    @roles_accepted('admin', 'logger')
    @marshal_with(log_album_render, envelope="log")
    def put(self, _id=None):
        '''
        Update an album log

        :param_id: The _id of a Log object to update
        '''

        put_args = {
            'id': {'required': True, 'help': 'album is is require'},
            'published': {'type': bool}, 'published_date': {},
            'recommended': {'type': bool}, 'message': {}}

        content = parse_request(put_args)

        try:
            log = Log.objects.get(id=content['id'])
        except (DoesNotExist, ValidationError):
            abort(404)

        if not current_user.has_role('admin'):
            if log.author.id != current_user.id:
                abort(403)

        log.modify(**content)
        log.save()
        log.reload()

        return log

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

        if not current_user.has_role('admin') and \
           str(log.author.id) != str(current_user.id):
            abort(403)

        if log.published:
            abort(400)

        log.album.logs = [l for l in log.album.logs if l.id != log.id]

        log.album.save()
        log.delete()

        return ('', 204)
