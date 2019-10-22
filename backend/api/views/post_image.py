from rest_framework.decorators import api_view

from .utils import _upload_image


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
