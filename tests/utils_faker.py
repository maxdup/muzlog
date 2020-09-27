from muzapi import user_datastore
from muzapi.models import *
from flask_security.utils import hash_password
from faker import Faker

# FAKE it till you MAKE it
fake = Faker()


def fake_user(**kwargs):
    role = kwargs.pop('role', None)
    user = User(email=kwargs.pop('email', fake.email()),
                username=kwargs.pop('username', fake.name()),
                bio=kwargs.pop('bio', fake.text(max_nb_chars=200)),
                password=hash_password(kwargs.pop('password', 'password')),
                **kwargs)
    if role:
        user_datastore.add_role_to_user(user, role)
    return user


def make_user(**kwargs):
    user = fake_user(**kwargs)
    user.save()
    user.reload()
    return user


def fake_log(**kwargs):
    message = kwargs.pop('message', fake.text(max_nb_chars=200))
    published_date = kwargs.pop(
        'published_date', fake.date_this_year(before_today=True))
    recommended = kwargs.pop(
        'recommended', (fake.random_int(min=0, max=10) == 6))
    log = Log(message=message,
              published_date=published_date,
              recommended=recommended,
              **kwargs)
    return log


def make_log(**kwargs):
    log = fake_log(**kwargs)
    log.save()
    log.reload()
    return log


def fake_album(**kwargs):
    log = kwargs.pop('log', None)
    logs = kwargs.pop('logs', None)
    release_date = kwargs.pop(
        'release_date', fake.date_this_century(before_today=True))
    album = Album(title=kwargs.pop('title', fake.text(max_nb_chars=100)),
                  artist=kwargs.pop('artist', fake.text(max_nb_chars=100)),
                  release_date=release_date,
                  **kwargs)
    if logs:
        album.logs = logs
    if log:
        album.logs.append(log)

    return album


def make_album(**kwargs):
    album = fake_album(**kwargs)
    album.save()
    album.reload()
    return album
