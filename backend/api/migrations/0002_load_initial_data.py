import os
import sys
import csv
from datetime import datetime

from django.db import migrations
from django.conf import settings


SEED_DATA_PATH = os.path.join(settings.BASE_DIR, "fixtures/full-info.csv")


def forward_func(apps, schema_editor):
    Factory = apps.get_model("api", "Factory")

    with open(SEED_DATA_PATH, "r") as csvfile:
        reader = csv.DictReader(csvfile)
        seed_factories = []
        for idx, datum in enumerate(reader):
            if ("test" in sys.argv) and (idx > 100):
                # reduce the amount of seed data to speed up testing
                break
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
