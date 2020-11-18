from django.contrib import admin

from api.models import (
    Factory,
    Image,
    ReportRecord,
)
from api.models.factory import RecycledFactory
from api.models.document import Document, CETNext, CETReportStatus, GovResponseStatus, FollowUp
from api.models.image import RecycledImage
from api.models.report_record import RecycledReportRecord
from .factory import FactoryAdmin, RecycledFactoryAdmin
from .image import ImageAdmin, RecycledImageAdmin
from .report_record import ReportRecordAdmin, RecycledReportRecordAdmin
from api.admin.document import DocumentAdmin, CETNextAdmin, CETReportStatusAdmin, GovResponseStatusAdmin, FollowUpAdmin

# Register your models here.
admin.register(Factory)(FactoryAdmin)
admin.register(RecycledFactory)(RecycledFactoryAdmin)

admin.register(Image)(ImageAdmin)
admin.register(RecycledImage)(RecycledImageAdmin)

admin.register(ReportRecord)(ReportRecordAdmin)
admin.register(RecycledReportRecord)(RecycledReportRecordAdmin)

admin.register(Document)(DocumentAdmin)

admin.register(CETNext)(CETNextAdmin)
admin.register(CETReportStatus)(CETReportStatusAdmin)
admin.register(GovResponseStatus)(GovResponseStatusAdmin)
admin.register(FollowUp)(FollowUpAdmin)
