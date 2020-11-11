from api.utils import set_function_attributes


class RestoreMixin:

    @set_function_attributes(short_description="復原")
    def restore(self, request, queryset):
        queryset.undelete()
