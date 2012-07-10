import logging
from django.contrib.admin.sites import site
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


def autodiscover():
    """
    Auto-discover INSTALLED_APPS admin.py modules and fail silently when
    not present. This forces an import on them to register any admin bits they
    may want.
    """

    def import_file(app, file):
        import copy
        from django.utils.importlib import import_module
        from django.utils.module_loading import module_has_submodule
        mod = import_module(app)
        # Attempt to import the app's admin module.
        try:
            before_import_registry = copy.copy(site._registry)
            import_module('%s.%s' % (app, file))
        except ImportError:
            # Reset the model registry to the state before the last import as
            # this import will have to reoccur on the next request and this
            # could raise NotRegistered and AlreadyRegistered exceptions
            # (see #8245).
            site._registry = before_import_registry

    from django.conf import settings
    for app in settings.INSTALLED_APPS:
        import_file(app, "groups")
        import_file(app, "rules")

autodiscover()
