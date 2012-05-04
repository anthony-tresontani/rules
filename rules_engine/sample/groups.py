# Create your models here.
from rules_engine.rules import Group

class CustomerGroup(Group):
    name = "customergroup"

    @classmethod
    def belong(cls, obj):
        return obj.username == "customer"


class AdminGroup(Group):
    name = "admingroup"

    @classmethod
    def belong(cls, obj):
        return obj.username == "admin"

class AnonymousGroup(Group):
    name = "anonymous"

class RepGroup(Group):
    name = "rep"

    @classmethod
    def belong(cls, obj):
        return obj.username == "rep"


