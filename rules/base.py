import logging
from peak.rules.core import abstract, when
from django.db.models.query import QuerySet, Q

from rules.models import Rule

logger = logging.getLogger("rules")

def get_permissions(action, groups):
    permissions = Rule.objects.filter(action=action)
    logger.info("All rules for action '%s':", action)
    for rule in permissions:
        logger.info("    %s", rule)

    inclusive_permissions = permissions.filter(groups__name__in=groups, exclusive=False)
    exclusive_permissions =  permissions.filter(exclusive=True).exclude(groups__name__in=groups)
    deny_for_all = permissions.filter(groups=None, exclusive=True) 
    permissions = inclusive_permissions | exclusive_permissions | deny_for_all

    # Remove Deny rule if an apply rule matches
    for permission in permissions.filter(deny=True):    
        if permission.groups.exists():
            counter_exists = permissions.filter(deny=False, predicate=permission.predicate, action=permission.action, exclusive=permission.exclusive).exists()
        else:
            counter_exists = permissions.filter(deny=False, predicate=permission.predicate, action=permission.action).exists()
        if counter_exists:
            logger.info("Exclude deny rule as an apply has been found")
            permissions = permissions.exclude(id=permission.id)
    return permissions.order_by("deny")


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
        logger.info("GROUP \'%s\' registered", group_class.name)
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
        groups_names = [group.name for group in groups_in]
        logger.info("Obj %s belong to %s", obj, groups_names)
        return groups_names

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

    def check(self, obj):
        return _apply(self, obj)


class RuleHandler(object):
    no_permission_value = False

    def __init__(self, on, action, for_):
        self.on = on
        self.action = action
        self.for_ = for_
        self.groups = Group.get_groups(self.for_)
        self.permissions = get_permissions(self.action, self.groups)

    def check(self):
       logger.info("-"*8 + "CHECKING RULES" + "-"*8)
       logger.info("   Permissions: %s", self.permissions)
       result = self._check()
       logger.info("-"*8 + "RULES CHECKED" + "-"*8)
       return result

class ApplyRules(RuleHandler):
    def __init__(self, on, action, for_):
        super(ApplyRules, self).__init__(on, action, for_)
        self.model = self.on.model

    def apply_perm(self, perm, method):
        rule = Predicate.get_by_name(perm.predicate)
        filters = rule.apply(obj=self.on)
        filter_method = getattr(self.on, method)
        if isinstance(filters, dict):
            on = filter_method(**filters) # == self.on.filter(..)
        else:                             # or self.on.exclude(..)
            on = filter_method(filters)
        return on

    def _check(self):
        logger.info("   Rules applied on %d objects: %s", len(self.on), self.on)
        on = None
        for permission in self.permissions:
            method = "exclude" if permission.deny else "filter"
            self.on = self.apply_perm(permission, method=method)
            logger.info("        After filter %s: %s", permission, self.on)

        logger.info("   %d allowed objects: %s", len(self.on), self.on)
        return self.on


class IsRuleMatching(RuleHandler):
    def __init__(self, on, action, for_):
        super(IsRuleMatching, self).__init__(on, action, for_)
        self.reason = None

    def _check(self):
        logger.info("   Rules applied on objects: %s", self.on)
        result = True
        for permission in self.permissions:
            rule = Predicate.get_by_name(permission.predicate)
            logger.info("Predicate name %s", permission.predicate)
            result = rule.apply(obj=self.on)
            result = not result if permission.deny else result
            if not result:
                logger.info("        rule '%s' failed", rule)
                self.reason = rule.get_message()
                return False

        logger.info("    Return %s", result)
        return result


def get_view_decorator(action):
    def decorator(fn=None, deny=lambda x:""):
        if fn:
            def wrapped(self, *arg, **kwargs):
                request = kwargs['request']
                user = getattr(request, "user", None)
                if IsRuleMatching(on=self, action=action, for_=user).check():
                    val = fn(self, *arg, **kwargs)
                else:
                    val = deny(self)
                return val
            return wrapped
        else:
            def partial_inner(func):
                return decorator(func, deny)   
            return partial_inner
    return decorator
