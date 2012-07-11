import logging
import collections

from django.db import models
from django.db.models.signals import post_syncdb
from django.dispatch.dispatcher import receiver

logger = logging.getLogger("rules")

class RuleManager(models.Manager):
    def create_rule(self, predicate, groups_in=None, not_groups_in=None, can_do=None, cant_do=None):
        if groups_in:
            groups = groups_in
            exclusive=False
        elif not_groups_in:
            groups = not_groups_in
            exclusive=True
        else:
            groups = []
            exclusive = True
        self.create_rules_for_groups(groups, can_do, cant_do, predicate, exclusive=exclusive)

    def create_rules_for_groups(self, groups, can_do, cant_do, predicate, exclusive):
        if not isinstance(groups, collections.Iterable) or isinstance(groups, str):
            groups =  [groups]
        if can_do:
            rule, created = self.get_or_create(action=can_do, predicate=predicate, exclusive=exclusive)
        elif cant_do:
            rule, created = self.get_or_create(action=cant_do, predicate=predicate, deny=True, exclusive=exclusive)
        rule.save()
        for group in groups:
            group, created = GroupName.objects.get_or_create(name=group)
            rule.groups.add(group)

class GroupName(models.Model):
    name = models.CharField(max_length=80, null=True, blank=False)

class Rule(models.Model):
    deferred_rules = []

    ALLOW, DENY = "ALLOW", "DENY"
    action_type = (("Allow", ALLOW), ("Deny", DENY))

    action = models.CharField(max_length=20, null=False)
    groups = models.ManyToManyField(GroupName)
    predicate = models.CharField(max_length=80)
    deny = models.BooleanField(default=False)
    exclusive = models.BooleanField()
    auto = models.BooleanField(default=False)

    objects = RuleManager()

    def save(self, *args, **kwargs):
        from rules.base import Group, Predicate
        if self.pk:
            for group in self.groups.all():
                if group not in Group.get_group_names():
                    raise ValueError("Group %s has not been registered" % group)
            if self.predicate not in Predicate.get_rule_names() and self.predicate:
                raise ValueError("Predicate %s has not been registered" % self.predicate)
        super(Rule, self).save(*args, **kwargs)

    def __repr__(self):
        group = "for groups in %s"
        if self.exclusive:
            group = "for groups NOT in %s"
        groups_list = " AND ".join([g.name for g in self.groups.all()])
        if not groups_list:
           group = "for %s" 
           groups_list = "ALL"
        action = "CAN %s"
        if self.deny:
            action = "CAN'T %s"
        msg= action + " " + "%s " + group
        return msg  % (self.action, self.predicate, groups_list )

    def __str__(self):
        return self.__repr__()
 
    @classmethod
    def deferred(self, **kwargs):
        self.deferred_rules.append(kwargs)

@receiver(post_syncdb, )
def create_deferred_rules(sender, **kwargs):
    for rule in Rule.deferred_rules:
        Rule.objects.get_or_create(**rule)

