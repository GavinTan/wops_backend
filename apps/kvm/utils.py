#from .common import vmxml
from kvm.models import VmInstance
#from .common import utils
from django.core.cache import cache
import libvirt
import subprocess
import threading


def convert_bytes(size):
    for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024:
            return "%1.0f %s" % (size, x)
        size /= 1024
    return size


def get_vm_ip(node, mac):
    print(node, mac)
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
        print(outs)
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

    def run():
        data = []

        if node.get_status is True:
            node.status = True
            node.cpu = node.get_cpu_count
            node.memory = convert_bytes(node.get_memory_size)
            node.memory_usage = node.get_memory_usage
            node.save()

            node_all_domains = node.proxy.wvm.listAllDomains()
            # node_domain_names = [d.name() for d in node_all_domains]
            #
            # Domains.objects.filter(node=node).exclude(name__in=node_domain_names).delete()

            names = VmInstance.objects.filter(node=node).values_list('name', flat=True)
            for domain in node_all_domains:
                domain_name = domain.name()
                domain_proxy = node.domain_proxy(domain_name)
                vm_data = {
                    'vid': domain_proxy.instance.ID(),
                    'name': domain_name,
                    'uuid': domain_proxy.get_uuid(),
                    'networks': domain_proxy.get_net_devices(),
                    'disks': domain_proxy.get_disk_devices(),
                    'console_type': domain_proxy.get_console_type(),
                    'console_port': domain_proxy.get_console_port(),
                    'status': domain_proxy.get_status(),
                    'cpu': domain_proxy.get_vcpu(),
                    'memory': convert_bytes(domain_proxy.get_memory())
                }

                VmInstance.objects.update_or_create(defaults=vm_data, name=domain_name, node=node)
                data.append(vm_data)

        cache.set(f'kvm:{node.host}:data', data, timeout=60 * 60)

    t = threading.Thread(target=run)
    t.start()
