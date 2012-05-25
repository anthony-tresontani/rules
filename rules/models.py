import logging

from django.db import models

logger = logging.getLogger("rules")


class Rule(models.Model):
    ALLOW, DENY = "ALLOW", "DENY"
    action_type = (("Allow", ALLOW), ("Deny", DENY))

    action = models.CharField(max_length=20, null=False)
    group = models.CharField(max_length=80)
    rule = models.CharField(max_length=80)
    type = models.CharField(max_length=10, choices=action_type, null=False, blank=False)

    def save(self, *args, **kwargs):
        from rules.base import Group, Predicate
        if self.group not in Group.get_group_names() and self.group:
            raise ValueError("Group %s has not been registered" % self.group)
        if self.rule not in Predicate.get_rule_names() and self.rule:
            raise ValueError("Rule %s has not been registered" % self.rule)
        super(Rule, self).save(*args, **kwargs)

    def __repr__(self):
        return "%s - %s" % (self.type, self.rule)

