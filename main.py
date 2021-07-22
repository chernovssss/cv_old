#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os

import cv2 as cv
from PyQt5.QtCore import QPoint, QSize, QRect
from PyQt5.QtGui import QPalette, QImage, QPixmap, QIcon
from PyQt5.QtWidgets import QFileDialog, QMainWindow, QLabel, \
    QSizePolicy, QScrollArea, QAction, QMenu, QMessageBox, QRubberBand, QActionGroup
from PIL import Image

from PyQyWrapper import convertCv2ToQimage, convertQImageToMat
from restorer import removeDamage, colorize, inpaintDamage, Rect, blurDamage

from settingsWindow import SettingsWindow
import data_singleton


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.cvImage = None
        self.originImage = None
        self.image = None
        self.rect = None
        self.filePath = os.getcwd() + "file.png"
        self.colorized = None

        self.imageLabel = QLabel()
        self.imageLabel.setBackgroundRole(QPalette.Base)
        self.imageLabel.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.imageLabel.setScaledContents(True)

        self.rubberband = QRubberBand(QRubberBand.Rectangle, self.imageLabel)
        self.setMouseTracking(True)

        self.scrollArea = QScrollArea()
        self.scrollArea.setBackgroundRole(QPalette.Dark)
        self.scrollArea.setWidget(self.imageLabel)
        self.scrollArea.setVisible(False)

        self.settingsWindow = SettingsWindow(self)

        self.createActions()
        self.createMenus()
        self.createToolBars()

        self.setCentralWidget(self.scrollArea)
        self.setWindowTitle("Some shity app...")
        self.resize(800, 800)

    def createToolBars(self):
        self.toolbar = self.addToolBar('Restore')
        self.toolbar.setMovable(False)

        self.toolbar.addAction(self.restorePartAct)
        self.toolbar.addAction(self.undoPartAct)
        self.toolbar.addAction(self.applyBlurAct)
        self.toolbar.addSeparator()
        self.toolbar.addSeparator()
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.inpaintPartAct)

    def createActions(self):
        # TODO: Add ShortCut's
        self.openAct = QAction("&Open...", self, shortcut="Ctrl+O", triggered=self.open)
        self.saveAct = QAction("&Save...", self, shortcut="Ctrl+S", triggered=self.save)
        self.exitAct = QAction("E&xit", self, shortcut="Ctrl+Q", triggered=self.close)

        self.settingsOpenAct = QAction("Settings", self, shortcut="", triggered=self.settingsOpen)

        self.restoreAct = QAction("&Restore", self, shortcut="", triggered=self.restore, enabled=False)
        self.colorizeAct = QAction("&Colorize", self, shortcut="", triggered=self.colorize, enabled=False)


        self.restorePartAct = QAction(QIcon('icons/crack.png'), "R&estorePart", self, enabled=False,
                                      checkable=True, shortcut="")
        self.inpaintPartAct = QAction(QIcon('icons/paint-roller.png'), "InpaintPart", self, enabled=False,
                                      checkable=True, shortcut="")
        self.undoPartAct = QAction(QIcon('icons/undo.png'), "UndoPart", self, enabled=False,
                                   checkable=True, shortcut="")
        self.applyBlurAct = QAction(QIcon('icons/blur.png'), "BlurPart", self, enabled=False,
                                   checkable=True, shortcut="")

        self.restoreGroup = QActionGroup(QMenu('Tools', self))
        self.restoreGroup.addAction(self.restorePartAct)
        self.restoreGroup.addAction(self.inpaintPartAct)
        self.restoreGroup.addAction(self.undoPartAct)
        self.restoreGroup.addAction(self.applyBlurAct)

        self.restoreGroup.setExclusive(True)

    def settingsOpen(self):
        self.settingsWindow.show()

    def updateActions(self):
        self.restoreAct.setEnabled(True)
        self.colorizeAct.setEnabled(True)
        self.restorePartAct.setEnabled(True)
        self.inpaintPartAct.setEnabled(True)
        self.undoPartAct.setEnabled(True)
        self.saveAct.setEnabled(True)
        self.applyBlurAct.setEnabled(True)

    def undo(self):
        self.cvImage[
        self.rect.start.y: self.rect.end.y,
        self.rect.start.x: self.rect.end.x] = self.originImage[
                                              self.rect.start.y: self.rect.end.y,
                                              self.rect.start.x: self.rect.end.x]
        self.updateLabelPixmap(self.cvImage)

    def restore(self):
        if not self.restorePartAct.isChecked() or self.rect is None:
            self.cvImage = removeDamage(self.cvImage)
        else:
            restoredPart = removeDamage(
                self.cvImage[self.rect.start.y: self.rect.end.y, self.rect.start.x: self.rect.end.x])
            self.cvImage[self.rect.start.y: self.rect.end.y, self.rect.start.x: self.rect.end.x] = restoredPart
        self.updateLabelPixmap(self.cvImage)

    def colorize(self):
        self.colorized = colorize(self.cvImage)
        self.updateLabelPixmap(self.colorized)

    def blur(self):
        restoredPart = blurDamage(
            self.cvImage[self.rect.start.y: self.rect.end.y, self.rect.start.x: self.rect.end.x])
        self.cvImage[self.rect.start.y: self.rect.end.y, self.rect.start.x: self.rect.end.x] = restoredPart
        self.updateLabelPixmap(self.cvImage)

    def inpaint(self):
        restoredPart = inpaintDamage(self.cvImage, self.rect)
        self.cvImage[self.rect.start.y: self.rect.end.y, self.rect.start.x: self.rect.end.x] = restoredPart
        self.updateLabelPixmap(self.cvImage)

    def createMenus(self):
        self.fileMenu = QMenu("&File", self)
        self.fileMenu.addAction(self.openAct)
        self.fileMenu.addAction(self.saveAct)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.exitAct)

        # TODO Add rescale
        self.viewMenu = QMenu("&View", self)
        self.viewMenu.addSeparator()

        self.restoreMenu = QMenu('&Restore', self)
        self.restoreMenu.addAction(self.restoreAct)
        self.restoreMenu.addAction(self.colorizeAct)
        self.restoreMenu.addSeparator()
        self.restoreMenu.addAction(self.restorePartAct)
        self.restoreMenu.addAction(self.applyBlurAct)

        self.windowMenu = QMenu('Settings', self)
        self.windowMenu.addAction(self.settingsOpenAct)

        self.menuBar().addMenu(self.fileMenu)
        self.menuBar().addMenu(self.viewMenu)
        self.menuBar().addMenu(self.restoreMenu)
        self.menuBar().addMenu(self.windowMenu)

    def mousePressEvent(self, event):
        self.rubberband.hide()
        self.origin = self.imageLabel.mapFromParent(event.pos() -
                                                    QPoint(0, self.menuBar().size().height()
                                                           + self.toolbar.size().height()))
        self.rubberband.setGeometry(QRect(self.origin, QSize()))
        self.rubberband.show()

    def mouseReleaseEvent(self, event):
        rect = self.rubberband.geometry()
        self.rect = None
        if rect.width() > 10 and rect.height() > 10:
            self.rect = Rect(rect.x(), rect.y(), rect.width(), rect.height())
            self.selectedImage = self.cropImage(rect)

            if self.restorePartAct.isChecked():
                self.restore()
            elif self.inpaintPartAct.isChecked():
                self.inpaint()
            elif self.undoPartAct.isChecked():
                self.undo()
            elif self.applyBlurAct.isChecked():
                self.blur()

    def mouseMoveEvent(self, event):
        if self.rubberband.isVisible():
            # Control the Rubber within the imageViewer
            # rubberband ScrollArea support
            scrollBarPos = QPoint(self.scrollArea.horizontalScrollBar().value(),
                                  self.scrollArea.verticalScrollBar().value() -
                                  (self.menuBar().size().height() + self.toolbar.size().height())
                                  )
            self.rubberband.setGeometry(QRect(self.origin, event.pos() + scrollBarPos) & self.image.rect())

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
            self.originImage = self.cvImage.copy()
            self.updateLabelPixmap(self.cvImage)

            self.setWindowTitle(self.filePath)

            self.scrollArea.setVisible(True)
            self.updateActions()
            self.rubberband.hide()
            self.imageLabel.adjustSize()

    def updateLabelPixmap(self, cvImage):
        self.image = convertCv2ToQimage(cvImage)
        self.imageLabel.setPixmap(QPixmap.fromImage(self.image))

    def cropImage(self, rect):
        croppedImage = self.image.copy(rect)
        return convertQImageToMat(croppedImage)

    def save(self):
        if self.colorized is None:
            img = Image.fromarray(self.cvImage, mode=None)
        else:
            img = Image.fromarray(self.colorized, mode=None)
        path = QFileDialog.getSaveFileName(self, 'Save File')
        if path[0] and img is not None:
            print(path)
            img.save(f'{path[0]}.png')


if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication

    singleton = data_singleton.instance
    app = QApplication(sys.argv)
    restorer = MainWindow()
    restorer.show()
    sys.exit(app.exec_())
