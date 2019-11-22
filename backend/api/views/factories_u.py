from rest_framework.decorators import api_view

from django.http import HttpResponse
from ..models import Factory

from django.contrib.gis.geos import Point

#@api_view(['PUT'])
def update_factory_attribute(request):#, factory_id):
    # GIT before coding
    # git branch issue-name
    # ...
    # git pull
    # git push origin issue-name
    # factory = Factory.objects.get(pk=factory_id)
    # factory.update(pk=factory_id)

    # 1. validate
    # serialize

    # 2. parse GET body
    lat=request.GET['lat']
    lng=request.GET['lng']
    factory_id=request.GET['factory_id']
#   return HttpResponse([lat,lng,factory_id])

  # Revising to read GET body from urls.py /factories_update?factory_id=abc&lat=23.5&lng=120
 #  Factory.objects.filter(id=factory_id).update(**request['PUT'])
    queryset=Factory.objects.filter(id=factory_id)

    # 3. update database
    queryset.update(lat=lat)
    queryset.update(lng=lng)
    return HttpResponse(['lat=',queryset[0].lat,' lng=',queryset[0].lng,' id=',queryset[0].id])
#   queryset.update(point=Point(1,1))
#   queryset.update(status_time='2019-11-20')
