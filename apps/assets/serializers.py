from rest_framework import serializers
from assets.models import TreeNodes, Asset, Proxy, ProxyPlatform
from django.core.serializers import serialize


class TreeNodesSerializer(serializers.ModelSerializer):
    class Meta:
        model = TreeNodes
        fields = '__all__'


class AssetSerializer(serializers.ModelSerializer):

    class Meta:
        model = Asset
        fields = '__all__'

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['proxy'] = ProxySerializer(instance=instance.proxy).data
        return representation


class ProxySerializer(serializers.ModelSerializer):
    class Meta:
        model = Proxy
        fields = '__all__'

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['platform'] = ProxyPlatformSerializer(instance=instance.platform).data
        return representation


class ProxyPlatformSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProxyPlatform
        fields = '__all__'
