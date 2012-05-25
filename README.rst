Rules
=====

Flexible ACL library for Django

Install
=======

Install::

    pip install django-rules

Add ``rules`` to ``INSTALLED_APPS`` and run ``python manage.py syncdb`` to
create the appropriate database tables.

Use
===

...

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
