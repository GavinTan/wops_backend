from . import utils
from .kvm import KvmBase


class KvmStorageBase(KvmBase):
    def get_storages_info(self):
        get_storages = self.get_storages()
        storages = []
        for pool in get_storages:
            stg = self.get_storage(pool)
            stg_status = stg.isActive()
            stg_type = utils.get_xml_path(stg.XMLDesc(0), "/pool/@type")
            if stg_status:
                stg_vol = len(stg.listVolumes())
            else:
                stg_vol = None
            stg_size = stg.info()[1]
            storages.append({'name': pool, 'status': stg_status,
                             'type': stg_type, 'volumes': stg_vol,
                             'size': stg_size})
        return storages

    def define_storage(self, xml, flag):
        self.wvm.storagePoolDefineXML(xml, flag)

    def create_storage(self, name, target, source=None, stg_type='dir'):
        """
        stg_type: dir disk fs netfs logical gluster iscsi iscsi-direct scsi lvm mpath rbd sheepdog zfs vstorage

        link: https://libvirt.org/storage.html#StorageBackendDir
        """
        xml = f"""<pool type='{stg_type}'>
                 <name>{name}</name>"""
        if stg_type == 'logical':
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

    def create_storage_ceph(self, stg_type, name, ceph_pool, ceph_host, ceph_user, secret):
        xml = f"""
                <pool type='{stg_type}'>
                <name>{name}</name>
                <source>
                    <name>{ceph_pool}</name>
                    <host name='{ceph_host}' port='6789'/>
                    <auth username='{ceph_user}' type='ceph'>
                        <secret uuid='{secret}'/>
                    </auth>
                </source>
                </pool>
                """
        self.define_storage(xml, 0)
        stg = self.get_storage(name)
        stg.create(0)
        stg.setAutostart(1)

    def create_storage_netfs(self, stg_type, name, netfs_host, source, source_format, target):
        xml = f"""
                <pool type='{stg_type}'>
                <name>{name}</name>
                <source>
                    <host name='{netfs_host}'/>
                    <dir path='{source}'/>
                    <format type='{source_format}'/>
                </source>
                <target>
                    <path>{target}</path>
                </target>
                </pool>
                """
        self.define_storage(xml, 0)
        stg = self.get_storage(name)
        stg.create(0)
        stg.setAutostart(1)

        return stg


