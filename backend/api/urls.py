"""API URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path

from .views import (
    get_nearby_or_create_factories,
    update_factory_attribute,
    get_factory_report,
    post_image_url,
    post_factory_image_url,
    get_factories_count_by_townname,
    get_images_count_by_townname,
    get_report_records_count_by_townname,
    get_statistics_total,
)

urlpatterns = [
    path("factories", get_nearby_or_create_factories),
    path("factories/<factory_id>", update_factory_attribute),
    path("factories/<factory_id>/report_records", get_factory_report),
    path("factories/<factory_id>/images", post_factory_image_url),

    path("statistics/factories", get_factories_count_by_townname),
    path("statistics/images", get_images_count_by_townname),
    path("statistics/report_records", get_report_records_count_by_townname),
    path("statistics/total", get_statistics_total),

    path("images", post_image_url),
]
