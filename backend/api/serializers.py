from rest_framework.serializers import (
    ModelSerializer,
    CharField,
    SerializerMethodField,
)

from .models import Factory, Image, ReportRecord


class ImageSerializer(ModelSerializer):

    url = CharField(source="image_path")

    class Meta:
        model = Image
        fields = ["id", "image_path", "url"]


class FactorySerializer(ModelSerializer):

    images = ImageSerializer(many=True, read_only=True)
    type = CharField(source="factory_type")
    reported_at = SerializerMethodField()

    class Meta:
        model = Factory
        fields = [
            "id",
            "lat",
            "lng",
            "name",
            "landcode",
            "factory_type",
            "type",
            "status",
            "images",
            "reported_at",
        ]

    def get_reported_at(self, obj):
        report_records = ReportRecord.objects.only("created_at").filter(factory=obj)
        if len(report_records) == 0:
            return None
        reported_date = [record.created_at for record in report_records]
        return sorted(reported_date, reverse=True)[0]
