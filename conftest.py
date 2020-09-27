import pytest
from flask import testing
from werkzeug.datastructures import Headers

from muzapi import create_app, db
from muzapi.db_ensure import db_ensure_roles

DB_NAME = 'muzlog_test'


class TestClient(testing.FlaskClient):

    def _add_json_content_type(self, kwargs):
        kwargs['headers'] = kwargs.pop('headers', {})
        kwargs['headers'].update({'Content-Type': 'application/json'})
        return kwargs

    def open(self, *args, **kwargs):
        if args[0].startswith('api/') or args[0].startswith('/api/'):
            api_key_headers = {'Content-Type': 'application/json'}
            headers = kwargs.pop('headers', {})
            headers.update(api_key_headers)
            kwargs['headers'] = Headers(headers)
        return super().open(*args, **kwargs)

    def jget(self, *args, **kwargs):
        return super().get(*args, **self._add_json_content_type(kwargs))

    def jpost(self, *args, **kwargs):
        return super().post(*args, **self._add_json_content_type(kwargs))

    def jput(self, *args, **kwargs):
        return super().put(*args, **self._add_json_content_type(kwargs))


@pytest.fixture
def app():
    config_overrides = {
        'TEST': True,
        'MONGODB_DB': DB_NAME
    }
    app = create_app(config_overrides)
    app.test_client_class = TestClient
    db_ensure_roles(app)
    with app.app_context():
        db.connection.drop_database(DB_NAME)
        for fn in app.before_first_request_funcs:
            fn()

    return app
