from apps.kvm.common import vmxml
from apps.kvm.models import KvmDomains
from apps.kvm.common import utils
from django.core.cache import cache
import libvirt
import subprocess


def convert_bytes(size):
    for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            return "%3.1f %s" % (size, x)
        size /= 1024.0
    return size


def get_vm_ip(node, mac):
    net = node.split('.')
    del net[-1]
    net = '.'.join(net) + '.0'
    p = 24

    cmd = "ssh root@{0} nmap -sn {1}/{2}|grep -i '{3}' -B2".format(node, net, p, mac) + \
          "|grep 'Nmap scan report for'|awk '{print $5}'"

    s = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, close_fds=True,
                         executable='/bin/bash')
    ret = None
    try:
        outs, errs = s.communicate(timeout=30)
        if s.returncode == 0:
            ret = outs.decode("utf-8").strip()
    except subprocess.TimeoutExpired:
        s.kill()

    return ret


def get_vm_data(node_data):
    ret = {}
    data = []
    try:
        conn = libvirt.open(f"qemu+{node_data['conn_type']}://{node_data['username']}@{node_data['host']}/system")
        ret['memory'] = convert_bytes(conn.getInfo()[1] * 1024 * 1024)
        ret['cpu'] = conn.getInfo()[2]
        ret['status'] = True

        node_memory_stats = conn.getMemoryStats(-1, 0)
        if isinstance(node_memory_stats, dict):
            free_mem = (node_memory_stats['buffers'] +
                        node_memory_stats['free'] +
                        node_memory_stats['cached'])
            total_mem = node_memory_stats['total']
            percent = abs(100 - ((free_mem * 100) // total_mem))
            usage = (total_mem - free_mem)
            ret['memory_usage'] = percent

        domains = conn.listAllDomains()
        for domain in domains:
            domain_xml = domain.XMLDesc()
            x = vmxml.VmXmlParse(domain_xml)
            network = x.get_net_devices()
            console_port = x.get_console_port()
            console_type = x.get_console_type()
            ip = get_vm_ip(node_data['host'], network['mac_address'])
            vm_data = {'id': domain.ID() + node_data['id'] + 1000, 'host': ip, 'name': domain.name(),
                       'console_port': console_port, 'console_type': console_type,
                       'status': domain.info()[0], 'cpu': domain.info()[3],
                       'memory': convert_bytes(domain.info()[2] * 1024), 'form_host': node_data['host']}
            data.append(vm_data)
            # print(domain.ID(), domain.name(), domain.info())
        conn.close()

        ret['vm_data'] = data

    except Exception as exc:
        ret['status'] = False
        ret['cpu'] = ''
        ret['emory'] = ''
        ret['memory_usage'] = 0
        ret['vm_data'] = []

    finally:
        ret['id'] = node_data['id']
        ret['host'] = node_data['host']
        return ret


def get_domains(node):
    data = {'id': node.id, 'host': node.host, 'status': node.status}

    if node.status is True:
        data['cpu'] = node.cpu_count
        data['memory'] = convert_bytes(node.memory_size)
        data['memory_usage'] = node.memory_usage
        data['vm_data'] = []

        domains = node.proxy.wvm.listAllDomains()
        domain_names = [d.name() for d in domains]

        KvmDomains.objects.filter(node=node).exclude(name__in=domain_names).delete()

        names = KvmDomains.objects.filter(node=node).values_list('name', flat=True)
        for domain in domains:
            if domain.name() not in names:
                KvmDomains(node=node, name=domain.name(), uuid=domain.UUIDString()).save()
        for d in KvmDomains.objects.filter(node=node):
            vm_data = {'vid': d.proxy.instance.ID(), 'name': d.name, 'id': d.uuid, 'networks': d.networks,
                       'disks': d.disks, 'console_type': d.console_type, 'console_port': d.console_port,
                       'status': d.status, 'cpu': d.vcpu, 'memory': f'{d.memory} MB', 'node': d.node.host}
            data['vm_data'].append(vm_data)
    else:
        data['cpu'] = ''
        data['memory'] = ''
        data['memory_usage'] = 0
        data['vm_data'] = []

    cache.set(f'kvm:{node.host}:data', data, timeout=60 * 60)
