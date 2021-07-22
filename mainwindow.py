import os
import sys

import numpy as np
from PyQt5.QtGui import QPalette, QImage, QPixmap, QPainter, QPen, qRgb
from PyQt5.QtPrintSupport import QPrinter
from PyQt5.QtWidgets import QFileDialog, QMainWindow, QLabel, \
    QSizePolicy, QScrollArea, QAction, QMenu, QMessageBox, QFrame
from PyQt5.QtCore import Qt, QPoint
import cv2 as cv


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.cvImage = None
        self.filePath = os.getcwd() + "file.png"

        self.imageLabel = QLabel()
        self.imageLabel.setBackgroundRole(QPalette.Base)
        self.imageLabel.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.imageLabel.setScaledContents(True)

        self.scrollArea = QScrollArea()
        self.scrollArea.setBackgroundRole(QPalette.Dark)
        self.scrollArea.setWidget(self.imageLabel)
        self.scrollArea.setVisible(False)

        self.setCentralWidget(self.scrollArea)
        self.setWindowTitle("Image Viewer")
        self.resize(800, 600)
        self.open()

    def open(self):
        options = QFileDialog.Options()
        self.filePath, _ = QFileDialog.getOpenFileName(self, 'QFileDialog.getOpenFileName()', '',
                                                       'Images (*.png *.jpeg *.jpg *.bmp *.gif)', options=options)
        print(self.filePath)
        if self.filePath:
            image = QImage(self.filePath)
            if image.isNull():
                QMessageBox.information(self, "Image Viewer", "Cannot load %s." % self.filePath)
                return

        self.cvImage = cv.imread(self.filePath, 0)
        self.setWindowTitle(self.filePath)
        self.changeLabelPic(self.cvImage)

    def changeLabelPic(self, cvImage):
        self.image = self.convertCv2ToQimage(cvImage)
        self.imageLabel.setPixmap(QPixmap.fromImage(self.image))

    def convertCv2ToQimage(self, im):
        qim = QImage()
        if im is None:
            return qim
        if im.dtype == np.uint8:
            if len(im.shape) == 2:
                qim = QImage(im.data, im.shape[1], im.shape[0], im.strides[0], QImage.Format_Indexed8)
                qim.setColorTable([qRgb(i, i, i) for i in range(256)])
            elif len(im.shape) == 3:
                if im.shape[2] == 3:
                    qim = QImage(im.data, im.shape[1], im.shape[0], im.strides[0], QImage.Format_RGB888)
                elif im.shape[2] == 4:
                    qim = QImage(im.data, im.shape[1], im.shape[0], im.strides[0], QImage.Format_ARGB32)
        return qim
