from kvm.virt.utils import convert_bytes
import xml.etree.cElementTree as ET
from datetime import datetime
import libvirt


class VirtInstance:
    def __init__(self, server, domain):
        """
        @type server: libvirt.virConnect
        @type domain: libvirt.virDomain
        """

        self.server = server
        self.dom = domain

    def is_running(self):
        return self.dom.isActive()

    def start(self):
        return self.dom.create()

    def reboot(self):
        return self.dom.reboot()

    def shutdown(self):
        return self.dom.shutdown()

    def force_shutdown(self):
        return self.dom.destroy()

    def delete(self, flags=0):
        return self.dom.undefineFlags(flags)

    def get_xml(self):
        return self.dom.XMLDesc()

    def get_info(self):
        """
        list[0] 运行状态
        list[1] 最大内存（KB）
        list[2] 当前内存（KB）
        list[3] cpu使用时间（纳秒）
        """
        return self.dom.info()

    def get_status(self):
        """
        VIR_DOMAIN_RUNNING = 1
        VIR_DOMAIN_NOSTATE = 0
        VIR_DOMAIN_PAUSED = 3
        VIR_DOMAIN_SHUTOFF = 5
        """
        return self.get_info()[0]

    def get_uuid(self):
        return self.dom.UUIDString()

    def get_desc(self):
        xml_root = ET.fromstring(self.get_xml())
        return xml_root.find('description').text

    def get_block_info(self, path):
        """
        list[0] logical size in bytes of the image (how much storage the guest will see)
        list[1] host storage in bytes occupied by the image (such as highest allocated extent if there are no holes, similar to 'du')
        list[2] host physical size in bytes of the image container (last offset, similar to 'ls')
        """
        return self.dom.blockInfo(path)

    def get_devices_net(self):
        data = []
        xml_root = ET.fromstring(self.get_xml())
        for net in xml_root.findall('devices/interface'):
            data.append({
                'type': net.get('type'),
                'mac': net.find('mac').get('address'),
                'nic': net.find('source').get('bridge'),
                'model': net.find('model').get('type'),
            })
        return data

    def get_console_type(self):
        xml_root = ET.fromstring(self.get_xml())
        console_type = xml_root.find('devices/graphics/[@type]').get('type')
        return console_type

    def get_console_port(self, console_type=None):
        if console_type is None:
            console_type = self.get_console_type()
        xml_root = ET.fromstring(self.get_xml())
        port = xml_root.find(f"devices/graphics[@type='{console_type}']/[@port]").get('port')
        return port

    def get_vcpu(self, flags=0):
        return self.dom.vcpusFlags(flags)

    def set_vcpu(self, vcpu, flags=0):
        return self.dom.setVcpusFlags(vcpu, flags)

    def get_memory(self, max_memory=False):
        xml_root = ET.fromstring(self.get_xml())
        if max_memory:
            mem = xml_root.find('memory').text
        else:
            mem = xml_root.find('currentMemory').text
        return int(mem) * 1024

    def set_memory(self, size, flags=0):
        return self.dom.setMemoryFlags(size, flags)

    def get_devices_disk(self):
        data = []
        xml_root = ET.fromstring(self.get_xml())
        for disk in xml_root.findall('devices/disk'):
            data.append({
                'type': disk.get('type'),
                'device': disk.get('device'),
                'format': disk.find('driver').get('type'),
                'file': disk.find('source').get('file'),
                'dev': disk.find('target').get('dev'),
                'bus': disk.find('target').get('bus'),
                'readonly': False if disk.find('readonly') is None else True,
                'size': convert_bytes(self.get_block_info(disk.find('source').get('file'))[0]),
                'used': convert_bytes(self.get_block_info(disk.find('source').get('file'))[1])
            })
        return data

    def delete_all_disks(self):
        disks = self.get_devices_disk()
        for disk in disks:
            if disk.get('device') == 'disk':
                vol = self.server.storageVolLookupByPath(disk.get('file'))
                vol.delete(0)

    def get_snapshots(self):
        data = []
        snapshots = self.dom.snapshotListNames(0)
        for snapshot in snapshots:
            snap = self.dom.snapshotLookupByName(snapshot, 0)
            xml_root = ET.fromstring(snap.getXMLDesc())
            snap_create_time = xml_root.find('creationTime').text
            snap_state = xml_root.find('state').text
            desc = xml_root.find('description').text

            data.append({
                'name': snapshot,
                'state': snap_state,
                'create_time': datetime.fromtimestamp(int(snap_create_time)).strftime("%Y-%m-%d %H:%M:%S"),
                'desc': desc
            })

        return sorted(data, reverse=True, key=lambda k: k['create_time'])

    def snapshot_create(self, name, desc=' '):
        xml = f"""<domainsnapshot>
                    <description>{desc}</description>
                    <name>{name}</name>
                  </domainsnapshot>"""
                   
        return self.dom.snapshotCreateXML(xml)

    def snapshot_delete(self, snapshot):
        snap = self.dom.snapshotLookupByName(snapshot, 0)
        snap.delete(0)

    def snapshot_revert(self, snapshot):
        snap = self.dom.snapshotLookupByName(snapshot, 0)
        self.dom.revertToSnapshot(snap, 0)
