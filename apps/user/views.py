from django.contrib.auth.models import update_last_login
from rest_framework.response import Response
from rest_framework import viewsets, exceptions, permissions, authentication, status
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import action, renderer_classes, permission_classes
from django.contrib.auth import get_user_model
from .filters import UserFilter
from .serializers import UserSerializer
from datetime import datetime


class UserView(viewsets.ModelViewSet):
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer
    filterset_class = UserFilter

    @action(methods=['post'], detail=False, url_path='login', authentication_classes=[],
            permission_classes=[permissions.AllowAny])
    def login(self, request, *args, **kwargs):
        data = {}
        username = request.data.get('username')
        password = request.data.get('password')
        user_exists = self.get_queryset().filter(username=username).exists()

        if user_exists:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                if user.is_active:
                    update_last_login(None, user)
                    refresh = RefreshToken.for_user(user)
                    data['token'] = str(refresh.access_token)
                    data['status'] = 'ok'
                else:
                    data['status'] = 'error'
                    data['errmsg'] = '用户已禁用，请联系管理员！'
            else:
                data['status'] = 'error'
                data['errmsg'] = '密码错误！'
        else:
            data['status'] = 'error'
            data['errmsg'] = '账号不存在，请联系管理员！'

        return Response(data)

    @action(methods=['post'], detail=False, url_path='logout')
    def logout(self, request, *args, **kwargs):
        return Response()

    @action(methods=['delete'], detail=False, url_path='multiple_delete')
    def multiple_delete(self, request, *args, **kwargs):
        if request.data.get('ids'):
            del_list_id = request.data.get('ids')

            if del_list_id:
                self.queryset.filter(id__in=del_list_id).delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                raise exceptions.NotFound()

        raise exceptions.ValidationError({'detail': '没有删除的ids列表'})
