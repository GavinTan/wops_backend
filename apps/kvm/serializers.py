from django.contrib.auth.models import User, Group
from rest_framework import serializers
from .models import KvmNodes


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'username', 'email', 'groups')


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ('url', 'name')


class KvmNodesSerializer(serializers.ModelSerializer):
    class Meta:
        model = KvmNodes
        fields = '__all__'
        exclude = []


class KvmMangeSerializer(serializers.Serializer):
    node = serializers.CharField(max_length=60)
