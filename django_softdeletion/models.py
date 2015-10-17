from django.db.models import DateTimeField, Model, Manager
from django.db.models.query import QuerySet
from django.db.models.fields.related import OneToOneField
from django.utils.translation import ugettext_lazy as _
from django.utils.timezone import now
from django.core.exceptions import ObjectDoesNotExist


def _unset_related_objects_relations(obj):
    # Iterate over related fields of this objects.
    for related in obj._meta.get_all_related_objects():
        # Unset related objects' relation
        rel_name = related.get_accessor_name()

        if related.one_to_one:
            try:
                related_object = getattr(obj, rel_name)
            except ObjectDoesNotExist:
                pass
            else:
                setattr(related_object, related.field.name, None)
                related_object.save()
        else:
            related_objects = getattr(obj, rel_name)
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

    def delete(self, using=None):
        """Soft delete this object.
        """
        _unset_related_objects_relations(self)

        # Soft deleted objects' one-to-one fields must be set to None,
        # otherwise, they will be retrieved when accessed from the related
        # object.
        for field in self._meta.get_fields():
            if isinstance(field, OneToOneField):
                setattr(self, field.name, None)

        self.deleted = now()
        self.save()

    def undelete(self):
        """Undelete this soft-deleted object.
        """
        self.deleted = None
        self.save()
