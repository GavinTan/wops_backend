from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from rest_framework import serializers
from kvm.models import VmServer, VmInstance
from assets.serializers import ProxySerializer
from kvm.tasks import update_server_data, ssh_copy_id


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ('url', 'username', 'email', 'groups')


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ('url', 'name')


class VmServerSerializer(serializers.ModelSerializer):
    class Meta:
        model = VmServer
        fields = '__all__'
        exclude = []

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        return representation

    def create(self, validated_data):
        instance = self.Meta.model.objects.create(**validated_data)
        if validated_data.get('conn_type') == 'ssh':
            ssh_copy_id.delay(validated_data)
        update_server_data.delay(instance.pk)
        return instance


class KvmMangeSerializer(serializers.Serializer):
    node = serializers.CharField(max_length=60)
    node = serializers.SerializerMethodField()
    def get_node(self, obj):
        return obj.node.host


class VmInstanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = VmInstance
        fields = '__all__'
        exclude = []

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.server:
            representation['server'] = VmServerSerializer(instance=instance.server).data
        if instance.http_proxy:
            representation['http_proxy'] = ProxySerializer(instance=instance.http_proxy).data
        return representation
