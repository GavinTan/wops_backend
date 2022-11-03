from django.urls import path, include, re_path
from rest_framework import routers
from assets.views import AssetViewSet, ProxyViewSet, ProxyPlatformViewSet


router = routers.DefaultRouter()
router.register(r'asset', AssetViewSet)
router.register(r'proxy', ProxyViewSet)
router.register(r'platform', ProxyPlatformViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
