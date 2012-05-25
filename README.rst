Rules
=====

Install
=======

Usual steps:

    git clone git://github.com/anthony-tresontani/rules.git
    mkvirtualenv rules
    python setup.py develop
    pip install Django- You can have rule not applying to any group.
  ex: Deleted product without stock should not be visible (for anybody)

- A permission is an exemption for a rule to be applied to a group
Automatic group creation
========================

Any object is automatically assigned a group by default containing the all objects of the same model.
For ex, any Product instead will belong to the group group_product_model.
