import logging
import collections

from django.db import models

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
        if not isinstance(groups, collections.Iterable) or isinstance(groups, str):
            groups =  [groups]

        if can_do:
            deny = False
            action = can_do
        elif cant_do:
            deny = True
            action = cant_do

        rule, created = self.get_or_create(action=action, predicate=predicate, deny=deny, exclusive=exclusive)
        for group in groups:
            group, created = GroupName.objects.get_or_create(name=group)
            rule.groups.add(group)


class GroupName(models.Model):
    name = models.CharField(max_length=80, null=True, blank=False)

class Rule(models.Model):
    action = models.CharField(max_length=20, null=False)
    groups = models.ManyToManyField(GroupName)
    predicate = models.CharField(max_length=80)
    deny = models.BooleanField(default=False)
    exclusive = models.BooleanField()
    auto = models.BooleanField(default=False)

    objects = RuleManager()

    def save(self, *args, **kwargs):
        from rules.base import Group, Predicate
        super(Rule, self).save(*args, **kwargs)
        for group in self.groups.all():
            if group not in Group.get_group_names():
                self.delete()
                raise ValueError("Group '%s' has not been registered" % group)
        if self.predicate not in Predicate.get_rule_names() and self.predicate:
           self.delete()
           raise ValueError("Predicate '%s' has not been registered" % self.predicate)

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
