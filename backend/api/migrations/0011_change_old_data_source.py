from django.db import migrations, transaction


def forward_func(apps, schema_editor):
    Factory = apps.get_model("api", "Factory")

    # get the originally added factories from full_info.csv
    factories = Factory.objects.only("id").all().order_by("created_at")[:53918]

    init_factory_ids = [f.id for f in factories]
    with transaction.atomic():
        Factory.objects.filter(id__in=init_factory_ids).update(
            source="G",
        )


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0010_clarify_status_and_source"),
    ]

    operations = [
        migrations.RunPython(
            code=forward_func,
            reverse_code=None,
        ),
    ]
