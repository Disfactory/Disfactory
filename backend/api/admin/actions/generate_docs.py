import datetime
from django.db.models import Max

from api.models import Document, Factory
from api.utils import set_function_attributes, normalize_townname


class GenerateDocsMixin:
    @set_function_attributes(short_description="產生公文")
    def generate_docs(self, request, queryset):
        user = request.user
        taiwan_year = datetime.date.today().year - 1911

        # NOTE: code format YYYXXXX
        # YYY is taiwan year, XXXX is serial number
        previous_code = Document.objects.aggregate(Max("code"))["code__max"]

        if not previous_code or previous_code < taiwan_year * (10 ** 4):
            previous_code = taiwan_year * (10 ** 4)

        docs = []
        factories = []

        for code, factory in enumerate(queryset, start=previous_code + 1):
            docs.append(
                Document(
                    factory_id=factory.id,
                    creator_id=user.id,
                    code=code,
                    cet_staff="賴沛蓮",
                )
            )

            factory.cet_review_status = "X"
            factories.append(factory)

        Document.objects.bulk_create(docs)
        Factory.objects.bulk_update(factories, ["cet_review_status"])
