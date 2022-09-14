from api.utils import set_function_attributes
from django.db.models import Max

from api.models import Factory, Image, ReportRecord, Document, FollowUp


class MergeFactoriesMixin:
    @set_function_attributes(short_description="合併工廠")
    def merge_factories(self, request, queryset):
        selected_factories = list(queryset)
        selected_factories.sort(
            key=lambda item: item.display_number, reverse=True)

        # collect all images, report_records and documents.
        images = []
        report_records = []
        documents = []

        for selected_factory in selected_factories:
            for item in Image.objects.filter(factory=selected_factory):
                images.append(item)

            for item in ReportRecord.objects.filter(factory=selected_factory):
                report_records.append(item)

            for item in Document.objects.filter(factory=selected_factory):
                documents.append(item)

        # Copy latest factory
        new_factory = selected_factories[-1]
        new_factory.id = None
        num = Factory.raw_objects.aggregate(Max("display_number"))
        new_factory.display_number = num["display_number__max"] + 1
        new_factory.save()

        # copy report record
        report_record_id_map = {}
        for report_record in report_records:
            old_id = report_record.id
            report_record.id = None
            report_record.factory = new_factory
            report_record.save()
            report_record_id_map[old_id] = report_record.id

        # copy image
        for image in images:
            image.id = None
            image.factory = new_factory
            if image.report_record_id in report_record_id_map:
                image.report_record_id = report_record_id_map[image.report_record_id]
            image.save()

        # copy document

        # NOTE: code format YYYXXXX
        # YYY is taiwan year, XXXX is serial number
        previous_code = Document.objects.aggregate(Max("code"))["code__max"]
        for document in documents:
            follow_ups = FollowUp.objects.filter(document=document)

            document.id = None
            document.factory = new_factory
            document.code = previous_code + 1
            document.save()

            for follow_up in follow_ups:
                follow_up.id = None
                follow_up.document = document
                follow_up.save()

            previous_code += 1
