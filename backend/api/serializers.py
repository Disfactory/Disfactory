from datetime import timedelta

from rest_framework.serializers import (
    ModelSerializer,
    CharField,
    SerializerMethodField,
)
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone

from .models import Factory, Image, ReportRecord, FollowUp


VALID_FACTORY_TYPES = [t[0] for t in Factory.factory_type_list]


def _get_latest_time_or_none(objs):
    return max(
        (obj.created_at for obj in objs),
        default=None,
    )


class ImageSerializer(ModelSerializer):

    url = CharField(source="image_path")

    class Meta:
        model = Image
        fields = ["id", "image_path", "url"]


class FactoryLocationSerializer(ModelSerializer):
    class Meta:
        model = Factory
        fields = [
            "id",
            "lat",
            "lng",
            "landcode",
            "townname",
            "sectname",
            "sectcode",
        ]


class FactorySerializer(ModelSerializer):

    images = ImageSerializer(many=True, read_only=True)
    type = CharField(source="factory_type", required=False, allow_null=True)
    reported_at = SerializerMethodField()
    data_complete = SerializerMethodField()
    status = SerializerMethodField()  # should be DEPRECATED
    document_display_status = SerializerMethodField()
    follow_ups_for_user = SerializerMethodField()
    wont_fix = SerializerMethodField()

    class Meta:
        model = Factory
        fields = [
            "id",
            "display_number",
            "lat",
            "lng",
            "name",
            "landcode",
            "townname",
            "sectname",
            "sectcode",
            "source",
            "factory_type",
            "type",
            "cet_report_status",
            "wont_fix",
            "before_release",
            "images",
            "reported_at",
            "data_complete",
            "status",  # should be DEPRECATED
            "document_display_status",
            "follow_ups_for_user"
        ]
        extra_kwargs = {
            "display_number": {"required": False},
        }

    def get_wont_fix(self, obj):
        return obj.cet_review_status == 'O'

    def get_status(self, obj):
        return obj.cet_report_status

    def get_reported_at(self, obj):
        report_records = obj.report_records.all()
        return _get_latest_time_or_none(report_records)

    def get_data_complete(self, obj):
        # has_photo and reported_within_1_year and (not before_release or has_type)
        if len(obj.images.all()) == 0:
            return False  # no photo
        latest_record_time = _get_latest_time_or_none(obj.report_records.all())
        if not (latest_record_time and latest_record_time > timezone.now() - timedelta(days=365)):
            return False  # not reported or outdated

        if obj.before_release:
            return obj.factory_type is not None
        else:
            return True

    def get_document_display_status(self, obj):
        documents = obj.documents.all()
        if len(documents) > 0:
            latest_document = max(documents, key=lambda d: d.created_at)
            return latest_document.get_display_status_display()
        return None

    def get_follow_ups_for_user(self, obj):
        follow_up_query_set = []
        for document in obj.documents.all():
            follow_up_query_set.extend(
                document.follow_ups.filter(for_user=True))

        note_list = list(map(lambda item: {
            "note": item.note,
            "created_at": item.created_at.isoformat(),
        }, follow_up_query_set))

        return note_list

    def validate_lat(self, value):
        if not (settings.TAIWAN_MIN_LATITUDE <= value <= settings.TAIWAN_MAX_LATITUDE):
            raise ValidationError(
                f"latitude should be within {settings.TAIWAN_MIN_LATITUDE} "
                f"~ {settings.TAIWAN_MAX_LATITUDE}, but got {value}"
            )

    def validate_lng(self, value):
        if not (settings.TAIWAN_MIN_LONGITUDE <= value <= settings.TAIWAN_MAX_LONGITUDE):
            raise ValidationError(
                f"longitude should be within {settings.TAIWAN_MIN_LONGITUDE} "
                f"~ {settings.TAIWAN_MAX_LONGITUDE}, but got {value}"
            )

    def validate_type(self, value):
        if (value is not None) and (value not in VALID_FACTORY_TYPES):
            valid_type_msg = ", ".join(VALID_FACTORY_TYPES)
            raise ValidationError(
                f'Factory Type "{value}" is not one of the permitted values: {valid_type_msg}',
            )


class ReportRecordSerializer(ModelSerializer):
    class Meta:
        model = ReportRecord
        fields = [
            "id",
            "created_at",
            "others",
        ]
