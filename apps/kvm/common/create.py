import string
from apps.kvm.common import utils
from apps.kvm.common.kvm import KvmBase


def get_rbd_storage_data(stg):
    xml = stg.XMLDesc(0)
    ceph_user = utils.get_xml_path(xml, "/pool/source/auth/@username")

    def get_ceph_hosts(doc):
        hosts = list()
        for host in doc.xpath("/pool/source/host"):
            name = host.prop("name")
            if name:
                hosts.append({'name': name, 'port': host.prop("port")})
        return hosts

    ceph_hosts = utils.get_xml_path(xml, func=get_ceph_hosts)
    secret_uuid = utils.get_xml_path(xml, "/pool/source/auth/secret/@uuid")
    return ceph_user, secret_uuid, ceph_hosts


class VmCreate(KvmBase):

    def get_storages_images(self):
        """
        Function return all images on all storages
        """
        images = list()
        storages = self.get_storages(only_actives=True)
        for storage in storages:
            stg = self.get_storage(storage)
            try:
                stg.refresh(0)
            except:
                pass
            for img in stg.listVolumes():
                if img.lower().endswith('.iso'):
                    pass
                else:
                    images.append(img)
        return images

    def get_os_type(self):
        """Get guest os type"""
        return utils.get_xml_path(self.get_cap_xml(), "/capabilities/guest/os_type")

    def get_host_arch(self):
        """Get guest capabilities"""
        return utils.get_xml_path(self.get_cap_xml(), "/capabilities/host/cpu/arch")

    def create_volume(self, name, size, pool='default'):
        name = name + '.img'

        stgvol_xml = f"""
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
        stg.createXML(stgvol_xml, 0)
        try:
            stg.refresh(0)
        except:
            pass
        vol = stg.storageVolLookupByName(name)
        return vol.path()

    def get_volume_type(self, path):
        vol = self.get_volume_by_path(path)
        vol_type = utils.get_xml_path(vol.XMLDesc(0), "/volume/target/format/@type")
        if vol_type == 'unknown' or vol_type == 'iso':
            return 'raw'
        if vol_type:
            return vol_type
        else:
            return 'raw'

    def get_volume_path(self, volume, pool=None):
        if not pool:
            storages = self.get_storages(only_actives=True)
        else:
            storages = [pool]
        for storage in storages:
            stg = self.get_storage(storage)
            if stg.info()[0] != 0:
                stg.refresh(0)
                for img in stg.listVolumes():
                    if img == volume:
                        vol = stg.storageVolLookupByName(img)
                        return vol.path()

    def get_storage_by_vol_path(self, vol_path):
        vol = self.get_volume_by_path(vol_path)
        return vol.storagePoolLookupByVolume()

    def clone_from_template(self, clone, template, storage=None, metadata=False, disk_owner_uid=0, disk_owner_gid=0):
        vol = self.get_volume_by_path(template)
        if not storage:
            stg = vol.storagePoolLookupByVolume()
        else:
            stg = self.get_storage(storage)

        storage_type = utils.get_xml_path(stg.XMLDesc(0), "/pool/@type")
        format = utils.get_xml_path(vol.XMLDesc(0), "/volume/target/format/@type")
        if storage_type == 'dir':
            clone += '.img'
        else:
            metadata = False
        xml = f"""
            <volume>
                <name>{clone}</name>
                <capacity>0</capacity>
                <allocation>0</allocation>
                <target>
                    <format type='{format}'/>
                     <permissions>
                        <owner>{disk_owner_uid}</owner>
                        <group>{disk_owner_gid}</group>
                        <mode>0644</mode>
                        <label>virt_image_t</label>
                    </permissions>
                    <compat>1.1</compat>
                    <features>
                        <lazy_refcounts/>
                    </features>
                </target>
            </volume>"""
        stg.createXMLFrom(xml, vol, metadata)
        clone_vol = stg.storageVolLookupByName(clone)
        return clone_vol.path()

    def _defineXML(self, xml):
        self.wvm.defineXML(xml)

    def delete_volume(self, path):
        vol = self.get_volume_by_path(path)
        vol.delete()

    def create_instance(self, uuid, name, memory, vcpu, arch, machine, disk, image, floppy=None, mac=utils.randomMAC()):
        """
        Create VM function
        """
        caps = self.get_capabilities(arch)
        print(caps)
        dom_caps = self.get_dom_capabilities(arch, machine)
        print(dom_caps)

        memory = int(memory) * 1024

        xml = f"""<domain type='kvm'>
                  <name>{name}</name>
                  <uuid>{uuid}</uuid>
                  <memory unit='KiB'>{memory}</memory>
                  <vcpu>{vcpu}</vcpu>
                  <os>
                    <type arch='{arch}' machine='{machine}'>{caps["os_type"]}</type>
                    <boot dev='hd'/>
                    <boot dev='cdrom'/>
                    <bootmenu enable='yes'/>
                  </os>"""

        if caps["features"]:
            xml += """<features>"""
            if 'acpi' in caps["features"]:
                xml += """<acpi/>"""
            if 'apic' in caps["features"]:
                xml += """<apic/>"""
            if 'pae' in caps["features"]:
                xml += """<pae/>"""

            xml += """</features>"""
        xml += f"""
                  <cpu mode='host-model'/>
                  <clock offset='localtime'/>
                  <on_poweroff>destroy</on_poweroff>
                  <on_reboot>restart</on_reboot>
                  <on_crash>restart</on_crash>
                  <devices>
                    <disk type='file' device='disk'>
                      <source file='{disk}'/>
                      <driver name='qemu' type='qcow2'/>
                      <target dev='vda' bus='virtio'/>
                    </disk>"""
        if floppy:
            xml += f"""
                    <disk type='file' device='floppy'>
                      <source file='{floppy}'/>
                      <driver name='qemu' type='raw'/>
                      <target dev='fda' bus='fdc'/>
                    </disk>
                    """
        xml += f"""
                    <disk type='file' device='cdrom'>
                      <source file='{image}'/>
                      <target dev='hda' bus='ide'/>
                    </disk>
                    <interface type='bridge'>
                      <mac address='{mac}'/>
                      <source bridge='br0'/>
                      <model type='virtio'/>
                    </interface>
                    <console type="pty"/>"""

        if 'usb' in dom_caps['disk_bus']:
            xml += """<input type='mouse' bus='usb'/>"""
            xml += """<input type='keyboard' bus='usb'/>"""
            xml += """<input type='tablet' bus='usb'/>"""
        else:
            xml += """<input type='mouse'/>"""
            xml += """<input type='keyboard'/>"""
            xml += """<input type='tablet'/>"""

        xml += """<graphics type='vnc' port='-1' autoport='yes' listen='0.0.0.0'/>
                  <video>
                    <model type="vga"/>
                  </video>
                </devices>
              </domain>"""

        self._defineXML(xml)
