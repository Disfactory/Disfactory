from .models import Factory
import easymap


def update_landcode(factory_id):
    factory = Factory.objects.get(pk=factory_id)
    land_number = easymap.get_land_number(factory.lng, factory.lat)['landno']
    Factory.objects.filter(pk=factory_id).update(landcode=land_number)
