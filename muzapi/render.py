from flask_restplus import fields
from muzapi.util_rest import *


user_fields = {
    'id': fields.String,
    'email': stringRestricted,

    'bio': fields.String,
    'username': fields.String,
    'color': fields.String,

    'avatar': fields.String,
    'thumb': fields.String,

    'roles': listRestricted(fields.String()),
}

users_render = {
    'profiles': fields.List(fields.Nested(user_fields))
}


comment_fields_base = {
    'id': fields.String,
    'author': fields.Nested(user_fields),
    'message': fields.String,
    'published_date': fields.String,
    'username': fields.String,
}

album_fields_base = {
    'id': fields.String,
    'title': fields.String,
    'artist': fields.String,
    'release_type': fields.String,
    'release_date': fields.String,
    'release_year': fields.String(attribute=lambda x: x.release_date.year
                                  if x and x.release_date else ''),
    'cover': fields.String,
    'thumb': fields.String,
}

log_fields_base = {
    'id': fields.String,
    'author': fields.Nested(user_fields),
    'message': fields.String,
    'published': fields.Boolean,
    'published_date': fields.String,
    'recommended': fields.Boolean,
    'comments': fields.List(fields.Nested(comment_fields_base)),
    'hits': fields.Integer,
}


album_fields = {
    'mbrgid': fields.String,
    'mbaid': fields.String,
    'label': fields.String,
    'country': fields.String,
    'country_code': fields.String,
    'logs': fields.List(fields.Nested(log_fields_base)),
}
album_fields.update(album_fields_base)

album_render = {
    'album': fields.Nested(album_fields)
}
albums_render = {
    'albums': fields.List(fields.Nested(album_fields_base))
}
log_album_render = {
    'album': fields.Nested(album_fields_base)
}
log_album_render.update(log_fields_base)

logs_album_render = {
    'logs': fields.List(fields.Nested(log_album_render))
}
