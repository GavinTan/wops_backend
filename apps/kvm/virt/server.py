from kvm.virt.conn import VirtConnManage
from kvm.virt.instance import VirtInstance
from kvm.virt.utils import randomMAC
import xml.etree.ElementTree as ET
from uuid import uuid4
import libvirt
import string



class VirtServer:
    """
    @type conn: libvirt.virConnect
    """
    def __init__(self, host, username='root', password=None, conn_type=2, conn_port=22, timeout=0):
        self.conn = VirtConnManage(host, username, password,  conn_type, conn_port, timeout).connect

    def close(self):
        self.conn.close()

    def get_instance(self, name):
        return VirtInstance(self.conn, self.conn.lookupByName(name))

    def get_all_domain(self):
        return self.conn.listAllDomains()

    def get_info(self):
        """
        list[0]	string indicating the CPU model
        list[1]	memory size in megabytes
        list[2]	the number of active CPUs
        list[3]	expected CPU frequency (mhz)
        list[4]	the number of NUMA nodes, 1 for uniform memory access
        list[5]	number of CPU sockets per node
        list[6]	number of cores per socket
        list[7]	number of threads per core
        """
        return self.conn.getInfo()

    def get_memory_usage(self):
        mem_state = self.conn.getMemoryStats(libvirt.VIR_NODE_MEMORY_STATS_ALL_CELLS, 0)

        if isinstance(mem_state, dict):
            mem_total = mem_state['total']
            mem_free = mem_state['buffers'] + mem_state['free'] + mem_state['cached']
            mem_usage = (mem_total - mem_free)
            mem_percent = abs(100 - (mem_free * 100) // mem_total)
            data = {'total': mem_total, 'usage': mem_usage, 'percent': mem_percent}
        else:
            data = {'total': None, 'usage': None, 'percent': None}
        return data

    def get_storages(self):
        pools = []
        for pool in self.conn.listAllStoragePools():
            pools.append(pool.name())

        return pools

    def get_storage(self, name, path=False):
        pool = self.conn.storagePoolLookupByName(name)
        if path:
            xml_root = ET.fromstring(pool.XMLDesc())
            path = xml_root.find('target/path').text
            return {'name': pool.name(), 'path': path}
        return pool

    def get_media_files(self, media_type='cdrom', pool=None):
        data = []

        suffix = ('.iso',)
        if media_type == 'disk':
            suffix = ('.img', '.qcow2')
        if media_type == 'floppy':
            suffix = ('.vfd',)

        for storage in self.conn.listAllStoragePools():
            if storage.info()[0] != 0:
                try:
                    storage.refresh(0)
                except libvirt.libvirtError as e:
                    print(e)
                for volume in storage.listAllVolumes():
                    if volume.name().lower().endswith(suffix):
                        if pool is None:
                            data.append({'name': volume.name(), 'path': volume.path()})
                        else:
                            if storage.name() == pool:
                                data.append({'name': volume.name(), 'path': volume.path()})
        return data

    def get_volume_by_path(self, path):
        return self.conn.storageVolLookupByPath(path)

    def delete_volume(self, path):
        vol = self.get_volume_by_path(path)
        vol.delete()

    def define_domain(self, xml):
        return self.conn.defineXML(xml)

    def define_storage(self, xml, flag):
        self.conn.storagePoolDefineXML(xml, flag)

    def create_storage(self, name, target, source=None, stg_type='dir'):
        """
        stg_type: dir disk fs netfs logical gluster iscsi iscsi-direct scsi lvm mpath rbd sheepdog zfs vstorage

        link: https://libvirt.org/storage.html#StorageBackendDir
        """
        xml = f"""<pool type='{stg_type}'>
                 <name>{name}</name>"""
        if stg_type == 'logical' and source:
            xml += f"""<source>
                        <device path='{source}'/>
                          <name>{name}</name>
                          <format type='lvm2'/>
                        </source>"""
        if stg_type == 'logical':
            target = '/dev/' + name
        xml += f"""
                  <target>
                       <path>{target}</path>
                  </target>
                </pool>"""
        self.define_storage(xml, 0)
        stg = self.get_storage(name)
        if stg_type == 'logical':
            stg.build(0)
        stg.create(0)
        stg.setAutostart(1)

        return stg

    def create_volume(self, name, size, pool='default'):
        name = name + '.img'

        vol_xml = f"""
        <volume>
          <name>{name}</name>
          <allocation>0</allocation>
          <capacity unit="G">{size}</capacity>
          <target>
            <format type='qcow2'/>
            <permissions>
              <owner>107</owner>
              <group>107</group>
              <mode>0644</mode>
              <label>virt_image_t</label>
            </permissions>
          </target>
        </volume>"""

        stg = self.get_storage(pool)
        stg.createXML(vol_xml, 0)
        try:
            stg.refresh(0)
        except:
            pass
        vol = stg.storageVolLookupByName(name)
        return vol.path()

    def get_hypervisors_domain_types(self):
        """
        :return: hypervisor domain types
        """
        data = {}
        xml_root = ET.fromstring(self.get_cap_xml())
        for arch in xml_root.findall('guest/arch'):
            data[arch.get('name')] = arch.find('domain').get('type')
        return data

    def get_emulator(self, arch):
        """
        :return: emulator list
        """
        xml_root = ET.fromstring(self.get_cap_xml())
        return xml_root.find(f'guest/arch[@name="{arch}"]/emulator').text

    def get_machine_types(self, arch):
        """
        :return: canonical(if exist) name of machine types
        """
        xml_root = ET.fromstring(self.get_cap_xml())
        canonical_data = xml_root.findall(f'guest/arch[@name="{arch}"]/machine[@canonical]')
        if not canonical_data:
            canonical_data = xml_root.findall(f'guest/arch[@name="{arch}"]/machine')

        data = [i.text for i in canonical_data]

        return data

    def get_os_loaders(self, arch='x86_64', machine='pc'):
        """return available os loaders list"""

        xml_root = ET.fromstring(self.get_dom_cap_xml(arch, machine))

        return [i.text for i in xml_root.findall("os/loader[@supported='yes']/value")]

    def get_os_loader_enums(self, arch='x86_64', machine='pc'):
        """return available os loaders list"""
        data = {}
        xml_root = ET.fromstring(self.get_dom_cap_xml(arch, machine))
        for enum in xml_root.findall("os/loader[@supported='yes']/enum"):
            data[enum.get('name')] = [i.text for i in enum.findall('value')]

        return data

    def get_cpu_modes(self, arch, machine):
        """return: available cpu modes"""
        xml_root = ET.fromstring(self.get_dom_cap_xml(arch, machine))

        return [i.get('name') for i in xml_root.findall("cpu/mode[@supported='yes']")]

    def get_cpu_custom_types(self, arch, machine):
        """return available graphics types"""
        data = []

        xml_root = ET.fromstring(self.get_dom_cap_xml(arch, machine))
        model_data = xml_root.findall("cpu/mode[@name='custom'][@supported='yes']/model")
        for model in model_data:
            if model.get('usable') == 'yes' or model.get('usable') == 'unknown':
                data.append(model.text)

        return data

    def get_disk_device_types(self, arch, machine):
        """return: available disk device type list"""
        xml_root = ET.fromstring(self.get_dom_cap_xml(arch, machine))
        return [i.text for i in xml_root.findall("devices/disk/enum[@name='diskDevice']/value")]

    def get_disk_bus_types(self, arch, machine):
        """return: available disk bus types list"""
        xml_root = ET.fromstring(self.get_dom_cap_xml(arch, machine))
        return [i.text for i in xml_root.findall("devices/disk/enum[@name='bus']/value")]

    def get_graphics_types(self, arch, machine):
        """return: available graphics types"""
        xml_root = ET.fromstring(self.get_dom_cap_xml(arch, machine))
        return [i.text for i in xml_root.findall("devices/graphics/enum[@name='type']/value")]

    def get_video_types(self, arch, machine):
        """return: available graphics video types"""
        data = []
        xml_root = ET.fromstring(self.get_dom_cap_xml(arch, machine))
        for value in xml_root.findall("devices/video/enum[@name='modelType']/value"):
            data.append(value.text)

        return data

    def get_hostdev_modes(self, arch, machine):
        """return: available nodedev modes"""
        xml_root = ET.fromstring(self.get_dom_cap_xml(arch, machine))
        return [i.text for i in xml_root.findall("devices/hostdev/enum[@name='mode']/value")]

    def get_hostdev_startup_policies(self, arch, machine):
        """return: available hostdev startup policy"""
        xml_root = ET.fromstring(self.get_dom_cap_xml(arch, machine))
        return [i.text for i in xml_root.findall("devices/hostdev/enum[@name='startupPolicy']/value")]

    def get_hostdev_subsys_types(self, arch, machine):
        """return: available nodedev sub system types"""
        xml_root = ET.fromstring(self.get_dom_cap_xml(arch, machine))
        return [i.text for i in xml_root.findall("devices/hostdev/enum[@name='subsysType']/value")]

    def get_cap_xml(self):
        """Return xml capabilities"""
        return self.conn.getCapabilities()

    def get_dom_cap_xml(self, arch, machine):
        """ Return domain capabilities xml"""

        emulatorbin = self.get_emulator(arch)
        virttype = 'kvm' if 'kvm' in self.get_hypervisors_domain_types()[arch] else 'qemu'

        machine_types = self.get_machine_types(arch)
        if not machine or machine not in machine_types:
            machine = 'pc' if 'pc' in machine_types else machine_types[0]
        return self.conn.getDomainCapabilities(emulatorbin, arch, machine, virttype)

    def get_capabilities(self, arch):
        print(arch)
        xml_root = ET.fromstring(self.get_cap_xml())
        arch_data = xml_root.find(f'guest/arch[@name="{arch}"]')
        guest_data = xml_root.find(f'guest/arch[@name="{arch}"]/..')

        data = {
            'wordsize': arch_data.find('wordsize').text,
            'emulator': arch_data.find('emulator').text,
            'domain': [i.get('type') for i in arch_data.findall('domain')],
            'machine': [{'machine': i.text, 'max_cpu': i.get('maxCpus'), 'canonical': i.get('canonical')} for i in arch_data.findall('machine')],
            'features': [i.tag for i in list(guest_data.find('features'))],
            'os_type': guest_data.find('os_type').text
        }

        return data

    def get_dom_capabilities(self, arch, machine):
        """Return domain capabilities"""
        xml_root = ET.fromstring(self.get_dom_cap_xml(arch, machine))

        data = {
            'path': xml_root.find('path').text,
            'domain': xml_root.find('domain').text,
            'machine': xml_root.find('machine').text,
            'vcpu_max': xml_root.find('vcpu').get('max'),
            'iothreads_support': xml_root.find('iothreads').get('supported'),
            'os_support': xml_root.find('os').get('supported'),
            'loader_support': xml_root.find('os/loader').get('supported'),
            'disk_support': xml_root.find('devices/disk').get('supported'),
            'graphics_support': xml_root.find('devices/graphics').get('supported'),
            'video_support': xml_root.find('devices/video').get('supported'),
            'hostdev_support': xml_root.find('devices/hostdev').get('supported'),
            'features_gic_support': xml_root.find('features/gic').get('supported'),
            'features_genid_support': xml_root.find('features/genid').get('supported'),
            'features_vmcoreinfo_support': xml_root.find('features/vmcoreinfo').get('supported'),
            'features_sev_support': xml_root.find('features/sev').get('supported'),
        }

        if data['loader_support'] == 'yes':
            data['loaders'] = self.get_os_loaders(arch, machine)
            data['loader_enums'] = self.get_os_loader_enums(arch, machine)

        data['cpu_modes'] = self.get_cpu_modes(arch, machine)
        if 'custom' in data['cpu_modes']:
            # supported and unknown cpu models
            data['cpu_custom_models'] = self.get_cpu_custom_types(arch, machine)

        if data['disk_support'] == 'yes':
            data['disk_devices'] = self.get_disk_device_types(arch, machine)
            data['disk_bus'] = self.get_disk_bus_types(arch, machine)

        if data['graphics_support'] == 'yes':
            data['graphics_types'] = self.get_graphics_types(arch, machine)

        if data['video_support'] == 'yes':
            data['video_types'] = self.get_video_types(arch, machine)

        if data['hostdev_support'] == 'yes':
            data['hostdev_types'] = self.get_hostdev_modes(arch, machine)
            data['hostdev_startup_policies'] = self.get_hostdev_startup_policies(arch, machine)
            data['hostdev_subsys_types'] = self.get_hostdev_subsys_types(arch, machine)

        return data

    def create_instance(self, name, memory, vcpu, disk, arch='x86_64', machine='pc', media=None, desc=' '):
        if media is None:
            media = []

        uuid = str(uuid4())
        mac = randomMAC()

        caps = self.get_capabilities(arch)
        dom_caps = self.get_dom_capabilities(arch, machine)

        memory = int(memory) * 1024
        vd_disk_letters = list(string.ascii_lowercase)
        fd_disk_letters = list(string.ascii_lowercase)
        hd_disk_letters = list(string.ascii_lowercase)

        xml_tpl = f"""<domain type="kvm">
                       <description>{desc}</description>
                       <name>tt2</name>
                       <uuid>eea76e77-d1ce-4995-a47f-715e6ade280c</uuid>
                       <memory unit='KiB'>2097152</memory>
                       <currentMemory unit='KiB'>2097152</currentMemory>
                       <vcpu>2</vcpu>
                       <os>
                         <type arch="x86_64">hvm</type>
                         <boot dev="hd"/>
                       </os>
                       <features>
                         <acpi/>
                         <apic/>
                         <hyperv>
                           <relaxed state="on"/>
                           <vapic state="on"/>
                           <spinlocks state="on" retries="8191"/>
                         </hyperv>
                       </features>
                       <cpu mode="host-model"/>
                       <clock offset="localtime">
                         <timer name="rtc" tickpolicy="catchup"/>
                         <timer name="pit" tickpolicy="delay"/>
                         <timer name="hpet" present="no"/>
                         <timer name="hypervclock" present="yes"/>
                       </clock>
                       <on_poweroff>destroy</on_poweroff>
                       <on_reboot>restart</on_reboot>
                       <on_crash>restart</on_crash>
                       <pm>
                         <suspend-to-mem enabled="no"/>
                         <suspend-to-disk enabled="no"/>
                       </pm>
                       <devices>
                         <interface type="bridge">
                           <source bridge="virbr0"/>
                           <mac address="52:54:00:05:87:f8"/>
                           <model type="e1000"/>
                         </interface>
                         <input type="tablet" bus="usb"/>
                         <graphics type="vnc" port="-1" listen="0.0.0.0"/>
                         <console type="pty"/>
                         <video>
                           <model type="vga"/>
                         </video>
                       </devices>
                     </domain>"""

        xml_root = ET.fromstring(xml_tpl)
        xml_root.find('name').text = name
        xml_root.find('uuid').text = uuid
        xml_root.find('memory').text = str(memory)
        xml_root.find('currentMemory').text = str(memory)
        xml_root.find('vcpu').text = vcpu
        xml_root.find('os/type').text = caps.get('os_type')
        xml_root.find('os/type').set('machine', machine)
        xml_root.find('os/type').set('arch', arch)

        xml_disk = ET.Element('disk')
        xml_disk.set('type', 'file')
        xml_disk.set('device', 'disk')
        ET.SubElement(xml_disk, 'source').set('file', disk)

        xml_disk_driver = ET.SubElement(xml_disk, 'target')
        xml_disk_driver.set('dev', f'vd{vd_disk_letters.pop(0)}')
        xml_disk_driver.set('bus', 'virtio')

        xml_disk_driver = ET.SubElement(xml_disk, 'driver')
        xml_disk_driver.set('name', 'qemu')
        xml_disk_driver.set('type', 'qcow2')

        xml_root.find('devices').insert(0, xml_disk)

        for i in media:
            bus = 'ide'
            dev = f'hd{hd_disk_letters.pop(0)}'

            if i.get('type') == 'disk':
                bus = 'virtio'
                dev = f'vd{vd_disk_letters.pop(0)}'
            if i.get('type') == 'floppy':
                bus = 'fdc'
                dev = f'fd{fd_disk_letters.pop(0)}'

            xml_disk = ET.Element('disk')
            xml_disk.set('type', 'file')
            xml_disk.set('device', i.get('type'))
            ET.SubElement(xml_disk, 'source').set('file', i.get('file'))

            xml_disk_driver = ET.SubElement(xml_disk, 'target')
            xml_disk_driver.set('dev', dev)
            xml_disk_driver.set('bus', bus)

            xml_disk_driver = ET.SubElement(xml_disk, 'driver')
            xml_disk_driver.set('name', 'qemu')

            if i.get('type') == 'disk':
                xml_disk_driver.set('type', 'qcow2')
            else:
                xml_disk_driver.set('type', 'raw')

            if i.get('type') == 'floppy':
                ET.SubElement(xml_disk, 'readonly')

            xml_root.find('devices').insert(1, xml_disk)

        xml_root.find('devices/interface/mac').set('address', mac)
        xml_root.find('devices/interface/model').set('type', 'virtio')

        xml = ET.tostring(xml_root).decode()

        return self.conn.defineXML(xml)
