from django.urls import path, include, re_path
from rest_framework import routers
from kvm.views import VmServerView, VmInstanceView, KvmStorageView, FileUploadView
from kvm.websocket import Kvm

router = routers.DefaultRouter()
router.register(r'server', VmServerView)
router.register(r'instance', VmInstanceView)
# router.register(r'vm', views.KvmVmView, basename='vm')
router.register(r'storage', KvmStorageView, basename='storage')
router.register(r'upload', FileUploadView, basename='upload')

urlpatterns = [
    path('', include(router.urls)),
]

websocket_urlpatterns = [
    re_path(r'ws/kvm/$', Kvm.as_asgi()),
]
