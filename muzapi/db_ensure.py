from flask_security import hash_password
from flask import current_app as app

from muzapi import user_datastore
from muzapi.models import Role, User


def db_ensure_roles(app):

    @app.before_first_request
    def ensure_roles():
        admin = user_datastore.find_or_create_role(
            'admin', description="includes all permissions")
        logger = user_datastore.find_or_create_role(
            'logger', description="common poster")
        password = hash_password(app.config['ADMIN_DEFAULT_PASSWORD'])


def db_ensure_admin(app):
    @app.before_first_request
    def ensure_admin():
        try:
            User.objects.get(email="admin@muzlog.com")
        except:
            user_datastore.create_user(email="admin@muzlog.com",
                                       password=password,
                                       roles=[admin])
