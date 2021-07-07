import cv2
import time
import datetime
import requests
import numpy as np


class Camera:
    def __init__(self, is_webcam=False, username='justice', password='neverdie', url='', img_dir='save_data/img/'):
        self.is_webcam = is_webcam
        self.username = username
        self.password = password
        self.url = url
        self.img_dir = img_dir
        self.cnt = int(input('whats next(camera) : '))

        if is_webcam is False:
            CAM_ID = 0
            #self.cam = cv2.VideoCapture(cv2.CAP_DSHOW+CAM_ID)
            self.cam = cv2.VideoCapture(CAM_ID)

            if self.cam.isOpened() is False:
                print("Failed to open the cam")
            else:
                # 3은 가로 4는 세로 길이, default 설정에서 잘 변하지 않음.
                self.cam.set(3, 720)
                self.cam.set(4, 1080)

                self.cam.set(cv2.CAP_PROP_FPS, 30)  # fps 설정인데 안되는듯.
                frame_size = (int(self.cam.get(cv2.CAP_PROP_FRAME_WIDTH)),
                              int(self.cam.get(cv2.CAP_PROP_FRAME_HEIGHT)))
                # default 설정에서 안 바뀜.  30fps,  640 * 480
                print("frame_size", frame_size)
                print("fps", self.cam.get(cv2.CAP_PROP_FPS))

        self.prev_time = 0
        self.frame_rate = 30.0
        self.file_name = ''

    def get_img_from_cam(self):
        img = None
        if self.is_webcam is True:
            imgResp = requests.get(self.url, auth=(self.username, self.password))
            if imgResp.status_code == 200:
                ret = True
                imgNp = np.array(bytearray(imgResp.content), dtype=np.uint8)
                img = cv2.imdecode(imgNp, -1)
            else:
                ret = False
                print("Failed to request")
        else:
            ret, img = self.cam.read()

        return ret, img

    def get_img_name(self):
        # now = datetime.datetime.now()
        # now --> '%Y-%m-%d %H:%M:%S.6666'  소수점 초 까지 나옴.
        # nowDatetime = now.strftime('%Y-%m-%d_%H-%M-%S')
        # print(nowDatetime)
        # now = str(now).replace(' ', '_').replace(':', '-')
        now = self.cnt
        self.file_name = now
        self.cnt += 1
        # print(now)
        return now

    def save_img(self, is_show=False):
        ret, img = self.get_img_from_cam()
        img_name = str(self.get_img_name()).zfill(8)
        cv2.imwrite(self.img_dir + img_name +'.jpg', img)
        if is_show is True:
            cv2.imshow("Camera", img)