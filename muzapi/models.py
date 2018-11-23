from flask_security import UserMixin, RoleMixin
from flask_security.core import _security
from datetime import datetime
from . import db


class Role(db.Document, RoleMixin):
    name = db.StringField(max_length=80, nullable=False, unique=True)
    description = db.StringField(max_length=255)

    def __str__(self):
        return self.name

    def __repr__(self):
        return '<Role %r>' % self.name


class UserProfile(db.EmbeddedDocument):
    username = db.StringField(max_length=75, nullable=False)
    bio = db.StringField(max_length=400, nullable=True)
    color = db.StringField(min_length=7, max_length=7, nullable=True)
    avatar = db.StringField(default="")
    thumb = db.StringField(default="")


class User(db.Document, UserMixin):
    email = db.EmailField(max_length=255, nullable=False,
                          unique=True, sparse=True)
    password = db.StringField(max_length=255, nullable=False)

    profile = db.EmbeddedDocumentField(UserProfile, default=UserProfile)

    # handled by flask-security
    active = db.BooleanField(default=True)
    confirmed_at = db.DateTimeField()
    last_login_at = db.DateTimeField()
    current_login_at = db.DateTimeField()
    last_login_ip = db.StringField(max_length=45)
    current_login_ip = db.StringField(max_length=45)
    login_count = db.IntField()

    roles = db.ListField(db.ReferenceField(Role), default=[])

    def __repr__(self):
        return '<User %r>' % self.id


class Message(db.Document):
    author = db.ReferenceField(User, nullable=False)
    message = db.StringField(Required=True)

    published_date = db.DateTimeField(default=datetime.now())
    published = db.BooleanField(default=False)

    meta = {'allow_inheritance': True}


class Album(db.Document):
    mbid = db.StringField(max_length=255, unique=True, sparse=True)
    asin = db.StringField(max_length=255, unique=True, sparse=True)

    artist = db.StringField(required=True)
    title = db.StringField(required=True)

    label = db.StringField()
    country = db.StringField()
    release_year = db.IntField()
    release_date = db.DateTimeField()

    cover = db.StringField()
    thumb = db.StringField()

    logs = db.ListField(db.ReferenceField(Message))

    recommended = db.BooleanField(default=False)
    recommended_by = db.ReferenceField(User, nullable=True)
    published = db.BooleanField(default=False)
    published_by = db.ReferenceField(User, nullable=True)
    published_date = db.DateTimeField()

    deleted = db.BooleanField(default=False)


class Comment(db.EmbeddedDocument):
    author = db.ReferenceField(User, nullable=False)
    message = db.StringField(Required=True)

    published_date = db.DateTimeField(default=datetime.now())
    published = db.BooleanField(default=False)
    user_name = db.StringField()


class Log(Message):
    album = db.ReferenceField(Album, nullable=False)
    recommended = db.BooleanField(default=False)
    recommended_by = db.ReferenceField(Album, nullable=True)

    comments = db.ListField(db.EmbeddedDocumentField(Comment, default=Comment))
