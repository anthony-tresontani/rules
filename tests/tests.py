from django.test import TestCase

from hamcrest import *
from django_dynamic_fixture import get

from rules.base import ApplyRules, IsRuleMatching, Group, get_permissions
from rules.models import Rule
from sample.models import *
from sample.acl import *
from sample.groups import *


class TestSingleRule(TestCase):
    """
       By default, everything is allowed.
       That means adding a can_do rule does not do anything.

       Rule:
           admin users can see all products
    """

    def setUp(self):
        self.admin = User.objects.create(username="admin")
        self.anonymous = User.objects.create(username="anonymous")

        for product_type in ["A", "B", "C", "D"]:
            get(Product, product_type=product_type)

        self.create_rules()

    def create_rules(self):
        Rule.objects.create_rule(groups_in="admingroup", can_do="see_products", predicate="all_products")

    def test_anynomous_cant_see_any_product(self):
        assert_that( ApplyRules(on=Product.objects.all(), action="see_products", for_=self.anonymous).check().count(), is_(4))

    def test_admin_can_see_all_products(self):
        assert_that( ApplyRules(on=Product.objects.all(), action="see_products", for_=self.admin).check().count(), is_(4))


class TestSingleNegativeRule(TestSingleRule):
    """
       Cant do rule remove any objects

       Rule:
           anonymous users can't see any products
    """
    def create_rules(self):
        Rule.objects.create_rule(groups_in="anonymous", cant_do="see_products", predicate="all_products")

    def test_anynomous_cant_see_any_product(self):
        assert_that( ApplyRules(on=Product.objects.all(), action="see_products", for_=self.anonymous).check().count(), is_(0))

    def test_admin_can_see_all_products(self):
        assert_that( ApplyRules(on=Product.objects.all(), action="see_products", for_=self.admin).check().count(), is_(4))



class TestSingleExcludeNegativeRule(TestSingleRule):
    """
       Rule:
           users not admin can't see any products
    """
    def create_rules(self):
        Rule.objects.create_rule(not_groups_in="admingroup", cant_do="see_products", predicate="all_products")

    def test_anynomous_cant_see_any_product(self):
        assert_that( ApplyRules(on=Product.objects.all(), action="see_products", for_=self.anonymous).check().count(), is_(0))

    def test_admin_can_see_all_products(self):
        assert_that( ApplyRules(on=Product.objects.all(), action="see_products", for_=self.admin).check().count(), is_(4))



class TestTwoRules(TestSingleRule):
    """
        Rules:
            admin users can see all products
            admin users can't see D products
    """
    def setUp(self):
        super(TestTwoRules, self).setUp()
        self.customer = User.objects.create(username="customer")

    def create_rules(self):
        Rule.objects.create_rule(groups_in="admingroup", can_do="see_products", predicate="all_products")
        Rule.objects.create_rule(groups_in="admingroup", cant_do="see_products", predicate="D_products")

    def test_anynomous_cant_see_any_product(self):
        assert_that( ApplyRules(on=Product.objects.all(), action="see_products", for_=self.anonymous).check().count(), is_(4))

    def test_admin_can_see_all_products(self):
        assert_that( ApplyRules(on=Product.objects.all(), action="see_products", for_=self.admin).check().count(), is_(3))


class TestRules(TestCase):

    def setUp(self):
        Group.default = None

        self.customer = User.objects.create(username="customer")
        self.rep = User.objects.create(username="rep")
        self.admin = User.objects.create(username="admin")
        self.anonymous = User.objects.create(username="anonymous")

        # Means that rule apply to customergroup
        Rule.objects.create_rule(not_groups_in=["customergroup","admingroup"], cant_do="see_products", predicate="all_products")
        Rule.objects.create_rule(not_groups_in="admingroup", cant_do="see_products", predicate="C_products")
        Rule.objects.create_rule(not_groups_in="admingroup", cant_do="see_products", predicate="D_products")

        Rule.objects.create_rule(not_groups_in=["rep", "admingroup"], predicate="as_any", cant_do="masquerade")
        Rule.objects.create_rule(groups_in="rep", predicate="as_any", can_do="masquerade")
        Rule.objects.create_rule(groups_in="admingroup", predicate="as_customer", can_do="masquerade")

        for product_type in ["A", "B", "C", "D"]:
            get(Product, product_type=product_type)

        self.product_C = Product.objects.get(product_type="C")
        self.product_A = Product.objects.get(product_type="A")

    def test_customer_can_see_some_products(self):
        assert_that( ApplyRules(on=Product.objects.all(), action="see_products", for_=self.customer).check().count(), is_(2))

    def test_product_A_is_not_allowed_for_anonymous(self):
        assert_that( IsRuleMatching(on=self.product_A, action="see_products", for_=self.anonymous).check(), is_(False))

    def test_product_A_is_allowed_for_customer(self):
        assert_that( IsRuleMatching(on=self.product_A, action="see_products", for_=self.customer).check(), is_(True))

    def test_product_C_is_not_allowed_for_customer(self):
        assert_that( IsRuleMatching(on=self.product_C, action="see_products", for_=self.customer).check(), is_(False))

    def test_product_C_is_allowed_for_admin(self):
        assert_that( IsRuleMatching(on=self.product_C, action="see_products", for_=self.admin).check(), is_(True))

    def test_customer_cant_masquerade_as_customer(self):
        assert_that( IsRuleMatching(on=self.customer, action="masquerade", for_=self.customer).check(), is_(False))

    def test_salesrep_can_masquerade_as_customer(self):
        assert_that( IsRuleMatching(on=self.customer, action="masquerade", for_=self.rep).check(), is_(True))

    def test_admin_can_masquerade_as_customer(self):
        assert_that( IsRuleMatching(on=self.customer, action="masquerade", for_=self.admin).check(), is_(True))

    def test_salesrep_can_masquerade_as_customer(self):
        assert_that( IsRuleMatching(on=self.customer, action="masquerade", for_=self.rep).check(), is_(True))

    def test_salesrep_can_masquerade_as_salesrep(self):
        assert_that( IsRuleMatching(on=self.rep, action="masquerade", for_=self.rep).check(), is_(True))

    def test_admin_cant_masquerade_as_admin(self):
        assert_that( IsRuleMatching(on=self.admin, action="masquerade", for_=self.admin).check(), is_(False))

    def test_match_reason(self):
        match = IsRuleMatching(on=self.product_C, action="see_products", for_=self.customer)
        match.check()
        assert_that(match.reason, is_("Cannot see C product"))

    def test_belong_to_group(self):
        assert_that( CustomerGroup.belong(self.customer), is_(True))
        assert_that( CustomerGroup.belong(self.admin), is_(False))
        assert_that( AdminGroup.belong(self.customer), is_(False))
        assert_that( AdminGroup.belong(self.admin), is_(True))

    def test_get_group(self):
        assert_that( Group.get_groups(self.customer), has_item('customergroup'))
        assert_that( Group.get_groups(self.admin), has_item('admingroup'))

    def test_get_group_by_name(self):
       assert_that( Group.get_by_name("customergroup"), not_none())

    def test_model_group(self):
       assert_that( Group.get_groups(self.product_C), is_(['group_product_model']))

    def test_validating_subclass(self):
       with self.assertRaises(AttributeError):
           type("invalidRule", (Predicate,), {"apply_obj": lambda x:x})
       type("validRule", (Predicate,), {"apply_obj": 10, "name": "name", "group_name": "group_name"}) # Should not raise an exception
