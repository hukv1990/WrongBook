# coding=utf-8
import os
import logging

import cv2
import numpy as np

from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QMainWindow, QFileDialog
from ui_main_window import Ui_MainInterface

from ocr_reg import OcrAipBaidu


class MainInterface(QMainWindow, Ui_MainInterface, QObject):
    def __init__(self):
        super(MainInterface, self).__init__()
        self._set_ui()
        self._src_root = ''
        self._image_list = []
        self._cur_idx = -1

        self._img_ext = ['.jpg', '.bmp', '.jpeg', '.png']
        self.ocr = OcrAipBaidu()
        self.questions = dict()

    def _set_ui(self):
        self.setupUi(self)
        self.setWindowTitle(u'OCR')

        self.actionOpen.triggered.connect(self.action_open_triggered_slot)
        self.actionNext.triggered.connect(self.action_next_triggered_slot)
        self.actionPrevious.triggered.connect(self.action_prev_triggered_slot)
        self.actionSave.triggered.connect(self.action_save_slot)

        self.label.ocr_signal.connect(self.ocr_recog_slot)

        self.setFocus()

    def _is_image(self, filepath):
        postfix = os.path.splitext(filepath)[-1]
        return postfix in self._img_ext

    def _get_image_paths(self, src_root):
        self._src_root = src_root
        for fn in os.listdir(self._src_root):
            filepath = os.path.join(self._src_root, fn)
            if self._is_image(filepath):
                self._image_list.append(filepath)

    def action_open_triggered_slot(self):
        image_root = QFileDialog.getExistingDirectory(self, 'FileOpen')
        if image_root is None or len(image_root) == 0:
            return
        self._get_image_paths(image_root)
        if len(self._image_list) != 0:
            self._cur_idx = 0
        self._show_image()

    def action_next_triggered_slot(self, status):
        self._change_index(offset=1)

    def action_prev_triggered_slot(self, status):
        self._change_index(offset=-1)

    def action_save_slot(self):
        self.questions[self._cur_idx] = self.textEdit.toPlainText()
        filepath:str = QFileDialog.getSaveFileName(self, 'Save to', filter='*.txt')[0]
        if filepath is None or len(filepath) == 0:
            return
        with open(filepath, 'w', encoding='utf-8') as fout:
            for page in self.questions.keys():
                print(self.questions[page], file=fout)

    def _change_index(self, offset=0):
        if len(self._image_list) == 0:
            return
        self.questions[self._cur_idx] = self.textEdit.toPlainText()
        self._cur_idx += offset
        if self._cur_idx < 0:
            self._cur_idx = 0
        elif self._cur_idx >= len(self._image_list):
            self._cur_idx = len(self._image_list) - 1
        self.label.clear_rects()
        self._show_image()
        self.textEdit.setText(self.questions.get(self._cur_idx, ''))

    def ocr_recog_slot(self, roi):
        ret = self.ocr(roi)
        if ret is None:
            return
        str = ''
        for w_dict in ret:
            line = w_dict['words']
            if len(line) > 2:
                if line[0] in ['A', 'B', 'C','D', 'E', 'F', 'G']:
                    if line[1] in ['.', ':', ' ']:
                        line = f"{line[0]}.{line[2:]}"
                    else:
                        line = f"{line[0]}.{line[1:]}"
            str += line + '\n'
        # self.textEdit.setText(str + '\n')
        self.textEdit.append(str + '\n')
        return str

    def _load_image(self, filepath, flags=cv2.IMREAD_COLOR):
        return cv2.imdecode(np.fromfile(filepath, dtype=np.uint8), flags)

    def _show_image(self):
        if len(self._image_list) == 0:
            return
        image_path = self._image_list[self._cur_idx]
        logging.info(image_path)
        image = self._load_image(image_path)
        if image is None:
            return
        self.label.show_image(image)
        self.statusbar.showMessage(f"{self._cur_idx + 1}/{len(self._image_list)}")



