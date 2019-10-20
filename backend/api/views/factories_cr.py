from django.http import HttpResponse, JsonResponse
from django.utils.datastructures import MultiValueDictKeyError

from rest_framework.decorators import api_view

from .utils import _get_nearby_factories
from ..models import Factory
from ..serializers import FactorySerializer


def _not_in_taiwan(lat, lng):
    lat_invalid = lat < 22 or lat > 25
    lng_invalid = lng < 120 or lng > 122
    return lat_invalid or lng_invalid


def _radius_strange(radius):
    # NOTE: need discussion about it
    return radius > 100 or radius < 0.01


@api_view(["GET", "POST"])
def get_nearby_or_create_factories(request):
    # TODO
    if request.method == "GET":
        try:
            latitude = request.GET["lat"]  # 緯度: y
            longitude = request.GET["lng"]  # 經度: x
            radius = request.GET["range"]  # km
        except MultiValueDictKeyError:
            missing_params = [
                p
                for p in ("lat", "lng", "range")
                if p not in request.GET
            ]
            missing_params = ", ".join(missing_params)
            return HttpResponse(
                f"Missing query parameter: {missing_params}.",
                status=400,
            )

        latitude = float(latitude)
        longitude = float(longitude)
        if _not_in_taiwan(latitude, longitude):
            return HttpResponse(
                "The query position is not in the range of Taiwan."
                "Valid query parameters should be: "
                "120 < lng < 122, "
                "22 < lat < 25.",
                status=400,
            )

        radius = float(radius)
        if _radius_strange(radius):
            return HttpResponse(
                f"`range` should be within 0.01 to 100 km, but got {radius}",
                status=400,
            )

        nearby_factories = _get_nearby_factories(
            latitude=latitude,
            longitude=longitude,
            radius=radius,
        )

        serializer = FactorySerializer(nearby_factories, many=True)
        return JsonResponse(serializer.data, safe=False)
    elif request.method == "POST":
        pass
