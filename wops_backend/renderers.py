from rest_framework.renderers import JSONRenderer
from rest_framework.views import exception_handler
from rest_framework import status


class CustomJSONRenderer(JSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):

        status_code = renderer_context.get('response').status_code
        if status_code == status.HTTP_200_OK and renderer_context.get('view').get_view_name() != 'Api Root':
            data = {'code': status_code, 'success': True, 'data': data}
        response = super().render(data, accepted_media_type, renderer_context)
        return response


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        data = {
            'code': response.status_code,
            'data': {},
            'errmsg': str(exc)
        }
        response.data = data
    else:
        print(99999)
        print(exc)
    return response
