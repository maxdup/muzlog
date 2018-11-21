from flask import current_app as app, Blueprint, request
from flask_security import current_user, roles_accepted
from flask_restful import abort
from mongoengine.queryset import DoesNotExist

from muzapi.models import Album

import os
import uuid
import requests
import urllib.request

from PIL import Image

from resizeimage import resizeimage

muzlog_upload = Blueprint('muzlog_upload', __name__)


def downloadBrainzCover(mbid):
    thumb_url = 'http://coverartarchive.org/release/' + mbid + '/front-250.jpg'
    cover_url = 'http://coverartarchive.org/release/' + mbid + '/front-1200.jpg'
    thumb_filename = mbid + '-thumb.jpg'
    cover_filename = mbid + '-cover.jpg'
    urllib.request.urlretrieve(
        thumb_url, app.config['UPLOAD_FOLDER'] + thumb_filename)
    urllib.request.urlretrieve(
        cover_url, app.config['UPLOAD_FOLDER'] + cover_filename)

    return {'thumb': thumb_filename, 'cover': cover_filename}


@muzlog_upload.route('/upload_album_cover/<_id>', methods=['POST'])
@login_required
@roles_accepted('logger')
def upload_cover(_id=None):
    '''
    Upload an Album cover

    :param_id: The _id of an Album object to add a cover to
    '''
    if (_id):
        album = Album.objects.get(id=_id)
        if not album:
            abort(404)
    else:
        abort(400)

    if 'file' not in request.files:
        return 406

    cover_file = request.files['file']
    if cover_file.filename == '':
        return 406

    file_id = str(uuid.uuid4())
    cover_filename = file_id + '-cover.jpg'
    thumb_filename = file_id + '-thumb.jpg'

    # Save file locally
    try:
        with Image.open(cover_file) as image:
            size = min(image.height, image.width)
            cover = resizeimage.resize_cover(image, [size, size])
            cover.save(os.path.join(
                app.config['UPLOAD_FOLDER'], cover_filename), image.format)
            thumb = resizeimage.resize_cover(image, [250, 250])
            thumb.save(os.path.join(
                app.config['UPLOAD_FOLDER'], thumb_filename), image.format)

        album.cover = cover_filename
        album.thumb = thumb_filename

        album.save()
    except Exception as e:
        print(e)
        abort(500)

    return (cover_filename, 200)
