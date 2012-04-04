from core.models import Permission, Group, Rule

def apply_rules(on, to, for_):
    rule = Rule.get_by_name(to)
    if not has_permission(for_, to):
        return rule.apply(obj=on) 
    return on

def match_rule(on, to, for_):
    rule = Rule.get_by_name(to)
    if not has_permission(for_, to):
        return not rule.apply(obj=on)
    return True


def has_permission(obj, rule):
    permission_for_rule = Permission.objects.filter(rule=rule)
    for group_name in [perm.group for perm in permission_for_rule]:
        group = Group.get_by_name(group_name)
        if group.belong(obj):
            return True
    return False
    
