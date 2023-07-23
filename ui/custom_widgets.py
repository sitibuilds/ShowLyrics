import enum
from .qt_imports import *
from typing import Callable
from .resources import icons_rc
from .utils import fadeAnimation


class CustomQWidget(QWidget):
    def __init__(self, parent, windowType=None):
        # type: (QWidget | None, QtCore.Qt.WindowType | None) -> None
        if windowType is None:
            super().__init__(parent)
        else:
            super().__init__(parent, windowType)

        # self.setAttribute(WidgetAttributes.WA_Hover, True)
        self.setAttribute(WidgetAttributes.WA_MouseTracking, True)
        effect = QGraphicsOpacityEffect(self)
        effect.setOpacity(1)
        self.setGraphicsEffect(effect)

    def __customPaintEvent(self, event):
        # type: (QPaintEvent) -> None
        # https://forum.qt.io/topic/100691/custom-qwidget-setstylesheet-not-working-python/4

        o = QStyleOption()
        o.initFrom(self)
        p = QPainter(self)
        self.style().drawPrimitive(QStyle.PrimitiveElement.PE_Widget, o, p, self)

    def _waitForPainter(self):
        currEngine = self.paintEngine()
        currPainter = currEngine.painter() if currEngine else None
        while currPainter is not None and currPainter.isActive():
            print("active...")

    def fadeIn(self, duration=250):
        # type: (int) -> None
        # duration => milliseconds
        return fadeAnimation(self, duration, True)

    def fadeOut(self, duration=250):
        # type: (int) -> None
        # duration => milliseconds
        return fadeAnimation(self, duration, False)


