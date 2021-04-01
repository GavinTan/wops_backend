from django.shortcuts import render
from django.contrib.auth.models import User, Group
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, mixins
from .serializers import UserSerializer, GroupSerializer, KvmMangeSerializer, KvmNodesSerializer
from .models import KvmNodes, KvmDomains
from .utils import get_domains, convert_bytes
from apps.utils import CustomModelMixin
from django.core.cache import cache
from libvirt import libvirtError
from uuid import uuid4
from rest_framework.parsers import FileUploadParser, MultiPartParser
from rest_framework import status
from django.conf import settings
import os
import string


# Create your views here.


class UserViewSet(viewsets.ModelViewSet):
    """
    允许用户查看或编辑的API路径。
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer


class GroupViewSet(viewsets.ModelViewSet):
    """
    允许组查看或编辑的API路径。
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class KvmNodesView(CustomModelMixin, viewsets.ModelViewSet):
    queryset = KvmNodes.objects.all()
    serializer_class = KvmNodesSerializer

    # renderer_classes = (CustomJSONRenderer,)

    def destroy(self, *args, **kwargs):
        serializer = self.get_serializer(self.get_object())
        cache.delete_pattern(f"kvm:{serializer.data['host']}:data")
        return super().destroy(self, *args, **kwargs)


class KvmVmView(viewsets.ViewSet):

    def list(self, request):
        ret = []
        action = request.query_params.get('a', None)
        vid = request.query_params.get('id', None)

        if action == 'suspend':
            domain = KvmDomains.objects.get(uuid=vid)
            domain.proxy.suspend()
            get_domains(domain.node)
            return Response(ret)

        if action == 'resume':
            domain = KvmDomains.objects.get(uuid=vid)
            domain.proxy.resume()
            get_domains(domain.node)
            return Response(ret)

        if action == 'start':
            domain = KvmDomains.objects.get(uuid=vid)
            domain.proxy.start()
            get_domains(domain.node)
            return Response(ret)

        if action == 'shutdown':
            domain = KvmDomains.objects.get(uuid=vid)
            domain.proxy.shutdown()
            get_domains(domain.node)
            return Response(ret)

        if action == 'delete':
            import json
            del_disk = json.loads(request.query_params.get('del_disk', 'false'))
            domain = KvmDomains.objects.get(uuid=vid)
            if domain.status == 1:
                domain.proxy.force_shutdown()

            for snapshot in domain.snapshots:
                domain.proxy.snapshot_delete(snapshot['name'])

            if del_disk:
                domain.proxy.delete_all_disks()
            domain.proxy.instance.undefine()
            get_domains(domain.node)
            return Response(ret)

        for node in KvmNodes.objects.all():
            if action == 'refresh':
                get_domains(node)
            else:
                data = cache.get(f'kvm:{node.host}:data')
                if not data:
                    get_domains(node)
            ret.append(cache.get(f'kvm:{node.host}:data'))

        return Response(ret)

    def create(self, request):
        ret = []
        data = request.data
        node = KvmNodes.objects.get(id=data.get('node'))
        machines = node.create.get_hypervisors_machines()
        arch = 'x86_64'
        machine = 'pc'
        uuid = str(uuid4())
        disk = None

        try:
            disk = node.create.create_volume(data.get('name'), data.get('disk_size'), data.get('storage'))
            node.create.create_instance(uuid, data.get('name'), data.get('memory'), data.get('cpu'), arch, machine, disk, data.get('image'), data.get('floppy'))
            KvmDomains(name=data.get('name'), uuid=uuid, node=node).save()
            node.proxy.wvm.lookupByName(data.get('name')).create()

        except libvirtError as lib_err:
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
        node = KvmNodes.objects.get(id=pk)
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


