import logging
from django.db.models.signals import class_prepared
from django.dispatch.dispatcher import receiver
from rules_engine.rules import Group

logger = logging.getLogger("rules")

def get_model_group_name(cls_name):
    return "group_" + cls_name.lower() + "_model"


def create_group_class(cls):
    def belong(cls_, obj):
        return isinstance(obj, cls)
    name = get_model_group_name(cls.__name__)
    return type(name, (Group,), {"belong": classmethod(belong), "name": name})


@receiver(class_prepared)
def create_group_model(sender, **kwargs):
    logging.debug("Receive prepared signal for %s", sender)
    if isinstance(sender, type):
        class_name = get_model_group_name(sender.__name__)
        if not Group.get_by_name(class_name):
            group = create_group_class(sender)
            Group.register(group)
            logger.info("Creating and registering automatic group %s" , class_name)