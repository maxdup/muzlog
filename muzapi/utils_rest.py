from flask import request
from flask_restx import fields, reqparse
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


class MuzArgument(reqparse.Argument):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.store_missing = False
        self.nullable = False
        return


class RequestParser(reqparse.RequestParser):

    def __init__(self, argument_class=MuzArgument,
                 result_class=reqparse.ParseResult, arguments={}):
        super().__init__(argument_class=MuzArgument,
                         result_class=reqparse.ParseResult)
        for key, value in arguments.items():
            self.add_argument(key, **value)
        return
