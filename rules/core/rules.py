from core.models import Permission, Group, Rule


def get_rules(to):
    rules = Rule.get_by_name(to)
    if not rules:
        raise ValueError("No rules found for action group %s" % to)
    return rules

def apply_rules(on, to, for_):
    for rule in get_rules(to):
        if not has_permission(for_, rule.name):
            print "Rule",rule,"applied to", for_
            on = rule.apply(obj=on)
    return on

def match_rule(on, to, for_):
    for rule in get_rules(to):
        if not has_permission(for_, rule.name):
            result = not rule.apply(obj=on)
            if not result:
               return result
        return True

def has_permission(obj, rule):
    permission_for_rule = Permission.objects.filter(rule=rule)
    for group_name in [perm.group for perm in permission_for_rule]:
        group = Group.get_by_name(group_name)
        if group.belong(obj):
            return True
    return False
    
