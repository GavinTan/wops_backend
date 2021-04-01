from channels.generic.websocket import WebsocketConsumer
import socket
import cv2
import base64
import threading

camera1=[]
frame=cv2.imread("1.jpg", cv2.IMREAD_COLOR)
rtsp_path='rtsp://admin:HuaWei123@nb33.3322.org:8331/LiveMedia/ch1/Media1/trackID=1'


class VncConsumer(WebsocketConsumer):
    a = 0

    def vedio_thread1(self):
        print('send')
        while True:
            if self.a > 0:
                image = cv2.imencode('.jpg', frame)[1]
                base64_data = base64.b64encode(image)
                s = base64_data.decode()
                print(1111)
                # print('data:image/jpeg;base64,%s'%s)
                self.send('data:image/jpeg;base64,%s' % s)

    def vedio_thread2(self):
        global camera1
        camera1 = cv2.VideoCapture(rtsp_path)
        global frame
        while True:
            _, img_bgr = camera1.read()
            if img_bgr is None:
                camera1 = cv2.VideoCapture(rtsp_path)
                print('丢失帧')
            else:
                frame = img_bgr
                self.a = 1

    def connect(self):
        self.accept()
        thread1 = threading.Thread(target=self.vedio_thread1)
        #     thread1.setDaemon(True)
        thread1.start()
        thread2 = threading.Thread(target=self.vedio_thread2)
        #     thread1.setDaemon(True)
        thread2.start()
        # self.send(s)


    def receive(self, *, text_data):
        pass

    def disconnect(self, message):
        pass
