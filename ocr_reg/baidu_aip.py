# coding=utf-8
import base64

from aip import AipOcr
import json
import cv2
import numpy as np


class OcrAipBaidu(object):
    APP_ID = '21767670'
    API_KEY = 'T1hcKpVvikhnOLfZRUIbUUl2'
    SECRET_KEY = 'wRB70sukGq2pqMFIDPF9thaegyrO4fED'

    def __init__(self):
        self.client = AipOcr(self.APP_ID, self.API_KEY, self.SECRET_KEY)

    @staticmethod
    def get_file_content(filePath):
        with open(filePath, 'rb') as fp:
            return fp.read()

    def __call__(self, image):
        if isinstance(image, str):
            image = self.get_file_content(image)
        elif isinstance(image, np.ndarray):
            image = cv2.imencode('.jpg', image)[1].tostring()
        return self.client.basicGeneral(image).get('words_result', None)


if __name__ == '__main__':

    image= cv2.imread('../images/2.jpg')
    ocr = OcrAipBaidu()
    ret = ocr(image)
    print(ret)