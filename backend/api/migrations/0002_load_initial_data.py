import csv
import itertools
import os
import sys
from datetime import datetime

from django.db import migrations
from django.conf import settings


SEED_DATA_PATH = os.path.join(settings.BASE_DIR, "fixtures/full-info.csv")


def forward_func(apps, schema_editor):
    Factory = apps.get_model("api", "Factory")

    # TODO don't import fucking data in migration
    with open(SEED_DATA_PATH, "r") as csvfile:
        reader = csv.DictReader(csvfile)
        # HACK
        if any("test" in arg for arg in sys.argv):
            reader = itertools.islice(reader, 0, 101)

        seed_factories = []
        for idx, datum in enumerate(reader):
            try:
                lng = float(datum["經度"])
                lat = float(datum["緯度"])
            except ValueError:
                continue
            factory = Factory(
                lng=lng,
                lat=lat,
                landcode=datum["地號"],
                status="A",
                status_time=datetime.now(),
                name=f"full-info: row_{idx}",
            )
            seed_factories.append(factory)

    Factory.objects.bulk_create(seed_factories)


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(
            code=forward_func,
            reverse_code=None,
        ),
    ]
