from PySide6 import QtCore, QtSvg, QtGui
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QFrame,
    QStyleOption,
    QStyle,
    QSizeGrip,
    QHBoxLayout,
    QLabel,
    QSpacerItem,
    QSizePolicy,
)
from PySide6.QtSvgWidgets import QSvgWidget

WindowTypes = QtCore.Qt.WindowType
WidgetAttributes = QtCore.Qt.WidgetAttribute
Qt = QtCore.Qt
QObject = QtCore.QObject
QEvent = QtCore.QEvent
QMouseEvent = QtGui.QMouseEvent
QHoverEvent = QtGui.QHoverEvent
QCursor = QtGui.QCursor
CursorShape = Qt.CursorShape
QPainter = QtGui.QPainter
QPaintEvent = QtGui.QPaintEvent
QDragEnterEvent = QtGui.QDragEnterEvent
QDragLeaveEvent = QtGui.QDragLeaveEvent
QDragMoveEvent = QtGui.QDragMoveEvent
QPalette = QtGui.QPalette
QBrush = QtGui.QBrush
QColor = QtGui.QColor
QImage = QtGui.QImage
AlignmentFlag = Qt.AlignmentFlag
QPixmap = QtGui.QPixmap