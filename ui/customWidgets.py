import enum
from typing import Optional
import PySide6.QtCore
import PySide6.QtGui
import PySide6.QtWidgets
from .imports import (
    QWidget,
    QStyle,
    QStyleOption,
    QtCore,
    QPaintEvent,
    QPainter,
    WindowTypes,
    WidgetAttributes,
    QCursor,
    QEvent,
    QMouseEvent,
    CursorShape,
    QObject,
    QFrame,
    QHBoxLayout,
    QtSvg,
    QImage,
    QSvgWidget,
    QSizePolicy,
    AlignmentFlag,
    QPixmap,
)
from . import icons_rc


class CustomQWidget(QWidget):
    def __init__(self, parent, windowType=None):
        # type: (QWidget | None, QtCore.Qt.WindowType | None) -> None
        if windowType is None:
            super().__init__(parent)
        else:
            super().__init__(parent, windowType)

    def paintEvent(self, pEvent):
        # type: (QPaintEvent) -> None
        # https://forum.qt.io/topic/100691/custom-qwidget-setstylesheet-not-working-python/4
        o = QStyleOption()
        o.initFrom(self)
        p = QPainter(self)
        self.style().drawPrimitive(QStyle.PE_Widget, o, p, self)


class ResizableFramelessWidget(
    CustomQWidget,
):
    OBJECTNAME = "ResizableFramelessWidget"

    class BorderStyle:
        def __init__(self, **kwargs):
            # type: (...) -> None
            obj = kwargs.get("obj", None)
            if type(obj) == type(self):
                self.setStyle(**obj.__toDict())

            else:
                # Default border style
                self.thickness = 5
                self.color = "white"
                self.radius = 5
                self.setStyle(**kwargs)

        def setStyle(self, **kwargs):
            # type: (...) -> None
            if "thickness" in kwargs:
                self.thickness = kwargs["thickness"]

            if "radius" in kwargs:
                self.radius = kwargs["radius"]

            if "color" in kwargs:
                self.color = kwargs["color"]

        def stylesheet(self):
            # type: () -> str
            return (
                f"#{ResizableFramelessWidget.OBJECTNAME}"
                " { "
                f"background-color: {self.color}; border: 1px solid {self.color}; border-radius: {self.radius}px;"
                " }"
            )

        def __toDict(self):
            # type: () -> dict
            return {
                "thickness": self.thickness,
                "radius": self.radius,
                "color": self.color,
            }

    class __ResizableWidgetBorder(enum.Flag):
        LEFT = enum.auto()
        RIGHT = enum.auto()
        TOP = enum.auto()
        BOTTOM = enum.auto()
        UNSET = enum.auto()
        TOPLEFT = TOP | LEFT
        TOPRIGHT = TOP | RIGHT
        BOTTOMRIGHT = BOTTOM | RIGHT
        BOTTOMLEFT = BOTTOM | LEFT

    def __init__(self, parent, f: WindowTypes = None):
        if f is None:
            super().__init__(parent, WindowTypes.FramelessWindowHint)
        else:
            super().__init__(parent, WindowTypes.FramelessWindowHint | f)

        self.setObjectName(self.OBJECTNAME)
        self.setAttribute(WidgetAttributes.WA_StyledBackground, True)

        # Resizing support
        self.setMouseTracking(True)

        self._borderStyle = self.BorderStyle()
        self.__minBorderWidth = 1
        self.__resizeActive = False
        self._offendingBorder = self.__ResizableWidgetBorder.UNSET
        # self.setBorderStyle(self._borderStyle)

    def setBorderStyle(self, borderStyle):
        # type: (BorderStyle | None) -> None

        if not isinstance(borderStyle, self.BorderStyle):
            return

        self._borderStyle = borderStyle
        print(borderStyle.stylesheet())
        # Update border styling
        self.setStyleSheet(borderStyle.stylesheet())

        # Update border thickness
        val = max(self.__minBorderWidth, borderStyle.thickness)

        if self.layout():
            self.layout().setContentsMargins(*(val,) * 4)
        else:
            self.setContentsMargins(*(val,) * 4)

    def __updateCursor(self, border=None):
        # type: (__ResizableWidgetBorder) -> None
        border_to_cursor = {
            self.__ResizableWidgetBorder.BOTTOM: CursorShape.SizeVerCursor,
            self.__ResizableWidgetBorder.TOP: CursorShape.SizeVerCursor,
            self.__ResizableWidgetBorder.LEFT: CursorShape.SizeHorCursor,
            self.__ResizableWidgetBorder.RIGHT: CursorShape.SizeHorCursor,
            self.__ResizableWidgetBorder.BOTTOMLEFT: CursorShape.SizeBDiagCursor,
            self.__ResizableWidgetBorder.TOPRIGHT: CursorShape.SizeBDiagCursor,
            self.__ResizableWidgetBorder.BOTTOMRIGHT: CursorShape.SizeFDiagCursor,
            self.__ResizableWidgetBorder.TOPLEFT: CursorShape.SizeFDiagCursor,
        }
        cursor_shape = border_to_cursor.get(border, None)
        if cursor_shape is not None:
            self.setCursor(cursor_shape)
        else:
            self.unsetCursor()

    def __getHoveredBorder(self, relPosX, relPosY):
        # type: ( int, int) -> __ResizableWidgetBorder
        w, h = self.width(), self.height()
        border = self.__ResizableWidgetBorder.UNSET
        if relPosX <= 0 + self._borderStyle.thickness:
            border |= self.__ResizableWidgetBorder.LEFT
        elif w - self._borderStyle.thickness <= relPosX <= w or relPosX > w:
            border |= self.__ResizableWidgetBorder.RIGHT

        if relPosY <= 0 + self._borderStyle.thickness:
            border |= self.__ResizableWidgetBorder.TOP
        elif h - self._borderStyle.thickness <= relPosY <= h or relPosY > h:
            border |= self.__ResizableWidgetBorder.BOTTOM

        if border == self.__ResizableWidgetBorder.UNSET:
            return border
        return border ^ self.__ResizableWidgetBorder.UNSET

    def __isCursorInBorder(self, relPosX, relPosY):
        # type: (int, int) -> bool
        border = self.__getHoveredBorder(relPosX, relPosY)
        if border == self.__ResizableWidgetBorder.UNSET:
            return False
        return True

    def event(self, event):
        # type: (QEvent | QMouseEvent) -> bool

        if isinstance(event, QMouseEvent):
            pos = event.position()
            relPosX, relPosY = pos.x(), pos.y()

            if event.type() == QEvent.Type.MouseButtonPress:
                self.__resizeActive = self.__isCursorInBorder(relPosX, relPosY)
                self._offendingBorder = self.__getHoveredBorder(relPosX, relPosY)

            elif event.type() == QEvent.Type.MouseButtonRelease:
                if self.__resizeActive:
                    self.__resizeActive = False

                self._offendingBorder = self.__ResizableWidgetBorder.UNSET

            elif event.type() == QEvent.Type.MouseMove:

                if not self.__resizeActive:
                    hoveredBorder = self.__getHoveredBorder(relPosX, relPosY)
                    self.__updateCursor(hoveredBorder)

                else:
                    size = self.size()
                    oldW, oldH = size.width(), size.height()
                    x, y = self.x(), self.y()

                    globalPosition = event.globalPosition()
                    cursorGlobalX, cursorGlobalY = (
                        globalPosition.x(),
                        globalPosition.y(),
                    )

                    y1, y2, x1, x2 = y, y + oldH, x, x + oldW

                    if self.__ResizableWidgetBorder.TOP in self._offendingBorder:
                        y1 = cursorGlobalY

                    elif self.__ResizableWidgetBorder.BOTTOM in self._offendingBorder:
                        y2 = cursorGlobalY

                    if self.__ResizableWidgetBorder.LEFT in self._offendingBorder:
                        x1 = cursorGlobalX

                    elif self.__ResizableWidgetBorder.RIGHT in self._offendingBorder:
                        x2 = cursorGlobalX

                    newX, newY = x1, y1
                    newW, newH = max(0, x2 - x1), max(0, y2 - y1)

                    self.setGeometry(newX, newY, newW, newH)

                return True
        return False


class WindowControlGroup(QFrame):
    def __init__(self, parent, f: WindowTypes = None) -> None:
        if f is None:
            super().__init__(parent)
        else:
            super().__init__(parent, f)

        hbox = QHBoxLayout(self)
        self.setLayout(hbox)

        close_file = ":/icons/Close.svg"
        closeSvg = QSvgWidget(close_file, self)
        closeSvg.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        minimizeSvg = QSvgWidget(":/icons/Minimize.svg", self)
        minimizeSvg.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        hbox.addWidget(minimizeSvg)
        hbox.addWidget(closeSvg)
        hbox.addStretch(1)

        hbox.setAlignment(AlignmentFlag.AlignTop)
        hbox.setContentsMargins(0, 0, 0, 0)
