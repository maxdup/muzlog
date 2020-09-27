from flask import request, jsonify
from flask_restx import Resource, fields, marshal, marshal_with, abort, Namespace
from flask_security import current_user, roles_accepted, login_required
from mongoengine.queryset import DoesNotExist
from mongoengine.errors import ValidationError

from datetime import datetime

from muzapi.utils_rest import RequestParser
from muzapi.models import *
from muzapi.render import logs_album_render, log_album_render

log_api = Namespace('Logs', path='/log',
                    description="Log resource")

post_args = {
    'album': {'required': True, 'help': "album is required"},
    'message': {'required': True, 'help': "message is required"},
    'published': {'type': bool}, 'recommended': {'type': bool},
    'published_date': {}
}
post_parser = RequestParser(arguments=post_args)

put_args = {
    'published': {'type': bool}, 'published_date': {},
    'recommended': {'type': bool}, 'message': {}}
put_parser = RequestParser(arguments=put_args)


@log_api.route('/')
class Logs_res(Resource):

    @log_api.marshal_with(logs_album_render)
    def get(self, _id=None):
        '''Get available logs'''
        return {'logs': Log.objects(published=True).order_by('-published_date')}

    @login_required
    @roles_accepted('admin', 'logger')
    @log_api.expect(post_parser)
    @log_api.marshal_with(log_album_render)
    def post(self, id=None):
        '''Create an album log'''

        content = post_parser.parse_args()

        try:
            content['album'] = Album.objects.get(id=content['album'])
            content['author'] = current_user.id
        except DoesNotExist:
            abort(404)

        log = Log(**content)

        try:
            log.save()
            log.reload()
            log.album.logs.append(log)
            log.album.save()
        except ValidationError:
            abort(406)

        return {'log': log}


@log_api.route('/me')
class myLogs_res(Resource):

    @login_required
    @roles_accepted('admin', 'logger')
    @log_api.marshal_with(logs_album_render)
    def get(self, _id=None):
        '''Get authenticated user's logs'''
        return {'logs': Log.objects(author=current_user.id).order_by(
            'published', '-published_date')}


@log_api.route('/<string:_id>')
class Log_res(Resource):

    @log_api.marshal_with(log_album_render)
    def get(self, _id=None):
        '''Get a specific log'''
        try:
            return {'log': Log.objects.get(id=_id)}
        except (DoesNotExist, ValidationError):
            abort(404)

    @login_required
    @roles_accepted('admin', 'logger')
    @log_api.expect(put_parser)
    @log_api.marshal_with(log_album_render)
    def put(self, _id=None):
        '''Update an album log'''
        content = put_parser.parse_args()

        try:
            log = Log.objects.get(id=_id)
        except (DoesNotExist, ValidationError):
            abort(404)

        if not current_user.has_role('admin'):
            if log.author.id != current_user.id:
                abort(403)

        if content:
            try:
                log.update(**content)
                log.save()
                log.reload()
            except ValidationError:
                abort(406)

        return {'log': log}

    @login_required
    @roles_accepted('admin', 'logger')
    def delete(self, _id=None):  # delete room
        '''Delete an ablum log'''
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
