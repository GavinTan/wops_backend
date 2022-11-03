from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.


class User(AbstractUser):
    name = models.CharField(max_length=20, blank=True)
    phone = models.CharField(max_length=11, blank=True)
    address = models.CharField(max_length=200, blank=True)
    role = models.JSONField(default=list)
    avatar = models.URLField(default='https://gw.alipayobjects.com/zos/antfincdn/XAosXuNZyF/BiazfanxmamNRoxxVxka.png')

    # 登录使用字段
    USERNAME_FIELD = 'username'
    # 通过 createsuperuser 命令行时候必填字段
    REQUIRED_FIELDS = ['name']

    class Meta:
        verbose_name = '用户列表'
        db_table = 'auth_user'
