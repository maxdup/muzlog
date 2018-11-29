from flask_restplus import fields
from flask_security import current_user
from muzapi import Role


class listRestricted(fields.List):
    def output(self, key, data, ordered=False, **kwargs):
        if (data and 'id' in data and data.id == current_user.id)\
           or current_user.has_role('admin'):
            return fields.List.output(self, key, data, ordered, **kwargs)
        else:
            return fields.List.output(self, key, {}, ordered, **kwargs)


class stringRestricted(fields.String):
    def output(self, key, data, **kwargs):
        if (data and 'id' in data and data.id == current_user.id)\
           or current_user.has_role('admin'):
            return fields.String.output(self, key, data, **kwargs)
        else:
            return fields.String.output(self, key, {}, **kwargs)
