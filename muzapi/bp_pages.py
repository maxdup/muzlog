from flask import Blueprint, render_template, session
from flask_security import roles_accepted, login_required

muzlog_pages = Blueprint('user_util', __name__)


@muzlog_pages.route('/cms/', defaults={'path': '', 'param': ''})
@muzlog_pages.route('/cms/<path:path>', defaults={'param': ''})
@muzlog_pages.route('/cms/<path:path>/<path:param>')
@login_required
@roles_accepted('admin', 'logger')
def admin_app(path, param):
    return render_template('/admin.html')


@muzlog_pages.route('/', methods=['GET'])
def home():
    return render_template('/index.html', path="/")
