import os

import cv2 as cv
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QPoint, QSize, QRect
from PyQt5.QtGui import QPalette, QImage, QPixmap, QIcon
from PyQt5.QtWidgets import QFileDialog, QMainWindow, QLabel, \
    QSizePolicy, QScrollArea, QAction, QMenu, QMessageBox, QRubberBand, QActionGroup, QWidget, QGridLayout, QGroupBox, \
    QRadioButton, QSlider, QVBoxLayout, QHBoxLayout
from PIL import Image

import data_singleton
from PyQyWrapper import convertCv2ToQimage, convertQImageToMat
from restorer import removeDamage, colorize, inpaintDamage, Rect


class SettingsWindow(QMainWindow):
    def __init__(self, parent=None):
        super(SettingsWindow, self).__init__(parent)
        self.setCentralWidget(Sliders())
        self.setWindowTitle("Settings")
        self.resize(400, 200)


class Sliders(QWidget):
    def __init__(self):
        super(Sliders, self).__init__()
        self.singleton = data_singleton.instance
        grid = QGridLayout()

        self.closing_gbox = self.get_slider('Closing', self.singleton.set_closing, self.singleton.closing_value)

        self.dilation_gbox = self.get_slider('Dilation', self.singleton.set_dilation, self.singleton.dilation_value)

        self.blur_gbox = self.get_slider('Blur', self.singleton.set_blur, self.singleton.blur_value)

        grid.addWidget(self.closing_gbox)
        grid.addWidget(self.dilation_gbox)
        grid.addWidget(self.blur_gbox)

        self.setLayout(grid)

    def get_slider(self, label_text, value_var, default):
        slider = QSlider(Qt.Horizontal)
        slider.setFocusPolicy(Qt.StrongFocus)
        slider.setTickPosition(QSlider.TicksBelow)
        slider.setValue(default)
        slider.setTickInterval(1)
        slider.setSingleStep(1)
        slider.setMinimum(1)
        slider.setMaximum(15)

        vbox = QVBoxLayout()
        vbox.addWidget(slider)
        vbox.addStretch(1)

        gbox = QGroupBox(label_text)
        gbox.setLayout(vbox)
        slider.valueChanged[int].connect(value_var)
        return gbox