class KvmStorageView(viewsets.ViewSet):
    def list(self, request):
        ret = []
        domain = KvmDomains.objects.get(id=3)
        # a = node.get_volumes
        # print(a)
        print(domain.node.create.get_hypervisors_machines())
        # print(domain.media_iso)
        for i in domain.node.proxy.wvm.listStoragePools():
            # ret.append(domain.proxy.get_storage(i, path=True))
            print(domain.proxy.get_iso_media())

        # a = domain.node.create.create_volume('f1', 20)
        # print(a)

        return Response(ret)

    def create(self, request):
        pass

    def retrieve(self, request, pk=None):
        ret = []
        images = []
        node = KvmNodes.objects.get(id=pk)

        action = request.query_params.get('a', None)
        if node.status is True:
            for p in node.proxy.wvm.listStoragePools():
                stg = node.proxy.get_storage(p, path=True)
                if action == 'image':
                    for i in node.proxy.get_storage(p).listVolumes():
                        if i.lower().endswith('.iso'):
                            image = os.path.join(stg['path'], i)
                            if image not in images:
                                images.append(image)
                if action == 'floppy':
                    for i in node.proxy.get_storage(p).listVolumes():
                        if i.lower().endswith(('.iso', 'vfd')):
                            image = os.path.join(stg['path'], i)
                            if image not in images:
                                images.append(image)
                else:
                    ret.append(stg)
        return Response(images if images else ret)

from .documents import IUser
from datetime import datetime
import random
import threading
class EsView(viewsets.ViewSet):
    def list(self, request):
        ret = []
        p = request.GET
        s = IUser.search()
        star = 0 if int(p.get('page')) == 1 else int(p.get('page')) + int(p.get('limit')) - 1
        end = int(p.get('limit')) if int(p.get('page')) == 1 else star + int(p.get('limit'))
        for hit in s[star:end]:
            ret.append(hit.to_dict())
        return Response({'total': s.count(), 'result': ret})

    def create(self, request):
        ret = []
        data = request.data
        p = request.GET

        if data.get('action') == 'search':
            '''.params(size=10000)'''
            s = IUser.search().highlight('desc', pre_tags='<span style="color:red">', post_tags='</span>').query('match_phrase', desc=data.get('q'))
            star = 0 if int(p.get('page')) == 1 else int(p.get('page')) + int(p.get('limit')) - 1
            end = int(p.get('limit')) if int(p.get('page')) == 1 else star + int(p.get('limit'))
            for hit in s[star:end]:
                d = hit.to_dict()
                for fragment in hit.meta.highlight.desc:
                    d['desc'] = fragment
                ret.append(d)
            return Response({'total': s.count(), 'result': ret})

        # IUser.search().params(size=1000).query('match_all').delete()
        IUser.init()
        def to_save(name, n):
            for i in range(1000):
                u = IUser(name=name, age=n, desc=f'{name}{n}{i}带我去看看世界', timestamp=datetime.now())
                u.save()

        names = ('张三', '李四', '王二', '麻子')
        for i in range(100):
            name = random.choice(names)
            t = threading.Thread(target=to_save, args=(name, i))
            t.start()

        return self.list(request)

    def destroy(self, request, pk=None):
        s = IUser.search().query('match_all')
        s.delete()
        return Response({'total': s.count(), 'result': {}})


class WangView(viewsets.ViewSet):
    authentication_classes = ()
    permission_classes = ()

    def list(self, request):
        print(request.query_params)
        print(request.data)

        return Response()

    def create(self, request):
        print(request.query_params)
        print(request.data)
        print(settings.UPLOAD_PATH)

        return Response()

    def retrieve(self, request, pk=None):
        pass

    def update(self, request, pk=None):
        pass

    def partial_update(self, request, pk=None):
        pass

    def destroy(self, request, pk=None):
        return Response()


class FileUploadView(viewsets.ViewSet):
    """ 文件上传接口 """
    parser_classes = (MultiPartParser,)

    def create(self, request, format=None):
        if request.FILES:
            file_list = list()
            upload_dir = settings.UPLOAD_PATH
            for i in request.FILES:
                file_obj = request.FILES.get(i)
                file_list.append(request.scheme + '://' + request.META.get('HTTP_HOST') + '/upload/' + file_obj.name)
                file = upload_dir + file_obj.name
                if os.path.exists(file):
                    random_str = ''.join(random.sample(string.ascii_letters + string.digits, 6))
                    os.rename(file, upload_dir + file_obj.name + '.' + random_str)
                with open(file, 'wb+') as f:
                    for chunk in file_obj.chunks():
                        f.write(chunk)
                os.system('dos2unix {}'.format(file))
            return Response({'files': file_list}, status.HTTP_200_OK)
        else:
            return Response({'error': '参数不正确'}, status.HTTP_400_BAD_REQUEST)


def index(request):
    return render(request, 'index.html')