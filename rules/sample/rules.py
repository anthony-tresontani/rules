from core.models import Rule

class CanSeeCProducts(Rule):
    group_name="can_see"

    @classmethod
    def apply_qs(cls, qs):
        return qs.exclude(product_type="C")

    @classmethod
    def apply_obj(cls, obj):
        return obj.product_type == "C"


class CanSeeAnyProducts(Rule):
    group_name="can_see"

    @classmethod
    def apply_qs(cls, qs):
        return qs.none()

    @classmethod
    def apply_obj(cls, obj):
        return False
