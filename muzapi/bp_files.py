from flask import current_app as app, Blueprint, request
from flask_security import current_user, roles_accepted, login_required
from flask_restful import abort
from mongoengine.queryset import DoesNotExist

from muzapi.models import Album, User

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


def save_image(image_file, filename_large, filename_small, max_size):
    try:
        with Image.open(image_file) as image:
            size = min(min(image.height, image.width), max_size)
            image_file = resizeimage.resize_cover(image, [size, size])
            image_file.save(os.path.join(
                app.config['UPLOAD_FOLDER'], filename_large), image.format)
            thumb_file = resizeimage.resize_cover(image, [250, 250])
            thumb_file.save(os.path.join(
                app.config['UPLOAD_FOLDER'], filename_small), image.format)
    except Exception as e:
        print(e)
        return False

    return True


@muzlog_upload.route('/api/upload_album_cover/<_id>', methods=['POST'])
@login_required
@roles_accepted('logger', 'admin')
def upload_cover(_id=None):
    '''
    Upload an Album cover

    :param_id: The _id of an Album object to add a cover to
    '''

    if 'file' not in request.files or not _id:
        abort(406)

    album = Album.objects.get(id=_id)
    if not album:
        abort(404)

    file_id = str(uuid.uuid4())
    cover_filename = file_id + '-cover.jpg'
    thumb_filename = file_id + '-thumb.jpg'

    if save_image(request.files['file'], cover_filename, thumb_filename, 1200):
        album.cover = cover_filename
        album.thumb = thumb_filename
        album.save()
    else:
        abort(500)

    return (thumb_filename, 200)


@muzlog_upload.route('/api/upload_profile_avatar/<_id>', methods=['POST'])
@login_required
@roles_accepted('logger', 'admin')
def upload_avatar(_id=None):
    '''
    Upload a Profile avatar

    :param_id: The _id of a Profile object to add an avatar to
    '''
    print('plz')
    if 'file' not in request.files or not _id:
        abort(406)

    if (_id):
        if _id == str(current_user.id) or \
           current_user.has_role('admin'):
            user = User.objects.get(id=_id)
        else:
            abort(403)
    else:
        user = current_user

    if not user:
        abort(404)

    file_id = str(uuid.uuid4())
    avatar_filename = file_id + '-avatar.jpg'
    thumb_filename = file_id + '-thumb.jpg'

    if save_image(request.files['file'], avatar_filename, thumb_filename, 500):
        user.profile.avatar = avatar_filename
        user.profile.thumb = thumb_filename
        user.save()
        print('user saved')
    else:
        abort(500)

    return (thumb_filename, 200)
