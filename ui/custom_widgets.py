import enum

from ui.qt_imports import QPaintEvent

from .qt_imports import *
from typing import Callable
from . import icons_rc


class CustomQWidget(QWidget):
    def __init__(self, parent, windowType=None):
        # type: (QWidget | None, QtCore.Qt.WindowType | None) -> None
        if windowType is None:
            super().__init__(parent)
        else:
            super().__init__(parent, windowType)

        # self.setAttribute(WidgetAttributes.WA_Hover, True)
        self.setAttribute(WidgetAttributes.WA_MouseTracking, True)
        self.__opacity_effect = QGraphicsOpacityEffect(self)

    def __customPaintEvent(self, event):
        # type: (QPaintEvent) -> None
        # https://forum.qt.io/topic/100691/custom-qwidget-setstylesheet-not-working-python/4
        print("CustomQWidget PaintEvent")
        o = QStyleOption()
        o.initFrom(self)
        p = QPainter(self)
        self.style().drawPrimitive(QStyle.PrimitiveElement.PE_Widget, o, p, self)

    def mouseMoveEvent(self, event):
        # type: (QMouseEvent) -> None
        self.setCursor(CursorShape.ArrowCursor)
        return False
        # return super().mouseMoveEvent(event)

    def fadeIn(self, duration):
        # type: (int) -> None
        # duration => milliseconds
        if not isinstance(duration, int):
            raise TypeError("Duration must be an integer")

        self.setGraphicsEffect(self.__opacity_effect)
        self.__fade_in_animation = QPropertyAnimation(self, "opacity")
        self.__fade_in_animation.setDuration(duration)

        self.__fade_in_animation.setStartValue(0)
        self.__fade_in_animation.setEndValue(1)
        self.__fade_in_animation.setEasingCurve(QEasingCurve(QEasingCurve.Type.InBack))

        self.__fade_in_animation.start(
            QPropertyAnimation.DeletionPolicy.KeepWhenStopped
        )

    def fadeOut(self, duration):
        # type: (int) -> None
        # duration => milliseconds
        if not isinstance(duration, int):
            raise TypeError("Duration must be an integer")

        self.setGraphicsEffect(self.__opacity_effect)
        self.__fade_out_animation = QPropertyAnimation(self, "opacity")
        self.__fade_out_animation.setDuration(duration)

        self.__fade_out_animation.setStartValue(0)
        self.__fade_out_animation.setEndValue(1)
        self.__fade_out_animation.setEasingCurve(
            QEasingCurve(QEasingCurve.Type.OutBack)
        )

        self.__fade_out_animation.start(
            QPropertyAnimation.DeletionPolicy.DeleteWhenStopped
        )


