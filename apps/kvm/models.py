from django.db import models
from django.utils.functional import cached_property
from apps.kvm.common.node import KvmNodeBase
from apps.kvm.common.kvm import connection_manager
from apps.kvm.common.vm import KvmVmBase, VmStorage
from apps.kvm.common.create import VmCreate
from libvirt import virConnect
from libvirt import VIR_DOMAIN_XML_SECURE
import uuid

# Create your models here.


class KvmNodes(models.Model):
    class Meta:
        verbose_name = 'KVM宿主机'

    host = models.CharField('IP', max_length=20)
    username = models.CharField('用户名', max_length=20, default='root')
    password = models.CharField('密码', max_length=200, null=True, blank=True)
    conn_type = models.CharField('连接类型', max_length=20, default='ssh')

    @cached_property
    def connection(self):
        try:
            return connection_manager.get_connection(
                self.host,
                self.username,
                self.password,
                self.conn_type,
            )
        except Exception as e:
            return e

    @cached_property
    def status(self):
        # return connection_manager.host_is_up(self.type, self.hostname)
        # TODO: looks like socket has problems connecting via VPN
        if isinstance(self.connection, virConnect):
            return True
        else:
            return self.connection

    @cached_property
    def proxy(self):
        return KvmNodeBase(
            self.host,
            self.username,
            self.password,
            self.conn_type,
        )

    @cached_property
    def get_volumes(self):
        conn = VmStorage(self.host, self.username, self.password, self.conn_type, 'iso')
        conn.refresh()
        return conn.get_volumes()

    @cached_property
    def cpu_count(self):
        return self.proxy.get_node_info()[3]

    @cached_property
    def memory_size(self):
        return self.proxy.get_node_info()[2]

    @cached_property
    def memory_usage(self):
        return self.proxy.get_memory_usage()['percent']

    @cached_property
    def create(self):
        conn = VmCreate(self.host, self.username, self.password, self.conn_type)
        return conn


class KvmDomains(models.Model):
    class Meta:
        verbose_name = '虚拟机'

    name = models.CharField('名称', max_length=120, db_index=True, unique=True)
    uuid = models.CharField('uuid', max_length=36, db_index=True)
    node = models.ForeignKey(KvmNodes, on_delete=models.CASCADE)

    @cached_property
    def proxy(self):
        return KvmVmBase(
            self.node.host,
            self.node.username,
            self.node.password,
            self.node.conn_type,
            self.name,
        )

    @cached_property
    def media(self):
        return self.proxy.get_media_devices()

    @cached_property
    def media_iso(self):
        return sorted(self.proxy.get_iso_media())

    @cached_property
    def disks(self):
        return self.proxy.get_disk_devices()

    @cached_property
    def status(self):
        return self.proxy.get_status()

    @cached_property
    def autostart(self):
        return self.proxy.get_autostart()

    @cached_property
    def bootmenu(self):
        return self.proxy.get_bootmenu()

    @cached_property
    def boot_order(self):
        return self.proxy.get_bootorder()

    @cached_property
    def arch(self):
        return self.proxy.get_arch()

    @cached_property
    def machine(self):
        return self.proxy.get_machine_type()

    @cached_property
    def firmware(self):
        return self.proxy.get_loader()

    @cached_property
    def nvram(self):
        return self.proxy.get_nvram()

    @cached_property
    def vcpu(self):
        return self.proxy.get_vcpu()

    @cached_property
    def vcpu_range(self):
        return self.proxy.get_max_cpus()

    @cached_property
    def cur_vcpu(self):
        return self.proxy.get_cur_vcpu()

    @cached_property
    def vcpus(self):
        return self.proxy.get_vcpus()

    @cached_property
    def get_uuid(self):
        return self.proxy.get_uuid()

    @cached_property
    def memory(self):
        return self.proxy.get_memory()

    @cached_property
    def cur_memory(self):
        return self.proxy.get_cur_memory()

    @cached_property
    def title(self):
        return self.proxy.get_title()

    @cached_property
    def description(self):
        return self.proxy.get_description()

    @cached_property
    def networks(self):
        return self.proxy.get_net_devices()

    @cached_property
    def qos(self):
        return self.proxy.get_all_qos()

    @cached_property
    def telnet_port(self):
        return self.proxy.get_telnet_port()

    @cached_property
    def console_type(self):
        return self.proxy.get_console_type()

    @cached_property
    def console_port(self):
        return self.proxy.get_console_port()

    @cached_property
    def console_keymap(self):
        return self.proxy.get_console_keymap()

    @cached_property
    def console_listen_address(self):
        return self.proxy.get_console_listen_addr()

    @cached_property
    def guest_agent(self):
        return False if self.proxy.get_guest_agent() is None else True

    @cached_property
    def guest_agent_ready(self):
        return self.proxy.is_agent_ready()

    @cached_property
    def video_model(self):
        return self.proxy.get_video_model()

    @cached_property
    def video_models(self):
        return self.proxy.get_video_models(self.arch, self.machine)

    @cached_property
    def snapshots(self):
        return sorted(self.proxy.get_snapshot(), reverse=True, key=lambda k: k['date'])

    @cached_property
    def inst_xml(self):
        return self.proxy._XMLDesc(VIR_DOMAIN_XML_SECURE)

    @cached_property
    def has_managed_save_image(self):
        return self.proxy.get_managed_save_image()

    @cached_property
    def console_passwd(self):
        return self.proxy.get_console_passwd()

    @cached_property
    def cache_modes(self):
        return sorted(self.proxy.get_cache_modes().items())

    @cached_property
    def io_modes(self):
        return sorted(self.proxy.get_io_modes().items())

    @cached_property
    def discard_modes(self):
        return sorted(self.proxy.get_discard_modes().items())

    @cached_property
    def detect_zeroes_modes(self):
        return sorted(self.proxy.get_detect_zeroes_modes().items())

    @cached_property
    def formats(self):
        return self.proxy.get_image_formats()