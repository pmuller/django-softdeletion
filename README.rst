django-softdeletion implements soft deletion of Django models.


Usage:

.. code-block:: python

    from django_softdeletion import SoftDeleteModel


    class Foo(SoftDeleteModel):
        pass


It will add a ``deleted`` field to the Foo model.
When deleting foo objects, the deletion timestamp will be stored in this field.

SoftDeleteModel's default manager excludes objects having a soft deletion
timestamp.
You can still access soft deleted objects using the ``deleted()`` and
``with_deleted()`` methods of the manager.


Soft deleted objects can be undeleted using the ``undelete()`` method.


Using SoftDeleteModel implies a few constraints:

    * ForeignKey and OneToOneField MUST have null=True,
      because these fields are set to None when their relation is soft deleted.


Development
===========

Setup your development environment:

.. code-block:: console

    $ virtualenv .env
    $ . .env/bin/activate
    $ pip install -r requirements/dev.txt

To run the tests:

.. code-block:: console

    $ ./setup.py test

Coverage:

.. code-block:: console

    $ coverage run ./setup.py test
    $ coverage report
