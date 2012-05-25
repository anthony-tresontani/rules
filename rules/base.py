import logging
from peak.rules.core import abstract, when
from django.db.models.query import QuerySet

from rules.models import Rule

logger = logging.getLogger("rules")

def get_permissions(for_, action, groups):
    apply_permissions = Rule.objects.filter(group__in=groups, action=action, type=Rule.ALLOW)
    deny_permissions = Rule.objects.filter(action=action, type=Rule.DENY)
    return apply_permissions, deny_permissions


class GroupMetaClass(type):
    def __new__(meta, classname, bases, classDict):
        cls = type.__new__(meta, classname, bases, classDict)
        if classname != "Group":
            cls.register(cls)
        return cls


class Group(object):
    __metaclass__ = GroupMetaClass
    groups = set([])

    @classmethod
    def register(cls, group_class):
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

class PredicateMetaClass(type):
    def __new__(meta, classname, bases, classDict):
        cls = type.__new__(meta, classname, bases, classDict)
        if classname != "Predicate":
            for attr in classDict:
                if attr.startswith("apply_") and callable(classDict[attr]) and not getattr(classDict[attr], "im_self", None):
                    raise AttributeError("method %s of class %s should be a classmethod" % (attr, classname))
            if not "name" in classDict:
                raise AttributeError("Rule %s should have a name attribute" % classname)
            if not "group_name" in classDict:
                raise AttributeError("Rule %s should have a group_name attribute" % classname)
            cls.register(cls)
        return cls


class Predicate(object):
    __metaclass__ = PredicateMetaClass
    rules = set([])

    def __init__(self, next_=None):
        self.next = next_

    @classmethod
    def register(cls, rule_class):
        cls.rules.add(rule_class)

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



class RuleHandler(object):
    no_permission_value = False

    def __init__(self, on, action, for_):
        self.on = on
        self.action = action
        self.for_ = for_
        self.groups = Group.get_groups(self.for_)
        self.apply_permissions, self.deny_permissions = get_permissions(self.for_, self.action, self.groups)

    def no_perm_value(self):
        if hasattr(self, "get_no_permission_value"):
            return getattr(self, "get_no_permission_value")()
        else:
            return self.no_permission_value

    def check(self):
        if not self.apply_permissions:
            logger.info("No permission found")
            self.reason = "No permission found"
            return self.no_perm_value()
        return self._check()

    def _check(self):
        raise NotImplementedError()


class ApplyRules(RuleHandler):
    def __init__(self, on, action, for_):
        super(ApplyRules, self).__init__(on, action, for_)
        self.model = self.on.model

    def get_no_permission_value(self):
        return self.model.objects.none()

    def apply_perm(self, perm, method):
        rule = Predicate.get_by_name(perm.rule)
        filters = rule.apply(obj=self.on)
        filter_method = getattr(self.model.objects, method)
        if isinstance(filters, dict):
            on = filter_method(**filters)
        else:
            on = filter_method(filters)
        return on

    def _check(self):
        on = None
        for permission in self.apply_permissions:
            on = self.apply_perm(permission, method="filter")

        for permission in self.deny_permissions:
            if not Rule.objects.filter(action=self.action, group__in=self.groups, rule=permission.rule).exists():
                on = self.apply_perm(permission, method="exclude")
        return on


class IsRuleMatching(RuleHandler):

    def __init__(self, on, action, for_):
        super(IsRuleMatching, self).__init__(on, action, for_)
        self.reason = None

    def _check(self):
        for permission in self.apply_permissions:
            rule = Predicate.get_by_name(permission.rule)
            result = rule.apply(obj=self.on)
            if not result:
                logger.info("Allow rule %s failed", rule)
                self.reason = rule.get_message()
                return False

        for permission in self.deny_permissions:
            if not Rule.objects.filter(action=self.action, group__in=self.groups, rule=permission.rule).exists():
                rule = Predicate.get_by_name(permission.rule)
                exclude = rule.apply(obj=self.on)
                if exclude:
                    logger.info("Deny rule %s failed", rule)
                    self.reason = rule.get_message()
                    return False
        return result

