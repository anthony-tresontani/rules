from django.contrib.auth.models import Permission
from django.db import models
from django.db.models.query import QuerySet

from peak.rules import abstract, when

# Create your models here.
class Group(object):
    groups = set([])

    @classmethod
    def register(cls, group_class, default=False):
        cls.groups.add(group_class)

    @classmethod
    def belong(cls, obj):
        return False

    @classmethod
    def get_group_names(cls):
        return [group.name for group in cls.groups]

    @classmethod
    def get_groups(cls, obj):
        groups_in = []
        for group in cls.groups:
            try:
                if group.belong(obj):
                    groups_in.append(group)
            except AttributeError, e:
                pass
        return [group.name for group in groups_in]

    @classmethod
    def get_by_name(cls, name):
        for group in cls.groups:
            if group.name == name:
                return group



@abstract
def _apply(cls, obj):
    pass


@when(_apply, "isinstance(obj, QuerySet)")
def _apply_qs(cls, qs):
    return cls.apply_qs(qs)


@when(_apply, "not isinstance(obj, QuerySet)")
def _apply_obj(cls, qs):
    return cls.apply_obj(qs)


class ACL(models.Model):
    ALLOW, DENY = "ALLOW", "DENY"
    action_type = (("Allow", ALLOW), ("Deny", DENY))

    action = models.CharField(max_length=20, null=False)
    group = models.CharField(max_length=80)
    rule = models.CharField(max_length=80)
    type = models.CharField(max_length=10, choices=action_type, null=False, blank=False)

    def save(self, *args, **kwargs):
        if self.group not in Group.get_group_names() and self.group:
            raise ValueError("Group %s has not been registered" % self.group)
        if self.rule not in Rule.get_rule_names() and self.rule:
            raise ValueError("Rule %s has not been registered" % self.rule)
        super(ACL, self).save(*args, **kwargs)

    def __repr__(self):
        return "%s - %s" % (self.type, self.rule)


class Rule(object):
    rules = set([])

    def __init__(self, next_=None):
        self.next = next_

    @classmethod
    def register(cls, rule_class, type=ACL.ALLOW, action=None):
        cls.rules.add(rule_class)
        if type == ACL.DENY:
            ACL.objects.create(action=action, type=ACL.DENY, rule=rule_class.name)

    @classmethod
    def get_rule_names(cls):
        return [rule.name for rule in cls.rules]

    @classmethod
    def get_by_name(cls, name):
        for rule in cls.rules:
            if rule.name == name:
                return rule
    @classmethod
    def get_message(cls):
        if hasattr(cls, "message"):
            return cls.message
        return ""

    @classmethod
    def apply(cls, obj):
        return _apply(cls, obj)

    @classmethod
    def check_rules(cls, rules, obj):
        next_rules = rules[1:]
        next_rules.append(None)
        rules = [rule() for rule in rules]
        for (rule, next_) in zip(rules, next_rules):
            rule.next_ = next_
        rule[0].check(obj)

    def check(self, obj):
        return _apply(self, obj)
