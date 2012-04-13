from django.test import TestCase
from django.contrib.auth.models import User

from hamcrest import *
from django_dynamic_fixture import get

from core.models import Group, Permission
from core.rules import apply_rules, match_rule, has_permission, get_rules

from sample.models import *
from sample.rules import *
from sample.groups import *


class TestRules(TestCase):

    def setUp(self):
        self.customer = User.objects.create(username="customer")
        self.rep = User.objects.create(username="rep")
        self.admin = User.objects.create(username="admin")
        self.anonymous = User.objects.create(username="anonymous")


        Group.register(CustomerGroup)
        Group.register(AdminGroup)
        Group.register(AnonymousGroup, default=True)

        Rule.register(CanSeeCProducts)
        Rule.register(CanSeeAnyProducts)
        Rule.register(CanSeeAnyProducts)
        Rule.register(CanMasquerade)

        Permission.objects.create(group="admingroup", rule="can_see_C")
        Permission.objects.create(group="admingroup", rule="can_see_products")
        Permission.objects.create(group="customergroup", rule="can_see_products")

        for product_type in ["A", "B", "C"]:
            get(Product, product_type=product_type)

    def test_acceptance_rules(self):
        """
        Given 2 users being in 2 groups (customer and productAdmin) and a list of A, B and C products,
            the user 1 sees A and B product
            the user 2 sees A, B and C
        """
        assert_that( apply_rules(on=Product.objects.all(), to="can_see", for_=self.customer).count(), is_(2))
        assert_that( apply_rules(on=Product.objects.all(), to="can_see", for_=self.admin).count(), is_(3))
        assert_that( apply_rules(on=Product.objects.all(), to="can_see", for_=self.anonymous).count(), is_(0))

       
        product_C = Product.objects.get(product_type="C")
        assert_that( match_rule(on=product_C, to="can_see", for_=self.customer), is_(False))
        assert_that( match_rule(on=product_C, to="can_see", for_=self.admin), is_(True))

    def test_acceptance_masquerading(self):
        assert_that( match_rule(on=self.customer, to="masquerade", for_=self.rep), is_(True))
        assert_that( match_rule(on=self.customer, to="masquerade", for_=self.admin), is_(True))
        assert_that( match_rule(on=self.customer, to="masquerade", for_=self.customer), is_(False))

        assert_that( match_rule(on=self.rep, to="masquerade", for_=self.admin), is_(True))
        assert_that( match_rule(on=self.rep, to="masquerade", for_=self.customer), is_(True))
        assert_that( match_rule(on=self.rep, to="masquerade", for_=self.rep), is_(True))

        assert_that( match_rule(on=self.admin, to="masquerade", for_=self.admin), is_(False))

    def test_belong_to_group(self):
        assert_that( CustomerGroup.belong(self.customer), is_(True))
        assert_that( CustomerGroup.belong(self.admin), is_(False))
        assert_that( AdminGroup.belong(self.customer), is_(False))
        assert_that( AdminGroup.belong(self.admin), is_(True))

    def test_get_group(self):
        assert_that( Group.get_groups(self.customer), is_(['customergroup']))
        assert_that( Group.get_groups(self.admin), is_(['admingroup']))
      

    def test_has_permission(self):
        assert_that( has_permission(self.admin, "can_see_C"), is_(True))
        assert_that( has_permission(self.customer, "can_see"), is_(False))

    def test_get_group_by_name(self):
       assert_that( Group.get_by_name("customergroup") == CustomerGroup)

    def test_default_group(self):
        assert_that( Group.get_groups(self.anonymous), is_(['anonymous']))

    def test_no_rules_exist(self):
        self.assertRaises(ValueError, get_rules, "doesnotexist")
