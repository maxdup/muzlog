from flask import request, jsonify
from flask_restful import Resource, fields, marshal, marshal_with, abort
from flask_security import current_user, roles_accepted
from mongoengine.queryset import DoesNotExist

from datetime import datetime

from muzapi.models import *


class Log_res(Resource):

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

    def get(self, _id=None):
        '''
        Get ablum reviews

        :param_id: The _id of an Album object
        '''
        if (_id):
            log = Log.objects(id=_id)
            return marshal({'log': log[0]}, self.log_render)
        else:
            abort(400)

    def post(self, _id=None):
        try:
            x = request.get_json()
            log = Log()

            #log.author = current_user.id

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

            log.save()
            log.reload()

            if 'album_id' in x and x['album_id'] != '':
                album = Album.objects.get(id=x['album_id'])
                album.logs.append(log)

                if not album.recommended and log.recommended:
                    album.recommended = log.recommended
                    #album.first_recommended_by = current_user.id

                if not album.published and log.published:
                    album.published = True
                    album.published_date = log.published_date

                album.save()

            return marshal({'log': log}, self.log_render)

        except Exception as e:
            print(e)
            abort(400)
