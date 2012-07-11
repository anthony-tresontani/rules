from django.contrib.auth.models import User
from django.db.models.query_utils import Q
from rules.models import Rule

from rules.base import Predicate, Group
from tests.sample.models import Product


class CProducts(Predicate):
    name = "C_products"
    message = "Cannot see C product"

    @classmethod
    def apply_qs(cls, qs):
        return Q(product_type="C")

    @classmethod
    def apply_obj(cls, obj):
        return obj.product_type == "C"

class DProducts(Predicate):
    name = "D_products"
    message = "Nobody can see D product"

    @classmethod
    def apply_qs(cls, qs):
        return Q(product_type="D")

    @classmethod
    def apply_obj(cls, obj):
        return obj.product_type == "D"


class AllProducts(Predicate):
    name="all_products"

    @classmethod
    def apply_qs(cls, qs):
        return {'product_type__gte':"A"}

    @classmethod
    def apply_obj(cls, obj):
        return isinstance(obj, Product)

class DeletedProductOutOfStock(Predicate):
    name = "deleted_product_out_of_stock"

    @classmethod
    def apply_qs(cls, qs):
        return {"stock":0, "status":1}

    @classmethod
    def apply_obj(cls, obj):
        return obj.stock == 0 and obj.status == 1


class AsAny(Predicate):
    name = "as_any" 
    message = "Cant masquerade"

    @classmethod
    def apply_obj(cls, obj):
        return True

class AsCustomer(Predicate):
    name = "as_customer" 
    message = "Cannot masquerade as a customer" 

    @classmethod
    def apply_obj(cls, obj):
        if isinstance(obj, User):
           return "customergroup" in Group.get_groups(obj)
        return False
