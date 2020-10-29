# coding=utf-8

import sys
from PyQt5.QtWidgets import QApplication
from main_interface import MainInterface

if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = MainInterface()
    w.show()
    sys.exit(app.exec_())
