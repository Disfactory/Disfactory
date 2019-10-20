from django.http import HttpResponse, JsonResponse

from rest_framework.decorators import api_view

from .utils import _get_nearby_factories
from ..models import Factory
from ..serializers import FactorySerializer



@api_view(['GET', 'POST'])
def get_nearby_or_create_factories(request):
    # TODO
    if request.method == 'GET':
        latitude = request.GET.get('lat')
        longitude = request.GET.get('lng')
        radius = request.GET.get('range')  # km

        nearby_factories = _get_nearby_factories(latitude, longitude, radius)

        serializer = FactorySerializer(nearby_factories, many=True)
        return JsonResponse(serializer.data, safe=False)
    elif request.method == 'POST':
        pass
