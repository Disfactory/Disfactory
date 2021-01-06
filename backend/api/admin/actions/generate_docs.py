import datetime
from django.db.models import Max

from api.models import Document, Factory
from api.utils import set_function_attributes


def choose_cet_staff(townname):
    normalized_townname = townname.replace("台", "臺")

    cet_staff_mappings = {
        "蔡佳昇": {"臺北市", "桃園市", "新北市", "新竹縣", "新竹市", "苗栗縣", "臺中縣", "南投縣", "宜蘭縣", "花蓮縣", "金門縣"},
        "吳沅諭": {"彰化縣", "雲林縣", "嘉義縣", "嘉義市", "臺南市", "高雄市", "屏東縣", "臺東縣", "澎湖縣", "連江縣"},
    }

    for staff, counties in cet_staff_mappings.items():
        if any(county in normalized_townname for county in counties):
            return staff


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
                    cet_staff=choose_cet_staff(factory.townname),
                )
            )

            factory.cet_review_status = "X"
            factories.append(factory)

        Document.objects.bulk_create(docs)
        Factory.objects.bulk_update(factories, ["cet_review_status"])
