from core.models import Rule

class CanSeeCProducts(Rule):
    group_name="can_see"
    name = "can_see_c"

    @classmethod
    def apply_qs(cls, qs):
        return qs.exclude(product_type="C")

    @classmethod
    def apply_obj(cls, obj):
        return obj.product_type == "C"


class CanSeeAnyProducts(Rule):
    group_name="can_see"
    name="can_see_products"

    @classmethod
    def apply_qs(cls, qs):
        return qs.none()

    @classmethod
    def apply_obj(cls, obj):
        return False

class DeletedProductOutOfStock(Rule):
    group_name="can_see"

    @classmethod
    def apply_qs(cls, qs):
        return qs.exclude(stock=0, status=1)

    @classmethod
    def apply_obj(cls, obj):
        return obj.stock == 0 and obj.status == 1

