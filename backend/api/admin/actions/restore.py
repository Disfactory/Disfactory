class RestoreMixin:

    def restore(self, request, queryset):
        queryset.undelete()

    restore.short_description = '復原'
