from celery import shared_task, Task

from kvm.virt.server import VirtServer
from kvm.virt.instance import VirtInstance
from kvm.utils import convert_bytes
from kvm.models import VmServer, VmInstance
from django.core.cache import cache
import os
import threading
import libvirt
import multiprocessing
from django.conf import settings
import time

@shared_task
def ssh_copy_id(data):
    os.system(f"sshpass -p {data.get('password')} ssh-copy-id {data.get('host')}")


lock = threading.Lock()

a = []


@shared_task
def update_server_data(pk):
    print('update server data')
    try:
        server = VmServer.objects.get(pk=pk)
    except VmServer.DoesNotExist as e:
        print(e)
    else:
        status = server.is_available()
        server.status = status

        if status:
            vs = VirtServer(server.host, server.username, server.password, server.conn_type, server.conn_port)
            server.cpu = vs.get_info()[2]
            server.memory = convert_bytes(vs.get_info()[1] * 1024 * 1024)
            server.memory_usage = vs.get_memory_usage()['percent']
        server.save()


@shared_task
def update_instance_data(pk):
    print('update instance data')

    try:
        server = VmServer.objects.get(pk=pk)
    except VmServer.DoesNotExist as e:
        print(e)
    else:
        if server.is_available():
            data = []
            domain_name_list = []
            vs = VirtServer(server.host, server.username, server.password, server.conn_type, server.conn_port)

            for domain in vs.get_all_domain():
                name = domain.name()
                instance = vs.get_instance(name)

                vm_data = {
                    'vid': instance.dom.ID(),
                    'name': name,
                    'uuid': instance.dom.UUIDString(),
                    'networks': instance.get_devices_net(),
                    'disks': instance.get_devices_disk(),
                    'console_type': instance.get_console_type(),
                    'console_port': instance.get_console_port(),
                    'status': instance.get_status(),
                    'vcpu': instance.get_vcpu(),
                    'max_vcpu': instance.get_vcpu(4),
                    'memory': convert_bytes(instance.get_memory()),
                    'max_memory': convert_bytes(instance.get_memory(max_memory=True)),
                    'desc': instance.get_desc()
                }

                VmInstance.objects.update_or_create(defaults=vm_data, name=name, server=server)
                data.append(vm_data)
                domain_name_list.append(name)

            VmInstance.objects.filter(server=server).exclude(name__in=domain_name_list).delete()
            cache.set(f'kvm:{server.host}:data', data, timeout=60 * 60)


@shared_task
def update_data():
    for server in VmServer.objects.all():
        update_server_data.delay(server.pk)
        update_instance_data.delay(server.pk)
