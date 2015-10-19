from django.test import TestCase
from django.core.exceptions import ObjectDoesNotExist

from django_softdeletion.models import SoftDeleteManager, SoftDeleteQuerySet
from .project.app.models import Foo, Bar, Baz


class SoftDeletionTestCase(TestCase):

    def test_single_object(self):
        foo = Foo.objects.create()
        self.assertEqual(Foo.objects.count(), 1)

        foo.delete()
        self.assertEqual(Foo.objects.count(), 0)

        foo.undelete()
        self.assertEqual(Foo.objects.count(), 1)

    def test_foreign_key(self):
        foo = Foo.objects.create()
        bar = Bar.objects.create(foo=foo)
        self.assertEqual(Foo.objects.count(), 1)
        self.assertEqual(Bar.objects.count(), 1)

        foo.delete()
        bar.refresh_from_db()
        self.assertIsNone(bar.foo)

        foo.undelete()
        bar.delete()
        self.assertEqual(foo.bars.count(), 0)

    def test_queryset(self):
        assert isinstance(Foo.objects, SoftDeleteManager)
        assert isinstance(Foo.objects.all(), SoftDeleteQuerySet)

        foo = Foo.objects.create()
        bar = Bar.objects.create(foo=foo)
        Foo.objects.delete()
        self.assertEqual(Foo.objects.deleted().count(), 1)
        self.assertEqual(Foo.objects.with_deleted().count(), 1)
        self.assertEqual(Foo.objects.count(), 0)

        bar.refresh_from_db()
        self.assertIsNone(bar.foo)

    def test_many_to_many(self):
        bar1 = Bar.objects.create()
        baz1 = bar1.bazes.create()
        baz2 = bar1.bazes.create()
        self.assertEqual(bar1.bazes.count(), 2)

        baz1.delete()
        self.assertEqual(bar1.bazes.count(), 1)
        self.assertEqual(Baz.objects.deleted().count(), 1)
        self.assertEqual(Baz.objects.count(), 1)
        self.assertEqual(Baz.objects.with_deleted().count(), 2)

        baz2.delete()
        self.assertEqual(bar1.bazes.count(), 0)
        self.assertEqual(bar1.bazes.deleted().count(), 2)

        baz1.undelete()
        self.assertEqual(baz1.bars.count(), 1)

        bar2 = Bar.objects.create()
        baz1.bars.add(bar2)
        self.assertEqual(baz1.bars.count(), 2)

    def test_one_to_one(self):
        baz = Baz.objects.create()
        foo = Foo.objects.create(baz=baz)
        baz.delete()
        foo.refresh_from_db()
        self.assertIsNone(foo.baz)

        baz = Baz.objects.create()
        foo.baz = baz
        foo.save()
        foo.delete()
        baz.refresh_from_db()
        self.assertRaises(ObjectDoesNotExist, lambda: baz.foo)
