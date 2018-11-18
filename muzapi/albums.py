from flask import request, jsonify
from flask_restful import Resource, fields, marshal_with, abort
from flask_security import current_user, roles_accepted
from mongoengine.queryset import DoesNotExist

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

    album_fields = {
        'id': fields.String,
        'artist': fields.String,
        'title': fields.String,
        'release_year': fields.Integer,

        'logs': fields.List(fields.Nested(log_fields))
    }
    albums_fields = {
        'albums': fields.List(fields.Nested(album_fields))
    }

    @marshal_with(albums_fields)
    def get(self, _id=None):
        '''
        Get ablum reviews

        :param_id: The _id of an Album object
        '''
        albums = Album.objects()
        return {'albums': albums}
