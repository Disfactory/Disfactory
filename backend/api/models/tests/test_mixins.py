from datetime import datetime, timezone

from django.test import TestCase
from django.db import connection
from django.db.utils import ProgrammingError
from django.db.models.base import ModelBase
from freezegun import freeze_time

from ..mixins import SoftDeleteMixin


# ref: https://stackoverflow.com/a/51146819/5163166
class AbstractModelMixinTestCase(TestCase):
    """
    Base class for tests of model mixins/abstract models.
    To use, subclass and specify the mixin class variable.
    A model using the mixin will be made available in self.model
    """

    def setUp(self):
        # Create a dummy model which extends the mixin. A RuntimeWarning will
        # occur if the model is registered twice
        if not hasattr(self, "model"):
            self.model = ModelBase(
                "__TestModel__" + self.mixin.__name__,
                (self.mixin,),
                {"__module__": self.mixin.__module__},
            )

        # Create the schema for our test model. If the table already exists,
        # will pass
        try:
            with connection.schema_editor() as schema_editor:
                schema_editor.create_model(self.model)
            super().setUpClass()
        except ProgrammingError:
            pass

    def tearDown(self):
        # Delete the schema for the test model. If no table, will pass
        try:
            with connection.schema_editor() as schema_editor:
                schema_editor.delete_model(self.model)
            super().tearDownClass()
        except ProgrammingError:
            pass


class SoftDeleteMixinTestCase(AbstractModelMixinTestCase):

    mixin = SoftDeleteMixin

    def test_delete_then_undelete(self):
        obj1 = self.model.objects.create()
        obj2 = self.model.objects.create()
        obj3 = self.model.objects.create()

        assert obj1.deleted_at is None
        assert obj2.deleted_at is None
        assert obj3.deleted_at is None

        delete_time = datetime(2019, 11, 11, 11, 11, 11, tzinfo=timezone.utc)
        with freeze_time(delete_time):
            self.model.objects.filter(id=obj1.id).delete()

        assert self.model.objects.count() == 2
        assert self.model.raw_objects.count() == 3
        assert self.model.recycle_objects.count() == 1

        obj1.refresh_from_db()
        assert obj1.deleted_at == delete_time

        obj1.undelete()
        assert self.model.objects.count() == 3
        assert self.model.raw_objects.count() == 3
        assert self.model.recycle_objects.count() == 0

        obj1.refresh_from_db()
        assert obj1.deleted_at is None
