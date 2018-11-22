from muzapi.models import *
from flask_security.utils import hash_password
from faker import Faker

fake = Faker()


def fake_user():
    profile = UserProfile(username=fake.name(),
                          bio=fake.text(max_nb_chars=200))
    user = User(email=fake.email(),
                password=hash_password(fake.password(length=10)),
                profile=profile)
    return user


def fake_log(author, album):
    log = Log(author=author,
              album_id=str(album.id),
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
                  published=True)

    return album


def fake_comment(author=None):
    # todo
    return None