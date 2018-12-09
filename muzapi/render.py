from flask_restplus import Resource, fields, marshal, marshal_with, abort, Namespace
from muzapi.util_rest import *

render_api = Namespace('Models', description="resoruce renders")

base_user = render_api.model('Base User fields', {
    'id': fields.String,
    'email': stringRestricted,

    'bio': fields.String,
    'username': fields.String,
    'color': fields.String,

    'avatar': fields.String,
    'thumb': fields.String,

    'roles': listRestricted(fields.String()),
})
base_comment = render_api.model('Base Comment', {
    'id': fields.String,
    'author': fields.Nested(base_user),
    'message': fields.String,
    'published_date': fields.String,
    'username': fields.String,
})
base_log = render_api.model('Base Log fields', {
    'id': fields.String,
    'author': fields.Nested(base_user),
    'message': fields.String,
    'published': fields.Boolean,
    'published_date': fields.String,
    'recommended': fields.Boolean,
    'comments': fields.List(fields.Nested(base_comment)),
    'hits': fields.Integer,
})
base_album = render_api.model('Base Album', {
    'id': fields.String,
    'title': fields.String,
    'artist': fields.String,
    'release_type': fields.String,
    'release_date': fields.String,
    'release_year': fields.String(attribute=lambda x: x.release_date.year
                                  if x and x.release_date else ''),
    'cover': fields.String,
    'thumb': fields.String,
})
base_album_logs = render_api.inherit('Base Album with logs', base_album, {
    'mbrgid': fields.String,
    'mbaid': fields.String,
    'label': fields.String,
    'country': fields.String,
    'country_code': fields.String,
    'logs': fields.List(fields.Nested(base_log))
})
base_log_album = render_api.inherit('Base Log Album fields', base_log, {
    'album': fields.Nested(base_album)})

user_render = render_api.model('User Resource', {
    'profile': fields.Nested(base_user)})
users_render = render_api.model('Users Resource', {
    'profiles': fields.List(fields.Nested(base_user))})
log_album_render = render_api.model('Log Resource', {
    'log': fields.Nested(base_log_album)})
logs_album_render = render_api.model('Logs Resource', {
    'logs': fields.List(fields.Nested(base_log_album))})
album_render = render_api.model('Album Resource', {
    'album': fields.Nested(base_album_logs)})
albums_render = render_api.model('Albums Resource', {
    'albums': fields.List(fields.Nested(base_album))})