class FramelessRoundedBorderWidget(
    CustomQWidget,
):
    class BorderStyle:
        MIN_RADIUS = 0
        MIN_THICKNESS = 3

        def __init__(self, **kwargs):
            # type: (...) -> None

            # Default border style
            self.thickness = self.MIN_THICKNESS
            self.color = None
            self.radius = self.MIN_RADIUS
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
                    self.thickness = max(self.MIN_THICKNESS, kwargs["thickness"])

                if "radius" in kwargs:
                    self.radius = max(self.MIN_RADIUS, kwargs["radius"])

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

    def __init__(self, parent, f: WindowTypes = None):
        if f is None:
            super().__init__(parent, WindowTypes.FramelessWindowHint)
        else:
            super().__init__(parent, WindowTypes.FramelessWindowHint | f)

        self.setAttribute(WidgetAttributes.WA_TranslucentBackground, True)

        self._borderStyle = self.BorderStyle()

    def _custom_repaint(self):
        # type: () -> None
        painter = QPainter()

        brush = QBrush(BrushStyle.SolidPattern)
        bg_color = (
            self.__default_bg_color()
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

            frameGeometry = self.frameGeometry().topLeft()
            rect = QRect(
                frameGeometry.x(),
                frameGeometry.y(),
                max(self.width() - 1, 0),
                max(self.height() - 1, 0),
            )
            painter.drawRoundedRect(
                rect, self._borderStyle.radius, self._borderStyle.radius
            )
            painter.end()

    def __default_bg_color(self):
        # type: () -> QColor
        return self.palette().color(self.backgroundRole())

    def setBorderStyle(
        self, borderColor=None, borderThickness=-1, borderRadius=-1, borderStyle=None
    ):
        # type: (QColor, int, int, BorderStyle | None) -> None
        if borderStyle is not None:
            self._borderStyle.setStyle(
                obj=borderStyle, fallback_color=self.__default_bg_color()
            )
        else:
            self._borderStyle.setStyle(
                color=borderColor,
                thickness=borderThickness,
                radius=borderRadius,
                fallback_color=self.__default_bg_color(),
            )

    def event(self, event):
        # type: (QEvent | QMouseEvent) -> bool

        if event.type() == QEvent.Type.Paint:
            self._custom_repaint()
            return True

        return super().event(event)


class ResizableWidget(FramelessRoundedBorderWidget):
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

    __BORDER_TO_CURSOR_SHAPE = {
        __ResizableWidgetBorder.BOTTOM: CursorShape.SizeVerCursor,
        __ResizableWidgetBorder.TOP: CursorShape.SizeVerCursor,
        __ResizableWidgetBorder.LEFT: CursorShape.SizeHorCursor,
        __ResizableWidgetBorder.RIGHT: CursorShape.SizeHorCursor,
        __ResizableWidgetBorder.BOTTOMLEFT: CursorShape.SizeBDiagCursor,
        __ResizableWidgetBorder.TOPRIGHT: CursorShape.SizeBDiagCursor,
        __ResizableWidgetBorder.BOTTOMRIGHT: CursorShape.SizeFDiagCursor,
        __ResizableWidgetBorder.TOPLEFT: CursorShape.SizeFDiagCursor,
    }

    __BORDER_TO_NATIVE_EDGE = {
        __ResizableWidgetBorder.BOTTOM: Qt.Edge.BottomEdge,
        __ResizableWidgetBorder.TOP: Qt.Edge.TopEdge,
        __ResizableWidgetBorder.LEFT: Qt.Edge.LeftEdge,
        __ResizableWidgetBorder.RIGHT: Qt.Edge.RightEdge,
        __ResizableWidgetBorder.BOTTOMLEFT: Qt.Edge.BottomEdge | Qt.Edge.LeftEdge,
        __ResizableWidgetBorder.BOTTOMRIGHT: Qt.Edge.BottomEdge | Qt.Edge.RightEdge,
        __ResizableWidgetBorder.TOPLEFT: Qt.Edge.TopEdge | Qt.Edge.LeftEdge,
        __ResizableWidgetBorder.TOPRIGHT: Qt.Edge.TopEdge | Qt.Edge.RightEdge,
    }

    def __init__(self, parent, f=None):
        # type: (QWidget | None, WindowTypes | None) -> None
        super().__init__(parent, f)

        self.setAttribute(WidgetAttributes.WA_NativeWindow, True)

        # Resizing support
        self.setMouseTracking(True)

        self.__resizeActive = False
        self.__offendingBorder = self.__ResizableWidgetBorder.UNSET
        self.__resizeEnabled = True

    def setEnableResize(self, state):
        # type: (bool) -> None
        self.__resizeEnabled = state if type(state) is bool else True

    def isResizeEnabled(self):
        # type: () -> bool
        return self.__resizeEnabled

    def isResizeDisabled(self):
        # type: () -> bool
        return not self.__resizeEnabled

    def __fallbackMouseMove(self, event):
        # type: (QEvent | QMouseEvent) -> None
        pos = event.position()
        relPosX, relPosY = pos.x(), pos.y()
        if event.type() == QEvent.Type.MouseMove:

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

                if self.__ResizableWidgetBorder.TOP in self.__offendingBorder:
                    y1 = cursorGlobalY

                elif self.__ResizableWidgetBorder.BOTTOM in self.__offendingBorder:
                    y2 = cursorGlobalY

                if self.__ResizableWidgetBorder.LEFT in self.__offendingBorder:
                    x1 = cursorGlobalX

                elif self.__ResizableWidgetBorder.RIGHT in self.__offendingBorder:
                    x2 = cursorGlobalX

                newX, newY = x1, y1
                newW, newH = max(0, x2 - x1), max(0, y2 - y1)

                self.setGeometry(newX, newY, newW, newH)

    def event(self, event):
        # type: (QEvent| QMouseEvent) -> bool
        if isinstance(event, QMouseEvent):
            if self.__resizeEnabled:
                pos = event.position()
                relPosX, relPosY = pos.x(), pos.y()

                if event.type() == QEvent.Type.MouseButtonPress:
                    self.__resizeActive = self._isCursorInBorder(event)
                    self.__offendingBorder = self.__getHoveredBorder(relPosX, relPosY)

                    w = self.window()
                    if w is not None and self.__resizeActive:
                        nativeEdge = self.__BORDER_TO_NATIVE_EDGE.get(
                            self.__offendingBorder, None
                        )
                        if nativeEdge and w.windowHandle().startSystemResize(
                            nativeEdge
                        ):
                            return True

                elif event.type() == QEvent.Type.MouseButtonRelease:
                    if self.__resizeActive:
                        self.__resizeActive = False

                elif event.type() == QEvent.Type.MouseMove:
                    self.__updateCursor(self.__getHoveredBorder(relPosX, relPosY))

        elif event.type() == QEvent.Type.WindowActivate:
            if self.__resizeActive:
                self.__resizeActive = False
                self.__offendingBorder = self.__ResizableWidgetBorder.UNSET

        return super().event(event)

    def __updateCursor(self, border=None):
        # type: (__ResizableWidgetBorder) -> None
        cursor_shape = self.__BORDER_TO_CURSOR_SHAPE.get(border, None)
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

    def _isCursorInBorder(self, event):
        # type: (QMouseEvent) -> bool
        pos = event.position()
        relPosX, relPosY = pos.x(), pos.y()
        border = self.__getHoveredBorder(relPosX, relPosY)
        if border == self.__ResizableWidgetBorder.UNSET:
            return False
        return True


class QMovableResizableWidget(ResizableWidget):
    def __init__(self, parent, f: WindowTypes = None):
        super().__init__(parent, f)
        self.__systemMove = False

    def event(self, ev):
        # type: (QEvent | QMouseEvent) -> bool
        if (
            ev.type() == QEvent.Type.MouseButtonPress
            and ev.button() == Qt.MouseButton.LeftButton
            and not self._isCursorInBorder(ev)
        ):
            w = self.window()
            if w is not None and not self.__systemMove:
                if w.windowHandle().startSystemMove():
                    self.__systemMove = True
                    return True

        elif ev.type() == QEvent.Type.WindowActivate:
            if self.__systemMove:
                self.__systemMove = False

        return super().event(ev)


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

        self.setCursor(CursorShape.PointingHandCursor)
        self.__btnPressCallback = msBtnPressCallback
        self.__svgWidget = (
            QSvgWidget(svgFilePath, self)
            if svgFilePath and isinstance(svgFilePath, str)
            else QWidget(self)
        )

        self.__svgWidget.setAttribute(
            WidgetAttributes.WA_TransparentForMouseEvents, True
        )

        vBox = QVBoxLayout(self)
        vBox.addWidget(self.__svgWidget)
        self.setLayout(vBox)
        self.setAttribute(WidgetAttributes.WA_MouseTracking, True)
        vBox.setContentsMargins(0, 0, 0, 0)

    def svgWidget(self):
        # type: () -> QSvgWidget
        return self.__svgWidget

    def event(self, ev):
        # type: (QEvent | QMouseEvent) -> None

        if (
            ev.type() == QEvent.Type.MouseButtonPress
            and ev.button() == Qt.MouseButton.LeftButton
        ):
            if callable(self.__btnPressCallback):
                self.__btnPressCallback(ev)
            ev.accept()
            return True

        elif ev.type() == QEvent.Type.MouseButtonRelease:
            ev.accept()
            return True

        return super().event(ev)

    def setSvgFilePath(self, path):
        # type: (str) -> None
        self._replaceInnerWidget(
            QSvgWidget(path, self) if path and isinstance(path, str) else QWidget(self)
        )

    def _replaceInnerWidget(self, svgWidget):
        # type: (QSvgWidget)  -> QSvgWidget
        # Returns the old, replaced widget
        if not svgWidget:
            return self.__svgWidget
        if not isinstance(svgWidget, QWidget):
            raise TypeError("svgWidget must be an instance of QWidget")

        layout = self.layout()
        layout.replaceWidget(
            self.__svgWidget, svgWidget, Qt.FindChildOption.FindChildrenRecursively
        )
        prev_widget, self.__svgWidget = self.__svgWidget, svgWidget

        return prev_widget
