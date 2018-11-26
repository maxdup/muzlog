import json

from datetime import datetime
#from datetime import timezone
import re

import musicbrainzngs

from muzapi import create_app, db
from muzapi.models import Album, Product, Log
from muzapi.util_brainz import album_from_mb_release_group


class Import(db.Document):
    published_date = db.DateTimeField()  # post_date_gmt
    message = db.StringField()  # post_content
    album_title = db.StringField()  # post_title
    status = db.StringField()  # post_status

    album = db.ReferenceField(Album)
    mbrgid = db.StringField()
    mbid = db.StringField()


def import_from_json():

    app = create_app('config')

    print('--------------------')
    print('importing from json')
    print('--------------------')
    with app.app_context():
        Import.drop_collection()
        with open('daily_posts.json') as f:
            data = json.load(f)
            for post in data['posts']:

                if post['post_type'] == 'nav_menu_item':
                    continue

                imp = Import(message=post['post_content'],
                             album_title=post['post_title'],
                             status=post['post_status'])
                if imp.status != 'draft':
                    date = datetime.strptime(post['post_date_gmt'],
                                             "%Y-%m-%d %H:%M:%S")
                    imp.published_date = date
                imp.save()
                print(post['post_title'])
            print(str(Import.objects.count()) + " albums from json")


def set_imports_release_group_ids():

    app = create_app('config')
    musicbrainzngs.set_useragent(
        "Muzlogger",
        "0.1",
        "https://github.com/maxdup/muzlog")

    with app.app_context():
        imports = Import.objects()
        print('--------------------')
        print('settings release ids')
        print('--------------------')
        for imp in imports:
            print(imp.album_title)

            if imp.mbrgid != None:
                print(imp.mbrgid)
                continue

            rgs = musicbrainzngs.search_release_groups(query=imp['album_title'])
            imp.mbrgid = rgs['release-group-list'][0]['id']
            print(imp.mbrgid)
            imp.save()


def import_album_from_brainz():

    app = create_app('config')

    with app.app_context():

        print('--------------------------------')
        print('creating albums from musicbrainz')
        print('--------------------------------')
        imports = Import.objects()

        for imp in imports:
            print(imp.album_title)
            if imp.album:
                continue
            album = album_from_mb_release_group(imp.mbrgid)
            album.save()
            imp.album = album
            imp.save()


def create_logs_from_imports():
    app = create_app('config')

    with app.app_context():

        print('--------------------------')
        print('creating Logs from Imports')
        print('--------------------------')
        imports = Import.objects()

        Log.drop_collection()
        albums = Album.objects()
        for album in albums:
            album.logs = []
            album.save()

        for imp in imports:

            log = Log(album=imp.album,
                      message=imp.message,
                      published_date=imp.published_date)
            log.published = imp.status == 'publish'
            print(imp.album_title)
            log.save()
            log.reload()
            log.album.logs.append(log)
            log.album.published_date = log.published_date
            log.album.published = log.published
            log.album.save()


# import_from_json()
# set_imports_release_group_ids()
# import_album_from_brainz()
create_logs_from_imports()
