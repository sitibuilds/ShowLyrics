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
    QMainWindow,
    QCheckBox,
    QSpinBox,
    QToolButton,
    QColorDialog
)
from PySide6.QtSvgWidgets import QSvgWidget

Qt = QtCore.Qt
QByteArray = QtCore.QByteArray
QEasingCurve = QtCore.QEasingCurve
QEvent = QtCore.QEvent
QObject = QtCore.QObject
QPropertyAnimation = QtCore.QPropertyAnimation
QSize = QtCore.QSize
QRect = QtCore.QRect
QPoint = QtCore.QPoint

AlignmentFlag = Qt.AlignmentFlag
ApplicationAttributes = Qt.ApplicationAttribute
ApplicationStates = Qt.ApplicationState
BGMode = Qt.BGMode
BrushStyle = Qt.BrushStyle
CursorShape = Qt.CursorShape
GlobalColor = Qt.GlobalColor
SizeMode = Qt.SizeMode
WidgetAttributes = Qt.WidgetAttribute
WindowTypes = Qt.WindowType

QAction = QtGui.QAction
QBrush = QtGui.QBrush
QColor = QtGui.QColor
QCursor = QtGui.QCursor
QDragEnterEvent = QtGui.QDragEnterEvent
QDragMoveEvent = QtGui.QDragMoveEvent
QDragLeaveEvent = QtGui.QDragLeaveEvent
QFont = QtGui.QFont
QFontDatabase = QtGui.QFontDatabase
QHoverEvent = QtGui.QHoverEvent
QIcon = QtGui.QIcon
QImage = QtGui.QImage
QMouseEvent = QtGui.QMouseEvent
QPainter = QtGui.QPainter
QPainterPath = QtGui.QPainterPath
QPalette = QtGui.QPalette
QPen = QtGui.QPen
QPaintEvent = QtGui.QPaintEvent
QPalette = QtGui.QPalette
QPixmap = QtGui.QPixmap
QWindow = QtGui.QWindow