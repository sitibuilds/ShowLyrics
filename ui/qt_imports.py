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
    QGridLayout,
    QGraphicsOpacityEffect,
)
from PySide6.QtSvgWidgets import QSvgWidget

Qt = QtCore.Qt

QEasingCurve = QtCore.QEasingCurve
QEvent = QtCore.QEvent
QObject = QtCore.QObject
QPropertyAnimation = QtCore.QPropertyAnimation

BGMode = Qt.BGMode
BrushStyle = Qt.BrushStyle
GlobalColor = Qt.GlobalColor
WidgetAttributes = Qt.WidgetAttribute
WindowTypes = Qt.WindowType

ApplicationAttributes = Qt.ApplicationAttribute
ApplicationStates = Qt.ApplicationState
CursorShape = Qt.CursorShape

AlignmentFlag = Qt.AlignmentFlag
QBrush = QtGui.QBrush
QColor = QtGui.QColor
QCursor = QtGui.QCursor
QDragEnterEvent = QtGui.QDragEnterEvent
QDragMoveEvent = QtGui.QDragMoveEvent
QDragLeaveEvent = QtGui.QDragLeaveEvent
QFont = QtGui.QFont
QFontDatabase = QtGui.QFontDatabase
QHoverEvent = QtGui.QHoverEvent
QImage = QtGui.QImage
QMouseEvent = QtGui.QMouseEvent
QPainter = QtGui.QPainter
QPaintEvent = QtGui.QPaintEvent
QPalette = QtGui.QPalette
QPixmap = QtGui.QPixmap
