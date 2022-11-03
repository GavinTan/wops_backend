from kvm.models import VmInstance, VmServer
import django_filters


class VmInstanceFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains')

    class Meta:
        model = VmInstance
        fields = ['name', 'server', 'status']


class VmServerFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains')
    host = django_filters.CharFilter(field_name='host', lookup_expr='icontains')
    create_time = django_filters.DateTimeFilter(field_name='create_time', lookup_expr='gte')

    class Meta:
        model = VmServer
        fields = ['name', 'host', 'status', 'create_time']

