from django.db import models
from django.db.models.query import QuerySet

from peak.rules import abstract, when

# Create your models here.
class Group(object):
    groups = set([])

    @classmethod
    def register(cls, group_class):
        cls.groups.add(group_class)

    @classmethod
    def belong(cls, obj):
        return False

    @classmethod
    def get_groups(cls, obj):
        groups_in = filter(lambda gr: gr.belong(obj), cls.groups)
        return [group.name for group in groups_in]

    @classmethod
    def get_by_name(cls, name):
        for group in cls.groups:
            if group.name == name:
                return group

class Rule(object):
     rules = set([])

     @classmethod
     def register(cls, rule_class):
         cls.rules.add(rule_class)

     @classmethod
     def get_by_name(cls, name):
        return filter(lambda rule: rule.group_name == name, cls.rules)

     @classmethod
     def apply(cls, obj):
         return _apply(cls, obj)

@abstract
def _apply(cls, obj):
    pass

@when(_apply, "isinstance(obj, QuerySet)")
def _apply_qs(cls, qs):
    return cls.apply_qs(qs)

@when(_apply, "not isinstance(obj, QuerySet)")
def _apply_obj(cls, qs):
    return cls.apply_obj(qs)


class Permission(models.Model):

    group = models.CharField(max_length=80)
    rule = models.CharField(max_length=80)

