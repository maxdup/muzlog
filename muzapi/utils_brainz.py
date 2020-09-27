from flask import current_app as app
from flask_security import current_user
from flask_restx import abort
from muzapi import Role
from mongoengine.queryset import DoesNotExist
from mongoengine.errors import ValidationError

from datetime import datetime
from datetime import timezone
import re

import urllib.request
import requests
import shutil

import musicbrainzngs

from muzapi.models import Album, Product


def downloadBrainzCover(mbrid):
    cover_filename = mbrid + '-cover.jpg'
    thumb_filename = mbrid + '-thumb.jpg'

    r = requests.get(url='http://coverartarchive.org/release/' + mbrid)

    if r.status_code == 404:
        return False

    fronts = [l for l in r.json()['images'] if l['front']]

    if len(fronts) == 0:
        return False

    front = fronts[0]

    if 'small' not in front['thumbnails']:
        return False

    cover_url = front['image']
    thumb_url = front['thumbnails']['small']

    try:
        with urllib.request.urlopen(thumb_url) as response, \
                open(app.config['UPLOAD_FOLDER'] + thumb_filename, 'wb') \
                as out_file:
            shutil.copyfileobj(response, out_file)
        with urllib.request.urlopen(cover_url) as response, \
                open(app.config['UPLOAD_FOLDER'] + cover_filename, 'wb') \
                as out_file:
            shutil.copyfileobj(response, out_file)
    except Exception as e:
        print('failed')
        print(e)
        return False

    return {'thumb': thumb_filename, 'cover': cover_filename}


def album_from_mb_release_group(mbrgid, album=None, verbose=False):

    # get an album object from a musicbrainz id

    if album:
        album.mbrgid = mbrgid
    else:
        try:
            album = Album.objects.get(mbrgid=mbrgid)
            return album
        except (DoesNotExist, ValidationError):
            album = Album()
            album.mbrgid = mbrgid

    musicbrainzngs.set_useragent(
        "Muzlogger",
        "0.1",
        "https://github.com/maxdup/muzlog")
    try:
        rg = musicbrainzngs.get_release_group_by_id(
            id=mbrgid, includes=['artists', 'artist-credits',
                                 'releases', 'media'])['release-group']
    except musicbrainzngs.musicbrainz.ResponseError:
        abort(404)

    # set artist name, artist id, album title and release type
    album.artist = rg['artist-credit-phrase']
    album.mbaid = rg['artist-credit'][0]['artist']['id']

    if 'title' in rg:
        album.title = rg['title']
    if 'type' in rg:
        album.release_type = rg['type']

    year_re = re.compile('^[0-9]{4}$')
    date_re = re.compile('^[0-9]{4}-[0-9]{2}-[0-9]{2}$')

    if year_re.match(rg['first-release-date']):
        album.release_date = datetime.strptime(
            rg['first-release-date'], "%Y")
    elif date_re.match(rg['first-release-date']):
        album.release_date = datetime.strptime(
            rg['first-release-date'], "%Y-%m-%d")

    artists = musicbrainzngs.browse_artists(release_group=rg['id'])

    # determine album country from artist country
    for ac in rg['artist-credit']:
        for a in artists['artist-list']:
            if 'artist' in ac and a['id'] == ac['artist']['id']:
                if not album.country:
                    if 'country' in a:
                        album.country_code = a['country']
                    if 'area' in a:
                        album.country = a['area']['name']

    releases = musicbrainzngs.browse_releases(
        release_group=rg['id'], includes=['media', 'labels'])

    for release in releases['release-list']:

        # find products
        if 'asin' in release:
            product = Product(mbrid=release['id'],
                              asin=release['asin'])
            if 'format' in release['medium-list'][0]:
                product.medium = release['medium-list'][0]['format']
            if 'country' in release:
                product.country = release['country']
            album.products.append(product)

        # set label
        if not album.label and 'date' in release and \
           release['date'] == rg['first-release-date']:
            if len(release['label-info-list']) > 0:
                album.label = release['label-info-list'][0]['label']['name']

    # order cover candidates
    def sort_candidates(candidates):
        sorted_candidates = []
        for release in candidates:
            medium = release['medium-list'][0]
            if 'format' in release and release['format'] == 'Digital Media':
                sorted_candidates.append(release)
        for release in candidates:
            medium = release['medium-list'][0]
            if 'format' in release and 'CD' in release['format']:
                sorted_candidates.append(release)
        for release in candidates:
            medium = release['medium-list'][0]
            if 'format' in release and 'Vinyl' in release['format']:
                sorted_candidates.append(release)
        remaining = [x for x in candidates if x not in sorted_candidates]
        sorted_candidates = sorted_candidates + remaining
        return sorted_candidates

    cover_candidates = [x for x in releases['release-list'] if
                        x['cover-art-archive']['front']]
    sorted_candidates = sort_candidates(cover_candidates)

    # download a cover
    for release in sorted_candidates:
        cover_files = downloadBrainzCover(release['id'])
        if cover_files:
            album.cover = cover_files['cover']
            album.thumb = cover_files['thumb']
            break

    if verbose:
        print('title: ' + str(album.title))
        print('artist: ' + str(album.artist))
        print('country: ' + str(album.country))
        print('country_code: ' + str(album.country_code))
        print('release_type: ' + str(album.release_type))
        print('release_date: ' + str(album.release_date))
        print('mbrgid: ' + str(album.mbrgid))
        print('mbaid: ' + str(album.mbaid))
        print('label: ' + str(album.label))
        print('cover: ' + str(album.cover))
        print('thumb: ' + str(album.thumb))
        print('products-count: ' + str(len(album.products)))
        print('------------------')

    return album
