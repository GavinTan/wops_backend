from assets.models import TreeNodes, Asset, Proxy, ProxyPlatform
import django_filters


class ProxyFilter(django_filters.FilterSet):
    ip = django_filters.CharFilter(field_name='ip', lookup_expr='icontains')
    platform = django_filters.CharFilter(field_name='platform__name', lookup_expr='icontains')
    account = django_filters.CharFilter(field_name='account', lookup_expr='icontains')
    create_time = django_filters.DateTimeFilter(field_name='create_time', lookup_expr='gte')

    class Meta:
        model = Proxy
        fields = ['ip', 'platform', 'account', 'create_time']


class ProxyPlatformFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains')
    account = django_filters.CharFilter(field_name='account', lookup_expr='icontains')
    create_time = django_filters.DateTimeFilter(field_name='create_time', lookup_expr='gte')

    class Meta:
        model = ProxyPlatform
        fields = ['name', 'account', 'create_time']

