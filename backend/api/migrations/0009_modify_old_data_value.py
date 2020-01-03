from django.db import migrations, transaction


def forward_func(apps, schema_editor):
    Factory = apps.get_model("api", "Factory")

    # get the originally added factories from full_info.csv
    factories = Factory.objects.only("id").all().order_by("created_at")[:53918]

    init_factory_ids = [f.id for f in factories]
    with transaction.atomic():
        Factory.objects.filter(id__in=init_factory_ids).update(
            before_2016=True,
            factory_type=None,
        )
        factories = Factory.objects.only("id", "name").all().order_by("created_at")[:53918]
        for factory in factories:
            new_factory_name = factory.name.replace("full-info: row_", "既有違章工廠 No.")
            Factory.objects.filter(pk=factory.id).update(name=new_factory_name)


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0008_change_factory_status"),
    ]

    operations = [
        migrations.RunPython(
            code=forward_func,
            reverse_code=None,
        ),
    ]
