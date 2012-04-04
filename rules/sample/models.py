from django.db import models

from core.models import Group, Rule

# Create your models here.
class CustomerGroup(Group):
    name = "customergroup"

    @classmethod
    def belong(cls, obj):
        return obj.username == "customer"

class AdminGroup(Group):
    name = "admingroup"

    @classmethod
    def belong(cls, obj):
        return obj.username == "admin"


class CanSee(Rule):
    name="can_see"

    @classmethod
    def apply_qs(cls, qs):
        return qs.exclude(product_type="C")

    @classmethod
    def apply_obj(cls, obj):
        return obj.product_type == "C"

class Product(models.Model):
    product_type = models.CharField(max_length=20)
