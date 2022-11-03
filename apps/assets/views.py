from django.shortcuts import render
from rest_framework import filters
from rest_framework import viewsets, exceptions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from common.mixins import BulkDestroyModelMixin
from assets.models import TreeNodes, Asset, Proxy, ProxyPlatform
from assets.serializers import TreeNodesSerializer, AssetSerializer, ProxySerializer, ProxyPlatformSerializer
from assets.filters import ProxyFilter, ProxyPlatformFilter
from django.http import FileResponse
from django.conf import settings

# Create your views here.


class AssetViewSet(viewsets.ModelViewSet, BulkDestroyModelMixin):
    queryset = Asset.objects.all()
    serializer_class = AssetSerializer

    def get_queryset(self):
        tree_key = self.request.query_params.get('treeKey')
        if tree_key and tree_key != '0-0':
            self.queryset = Asset.objects.filter(tree_node=TreeNodes.objects.get(key=tree_key)).all()

        return super().get_queryset()

    @action(methods=['get', 'post', 'delete'], detail=False, url_path='tree')
    def get_tree_node(self, request, *args, **kwargs):
        if request.method == 'GET':
            a = request.query_params.get('a')
            if a == 'get_list':
                data = TreeNodesSerializer(TreeNodes.objects.all(), many=True).data
            else:
                data = [{'title': 'Default', 'key': '0-0', 'parent': '0'}]

                for i in TreeNodes.objects.all():
                    if i.key == '0-0':
                        data[0]['title'] = i.title
                    else:
                        data.append({'title': i.title, 'key': i.key, 'parent': i.parent})

                def generate_tree(source, parent):
                    tree = []
                    for item in source:
                        if item['parent'] == parent:
                            item['children'] = generate_tree(source, item['key'])
                            tree.append(item)
                    return tree
                data = generate_tree(data, '0')
            return Response(data)

        if request.method == 'POST':
            TreeNodes.objects.update_or_create(key=request.data.get('key'), defaults=request.data)
            return Response()

        if request.method == 'DELETE':
            t = TreeNodes.objects.filter(key=request.data.get('key')).first()
            if t:
                TreeNodes.objects.filter(parent=t.key)
                key = t.key
                for i in TreeNodes.objects.all():
                    if i.parent == key:
                        key = i.key
                        i.delete()
                t.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                raise exceptions.NotFound()


class ProxyViewSet(viewsets.ModelViewSet, BulkDestroyModelMixin):
    queryset = Proxy.objects.all()
    serializer_class = ProxySerializer
    filter_class = ProxyFilter


class ProxyPlatformViewSet(viewsets.ModelViewSet, BulkDestroyModelMixin):
    queryset = ProxyPlatform.objects.all()
    serializer_class = ProxyPlatformSerializer
    filter_class = ProxyPlatformFilter
