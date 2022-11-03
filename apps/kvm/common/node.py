import time
from xml.dom import minidom
from .kvm import KvmBase
from .utils import get_xml_path


def cpu_version(doc):
    for info in doc.xpath('/sysinfo/processor/entry'):
        elem = info.xpath('@name')[0]
        if elem == 'version':
            return info.text
    return 'Unknown'


class KvmNodeBase(KvmBase):
    def get_storages(self, only_actives=False):
        """
        :return: list of active or all storages
        """
        storages = []
        for pool in self.wvm.listStoragePools():
            storages.append(pool)
        if not only_actives:
            for pool in self.wvm.listDefinedStoragePools():
                storages.append(pool)
        return storages

    def get_media(self):
        data = []
        storages = self.get_storages(only_actives=True)
        for storage in storages:
            stg = self.get_storage(storage)
            if stg.info()[0] != 0:
                path = self.get_storage(storage, path=True).get('path')
                try:
                    stg.refresh(0)
                except:
                    pass
                for file in stg.listVolumes():
                    if file.lower().endswith(('.iso', '.vfd')):
                        data.append(f'{path}/{file}')
        return data

    def get_iso_media(self):
        iso = {}
        storages = self.get_storages(only_actives=True)
        for storage in storages:
            data = []
            stg = self.get_storage(storage)
            if stg.info()[0] != 0:
                try:
                    stg.refresh(0)
                except:
                    pass
                for img in stg.listVolumes():
                    if img.lower().endswith('.iso'):
                        data.append(img)
            iso[storage] = data
        return iso

    def get_floppy_media(self):
        floppy = {}
        storages = self.get_storages(only_actives=True)
        for storage in storages:
            data = []
            stg = self.get_storage(storage)
            if stg.info()[0] != 0:
                try:
                    stg.refresh(0)
                except:
                    pass
                for img in stg.listVolumes():
                    if img.lower().endswith('.vfd'):
                        data.append(img)
            floppy[storage] = data
        return floppy

    def get_storage(self, name, path=False):
        pool = self.wvm.storagePoolLookupByName(name)
        raw_xml = pool.XMLDesc()
        xml = minidom.parseString(raw_xml)
        stg_type = xml.documentElement.getAttribute('type')
        if path:
            path = get_xml_path(pool.XMLDesc(), "/pool/target/path")
            return {'name': pool.name(), 'path': path, 'type': stg_type, 'is_active': pool.isActive(), 'autostart': pool.autostart()}
        return pool

    def get_memory_usage(self):
        """
        Function return memory usage on node.
        """
        # mem_total = self.wvm.getInfo()[1] * 1024 * 1024
        mem_state = self.wvm.getMemoryStats(-1, 0)

        if isinstance(mem_state, dict):
            mem_total = mem_state['total']
            mem_free = mem_state['buffers'] + mem_state['free'] + mem_state['cached']
            mem_usage = (mem_total - mem_free)
            mem_percent = abs(100 - (mem_free * 100) // mem_total)
            data = {'total': mem_total, 'usage': mem_usage, 'percent': mem_percent}
        else:
            data = {'total': None, 'usage': None, 'percent': None}
        return data

    def get_cpu_usage(self):
        """
        Function return cpu usage on node.
        """
        prev_idle = 0
        prev_total = 0
        cpu = self.wvm.getCPUStats(-1, 0)
        if isinstance(cpu, dict):
            for num in range(2):
                idle = self.wvm.getCPUStats(-1, 0)['idle']
                total = sum(self.wvm.getCPUStats(-1, 0).values())
                diff_idle = idle - prev_idle
                diff_total = total - prev_total
                diff_usage = (1000 * (diff_total - diff_idle) / diff_total + 5) / 10
                prev_total = total
                prev_idle = idle
                if num == 0:
                    time.sleep(1)
                else:
                    if diff_usage < 0:
                        diff_usage = 0
        else:
            return {'usage': None}
        return {'usage': diff_usage}

    def get_node_info(self):
        """
        Function return host server information: hostname, cpu, memory, ...
        """
        info = list()
        info.append(self.wvm.getHostname())  # hostname
        info.append(self.wvm.getInfo()[0])  # architecture
        info.append(self.wvm.getInfo()[1] * 1024 * 1024)  # memory 默认mb 转换 bytes
        info.append(self.wvm.getInfo()[2])  # cpu core count
        info.append(get_xml_path(self.wvm.getSysinfo(0), func=cpu_version))  # cpu version
        info.append(self.wvm.getURI())  # uri
        return info
