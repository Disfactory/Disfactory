from .factories_cr import get_nearby_or_create_factories
from .factories_u import update_factory_attribute
from .factory_report_record_r import get_factory_report
from .image_c import post_image_url
from .factory_image_c import post_factory_image_url
from .statistics_r import get_factories_count_by_townname
from .statistics_r import get_images_count_by_townname
from .statistics_r import get_report_records_count_by_townname
from .statistics_r import get_statistics_total

# To be deprecated
from .miscellaneous.image_c import post_image
from .miscellaneous.factory_image_c import post_factory_image
