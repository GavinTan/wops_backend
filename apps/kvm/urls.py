from django.urls import path, include
from rest_framework import routers
from apps.kvm import views

router = routers.DefaultRouter()
# router.register(r'users', views.UserViewSet)
# router.register(r'groups', views.GroupViewSet)
router.register(r'node', views.KvmNodesView)
router.register(r'vm', views.KvmVmView, basename='vm')
router.register(r'storage', views.KvmStorageView, basename='storage')
router.register(r'es', views.EsView, basename='es')
router.register(r'wang', views.WangView, basename='wang')
router.register(r'upload', views.FileUploadView, basename='upload')

urlpatterns = [
    path('aa/', views.index),
    path('', include(router.urls)),
]
