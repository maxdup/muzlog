from flask import Blueprint, render_template

muzlog_pages = Blueprint('user_util', __name__)


@muzlog_pages.route('/', methods=['GET'])
def home():
    return render_template('/index.html', path="/")
