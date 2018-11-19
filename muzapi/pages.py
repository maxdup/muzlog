from flask import Blueprint, render_template

muzlog_pages = Blueprint('user_util', __name__)


@muzlog_pages.route('/admin/', defaults={'path': '', 'param': ''})
@muzlog_pages.route('/admin/<path:path>', defaults={'param': ''})
@muzlog_pages.route('/admin/<path:path>/<path:param>')
def admin_app(path, param):
    #auth = current_user.get_auth_token()
    return render_template('/admin.html')


@muzlog_pages.route('/', methods=['GET'])
def home():
    return render_template('/index.html', path="/")
