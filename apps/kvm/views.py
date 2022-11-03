from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, mixins
from kvm.serializers import *
from kvm.filters import *
from kvm.models import VmServer, VmInstance
from kvm.utils import get_domains, convert_bytes, get_vm_ip
from kvm.tasks import update_instance_data
#from kvm.common.utils import randomUUID, randomMAC
from common import exceptions
from django.core.cache import cache
from uuid import uuid4
from rest_framework.parsers import FileUploadParser, MultiPartParser
from rest_framework.decorators import action, renderer_classes
from rest_framework.request import Request
from rest_framework import status
from django.conf import settings
from common.mixins import BulkDestroyModelMixin
from wops_backend.pagination import CustomPagination
import os
import string
import random
import libvirt
import re
import xml.etree.cElementTree as ET
from rest_framework.pagination import LimitOffsetPagination


# Create your views here.


class UserViewSet(viewsets.ModelViewSet):
    """
    允许用户查看或编辑的API路径。
    """
    queryset = get_user_model().objects.all().order_by('-date_joined')
    serializer_class = UserSerializer


class GroupViewSet(viewsets.ModelViewSet):
    """python 字典删除key 不存在不报错
    允许组查看或编辑的API路径。
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class VmServerView(viewsets.ModelViewSet, BulkDestroyModelMixin):
    queryset = VmServer.objects.all()
    serializer_class = VmServerSerializer
    filter_class = VmServerFilter

    def create(self, request, *args, **kwargs):
        data = request.data
        return super().create(request, *args, **kwargs)

    def destroy(self, *args, **kwargs):
        serializer = self.get_serializer(self.get_object())
        cache.delete_pattern(f"kvm:{serializer.data['host']}:data")
        return super().destroy(*args, **kwargs)


class VmInstanceView(viewsets.ModelViewSet, BulkDestroyModelMixin):
    queryset = VmInstance.objects.all()
    serializer_class = VmInstanceSerializer
    filter_class = VmInstanceFilter

    def list(self, request, *args, **kwargs):
        a = request.query_params.get('a')
        if a == 'refresh':
            for server in VmServer.objects.all():
                update_instance_data.delay(server.pk)
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        data = request.data

        try:
            server = VmServer.objects.get(pk=data.pop('server'))
        except VmServer.DoesNotExist:
            pass
        else:
            print(data)
            domain_xml = data.get('xml')

            # tree = ET.fromstring(domain_xml)
            # for device in tree.findall('devices/disk'):
            #     if device.get('device') == 'disk':
            #         disk_file = device.find('source').get('file')

            if domain_xml:
                domain = server.proxy.xml_create(domain_xml)
                name = domain.name()
                # domain.create()

                # name = ''
                # for i in range(data.get('num')):
                #     if i > 0:
                #         new_name = name
                #         name_split = name.split('_')
                #         if len(name_split) > 0:
                #             domain_xml = re.sub('<uuid>.*</uuid>', f'<uuid>{uuid4()}</uuid>', domain_xml)
                #             name_suffix = name_split.pop(-1)
                #             if name_suffix.isdigit():
                #                 new_name = f"{'_'.join(name_split)}_{int(name_suffix) + i}"
                #             else:
                #                 new_name = f"{'_'.join(name_split)}_{name_suffix}_{i}"
                #         domain_xml = domain_xml.replace(f'<name>{name}</name>', f'<name>{new_name}</name>')
                #     domain = node.create.wvm.defineXML(domain_xml)
                #     name = domain.name()
                #     # domain.create()

            elif data.get('tpl'):
                pass
            else:
                new_volume = None
                try:
                    name = data.get('name')
                    pool = data.pop('pool')
                    autostart = data.pop('autostart')
                    sys_disk_type = data.pop('sysDiskType')
                    data['arch'] = server.proxy.get_info()[0]

                    for i in range(data.pop('num')):
                        if i > 0:
                            name_split = name.split('_')
                            if len(name_split) > 1:
                                name_suffix = name_split.pop(-1)
                                if name_suffix.isdigit():
                                    data['name'] = f"{'_'.join(name_split)}_{int(name_suffix) + i}"
                                else:
                                    data['name'] = f"{'_'.join(name_split)}_{name_suffix}_{i}"
                            else:
                                data['name'] = f'{name}_{i}'
                        if sys_disk_type == 'new':
                            new_volume = server.proxy.create_volume(data.get('name'), data.pop('diskSize'), pool)
                            data['disk'] = new_volume
                        domain = server.proxy.create_instance(**data)
                        domain.create()
                        if autostart:
                            domain.setAutostart(1)
                except libvirt.libvirtError as e:
                    if new_volume:
                        server.proxy.delete_volume(new_volume)
                    raise exceptions.APIException(e)
                else:
                    update_instance_data.delay(server.pk)
            return Response()

    def destroy(self, request, *args, **kwargs):
        data = request.data
        instance = self.get_object()

        if instance.proxy.is_running():
            snapshots = instance.proxy.get_snapshots()
            instance.proxy.force_shutdown()
        else:
            snapshots = []

        for i in data.get('delOption', []):
            if i == 'delSnapshot':
                for snapshot in snapshots:
                    instance.proxy.snapshot_delete(snapshot['name'])
            if i == 'delDisk':
                instance.proxy.delete_all_disks()

        instance.proxy.delete()
        return super().destroy(request, *args, **kwargs)

    @action(methods=['post'], detail=False, url_path='_action')
    def domain_action(self, request):
        a = request.data.get('action')
        instance_id = request.data.get('instanceId')
        print(request.data)
        try:
            instance = VmInstance.objects.get(id=instance_id)
        except VmInstance.DoesNotExist:
            raise exceptions.WorkflowError('实例不存在')

        if a == 'start':
            if instance.proxy.is_running() == 0:
                instance.proxy.start()
                instance.status = instance.proxy.get_status()
                instance.save()
            return Response()

        if a == 'shutdown':
            if instance.proxy.is_running():
                instance.proxy.shutdown()
                instance.status = instance.proxy.get_status()
                instance.save()
            return Response()

        if a == 'destroy':
            if instance.proxy.is_running():
                instance.proxy.force_shutdown()
                instance.status = instance.proxy.get_status()
                instance.save()
            return Response()

        if a == 'reboot':
            if instance.proxy.is_running():
                instance.proxy.reboot()
            return Response()

        if a == 'console':
            cache.set('console', VmInstanceSerializer(instance=instance).data)
            return Response()

        if a == 'getIp':
            mac = ''
            for i in instance.networks:
                if i.get('nic') == 'br0':
                    mac = i.get('mac')
            ip = get_vm_ip(instance.server.host, mac)
            instance.ip = ip
            instance.save()
            return Response({'ip': ip})

        if a == 'setProxy':
            proxy = request.data.get('proxy')
            instance.http_proxy_id = proxy
            instance.save()
            return Response({'http_proxy': ProxySerializer(instance=instance.http_proxy).data})

        if a == 'setName':
            name = request.data.get('name', instance.name)

            if instance.proxy.is_running():
                raise exceptions.Error('实例必须在关机状态下才能重命名!')
            elif instance.proxy.get_snapshots():
                raise exceptions.Error('存在快照不允许重命名!')
            else:
                instance.proxy.dom.rename(name)
                instance.name = name
                instance.save()
                return Response()

        if a == 'setCpu':
            vcpu = request.data.get('vcpu')
            max_vcpu = request.data.get('maxVcpu')

            try:
                if isinstance(max_vcpu, int):
                    if max_vcpu != instance.max_vcpu:
                        instance.proxy.set_vcpu(max_vcpu, 4 | 2)

                if isinstance(vcpu, int):
                    if instance.proxy.is_running():
                        if vcpu < instance.vcpu:
                            raise Exception('当前虚拟机在运行，通过热更新配置只能增加配置不能减少')
                        instance.proxy.set_vcpu(vcpu, 1)
                    instance.proxy.set_vcpu(vcpu, 2)
            except Exception as e:
                raise exceptions.Error(e)

            return Response()

        if a == 'setMemory':
            memory = request.data.get('memory')
            # b = instance.proxy.set_memory(memory * 1024, 4)
            # a = instance.proxy.set_memory(memory * 1024, 2)
            if isinstance(memory, int):
                size = int(memory) * 1024 * 1024

                instance.proxy.set_memory(size, 4)
                #
                # if instance.proxy.is_running():
                #     a = instance.proxy.set_memory(size, 1)
                # else:
                #     a = instance.proxy.set_memory(size, 2)

                print(memory)
                print(a)
                return Response()

            raise exceptions.Error('参数错误')

        if a == 'getBoot':
            ret = {}
            boot_list = []
            xml_root = ET.fromstring(instance.proxy.get_xml())
            xml_os = xml_root.find('os')

            if xml_os.find('bootmenu') is None:
                ret['bootmenu'] = False
            else:
                if xml_os.find('bootmenu').get('enable') == 'yes':
                    ret['bootmenu'] = True
                else:
                    ret['bootmenu'] = False

            if xml_os.find('boot') is None:
                for disk in xml_root.findall('devices/disk'):
                    dev = disk.find('target').get('dev')
                    boot = disk.find('boot')
                    data = {'dev': dev}

                    if boot is not None:
                        data['order'] = int(boot.get('order'))

                    boot_list.append(data)

                for i, e in enumerate(boot_list):
                    if e.get('order'):
                        boot_list.insert(e.get('order') - 1, boot_list.pop(i))
            else:
                data = [[], [], [], []]

                for boot_index, boot in enumerate(xml_os.findall('boot')):
                    for disk_index, disk in enumerate(xml_root.findall('devices/disk')):
                        boot_data = {'dev': disk.find('target').get('dev'), 'order': boot_index + disk_index + 1}
                        if boot.get('dev') == 'hd' and disk.get('device') == 'disk':
                            data[boot_index].append(boot_data)

                        elif boot.get('dev') == 'cdrom' and disk.get('device') == 'cdrom':
                            data[boot_index].append(boot_data)

                        elif boot.get('dev') == 'fd' and disk.get('device') == 'floppy':
                            data[boot_index].append(boot_data)
                        else:
                            data[3].append({'dev': disk.find('target').get('dev')})


                for i in data:
                    boot_list.extend(sorted(i, key=lambda x: x.get('dev')))

            print(boot_list)
            ret['bootlist'] = boot_list
            return Response(ret)

        if a == 'setBoot':
            print(request.data)
            bootmenu = request.data.get('bootmenu')
            boot_order_list = request.data.get('boot', [])

            xml_root = ET.fromstring(instance.proxy.get_xml())
            xml_os = xml_root.find('os')

            if xml_os.find('bootmenu') is None:
                xml_bootmenu = ET.SubElement(xml_os, 'bootmenu')
                xml_bootmenu.set('enable', 'yes' if bootmenu else 'no')
                xml_bootmenu.set('timeout', '3000')
            else:
                xml_os.find('bootmenu').set('enable', 'yes' if bootmenu else 'no')

            for disk in xml_root.findall('devices/disk'):
                dev = disk.find('target').get('dev')
                boot = disk.find('boot')

                if dev in boot_order_list:
                    for xml_os_boot in xml_os.findall('boot'):
                        xml_os.remove(xml_os_boot)

                    if boot is None:
                        new_boot = ET.SubElement(disk, 'boot')
                        new_boot.set('order', f'{boot_order_list.index(dev) + 1}')
                    else:
                        boot.set('order', f'{boot_order_list.index(dev) + 1}')
                else:
                    if boot is not None:
                        disk.remove(boot)
            instance.server.proxy.define_domain(ET.tostring(xml_root).decode())
            return Response()

        if a == 'revertSnapshot':
            snapshot_name = request.data.get('name')
            if instance.server.is_available():
                instance.proxy.snapshot_revert(snapshot_name)
            return Response()

        if a == 'getSnapshot':
            data = []
            if instance.server.is_available():
                data = instance.proxy.get_snapshots()
            return Response(data)

        if a == 'createSnapshot':
            snapshot_name = request.data.get('name')
            snapshot_desc = request.data.get('desc', ' ')
            if instance.server.is_available():
                instance.proxy.snapshot_create(snapshot_name, snapshot_desc)
            return Response(status=status.HTTP_201_CREATED)

        if a == 'delSnapshot':
            snapshot_name = request.data.get('name')
            if instance.server.is_available():
                instance.proxy.snapshot_delete(snapshot_name)
            return Response(status=status.HTTP_204_NO_CONTENT)

        if a == 'setDevice':
            new_device = request.data.get('device')
            raw_device = instance.proxy.get_devices_disk()
            new_dev_list = []

            xml_root = ET.fromstring(instance.proxy.get_xml())

            for new_media in new_device:
                if new_media.get('dev'):
                    print(new_media)
                    new_dev_list.append(new_media.get('dev'))

                    xml_root.find('devices/disk/target[@dev="{}"]'.format(new_media.get('dev')))
                    for device in xml_root.findall('devices/disk'):
                        dev = device.find('target').get('dev')
                        if dev == new_media.get('dev'):
                            print(dev)
                            device.set('device', new_media.get('type'))
                            device.find('source').set('file', new_media.get('file'))
                            print(ET.tostring(device).decode())
                else:
                    suffix_letters = list(string.ascii_lowercase)

                    dev = 'hda'
                    bus = 'ide'
                    if new_media.get('type') == 'floppy':
                        dev = 'fda'
                        bus = 'fdc'
                    if new_media.get('type') == 'disk':
                        dev = 'vda'
                        bus = 'virtio'
                    disk_element = xml_root.findall('devices/disk[@device="{}"]'.format(new_media.get('type')))
                    if disk_element:
                        raw_dev = disk_element[-1].find('target').get('dev')
                        raw_dev_suffix = raw_dev[-1]
                        dev = raw_dev[:-1] + suffix_letters[suffix_letters.index(raw_dev_suffix) + 1]

                    xml = f"""
                    <disk type='file' device='{new_media.get('type')}'>
                      <source file='{new_media.get('file')}'/>
                      <target dev='{dev}' bus='{bus}'/>
                      <driver name="qemu" type="{'qcow2' if new_media.get('type') == 'disk' else 'raw'}"/>
                      {'<readonly/>' if new_media.get('type') == 'floppy' else ''}
                    </disk>
                    """

                    xml_root.find('devices').append(ET.fromstring(xml))

                for raw_media in raw_device:
                    if raw_media.get('dev') not in new_dev_list:
                        for device in xml_root.findall('devices/disk'):
                            dev = device.find('target').get('dev')
                            if dev == raw_media.get('dev'):
                                xml_root.find('devices').remove(device)

            instance.server.proxy.define_domain(ET.tostring(xml_root).decode('utf-8'))
            return Response()
        raise exceptions.Error('请求错误')

    def perform_bulk_destroy(self, instances):
        for instance in instances:
            try:
                if instance.proxy.is_running():
                    instance.proxy.force_shutdown()

                instance.proxy.delete_all_disks()
                instance.proxy.delete(libvirt.VIR_DOMAIN_UNDEFINE_SNAPSHOTS_METADATA)
            except libvirt.libvirtError as e:
                print(e)

            self.perform_destroy(instance)


class KvmVmView1(viewsets.ViewSet):

    def list(self, request):
        ret = []
        action = request.query_params.get('a', None)
        vid = request.query_params.get('id', None)

        for node in VmServer.objects.all():
            if action == 'refresh':
                get_domains(node)
            else:
                data = cache.get(f'kvm:{node.host}:data')
                if not data:
                    get_domains(node)
            ret.extend(cache.get(f'kvm:{node.host}:data', []))

        if action == 'suspend':
            domain = VmInstance.objects.get(uuid=vid)
            domain.proxy.suspend()
            get_domains(domain.node)
            return Response(ret)

        if action == 'resume':
            domain = VmInstance.objects.get(uuid=vid)
            domain.proxy.resume()
            get_domains(domain.node)
            return Response(ret)

        if action == 'start':
            domain = VmInstance.objects.get(uuid=vid)
            domain.proxy.start()
            get_domains(domain.node)
            return Response(ret)

        if action == 'shutdown':
            domain = VmInstance.objects.get(uuid=vid)
            domain.proxy.shutdown()
            get_domains(domain.node)
            return Response(ret)

        if action == 'delete':
            import json
            del_disk = json.loads(request.query_params.get('del_disk', 'false'))
            domain = VmInstance.objects.get(uuid=vid)
            if domain.status == 1:
                domain.proxy.force_shutdown()

            for snapshot in domain.snapshots:
                domain.proxy.snapshot_delete(snapshot['name'])

            if del_disk:
                domain.proxy.delete_all_disks()
            domain.proxy.instance.undefine()
            get_domains(domain.node)
            return Response(ret)

        name = request.query_params.get('name')
        node = request.query_params.get('node')

        return Response({'data': ret, 'success': True, 'total': len(ret)})

    def create(self, request):
        ret = []
        data = request.data
        node = VmServer.objects.get(id=data.get('node'))
        machines = node.create.get_hypervisors_machines()
        arch = 'x86_64'
        machine = 'pc'
        uuid = str(uuid4())
        disk = None

        try:
            disk = node.create.create_volume(data.get('name'), data.get('disk_size'), data.get('storage'))
            node.create.create_instance(uuid, data.get('name'), data.get('memory'), data.get('cpu'), arch, machine,
                                        disk, data.get('image'), data.get('floppy'))
            VmInstance(name=data.get('name'), uuid=uuid, node=node).save()
            node.proxy.wvm.lookupByName(data.get('name')).create()

        except libvirt.libvirtError as lib_err:
            if disk:
                node.create.delete_volume(disk)
            for d in node.proxy.wvm.listAllDomains():
                if d.name() == data.get('name'):
                    d.undefine()
            return Response(str(lib_err), status=500)
        get_domains(node)
        ret.append(cache.get(f'kvm:{node.host}:data'))

        return Response(ret)

    def retrieve(self, request, pk=None):
        node = VmServer.objects.get(id=pk)
        ret = cache.get(f'kvm:{node.host}:data')
        if not ret:
            get_domains(node)
            ret = cache.get(f'kvm:{node.host}:data')

        return Response(ret)

    def update(self, request, pk=None):
        pass

    def partial_update(self, request, pk=None):
        pass

    def destroy(self, request, pk=None):
        pass


class KvmStorageView(viewsets.GenericViewSet):
    queryset = VmServer.objects.all()
    serializer_class = VmServerSerializer

    def list(self, request):
        ret = []
        for server in self.queryset:
            storage_list = []
            for pool in server.proxy.get_storages():
                data = server.proxy.get_storage(pool, path=True)
                storage_list.append(data)
            ret.append({server.host: storage_list})

        # print(domain.node.create.get_hypervisors_machines())
        # # print(domain.media_iso)
        # for i in domain.node.proxy.wvm.listStoragePools():
        #     ret.append(domain.proxy.get_storage(i, path=True))
        #     print(domain.proxy.get_iso_media())
        #
        # # a = domain.node.create.create_volume('f1', 20)
        # # print(a)

        # paginator = CustomPagination()
        # result_page = paginator.paginate_queryset(ret, request)
        page = self.paginate_queryset(ret)
        if page is not None:
            return self.get_paginated_response(page)

        return Response(ret)

    @action(methods=['get'], detail=False, url_path='media')
    def get_media(self, request):
        ret = []
        server_id = request.query_params.get('serverId')
        media_type = request.query_params.get('type')
        pool = request.query_params.get('pool')

        server = VmServer.objects.get(pk=server_id)

        if server.is_available():
            ret = server.proxy.get_media_files(media_type, pool)

        return Response(ret)

    def create(self, request):
        data = request.data
        pool = data.get('name')
        server = VmServer.objects.get(pk=data.pop('serverId'))

        if pool not in server.proxy.get_storages():
            try:
                server.proxy.create_storage(**data)
            except Exception as e:
                server.proxy.get_storage(pool).delete()
                raise exceptions.APIException(e)
        else:
            raise exceptions.APIException('存储池已经存在！')

        return Response()

    def retrieve(self, request, pk=None):
        ret = {}

        instance = self.get_object()
        for storage in instance.proxy.get_storages():
            ret.setdefault(instance.host, []).append(instance.proxy.get_storage(storage, path=True))
        print(request.data)
        print(instance.proxy.get_media_files())

        return Response(ret)


class FileUploadView(viewsets.ViewSet):
    """ 文件上传接口 """
    parser_classes = (MultiPartParser,)

    def list(self, request):
        ret = []
        for file in settings.UPLOAD_PATH.iterdir():
            ret.append(
                {'label': file.name, 'value': f"{request.scheme}://{request.META.get('HTTP_HOST')}/upload/{file.name}"})
        return Response(ret)

    def create(self, request):
        if request.FILES:
            file_list = list()
            upload_dir = settings.UPLOAD_PATH
            for i in request.FILES:
                file_obj = request.FILES.get(i)
                file_list.append(request.scheme + '://' + request.META.get('HTTP_HOST') + '/upload/' + file_obj.name)
                file = os.path.join(upload_dir, file_obj.name)
                if os.path.exists(file):
                    random_str = ''.join(random.sample(string.ascii_letters + string.digits, 6))
                    os.rename(file, f'{file}.{random_str}')
                with open(file, 'wb+') as f:
                    for chunk in file_obj.chunks():
                        f.write(chunk)
                os.system('dos2unix {}'.format(file))
            return Response({'files': file_list}, status.HTTP_200_OK)
        else:
            raise exceptions.APIException('参数不正确！')
