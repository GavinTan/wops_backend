from django.db import models

# Create your models here.


class TreeNodes(models.Model):
    class Meta:
        verbose_name = '资产树节点'

    title = models.CharField('名称', max_length=120, db_index=True)
    key = models.CharField('Key', max_length=60, db_index=True, unique=True)
    parent = models.CharField('父级ID', max_length=60)
    update_time = models.DateTimeField('更新时间', auto_now=True)
    create_time = models.DateTimeField('创建时间', auto_now_add=True)

    def __str__(self):
        return self.title


class Asset(models.Model):
    class Meta:
        verbose_name = '资产'

    name = models.CharField('名称', max_length=60)
    ip = models.CharField('IP', max_length=120, null=True, blank=True)
    proxy = models.ForeignKey('Proxy', on_delete=models.SET_NULL, null=True, blank=True)
    desc = models.TextField('描述', blank=True, null=True)
    tree_node = models.ForeignKey(TreeNodes, on_delete=models.CASCADE, verbose_name='树节点')
    update_time = models.DateTimeField('更新时间', auto_now=True)
    create_time = models.DateTimeField('创建时间', auto_now_add=True)


class ProxyPlatform(models.Model):
    class Meta:
        verbose_name = '代理平台'

    name = models.CharField('名称', max_length=120)
    account = models.JSONField('账号', blank=True, null=True)
    address = models.URLField('平台地址', blank=True, null=True)
    desc = models.TextField('描述', blank=True, null=True)
    update_time = models.DateTimeField('更新时间', auto_now=True)
    create_time = models.DateTimeField('创建时间', auto_now_add=True)

    def __str__(self):
        return self.name


class Proxy(models.Model):
    class Meta:
        verbose_name = '代理'

    ip = models.CharField('IP', max_length=120, db_index=True)
    account = models.JSONField('账号', blank=True, null=True)
    platform = models.ForeignKey(ProxyPlatform, on_delete=models.CASCADE, verbose_name='平台')
    desc = models.TextField('描述', blank=True, null=True)
    update_time = models.DateTimeField('更新时间', auto_now=True)
    create_time = models.DateTimeField('创建时间', auto_now_add=True)

    def __str__(self):
        return self.ip
