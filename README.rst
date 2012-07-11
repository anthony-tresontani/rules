Rules
=====

Flexible rules library for Django

Install
=======

Install::

    pip install django-rules

Add ``rules`` to ``INSTALLED_APPS`` and run ``python manage.py syncdb`` to
create the appropriate database tables.

Use
===

Some projects require complex and abstract business logic like:

    User A is allowed to buy product XYZ if attribute B of User A equals 58

You need then low level granularity.
Some solutions exist adding permission to the object itself in the DB.
But sometimes, we may want to get permissions for an object which is not in DB.

That's why rules!

In rules, you create a list of assumptions like your customer do.
For example:

    Anonymous users can't see any products
    Customer can see standard products
    Sales representatives can see VIP products
    Admin can see everything

to do that, you have to define:

`a group`
    Anonymous, Customer, Sales rep, Admin are all groups.

`a predicate`
    Any products, standard products, VIP products, everything are all predicates.

`a rule`
    The link between the group and the predicate through an action.
    Action may be: 'see products' in our example 

Here is what a rule looks file:

    Rule.objects.create_rule(groups_in="anonymous", cant_do="see_products", predicate="A_products")

You have then to explain 'rules' what anynomous and any_products means by subclassing Group and Predicate.

    class Anonymous(Group):
        name="anonymous"
        @classmethod
        def belong(cls, obj):
            return isinstance(obj, User) and obj.is_authenticated()

    then the Predicate.

    class Any(Predicate):
        @classmethod
        def apply_qs(cls, qs):
            return {"product_type":"A"}

then, to check for it, just do:

    list_of_products = ApplyRule(on=Product.objects.all(), action="see_products", for_=anonymous_user).check()

And you will get a queryset.

Contribute
==========

Install for contributing::

    git clone git://github.com/anthony-tresontani/rules.git
    mkvirtualenv rules
    cd rules
    python setup.py develop
    pip install -r requirements.txt

Run tests::

    ./run_tests.py

Understand
==========

Automatic group creation
------------------------

Any object is automatically assigned a group by default containing the all objects of the same model.
For ex, any Product instead will belong to the group group_product_model.
