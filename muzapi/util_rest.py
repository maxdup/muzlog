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


def parse_request():
    return None


class RequestParser(reqparse.RequestParser):

    def __init__(self, argument_class=reqparse.Argument,
                 result_class=reqparse.ParseResult, arguments={}):
        super().__init__(argument_class=reqparse.Argument,
                         result_class=reqparse.ParseResult)
        self.add_arguments(arguments)
        return

    def add_argument(self, *args, **kwargs):
        return super().add_argument(*args, store_missing=False, **kwargs)

    def add_arguments(self, args):
        for key, value in args.items():
            self.add_argument(key, **value)
