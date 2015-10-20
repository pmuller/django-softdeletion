import logging

from django.db.models import DateTimeField, Model, Manager
from django.db.models.query import QuerySet
from django.db.models.fields.related import \
    OneToOneField, ManyToManyField, ManyToManyRel
from django.utils.translation import ugettext_lazy as _
from django.utils.timezone import now
from django.core.exceptions import ObjectDoesNotExist


LOGGER = logging.getLogger(__name__)


def _unset_related_one_to_one(obj, field):
    old_value = getattr(obj, field.column)
    if old_value is not None:
        LOGGER.debug(
            'Setting %s.%s to None on object %s (old value: %s)',
            obj._meta.model.__name__, field.column, obj.pk, old_value)
        # Unset the fk field (e.g. Foo.baz_id)
        setattr(obj, field.column, None)
        # Unset the related object field (e.g. Foo.baz)
        setattr(obj, field.name, None)


def _unset_related_many_to_many(obj, field):
    manager = getattr(obj, field.name)
    old_values = manager.values_list('pk', flat=True)
    LOGGER.debug(
        'Removing all objects from %s.%s on object %s (old values: %s)',
        obj._meta.model.__name__, field.name, obj.pk,
        ', '.join(str(pk) for pk in old_values))
    manager.remove(*manager.all())


def _unset_related_objects_relations(obj):
    LOGGER.debug('Soft-deleting object %s %s',
                 obj._meta.model.__name__, obj.pk)

    for field in obj._meta.get_fields():
        field_type = type(field)

        if field_type is OneToOneField:
            _unset_related_one_to_one(obj, field)
        elif field_type in (ManyToManyRel, ManyToManyField):
            _unset_related_many_to_many(obj, field)

    for related in obj._meta.get_all_related_objects():
        # Unset related objects' relation
        rel_name = related.get_accessor_name()

        if related.one_to_one:
            # Handle one-to-one relations.
            try:
                related_object = getattr(obj, rel_name)
            except ObjectDoesNotExist:
                pass
            else:
                _unset_related_one_to_one(related_object, related.field)
                related_object.save()

        else:
            # Handle one-to-many and many-to-many relations.
            related_objects = getattr(obj, rel_name)
            if related_objects.count():
                affected_objects_id = ', '.join(
                    str(pk) for pk in related_objects.values_list(
                        'pk', flat=True))
                old_values = ', '.join(
                    str(val) for val in related_objects.values_list(
                        related.field.name, flat=True))
                LOGGER.debug(
                    'Setting %s.%s to None on objects %s (old values: %s)',
                    related_objects.model.__name__, related.field.name,
                    affected_objects_id, old_values)
                related_objects.update(**{related.field.name: None})


class SoftDeleteQuerySet(QuerySet):
    """This QuerySet subclass implements soft deletion of objects.
    """
    def delete(self):
        """Soft delete all objects included in this queryset.
        """
        for obj in self:
            _unset_related_objects_relations(obj)

        self.update(deleted=now())


class SoftDeleteManager(Manager.from_queryset(SoftDeleteQuerySet)):
    """This Manager hides soft deleted objects by default,
    and exposes methods to access them.
    """
    def _get_base_queryset(self):
        return super(SoftDeleteManager, self).get_queryset()

    def get_queryset(self):
        """Return NOT DELETED objects.
        """
        return self._get_base_queryset().filter(deleted__isnull=True)

    def deleted(self):
        """Return DELETED objects.
        """
        return self._get_base_queryset().filter(deleted__isnull=False)

    def with_deleted(self):
        """Return ALL objects.
        """
        return self._get_base_queryset()


class SoftDeleteModel(Model):
    """Simply inherit this class to enable soft deletion on a model.
    """
    class Meta:
        abstract = True

    objects = SoftDeleteManager()
    deleted = DateTimeField(verbose_name=_('deleted'), null=True, blank=True)

    def delete(self):
        """Soft delete this object.
        """
        _unset_related_objects_relations(self)
        self.deleted = now()
        self.save()

        return self

    def undelete(self):
        """Undelete this soft-deleted object.
        """
        if self.deleted is not None:
            LOGGER.debug('Soft-undeleting object %s %s',
                         self._meta.model.__name__, self.pk)
            self.deleted = None
            self.save()

        return self
