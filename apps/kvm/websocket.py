import json
import time

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from guacamole.client import GuacamoleClient
from threading import Thread
import uuid
from django.conf import settings
from django.core.cache import cache


class Kvm(WebsocketConsumer):
    def connect(self):
        print(self.scope)
        self.accept('guacamole')
        self.client = GuacamoleClient('172.16.7.14', 4822)
        print(cache.get('console'))
        self.client.handshake(protocol='vnc', hostname=cache.get('console').get('server').get('host'), port=cache.get('console').get('console_port'), font_name='Menlo')
        # self.client.handshake(protocol='vnc', hostname='172.16.7.254', width=1920, height=1080, port=5908, font_name='Menlo')
        # self.client.handshake(protocol='rdp',
        #                  hostname='172.16.7.17',
        #                  port=3389,
        #                  username='administrator',
        #                  password='abcu123456',
        #                  ignore_cert='true',
        #                       color_depth=24,
        #                       enable_wallpaper='true',
        #                       enable_theming='true',
        #                  disable_glyph_caching='true',
        #                       enable_font_smoothing='true',
        #                       enable_desktop_composition='true',
        #                       enable_menu_animations='true',
        #                       enable_drive='true',
        #                       drive_path='/tmp/aa',
        #                       drive_name='aa',
        #                       create_drive_path='true'
        #                  )

        self.send('0.,36.83940151-b2f9-4743-b5e4-b6eb85a97743;')
        def f1():
            while True:
                instruction = self.client.receive()
                if instruction:
                    self.send(text_data=instruction)
                else:
                    print('no ret')

        t1 = Thread(target=f1)
        t1.setDaemon(True)
        t1.start()

    def disconnect(self, close_code):
        self.client.close()

    def receive(self, text_data):
        print(text_data)
        self.client.send(text_data)
        pass
        # self.client.send(str(text_data))
        # text_data_json = json.loads(text_data)
        # message = text_data_json['message']
        #
        # self.send(text_data=json.dumps({
        #     'message': message
        # }))

    def send_message(self, event):
        self.send(event.get('output'))
