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
    post_image,
    post_factory_image,
)


urlpatterns = [
    path("factories/", get_nearby_or_create_factories),
    path("factories/<id>/", update_factory_attribute),
    path("factories/<id>/image/", post_factory_image),
    path("images/", post_image),
]
