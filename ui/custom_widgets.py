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
    QWidget,
):
    class BorderStyle:
        def __init__(self, **kwargs):
            # type: (...) -> None
            self._minRadius, self._minThickness = 0, 3

            # Default border style
            self.thickness = self._minThickness
            self.color = None
            self.radius = self._minRadius
            self.setStyle(**kwargs)

        def __arg_type_check(self, **kwargs):
            # type: (...) -> bool
            # True if all arguments have expected types
            state = True
            for val in kwargs:
                if val in ("color", "fallback_color"):
                    state = state and isinstance(kwargs[val], (QColor, type(None)))

                elif val in ("radius", "thickness"):
                    state = state and isinstance(kwargs[val], (int))
            return state

        def setStyle(
            self,
            **kwargs,
        ):
            # type: (...) -> None
            if not self.__arg_type_check(**kwargs):
                print("BorderStyle: setStyle received bad argument types")
                return

            obj = kwargs.get("obj", None)
            if type(obj) == type(self):
                _d = dict()
                if "fallback_color" in kwargs:
                    _d["fallback_color"] = kwargs["fallback_color"]
                _d.update(obj.__toDict())
                self.setStyle(**_d)

            else:
                if "thickness" in kwargs:
                    self.thickness = max(self._minThickness, kwargs["thickness"])

                if "radius" in kwargs:
                    self.radius = max(self._minRadius, kwargs["radius"])

                if self.color:
                    c = kwargs.get("color", None)
                    if c:
                        self.color = c

                else:
                    c = kwargs.get("color", "")
                    fallback = kwargs.get("fallback_color", None)
                    if c:
                        self.color = c
                    else:
                        self.color = fallback

        def __str__(self):
            # type: () -> str
            return str(self.__toDict())

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

        self.setAttribute(WidgetAttributes.WA_TranslucentBackground, True)

        # Resizing support
        self.setMouseTracking(True)

        self._borderStyle = self.BorderStyle()
        self.__resizeActive = False
        self._offendingBorder = self.__ResizableWidgetBorder.UNSET
        self.__enabled = True

    def enableResize(self, state):
        # type: (bool) -> None
        self.__enabled = state if type(state) is bool else True

    def isResizeEnabled(self):
        # type: () -> bool
        return self.__enabled

    def isResizeDisabled(self):
        # type: () -> bool
        return not self.__enabled

    def _custom_repaint(self):
        # type: () -> None

        painter = QPainter()
        brush = QBrush(BrushStyle.SolidPattern)
        bg_color = (
            self.__bg_color()
            if self._borderStyle.color is None
            else self._borderStyle.color
        )
        brush.setColor(bg_color)

        pen = QPen(GlobalColor.transparent, self._borderStyle.thickness)

        if painter.begin(self):
            painter.setBackgroundMode(BGMode.OpaqueMode)
            painter.setPen(pen)
            painter.setBrush(brush)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

            rect = QRect(0, 0, max(self.width() - 1, 0), max(self.height() - 1, 0))
            painter.drawRoundedRect(
                rect, self._borderStyle.radius, self._borderStyle.radius
            )
            painter.end()

    def __bg_color(self):
        # type: () -> QColor
        return self.palette().color(self.backgroundRole())

    def setBorderStyle(
        self, borderColor=None, borderThickness=-1, borderRadius=-1, borderStyle=None
    ):
        # type: (QColor, int, int, BorderStyle | None) -> None
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

        self.repaint()

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
        thickness = self._borderStyle.thickness + 3  # added padding

        if relPosX <= 0 + thickness:
            border |= self.__ResizableWidgetBorder.LEFT
        elif w - thickness <= relPosX <= w or relPosX > w:
            border |= self.__ResizableWidgetBorder.RIGHT

        if relPosY <= 0 + thickness:
            border |= self.__ResizableWidgetBorder.TOP
        elif h - thickness <= relPosY <= h or relPosY > h:
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

            if self.__enabled:
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

                        elif (
                            self.__ResizableWidgetBorder.BOTTOM in self._offendingBorder
                        ):
                            y2 = cursorGlobalY

                        if self.__ResizableWidgetBorder.LEFT in self._offendingBorder:
                            x1 = cursorGlobalX

                        elif (
                            self.__ResizableWidgetBorder.RIGHT in self._offendingBorder
                        ):
                            x2 = cursorGlobalX

                        newX, newY = x1, y1
                        newW, newH = max(0, x2 - x1), max(0, y2 - y1)

                        self.setGeometry(newX, newY, newW, newH)

                return True

            return False
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
