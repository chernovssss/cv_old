
import sys
import os
import sys

import numpy as np
from PyQt5.QtGui import QPalette, QImage, QPixmap, QPainter, QPen, qRgb
from PyQt5.QtPrintSupport import QPrinter
from PyQt5.QtWidgets import QFileDialog, QMainWindow, QLabel, \
    QSizePolicy, QScrollArea, QAction, QMenu, QMessageBox, QFrame, QRubberBand
from PyQt5.QtCore import Qt, QPoint, QSize, QRect
import cv2 as cv

def convertQImageToMat(incomingImage):
    ''' Converts a QImage into an opencv MAT format '''

    incomingImage = incomingImage.convertToFormat(4)
    width = incomingImage.width()
    height = incomingImage.height()
    ptr = incomingImage.bits()
    ptr.setsize(incomingImage.byteCount())
    arr = np.array(ptr).reshape(height, width, 4)  # Copies the data
    return cv.cvtColor(arr, cv.COLOR_BGR2GRAY)

def convertCv2ToQimage(im):
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
