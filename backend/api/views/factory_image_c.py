from rest_framework.decorators import api_view

from .utils import _upload_image


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
