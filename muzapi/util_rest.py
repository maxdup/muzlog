from flask import request
from flask_restplus import fields, reqparse
from flask_security import current_user


class listRestricted(fields.List):
    def output(self, key, data, ordered=False, **kwargs):
        if current_user.has_role('admin'):
            return fields.List.output(self, key, data, ordered, **kwargs)
        else:
            return fields.List.output(self, key, {}, ordered, **kwargs)


class stringRestricted(fields.String):
    def output(self, key, data, **kwargs):
        if current_user.has_role('admin'):
            return fields.String.output(self, key, data, **kwargs)
        else:
            return fields.String.output(self, key, {}, **kwargs)


def parse_request(args):
    data = request.get_json()
    parser = reqparse.RequestParser()
    for key, value in args.items():
        if 'required' in value and value['required']:
            parser.add_argument(key, **value)
        elif 'init' in value and value['init']:
            del value['init']
            parser.add_argument(key, **value)
        elif data and key in data:
            parser.add_argument(key, **value)

    return parser.parse_args()
