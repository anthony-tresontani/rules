from django.test import TestCase
from django.contrib.auth.models import User

from hamcrest import *
from django_dynamic_fixture import get

from core.models import Group, Permission
from core.rules import apply_rules, match_rule, has_permission

from sample.models import *
from sample.rules import *
from sample.groups import *


class TestRules(TestCase):

    def setUp(self):
        self.user1 = User.objects.create(username="customer")
        self.user2 = User.objects.create(username="admin")

        Group.register(CustomerGroup)
        Group.register(AdminGroup)

        Permission.objects.create(group="admingroup", rule="can_see")
        Rule.register(CanSeeCProducts)
        Rule.register(CanSeeCProducts)

        for product_type in ["A", "B", "C"]:
            get(Product, product_type=product_type)

    def test_acceptance_rules(self):
        """
        Given 2 users being in 2 groups (customer and productAdmin) and a list of A, B and C products,
            the user 1 sees A and B product
            the user 2 sees A, B and C
        """
        assert_that( apply_rules(on=Product.objects.all(), to="can_see", for_=self.user1).count(), 3)
        assert_that( apply_rules(on=Product.objects.all(), to="can_see", for_=self.user2).count(), 2)
       
        product_C = Product.objects.get(product_type="C")
        assert_that( match_rule(on=product_C, to="can_see", for_=self.user1), is_(False))
        assert_that( match_rule(on=product_C, to="can_see", for_=self.user2), is_(True))

    def test_belong_to_group(self):
        assert_that( CustomerGroup.belong(self.user1), is_(True))
        assert_that( CustomerGroup.belong(self.user2), is_(False))
        assert_that( AdminGroup.belong(self.user1), is_(False))
        assert_that( AdminGroup.belong(self.user2), is_(True))

    def test_get_group(self):
        assert_that( Group.get_groups(self.user1), is_(['customergroup']))
        assert_that( Group.get_groups(self.user2), is_(['admingroup']))
      

    def test_has_permission(self):
        assert_that( has_permission(self.user2, "can_see"), is_(True))
        assert_that( has_permission(self.user1, "can_see"), is_(False))

    def test_get_group_by_name(self):
       assert_that( Group.get_by_name("customergroup") == CustomerGroup)