class ResizableFramelessWidget(
    CustomQWidget,
):
    OBJECTNAME = "ResizableFramelessWidget"

    class BorderStyle:
        def __init__(self, **kwargs):
            # type: (...) -> None
            self._minRadius, self._minThickness = 5, 5

            # Default border style
            self.thickness = self._minThickness
            self.color = ""
            self.radius = self._minRadius
            self.setStyle(**kwargs)

        def setStyle(
            self,
            **kwargs,
        ):
            # type: (...) -> None
            obj = kwargs.get("obj", None)
            if type(obj) == type(self):
                _d = dict()
                if "fallback_color" in kwargs:
                    _d["fallback_color"] = kwargs["fallback_color"].strip()
                _d.update(obj.__toDict())
                self.setStyle(**_d)

            else:
                if "thickness" in kwargs:
                    self.thickness = max(self._minThickness, kwargs["thickness"])

                if "radius" in kwargs:
                    self.radius = max(self._minRadius, kwargs["radius"])

                if self.color:
                    c = kwargs.get("color", "").strip()
                    if c:
                        self.color = c

                else:
                    c = kwargs.get("color", "").strip()
                    fallback = kwargs.get("fallback_color", "").strip()
                    if c:
                        self.color = c
                    else:
                        self.color = fallback

        def __str__(self):
            # type: () -> str
            # return str(self.__toDict())
            return self.stylesheet

        @property
        def stylesheet(self):
            # type: () -> str
            _sheet = ""
            _sheet += f" border-width: 1px; border-style: solid; border-radius: {self.radius}px; "
            if self.color:
                _sheet += (
                    f"background-color: {self.color}; border-color: {self.color}; "
                )
                # _sheet += f"background-color: {self.color}; border: 1px solid {self.color};"
            # _sheet += f" border-radius: {self.radius}px;"

            return f"#{ResizableFramelessWidget.OBJECTNAME}" " { " + _sheet + " }"

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
        self.__minBorderWidth = 5
        self.__resizeActive = False
        self._offendingBorder = self.__ResizableWidgetBorder.UNSET

    
    # def _custom_repaint(self):
    #     # type: () -> None
    #     # https://stackoverflow.com/questions/32491282/qframe-round-border-transparent-background
    #     painter = QPainter()
    #     if painter.begin(self):
    #         painter.setBackgroundMode(BGMode.OpaqueMode)

    #         self.brush = QBrush(BrushStyle.SolidPattern)
    #         painter.setBrush(self.brush)
    #         self.brush.setColor(QColor(255, 0, 0, 1))
    #         painter.fillRect(self.rect(), self.brush)

    #         print("painter end ", painter.end())
    #         self.update()

    def __bg_color(self):
        # type: () -> str
        color = self.palette().color(self.backgroundRole())
        return f"rgb({color.red()+10}, {color.green()+10}, {color.blue()+10})"

    def setBorderStyle(
        self, borderColor="", borderThickness=-1, borderRadius=-1, borderStyle=None
    ):
        # type: (str, int, int, BorderStyle | None) -> None
        if borderStyle is not None:
            self._borderStyle.setStyle(
                obj=borderStyle, fallback_color=self.__bg_color()
            )
        else:
            self._borderStyle.setStyle(
                color=borderColor,
                thickness=borderThickness,
                radius=borderRadius,
                fallback_color=self.__bg_color(),
            )
        print(self._borderStyle)
        # Update border styling
        # self.setStyleSheet(self._borderStyle.stylesheet)

        # Update border thickness
        val = max(self.__minBorderWidth, self._borderStyle.thickness)

        if self.layout():
            self.layout().setContentsMargins(*(val,) * 4)
        else:
            self.setContentsMargins(*(val,) * 4)

        # self._custom_repaint()

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
        elif event.type() == QEvent.Type.Paint:
            self._custom_repaint()
            return True

        return False


class ClickableSvgWidget(QFrame):
    def __init__(
        self,
        parent: QWidget | None = ...,
        f=None,
        svgFilePath="",
        msBtnPressCallback=None,
    ) -> None:
        # type: (QWidget| None, WindowTypes, str|None, Callable[[QEvent], None]) -> None

        if f is None:
            super().__init__(parent)
        else:
            super().__init__(parent, f)

        self.__btnPressCallback = msBtnPressCallback
        self.__svgWidget = QSvgWidget(svgFilePath, self)

        vBox = QVBoxLayout(self)
        vBox.addWidget(self.__svgWidget)
        self.setLayout(vBox)

        self.setAttribute(WidgetAttributes.WA_MouseTracking, True)
        self.setAttribute(WidgetAttributes.WA_Hover, True)
        vBox.setContentsMargins(0, 0, 0, 0)

    def event(self, ev):
        # type: (QEvent | QMouseEvent) -> None

        if ev.type() == QEvent.Type.HoverEnter:
            self.setCursor(CursorShape.PointingHandCursor)
            return True

        elif ev.type() == QEvent.Type.HoverLeave:
            self.setCursor(CursorShape.ArrowCursor)
            return True

        elif ev.type() == QEvent.Type.MouseButtonPress:
            if callable(self.__btnPressCallback):
                self.__btnPressCallback(ev)
            return True

        elif ev.type() == QEvent.Type.MouseButtonRelease:
            return True

        return False
