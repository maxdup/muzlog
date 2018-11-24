from muzapi.models import *
from flask_security.utils import hash_password
from faker import Faker

fake = Faker()


def fake_user():
    user = User(email=fake.email(),
                username=fake.name(),
                bio=fake.text(max_nb_chars=200),
                password=hash_password(fake.password(length=10)))
    return user


def fake_log(author, album):
    log = Log(author=author,
              album=album,
              message=fake.text(max_nb_chars=200),
              published_date=fake.date_this_year(before_today=True),
              recommended=(fake.random_int(min=0, max=10) == 6))

    return log


def fake_album():
    release_date = fake.date_this_century(before_today=True)
    album = Album(title=fake.text(max_nb_chars=100),
                  artist=fake.text(max_nb_chars=100),
                  release_date=release_date,
                  release_year=release_date.year,
                  published=False)

    return album


def fake_comment(author=None):
    # todo
    return None
