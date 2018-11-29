from flask import Blueprint, render_template, session
from flask_security import roles_accepted, login_required

from muzapi.models import Album
muzlog_site = Blueprint('muzlog_site', __name__)


@muzlog_site.route('/', methods=['GET'])
def home():
    albums = Album.objects(deleted=False).order_by('-published_date')
    return render_template('/index.html', albums=albums)


@muzlog_site.route('/album/<_id>', methods=['GET'])
def album(_id):
    print(_id)
    albums = Album.objects.get(id=_id)
    return render_template('/album.html')
