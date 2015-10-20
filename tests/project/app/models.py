from django.db.models import ForeignKey, ManyToManyField, OneToOneField

from django_softdeletion.models import SoftDeleteModel


class Baz(SoftDeleteModel):

    def __repr__(self):
        return 'Baz(id=%s)' % self.id


class Foo(SoftDeleteModel):

    baz = OneToOneField(Baz, related_name='foo', null=True)

    def __repr__(self):
        return 'Foo(id=%s)' % self.id


class Bar(SoftDeleteModel):

    foo = ForeignKey(Foo, related_name='bars', null=True)
    bazes = ManyToManyField(Baz, related_name='bars')

    def __repr__(self):
        return 'Bar(id=%s)' % self.id
