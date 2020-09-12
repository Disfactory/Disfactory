from time import time

from django.db import migrations, models


def forward_func(apps, schema_editor):
    t1 = time()
    Factory = apps.get_model("api", "Factory")

    factories = Factory.objects.only("id", "created_at", "display_number").order_by("created_at").all()
    print("Prepare factory")
    factories_to_beupdated = []
    for number, factory in enumerate(factories):
        factory.display_number = number
        factories_to_beupdated.append(factory)
    print("bulk update", )
    Factory.objects.bulk_update(factories_to_beupdated, ["display_number"], batch_size=512)
    t2 = time()
    print(f"Update spent {t2 - t1} seconds")


def backward_func(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0023_auto_20200822_0649"),
    ]

    operations = [
        migrations.AddField(
            model_name="factory",
            name="display_number",
            field=models.IntegerField(null=True),
        ),
        migrations.RunPython(code=forward_func, reverse_code=backward_func),
        migrations.AlterField(
            model_name="factory",
            name="display_number",
            field=models.IntegerField(unique=True),
        ),
    ]
