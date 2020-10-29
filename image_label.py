# coding=utf-8
import cv2
import numpy as np
import matplotlib.pyplot as plt

from PyQt5 import QtGui
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QLabel

class QImageLabel(QLabel):
    ocr_signal = pyqtSignal(np.object)
    def __init__(self, *args, **kwargs):
        super(QImageLabel, self).__init__(*args, **kwargs)
        self._image = None
        self._mouse_status = None
        self.rects = []
        self._left_button_status = 0

    def mousePressEvent(self, ev: QtGui.QMouseEvent) -> None:
        if ev.button() == Qt.LeftButton:
            self._start_pos = ev.pos()
            self._left_button_status = 1

    def mouseMoveEvent(self, ev: QtGui.QMouseEvent) -> None:
        if self._left_button_status == 1:
            pt2 = ev.pos()
            self.show_image(rects=self.rects + [self._pretreat_pts(self._start_pos, pt2)])

    def mouseReleaseEvent(self, ev: QtGui.QMouseEvent) -> None:
        if ev.button() == Qt.LeftButton:
            self._left_button_status = 0
            pt1, pt2 = self._start_pos, ev.pos()
            rect = self._pretreat_pts(pt1, pt2)
            self.rects.append(rect)
            self.ocr_recognization(rect)
        if self._image is None:
            return
        self.show_image(rects=self.rects)

    def keyPressEvent(self, ev: QtGui.QKeyEvent) -> None:
        pass

    def ocr_recognization(self, rect):
        x1, y1, x2, y2 = rect
        roi = self._image[y1:y2, x1:x2]
        w, h = roi.shape[:2]
        if w < 5 or h < 5:
            return
        self.ocr_signal.emit(roi)

    def _pretreat_pts(self, pt1, pt2):
        x1, y1 = pt1.x(), pt1.y()
        x2, y2 = pt2.x(), pt2.y()
        return min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2)

    def draw_rects(self, image, rects):
        if not isinstance(image, np.ndarray) or image.ndim != 3:
            return
        for x1, y1, x2, y2 in rects:
            cv2.rectangle(image, (x1, y1), (x2, y2), (255, 128, 0), 2)
        return image

    def _to_pixmap(self, image):
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        h, w, d = image.shape
        q_image = QImage(image.data, w, h, w * d, QImage.Format_BGR888)
        pixmap = QPixmap.fromImage(q_image)
        return pixmap

    def show_image(self, image=None, rects=None):
        if image is not None:
            self._image = image
            fxy = min(self.width() / self._image.shape[0], self.height() / self._image.shape[1])
            self._image = cv2.resize(self._image, None, fx=fxy, fy=fxy, interpolation=cv2.INTER_AREA)
        image = np.copy(self._image)

        if rects is not None:
            image = self.draw_rects(image, rects)

        pixmap = self._to_pixmap(image)
        self.setPixmap(pixmap)

    def clear_rects(self):
        self.rects = []
