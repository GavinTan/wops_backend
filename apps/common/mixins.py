from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework import status, exceptions
from rest_framework.response import Response


class BulkDestroyModelMixin:
    @action(methods=['delete'], detail=False, url_path='_bulk')
    def bulk_destroy(self, request: Request):
        ids = request.data.get('ids')

        if ids and isinstance(ids, list):
            filtered = self.queryset.filter(id__in=ids)
            self.perform_bulk_destroy(filtered)
            return Response(status=status.HTTP_204_NO_CONTENT)

        raise exceptions.ValidationError({'detail': '没有删除的ids列表或参数错误!'})

    def perform_destroy(self, instance):
        instance.delete()

    def perform_bulk_destroy(self, instances):
        for instance in instances:
            self.perform_destroy(instance)
