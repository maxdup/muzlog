from flask_restful import fields, marshal
from flask_security import current_user
from muzapi import Role


class stringRestricted(fields.String):
    def output(self, key, obj):
        if (obj and 'id' in obj and obj.id == current_user.id) \
           or current_user.has_role('admin'):
            return fields.String.output(self, key, obj)
        else:
            return None


class listRestricted(fields.List):
    def output(self, key, data):
        if (data and 'id' in data and data.id == current_user.id) \
           or current_user.has_role('admin'):
            return fields.List.output(self, key, data)
        else:
            return []


class DictDiffer(object):
    def __init__(self, current_dict, past_dict):
        self.current_dict, self.past_dict = current_dict, past_dict
        self.current_keys, self.past_keys = [
            set(d.keys()) for d in (current_dict, past_dict)
        ]
        self.intersect = self.current_keys.intersection(self.past_keys)

    def added(self):
        return self.current_keys - self.intersect

    def removed(self):
        return self.past_keys - self.intersect

    def changed(self):
        return set(o for o in self.intersect
                   if self.past_dict[o] != self.current_dict[o])

    def unchanged(self):
        return set(o for o in self.intersect
                   if self.past_dict[o] == self.current_dict[o])
