from django.contrib.auth import get_user_model
import django_filters


class UserFilter(django_filters.FilterSet):

    class Meta:
        model = get_user_model()
        fields = ['username']
