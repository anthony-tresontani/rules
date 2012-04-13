from django.db import models
from django.db.models.query import QuerySet

from peak.rules import abstract, when

# Create your models here.
class Group(object):
    groups = set([])
    default = None

    @classmethod
    def register(cls, group_class, default=False):
        if default:
            cls.default = group_class
        else:
            cls.groups.add(group_class)

    @classmethod
    def belong(cls, obj):
        return False


    @classmethod
    def get_group_names(cls):
        return [group.name for group in cls.groups]

    @classmethod
    def get_groups(cls, obj):
        groups_in = filter(lambda gr: gr.belong(obj), cls.groups)
        if not groups_in and cls.default:
            groups_in =  [cls.default.name]
        else:
            groups_in = [group.name for group in groups_in]
        return groups_in

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
     def get_rule_names(cls):
         return [rule.name for rule in cls.rules]

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

    def save(self, *args, **kwargs):
        if self.group not in Group.get_group_names():
            raise ValueError("Group %s has not been registered" % self.group)
	if self.rule not in Rule.get_rule_names():
            raise ValueError("Rule %s has not been registered" % self.rule)
        super(Permission, self).save(*args, **kwargs)
        
