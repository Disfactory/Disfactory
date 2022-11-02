from django.contrib.admin import SimpleListFilter
from django.db.models import Count
from django.db.models.functions import Concat

class DuplicateSectLandFilter(SimpleListFilter):
    title = "Duplicate"
    # Parameter for the filter that will be used in the URL query
    parameter_name = "sect_land"

    def lookups(self, request, model_admin):
        return [
            ("sectland", "地段號")
        ]


    def queryset(self, request, queryset):
        if not self.value():
            return queryset

        if self.value().lower() == "sectland":
            sectland_queryset = queryset.annotate(sectland=Concat("sectcode", "landcode"))
            duplicates = sectland_queryset.values("sectland")\
                .annotate(sectland_count=Count("sectland"))\
                .order_by("sectland").filter(sectland_count__gt=1)

            records = sectland_queryset.filter(sectland__in=[item["sectland"] for item in duplicates])
            return records

