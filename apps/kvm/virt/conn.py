import libvirt
import socket
import threading
from django.conf import settings
from libvirt import libvirtError

CONN_SOCKET = 4
CONN_TLS = 3
CONN_SSH = 2
CONN_TCP = 1

TLS_PORT = 16514
SSH_PORT = 22
TCP_PORT = 16509


LIBVIRT_CONNECT_POOL = getattr(settings, 'LIBVIRT_CONNECT_POOL', {})
# libvirt.virEventRegisterDefaultImpl()


def server_available(server, port):
    try:
        socket_host = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket_host.settimeout(3)
        socket_host.connect((server, port))
        socket_host.close()
        return True
    except:
        return False


class VirtConn(object):
    """
    @type connect: libvirt.virConnect
    """

    def __init__(self, host, username, password=None, conn_type=2, conn_port=22):
        self.connect = None
        self.host = host
        self.username = username
        self.password = password
        self.conn_type = conn_type
        self.conn_port = conn_port
        self._connect()
        self._set_keepalive()

    def _connect(self):
        if self.conn_type == CONN_SSH:
            self.__connect__ssh()
        elif self.conn_type == CONN_TCP:
            self.__connect__tcp()
        else:
            raise ValueError('连接类型错误，目前只支持SSH！')

    def _set_keepalive(self):
        if self.connected:
            keepalive_interval = getattr(settings, 'LIBVIRT_KEEPALIVE_INTERVAL', 5)
            keepalive_count = getattr(settings, 'LIBVIRT_KEEPALIVE_COUNT', 5)
            self.connect.setKeepAlive(keepalive_interval, keepalive_count)

    def __connect__ssh(self):
        uri = f'qemu+ssh://{self.username}@{self.host}:{self.conn_port}/system'
        conn = libvirt.open(uri)
        self.connect = conn

    def __connect__tcp(self):
        uri = f'qemu+tcp://{self.host}:{self.conn_port}/system'
        conn = libvirt.open(uri)
        self.connect = conn

    @property
    def connected(self):
        try:
            return self.connect is not None and self.connect.isAlive()
        except libvirtError:
            return False


class VirtConnManage:
    def __init__(self, host, username='root', password=None, conn_type=2, conn_port=22, timeout=0):
        self.host = host
        self.username = username
        self.password = password
        self.conn_type = conn_type
        self.conn_port = conn_port
        self.timeout = timeout
        self.pool = LIBVIRT_CONNECT_POOL
        self._run_virt_event_loop()
        self.connect = self._to_connect()

    def _get_connect(self):
        if self.host in self.pool:
            for i, conn in enumerate(self.pool[self.host]):
                if conn.host == self.host and conn.username == self.username and conn.conn_type == self.conn_type:
                    if conn.connected:
                        return conn
                    else:
                        del self.pool[self.host][i]
        return None

    def _to_connect(self):
        conn = self._get_connect()
        if conn is None:
            conn = VirtConn(self.host, self.username, self.password, self.conn_type, self.conn_port)
            self.pool.setdefault(self.host, []).append(conn)
            if self.timeout > 0:
                libvirt.virEventAddTimeout(1000 * self.timeout, self._conn_timeout_callback, len(self.pool) - 1)
        if conn.connected:
            return conn.connect
        else:
            raise libvirtError('not connect')

    def _virt_event_loop(self):
        while True:
            libvirt.virEventRunDefaultImpl()

    def _run_virt_event_loop(self):
        t = threading.Thread(target=self._virt_event_loop)
        t.setDaemon(True)
        t.start()

    def _conn_timeout_callback(self, timer, opaque):
        print('timeout callback')
        # self.pool[self.host][opaque].connect.close()
        del self.pool[self.host][opaque]
        libvirt.virEventRemoveTimeout(timer)

    def __conn_close_callback(self, conn, reason, opaque):
        del self.pool[self.host][opaque]
        print(conn)
        print(reason)
        print(opaque)
        print('is close')
