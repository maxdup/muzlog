from flask import request, jsonify
from flask_restful import Resource, fields, marshal, marshal_with, abort, reqparse
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
    log_album_render = {
        'log': fields.Nested(log_album_fields)
    }
    logs_album_render = {
        'logs': fields.List(fields.Nested(log_album_fields))
    }

    # PUT parser
    put_parser = reqparse.RequestParser()
    put_parser.add_argument('id',
                            required=True, help="album id is required")
    put_parser.add_argument('message',
                            required=True, help="message is required")
    put_parser.add_argument('published_date')
    put_parser.add_argument('published', type=bool)
    put_parser.add_argument('recommended', type=bool)

    # POST parser
    post_parser = put_parser.copy()
    post_parser.remove_argument('id')
    post_parser.add_argument('album',
                             required=True, help="album is required")
    post_parser.replace_argument('message',
                                 required=True, help="message is required")

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
    def post(self):

        # Create an ablum log

        content = self.post_parser.parse_args()
        try:
            album = Album.objects.get(id=content['album'])
            log = Log(album=album,
                      author=current_user.id,
                      recommended=content['recommended'],
                      published=content['published'],
                      message=content['message'])

            if content['published_date']:
                date = datetime.strptime(content['published_date'], "%d/%m/%Y")
                log.published_date = date
            elif content['published']:
                log.published_date = datetime.now()

            if log.published and not log.album.published:
                log.album.published = True
                log.album.published_by = current_user.id
                log.album.published_date = log.published_date

            if log.recommended and not log.album.recommended:
                log.album.recommended = log.recommended
                log.album.recommended_by = current_user.id

            log.save()
            log.reload()
            log.album.logs.append(log)
            log.album.save()

            return marshal({'log': log}, self.log_album_render)

        except (DoesNotExist):
            abort(404)
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
        content = self.put_parser.parse_args()
        try:
            log = Log.objects.get(id=content['id'])
        except DoesNotExist:
            abort(404)

        if not current_user.has_role('admin'):
            if log.author.id != current_user.id:
                abort(403)

        delta = DictDiffer(content, log.to_mongo()).changed()

        log.modify(**content)
        log.save()

        # mirror log changes in album
        if 'published' in delta:
            still_published = False
            for l in log.album.logs:
                if l.published == True:
                    still_published = True
                    log.album.published = True
                    log.album.published_by = l.author
                    log.album.published_date = datetime.now()
                    break
            if not still_published:
                log.album.published = False
                log.album.published_by = None
                log.album.published_date = None
            log.album.save()

        if 'recommended' in delta:
            still_recommended = False
            for l in log.album.logs:
                if l.recommended:
                    still_recommended = True
                    log.album.recommended = True
                    log.album.recommended_by = l.author
                    break

            if not still_recommended:
                log.album.recommended = False
                log.album.recommended_by = None
            log.album.save()

        return marshal({'log': log}, self.log_album_render)

    @login_required
    @roles_accepted('admin', 'logger')
    def delete(self, _id=None):  # delete room
        '''
        Delete an ablum log

        :param_id: The _id of a Log object to delete
        '''
        if not _id:
            abort(400)
        try:
            log = Log.objects.get(id=_id)
        except DoesNotExist:
            abort(404)

        if log.published:
            abort(400)

        log.album.logs = [l for l in log.album.logs if l.id != log.id]

        log.album.save()
        log.delete()

        return (204)
