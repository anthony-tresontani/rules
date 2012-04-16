from django.contrib.auth.models import User
from core.models import Rule, Group
from sample.groups import CustomerGroup
from sample.models import Product

class CanSeeCProducts(Rule):
    group_name="can_see"
    name = "can_see_C"

    @classmethod
    def apply_qs(cls, qs):
        return {"product_type":"C"}

    @classmethod
    def apply_obj(cls, obj):
        return obj.product_type == "C"


class CanSeeAnyProducts(Rule):
    group_name="can_see"
    name="can_see_products"

    @classmethod
    def apply_qs(cls, qs):
        return {}

    @classmethod
    def apply_obj(cls, obj):
        return isinstance(obj, Product)

class DeletedProductOutOfStock(Rule):
    group_name = "can_see"
    name = "deleted_product_out_of_stock"

    @classmethod
    def apply_qs(cls, qs):
        return {"stock":0, "status":1}

    @classmethod
    def apply_obj(cls, obj):
        return obj.stock == 0 and obj.status == 1


class CanMasquerade(Rule):
    group_name="masquerade"
    name="can_masquerade_as_any" 

    @classmethod
    def apply_obj(cls, obj):
        return True

class CanMasqueradeAsCustomer(Rule):
    group_name="masquerade"
    name="can_masquerade_as_customer" 

    @classmethod
    def apply_obj(cls, obj):
        if isinstance(obj, User):
           return "customergroup" in Group.get_groups(obj)
        return False
