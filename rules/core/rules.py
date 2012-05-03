from django.db.models.query_utils import Q
from core.models import ACL, Group, Rule


def get_permissions(for_, action, groups):
    apply_permissions = ACL.objects.filter(group__in=groups, action=action, type=ACL.ALLOW)
    deny_permissions = ACL.objects.filter(action=action, type=ACL.DENY)
    return apply_permissions, deny_permissions

class ApplyRules(object):

    def __init__(self, on, action, for_):
        self.on = on
        self.action = action
        self.for_ = for_

    def check(self):
        model = self.on.model
        groups = Group.get_groups(self.for_)
        apply_permissions, deny_permissions = get_permissions(self.for_, self.action, groups)
        if not apply_permissions:
            return model.objects.none()

        for permission in apply_permissions:
            rule = Rule.get_by_name(permission.rule)
            filters = rule.apply(obj=self.on)
            if isinstance(filters, dict):
                on = model.objects.filter(**filters)
            else:
                on = model.objects.filter(filters)

        for permission in deny_permissions:
            if not ACL.objects.filter(action=self.action, group__in=groups, rule=permission.rule).exists():
                rule = Rule.get_by_name(permission.rule)
                filters = rule.apply(obj=self.on)
                if isinstance(filters, dict):
                    on = model.objects.exclude(**filters)
                else:
                    on = model.objects.exclude(filters)

        return on

def is_rule_matching(on, action, for_):
    groups = Group.get_groups(for_)
    apply_permissions, deny_permissions = get_permissions(for_, action, groups)
    if not apply_permissions:
        return False

    print apply_permissions
    for permission in apply_permissions:
        rule = Rule.get_by_name(permission.rule)
        result = rule.apply(obj=on)
        if not result:
            return result

    for permission in deny_permissions:
        if not ACL.objects.filter(action=action, group__in=groups, rule=permission.rule).exists():
            rule = Rule.get_by_name(permission.rule)
            exclude = rule.apply(obj=on)
            if exclude:
                return False
    return result

