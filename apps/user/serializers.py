from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['name'] = user.id
        # ...

        return token


class UserSerializer(serializers.ModelSerializer):
    # access = serializers.SerializerMethodField()

    class Meta:
        model = get_user_model()
        exclude = ['is_staff', 'last_name', 'first_name', 'user_permissions', 'groups']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.is_superuser:
            representation['role'] = representation['role'] + ['admin']
        return representation
