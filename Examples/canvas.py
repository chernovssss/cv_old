from PyQt5.QtGui import QPalette, QImage, QPixmap, QPainter, QPen
from PyQt5.QtPrintSupport import QPrinter
from PyQt5.QtWidgets import QFileDialog, QMainWindow, QLabel, \
    QSizePolicy, QScrollArea, QAction, QMenu, QMessageBox, QWidget, QUndoStack
from PyQt5.QtCore import Qt
import os.path


class Canvas(QWidget):
    def __init__(self, data_singleton):
        super().__init__()

        self.data_singleton = data_singleton

        # self.imageCopy = QImage()
        self.file_path = None

        self._edited = False
        self.mIsPaint = False
        self.m_is_resize = False
        self.mRightButtonPressed = False

        self.mPixmap = None
        self.mCurrentCursor = None
        self.mZoomFactor = 1.0

        self.mUndoStack = QUndoStack(self)
        self.mUndoStack.setUndoLimit(self.data_singleton.image.history_depth)

        self.setMouseTracking(True)

        # Цвет заднего фона, используется так же для ластика
        # self.background_color = Qt.transparent
        self.background_color = Qt.white

        im = QImage(self.data_singleton.image.base_width, self.data_singleton.image.base_height,
                    QImage.Format_ARGB32_Premultiplied)
        im.fill(self.background_color)
        self._image = None
        self.image = im

    # # Send primary color for ToolBar.
    # sendPrimaryColorView = Signal()
    #
    # # Send secondary color for ToolBar.
    # sendSecondaryColorView = Signal()
    #
    # send_new_image_size = Signal(int, int)
    # send_cursor_pos = Signal(int, int)
    # sendColor = Signal()
    #
    # # Send signal to restore previous checked instrument for ToolBar.
    # sendRestorePreviousInstrument = Signal()
    #
    # # Send instrument for ToolBar.
    # sendSetInstrument = Signal()
    #
    # # Send signal to enable copy cut actions in menu.
    # sendEnableCopyCutActions = Signal()
    #
    # # Send signal to selection instrument.
    # sendEnableSelectionInstrument = Signal()
    #
    # send_change_edited = Signal(bool)

    def save(self, file_path=None):
        # Если выполнено "Сохранить как", а холст не имеет файла
        if file_path is not None and self.file_path is None:
            self.file_path = file_path

        if file_path is not None:
            file_name = file_path
        else:
            file_name = self.file_path

        # Если не удалось сохранить
        if not self._image.save(file_name):
            raise Exception('Не удалось сохранить в "{}"'.format(file_name))

        # Если есть изменения и выполняем "сохранить как"
        # то edited=True, если текущий файл совпадает с сохраняемым
        if self.edited and file_path is not None:
            self.edited = self.file_path != file_path
        else:
            self.edited = False

    def load(self, file_path):
        self.file_path = file_path
        im = QImage()

        # Если не удалось загрузить
        if not im.load(file_path):
            raise Exception('Не удалось загрузить из "{}"'.format(file_path))

        self.edited = False
        self.image = im.convertToFormat(QImage.Format_ARGB32_Premultiplied)

    # def save(self):
    #     pass

    # def saveAs(self):
    #     pass
    #
    # def print(self):
    #     pass
    #
    # def resizeImage(self):
    #     pass
    #
    # def resizeCanvas(self):
    #     pass
    #
    # def rotateImage(self, flag):
    #     pass

    def get_file_name(self):
        if self.file_path is not None:
            return os.path.basename(self.file_path)

    def get_image(self):
        return self._image

    def set_image(self, im):
        self._image = im

        corner = self.rect_bottom_right_corner()
        self.resize(im.rect().right() + corner.width(), im.rect().bottom() + corner.height())
        self.update()

    image = property(get_image, set_image)

    def set_edited(self, flag):
        self._edited = flag
        self.send_change_edited.emit(flag)

    def get_edited(self):
        return self._edited

    edited = property(get_edited, set_edited)

    # def applyEffect(self, effect):
    #     pass
    #
    def restoreCursor(self):
        pass
    #
    # def zoomImage(self, factor):
    #     pass
    #
    # def setZoomFactor(self, factor):
    #     pass
    #
    # def getZoomFactor(self):
    #     pass

    def getUndoStack(self):
        return self.mUndoStack

    def setIsPaint(self, isPaint):
        self.mIsPaint = isPaint

    def isPaint(self):
        return self.mIsPaint

    # def emitPrimaryColorView(self):
    #     pass
    #
    # def emitSecondaryColorView(self):
    #     pass
    #
    # def emitColor(self, color):
    #     pass
    #
    # def emitRestorePreviousInstrument(self):
    #     pass
    #
    # def copyImage(self):
    #     pass
    #
    # def pasteImage(self):
    #     pass
    #
    # def cutImage(self):
    #     pass
    #
    # def saveImageChanges(self):
    #     pass

    def clearSelection(self):
        pass

    def push_undo_command(self, command):
        if command:
            self.mUndoStack.push(command)

    # def initializeImage(self):
    #     pass
    #
    # def open(self):
    #     pass
    #
    # def open(self, filePath):
    #     pass
    #
    # def drawCursor(self):
    #     pass
    #
    # def makeFormatsFilters(self):
    #     pass
    #
    # def autoSave(self):
    #     pass

    def rect_bottom_right_corner(self):
        return QRect(self._image.rect().right(), self._image.rect().bottom(), 6, 6)

    def get_instrument(self):
        return self.data_singleton.current_instrument

    def mousePressEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.rect_bottom_right_corner().contains(event.pos()):
            self.m_is_resize = True
            self.setCursor(Qt.SizeFDiagCursor)
        else:
            instrument = self.get_instrument()
            if instrument:
                instrument.mouse_press_event(event, self)

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        # InstrumentsEnum instrument = DataSingleton::Instance()->getInstrument();
        # mInstrumentHandler = mInstrumentsHandlers.at(DataSingleton::Instance()->getInstrument());
        # if(mIsResize)
        # {
        #      mAdditionalTools->resizeCanvas(event->x(), event->y());
        #      emit sendNewImageSize(mImage->size());
        # }
        # else if(event->pos().x() < mImage->rect().right() + 6 &&
        #         event->pos().x() > mImage->rect().right() &&
        #         event->pos().y() > mImage->rect().bottom() &&
        #         event->pos().y() < mImage->rect().bottom() + 6)
        # {
        #     setCursor(Qt::SizeFDiagCursor);
        #     if (qobject_cast<AbstractSelection*>(mInstrumentHandler))
        #         return;
        # }
        # else if (!qobject_cast<AbstractSelection*>(mInstrumentHandler))
        # {
        #     restoreCursor();
        # }
        # if(event->pos().x() < mImage->width() &&
        #         event->pos().y() < mImage->height())
        # {
        #     emit sendCursorPos(event->pos());
        # }
        #
        # if(instrument != NONE_INSTRUMENT)
        # {
        #     mInstrumentHandler->mouseMoveEvent(event, *this);
        # }

        x, y = event.pos().x(), event.pos().y()

        self.send_cursor_pos.emit(x, y)

        if self.m_is_resize:
            width, height = x, y

            if width > 1 or height > 1:
                temp_image = QImage(width, height, QImage.Format_ARGB32_Premultiplied)
                painter = QPainter(temp_image)
                painter.setPen(Qt.NoPen)
                # TODO: поддержать
                # painter.setBrush(QBrush(QPixmap("transparent.jpg")))
                painter.setBrush(self.data_singleton.secondary_color)
                painter.drawRect(QRect(0, 0, width, height))
                painter.drawImage(0, 0, self._image)
                painter.end()

                # Устанавлием изображение с новым размером и меняем размер холста
                self.image = temp_image
                self.edited = True
                self.clearSelection()

                self.send_new_image_size.emit(width, height)

        elif self.rect_bottom_right_corner().contains(event.pos()):
            self.setCursor(Qt.SizeFDiagCursor)
        else:
            # TODO: курсор должен зависить от текущего инструмента
            self.setCursor(Qt.ArrowCursor)

        # Рисуем, используя инструмент
        instrument = self.get_instrument()
        if instrument:
            instrument.mouse_move_event(event, self)

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.m_is_resize:
            self.m_is_resize = False
            self.restoreCursor()
        else:
            instrument = self.get_instrument()
            if instrument:
                instrument.mouse_release_event(event, self)

        super().mouseReleaseEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setPen(Qt.NoPen)

        # TODO: иконки через ресурсы брать
        # TODO: поддержать
        # painter.setBrush(QBrush(QPixmap("transparent.jpg")))
        painter.setBrush(self.data_singleton.secondary_color)
        painter.drawRect(0, 0,
                         self._image.rect().right() - 1,
                         self._image.rect().bottom() - 1)

        painter.drawImage(self._image.rect(), self._image)

        painter.setBrush(Qt.black)
        painter.drawRect(self.rect_bottom_right_corner())

        painter.end()

        super().paintEvent(event)