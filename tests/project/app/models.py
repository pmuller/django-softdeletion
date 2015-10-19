from django.db.models import ForeignKey, ManyToManyField, OneToOneField

from django_softdeletion.models import SoftDeleteModel


class Baz(SoftDeleteModel):
    pass


class Foo(SoftDeleteModel):

    baz = OneToOneField(Baz, related_name='foo', null=True)


class Bar(SoftDeleteModel):

    foo = ForeignKey(Foo, related_name='bars', null=True)
    bazes = ManyToManyField(Baz, related_name='bars')