class KvmStoragePool(KvmBase):
    def __init__(self, host, login, passwd, conn, pool):
        KvmBase.__init__(self, host, login, passwd, conn)
        self.pool = self.get_storage(pool)

    def get_name(self):
        return self.pool.name()

    def get_status(self):
        status = ['Not running', 'Initializing pool, not available', 'Running normally', 'Running degraded']
        try:
            return status[self.pool.info()[0]]
        except ValueError:
            return 'Unknown'

    def get_size(self):
        return [self.pool.info()[1], self.pool.info()[3]]

    def _XMLDesc(self, flags):
        return self.pool.XMLDesc(flags)

    def _createXML(self, xml, flags):
        self.pool.createXML(xml, flags)

    def _createXMLFrom(self, xml, vol, flags):
        self.pool.createXMLFrom(xml, vol, flags)

    def _define(self, xml):
        return self.wvm.storagePoolDefineXML(xml, 0)

    def is_active(self):
        return self.pool.isActive()

    def get_uuid(self):
        return self.pool.UUIDString()

    def start(self):
        self.pool.create(0)

    def stop(self):
        self.pool.destroy()

    def delete(self):
        self.pool.undefine()

    def get_autostart(self):
        return self.pool.autostart()

    def set_autostart(self, value):
        self.pool.setAutostart(value)

    def get_type(self):
        return utils.get_xml_path(self._XMLDesc(0), "/pool/@type")

    def get_target_path(self):
        return utils.get_xml_path(self._XMLDesc(0), "/pool/target/path")

    def get_allocation(self):
        return int(utils.get_xml_path(self._XMLDesc(0), "/pool/allocation"))

    def get_available(self):
        return int(utils.get_xml_path(self._XMLDesc(0), "/pool/available"))

    def get_capacity(self):
        return int(utils.get_xml_path(self._XMLDesc(0), "/pool/capacity"))

    def get_pretty_allocation(self):
        return utils.pretty_bytes(self.get_allocation())

    def get_pretty_available(self):
        return utils.pretty_bytes(self.get_available())

    def get_pretty_capacity(self):
        return utils.pretty_bytes(self.get_capacity())

    def get_volumes(self):
        return self.pool.listVolumes()

    def get_volume(self, name):
        return self.pool.storageVolLookupByName(name)

    def get_volume_size(self, name):
        vol = self.get_volume(name)
        return vol.info()[1]

    def get_volume_allocation(self, name):
        vol = self.get_volume(name)
        return vol.info()[2]

    def _vol_XMLDesc(self, name):
        vol = self.get_volume(name)
        return vol.XMLDesc(0)

    def del_volume(self, name):
        vol = self.pool.storageVolLookupByName(name)
        vol.delete(0)

    def get_volume_type(self, name):
        vol_xml = self._vol_XMLDesc(name)
        return utils.get_xml_path(vol_xml, "/volume/target/format/@type")

    def refresh(self):
        self.pool.refresh(0)

    def update_volumes(self):
        try:
            self.refresh()
        except Exception:
            pass
        vols = self.get_volumes()
        vol_list = []

        for volname in vols:
            vol_list.append(
                {'name': volname,
                 'size': self.get_volume_size(volname),
                 'allocation': self.get_volume_allocation(volname),
                 'type': self.get_volume_type(volname)}
            )
        return vol_list

    def create_volume(self, name, size, vol_fmt='qcow2', metadata=False, disk_owner_uid=0, disk_owner_gid=0):
        size = int(size) * 1073741824
        storage_type = self.get_type()
        alloc = size
        if vol_fmt == 'unknown':
            vol_fmt = 'raw'
        if storage_type == 'dir':
            if vol_fmt in ('qcow', 'qcow2'):
                name += '.' + vol_fmt
            else:
                name += '.img'
            alloc = 0
        xml = f"""
            <volume>
                <name>{name}</name>
                <capacity>{size}</capacity>
                <allocation>{alloc}</allocation>
                <target>
                    <format type='{vol_fmt}'/>
                     <permissions>
                        <owner>{disk_owner_uid}</owner>
                        <group>{disk_owner_gid}</group>
                        <mode>0644</mode>
                        <label>virt_image_t</label>
                    </permissions>"""
        if vol_fmt == 'qcow2':
            xml += """
                      <compat>1.1</compat>
                      <features>
                         <lazy_refcounts/>
                      </features>"""
        xml += """</target>
                </volume>"""
        self._createXML(xml, metadata)
        return name

    def clone_volume(self, name, target_file, vol_fmt=None, metadata=False, mode='0644', file_suffix='img', disk_owner_uid=0, disk_owner_gid=0):
        vol = self.get_volume(name)
        if not vol_fmt:
            vol_fmt = self.get_volume_type(name)

        storage_type = self.get_type()
        if storage_type == 'dir':
            if vol_fmt in ['qcow', 'qcow2']:
                target_file += '.' + vol_fmt
            else:
                suffix = '.' + file_suffix
                target_file += suffix if len(suffix) > 1 else ''

        xml = f"""
            <volume>
                <name>{target_file}</name>
                <capacity>0</capacity>
                <allocation>0</allocation>
                <target>
                    <format type='{vol_fmt}'/>
                    <permissions>
                        <owner>{disk_owner_uid}</owner>
                        <group>{disk_owner_gid}</group>
                        <mode>{mode}</mode>
                        <label>virt_image_t</label>
                    </permissions>"""
        if vol_fmt == 'qcow2':
            xml += """
                    <compat>1.1</compat>
                    <features>
                        <lazy_refcounts/>
                    </features>"""
        xml += """ </target>
            </volume>"""
        self._createXMLFrom(xml, vol, metadata)
        return target_file
