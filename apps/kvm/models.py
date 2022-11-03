from django.db import models
from django.utils.functional import cached_property
from kvm.virt.conn import server_available
from kvm.virt.server import VirtServer
from kvm.virt.instance import VirtInstance


# Create your models here.


class VmServer(models.Model):
    class Meta:
        verbose_name = 'KVM宿主机'

    name = models.CharField('名称', max_length=120, db_index=True, null=True, blank=True)
    host = models.CharField('IP', max_length=20, db_index=True, unique=True)
    username = models.CharField('用户名', max_length=20, default='root')
    password = models.CharField('密码', max_length=200, null=True, blank=True)
    conn_port = models.IntegerField('连接端口', default=22)
    conn_type = models.IntegerField('连接类型', default=2)
    cpu = models.IntegerField('CPU', null=True, blank=True)
    memory = models.CharField('内存', max_length=20, null=True, blank=True)
    memory_usage = models.IntegerField('内存使用率', default=0)
    status = models.BooleanField(default=False)
    update_time = models.DateTimeField('更新时间', auto_now=True)
    create_time = models.DateTimeField('创建时间', auto_now_add=True)

    @cached_property
    def proxy(self):
        return VirtServer(self.host, self.username, self.password, self.conn_type, self.conn_port)

    def is_available(self):
        return server_available(self.host, self.conn_port)


class VmInstance(models.Model):
    class Meta:
        verbose_name = '虚拟机'

    name = models.CharField('名称', max_length=120, db_index=True)
    vcpu = models.IntegerField('当前vCPU', null=True, blank=True)
    max_vcpu = models.IntegerField('最大vCPU', null=True, blank=True)
    memory = models.CharField('内存', max_length=20, null=True, blank=True)
    max_memory = models.CharField('最大内存', max_length=20, null=True, blank=True)
    console_type = models.CharField('终端类型', max_length=20, null=True, blank=True)
    console_port = models.CharField('终端端口', max_length=20, null=True, blank=True)
    networks = models.JSONField('网络配置', default=list)
    disks = models.JSONField('硬盘配置', default=list)
    uuid = models.CharField('UUID', max_length=36, null=True, blank=True)
    vid = models.IntegerField('虚拟机ID', null=True, blank=True)
    server = models.ForeignKey(VmServer, on_delete=models.CASCADE)
    ip = models.CharField('IP', max_length=120, null=True, blank=True)
    http_proxy = models.ForeignKey('assets.Proxy', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='代理')
    status = models.IntegerField('状态', null=True, blank=True)
    desc = models.TextField('描述', null=True, blank=True)
    update_time = models.DateTimeField('更新时间', auto_now=True, null=True, blank=True)
    create_time = models.DateTimeField('创建时间', auto_now_add=True, null=True, blank=True)

    @cached_property
    def proxy(self) -> VirtInstance:
        return VirtServer(
            self.server.host,
            self.server.username,
            self.server.password,
            self.server.conn_type,
            self.server.conn_port
        ).get_instance(self.name)
