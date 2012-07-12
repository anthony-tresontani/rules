# Create your models here.
from rules.base import Group

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

    @classmethod
    def belong(cls, obj):
        return obj.username == "anonymous"


class RepGroup(Group):
    name = "rep"

    @classmethod
    def belong(cls, obj):
        return obj.username == "rep"

class NoneGroup(Group):
    name = "anonymous"

    @classmethod
    def belong(cls, obj):
        return obj is None


