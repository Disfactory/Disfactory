from django.http import HttpResponse, JsonResponse

from rest_framework.decorators import api_view

from .serializers import FactorySerializer


def _get_nearby_factories(latitude, longitude, radius):
    """Return nearby factories based on position and search range.
    """
    # TODO
    # if use GeoDjango, the code might looks like:

    # from django.contrib.gis.geos import GEOSGeometry
    # from django.contrib.gis.measure import D
    # point = GEOSGeometry(
    #     f"POINT({longitude} {latitude})",
    #     srid=settings.DEFAULT_SRID,
    # )
    # return Factory.objects.filter(point__distance_lte=(point, D(km=radius))

    # ref: https://docs.djangoproject.com/en/2.2/ref/contrib/gis/db-api/#distance-lookups
    pass


def _upload_image(f_image):
    """Upload Image to certain service."""
    # TODO
    # image_binary = f_image.read()
    # resp = requests.post(...)
    path = "path to image cdn"
    return path


@api_view(['GET', 'POST'])
def get_nearby_or_create_factories(request):
    # TODO
    if request.method == 'GET':
        latitude = request.GET.get('lat')
        longitude = request.GET.get('lng')
        radius = request.GET.get('range')

        nearby_factories = _get_nearby_factories(latitude, longitude, radius)

        serializer = FactorySerializer(nearby_factories, many=True)
        return JsonResponse(serializer.data, safe=False)
    elif request.method == 'POST':
        pass


@api_view(['PUT'])
def update_factory_attribute(request, factory_id):
    # TODO
    pass


@api_view(['POST'])
def post_image(request):
    # TODO
    # f_image = request.FILE
    # path = _upload_image(f_image)
    # args = {
    #     'uri': path,
    # }
    # img = Image.object.create(**args)
    # token = img.token
    # return Response(...)
    pass


@api_view(['POST'])
def post_factory_image(request, factory_id):
    # TODO
    # f_image = request.FILE
    # path = _upload_image(f_image)
    # factory = Factory.objects.get(pk=factory_id)
    # args = {
    #     'uri': path,
    #     'factory': factory,
    # }
    # img = Image.object.create(**args)
    # token = img.token
    # return Response(...)
    pass
