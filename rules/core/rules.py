import logging

from django.db.models.query_utils import Q
from core.models import ACL, Group, Rule


logger = logging.getLogger("rules")

def get_permissions(for_, action, groups):
    apply_permissions = ACL.objects.filter(group__in=groups, action=action, type=ACL.ALLOW)
    deny_permissions = ACL.objects.filter(action=action, type=ACL.DENY)
    return apply_permissions, deny_permissions

class RuleHandler(object):
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


class ApplyRules(RuleHandler):

    def __init__(self, on, action, for_):
        super(ApplyRules, self).__init__(on, action, for_)
        self.model = self.on.model

    def get_no_permission_value(self):
        return self.model.objects.none()

    def apply_perm(self, perm, method):
	rule = Rule.get_by_name(perm.rule)
	filters = rule.apply(obj=self.on)
        filter_method = getattr(self.model.objects, method)
	if isinstance(filters, dict):
	    on = filter_method(**filters)
	else:
	    on = filter_method(filters)
        return on

    def _check(self):
        for permission in self.apply_permissions:
            on = self.apply_perm(permission, method="filter")

        for permission in self.deny_permissions:
            if not ACL.objects.filter(action=self.action, group__in=self.groups, rule=permission.rule).exists():
                on = self.apply_perm(permission, method="exclude")
        return on


class IsRuleMatching(RuleHandler):
    no_permission_value = False

    def __init__(self, on, action, for_):
        super(IsRuleMatching, self).__init__(on, action, for_)
        self.reason = None

    def _check(self):
	for permission in self.apply_permissions:
	    rule = Rule.get_by_name(permission.rule)
	    result = rule.apply(obj=self.on)
	    if not result:
                logger.info("Allow rule %s failed", rule)
                self.reason = rule.get_message()
		return False

	for permission in self.deny_permissions:
	    if not ACL.objects.filter(action=self.action, group__in=self.groups, rule=permission.rule).exists():
		rule = Rule.get_by_name(permission.rule)
		exclude = rule.apply(obj=self.on)
		if exclude:
                    logger.info("Deny rule %s failed", rule)
                    self.reason = rule.get_message() 
		    return False
	return result

