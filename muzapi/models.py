from flask_security import UserMixin, RoleMixin
from flask_security.core import _security
from datetime import datetime
from . import db
import re


class Role(db.Document, RoleMixin):
    name = db.StringField(max_length=80, nullable=False, unique=True)
    description = db.StringField(max_length=255)

    def __str__(self):
        return self.name


class User(db.Document, UserMixin):
    email = db.EmailField(max_length=255, nullable=False, unique=True)
    password = db.StringField(max_length=255, nullable=False)

    username = db.StringField(max_length=75, nullable=False)
    bio = db.StringField(max_length=400, nullable=True)
    re_color = re.compile('^#[A-Fa-f0-9]{6}$|^#[A-Fa-f0-9]{3}$')
    color = db.StringField(regex=re_color)

    avatar = db.StringField(default="")
    thumb = db.StringField(default="")

    # handled by flask-security
    active = db.BooleanField(default=True)
    confirmed_at = db.DateTimeField()
    last_login_at = db.DateTimeField()
    current_login_at = db.DateTimeField()
    last_login_ip = db.StringField(max_length=45)
    current_login_ip = db.StringField(max_length=45)
    login_count = db.IntField()

    roles = db.ListField(db.ReferenceField(Role), default=[])


class Message(db.Document):
    author = db.ReferenceField(User, nullable=False)
    message = db.StringField(Required=True)

    published_date = db.DateField(default=datetime.now())
    published = db.BooleanField(default=False)

    meta = {'allow_inheritance': True}


class Product(db.EmbeddedDocument):
    mbrid = db.StringField(required=True)
    asin = db.StringField(required=True)
    country = db.StringField()
    medium = db.StringField()


class Album(db.Document):

    mbrgid = db.StringField(min_length=36, max_length=36,
                            unique=True, sparse=True)
    mbaid = db.StringField(max_length=255)

    products = db.ListField(db.EmbeddedDocumentField(Product))

    title = db.StringField(required=True, nullable=False)
    artist = db.StringField(required=True, nullable=False)

    label = db.StringField()
    release_date = db.DateField()
    release_type = db.StringField()  # have that be a choice?
    country_code = db.StringField()
    country = db.StringField()

    cover = db.StringField()
    thumb = db.StringField()

    logs = db.ListField(db.ReferenceField(Message))

    deleted = db.BooleanField(default=False)


class Comment(db.EmbeddedDocument):
    author = db.ReferenceField(User, nullable=False)
    message = db.StringField(Required=True)

    published_date = db.DateTimeField(default=datetime.now())
    published = db.BooleanField(default=False)
    user_name = db.StringField()


class Log(Message):
    album = db.ReferenceField(Album, required=True, nullable=False)
    recommended = db.BooleanField(default=False)
    comments = db.ListField(db.EmbeddedDocumentField(Comment, default=Comment))
