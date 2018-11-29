from flask import current_app as app, Blueprint, request, render_template, session
from flask_security import current_user, roles_accepted, login_required
from flask_restful import abort, reqparse

from mongoengine.queryset import DoesNotExist
from mongoengine.errors import ValidationError

from muzapi.models import Album, User

import os
import uuid
import requests
import werkzeug

from PIL import Image

from resizeimage import resizeimage

muzlog_cms = Blueprint('muzlog_cms', __name__)


@muzlog_cms.route('/cms/', defaults={'path': '', 'param': ''})
@muzlog_cms.route('/cms/<path:path>', defaults={'param': ''})
@muzlog_cms.route('/cms/<path:path>/<path:param>')
@login_required
@roles_accepted('admin', 'logger')
def admin_app(path, param):
    return render_template('/admin.html')


@muzlog_cms.route('/api/upload_album_cover/<_id>', methods=['POST'])
@login_required
@roles_accepted('admin', 'logger')
def upload_cover(_id=None):
    '''
    Upload an Album cover

    :param_id: The _id of an Album object to add a cover to
    '''
    parser = reqparse.RequestParser()
    parser.add_argument('file', location='files', required=True,
                        type=werkzeug.datastructures.FileStorage,
                        help="file is required")

    try:
        album = Album.objects.get(id=_id)
    except (DoesNotExist, ValidationError) as e:
        abort(404)

    content = parser.parse_args()
    if not save_image(content['file'], album, 'cover', 1200):
        abort(400)

    return (album.cover, 200)


@muzlog_cms.route('/api/upload_profile_avatar/<_id>', methods=['POST'])
@login_required
@roles_accepted('admin', 'logger')
def upload_avatar(_id=None):
    '''
    Upload a Profile avatar

    :param_id: The _id of a Profile object to add an avatar to
    '''
    parser = reqparse.RequestParser()
    parser.add_argument('file', location='files', required=True,
                        type=werkzeug.datastructures.FileStorage,
                        help="file is required")

    if _id:
        if _id == str(current_user.id) or \
           current_user.has_role('admin'):
            try:
                user = User.objects.get(id=_id)
            except (DoesNotExist, ValidationError) as e:
                abort(404)
        else:
            abort(403)
    else:
        user = current_user

    content = parser.parse_args()
    if not save_image(content['file'], user, 'avatar', 500):
        abort(400)

    return (user.avatar, 200)


def save_image(image_file, resource, key, max_size):
    file_id = str(uuid.uuid4())
    resource[key] = file_id + '-avatar.jpg'
    resource.thumb = file_id + '-thumb.jpg'

    try:
        with Image.open(image_file) as image:
            size = min(min(image.height, image.width), max_size)
            image_file = resizeimage.resize_cover(image, [size, size])
            image_file.save(os.path.join(
                app.config['UPLOAD_FOLDER'], resource[key]), image.format)

            thumb_file = resizeimage.resize_cover(image, [250, 250])
            thumb_file.save(os.path.join(
                app.config['UPLOAD_FOLDER'], resource.thumb), image.format)
            resource.save()
    except Exception as e:
        print(e)
        return False

    return resource[key]
