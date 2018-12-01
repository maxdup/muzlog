from muzapi import Role


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


def ensure_roles():
    if not Role.objects(name="admin"):
        role_admin = Role(name="admin",
                          description="includes all permissions")
        role_admin.save()

    if not Role.objects(name="logger"):
        role_logger = Role(name="logger",
                           description="common poster")
        role_logger.save()
