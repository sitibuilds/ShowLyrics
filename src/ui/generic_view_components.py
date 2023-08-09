from typing import Callable
import enum

from .qt_imports import *
from .icon_components import CloseIcon
from .resources import icons_rc
from .fonts_import import CUSTOM_FONT_ID
from .utils import fadeAnimation, resetFixedSize
from functools import cache


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
                QtCore.qDebug("BorderStyle: setStyle received bad argument types")
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


class AppLabel(QLabel):
    def __init__(self, txt, parent, f=None, fontName="montserrat_bold", pixelSize=12):
        # type: (str, QWidget, WindowTypes, str, int)  -> None
        if f is None:
            super().__init__(txt, parent)
        else:
            super().__init__(txt, parent, f)

        self.opacity = 1
        self.FONTID = CUSTOM_FONT_ID.retrieve_font_id(fontName)
        if self.FONTID < 0:
            # QtCore.qDebug("Font couldn't load")
            pass
        else:
            families = QFontDatabase.applicationFontFamilies(self.FONTID)
            font = QFont(families[0])
            font.setPixelSize(pixelSize)
            self.setFont(font)

        self.setStyleSheet("color: rgba(255,255,255,255)")

    def setOpacity(self, value):
        # type: (float) -> None
        self.opacity = max(min(value, 1), 0) * 255
        self.setStyleSheet(f"color: rgba(255,255,255, {self.opacity})")

    def fadeIn(self, duration):
        # type: (int) -> None
        return fadeAnimation(self, duration, True)

    def fadeOut(self, duration):
        # type: (int) -> None
        return fadeAnimation(self, duration, True)


class TitleBarView(CustomQWidget):
    def __init__(self, parent, f=None, mainText="", subText="", onCloseCallback=None):
        # type: (QWidget | None, WindowTypes | None, str, str, Callable[[QEvent], None] | None) -> None

        if f is not None:
            super().__init__(parent, f)
        else:
            super().__init__(parent)

        self.mainTextLabel = AppLabel(mainText, self, pixelSize=20)
        self.subTextLabel = AppLabel(subText, self)

        closeSvg = CloseIcon(self, callback=onCloseCallback)
        self.closeSVG = closeSvg

        grid = QGridLayout(self)
        grid.addWidget(
            self.mainTextLabel,
            0,
            0,
            1,
            1,
            AlignmentFlag.AlignLeft | AlignmentFlag.AlignTop,
        )
        grid.addWidget(
            self.subTextLabel,
            1,
            0,
            1,
            2,
            AlignmentFlag.AlignLeft | AlignmentFlag.AlignTop,
        )
        grid.addWidget(
            self.closeSVG, 0, 1, AlignmentFlag.AlignRight | AlignmentFlag.AlignTop
        )
        grid.setVerticalSpacing(0)
        grid.setContentsMargins(0, 0, 0, 0)

        self.setLayout(grid)

    def fadeIn(self, duration: int = 250) -> None:

        return super().fadeIn(duration)


class GenericWindowView(QMovableResizableWidget):
    def __init__(
        self,
        parent,
        titleBarViewMainText,
        titleBarViewSubText,
        *childViews,
        footer=None,
    ):
        # type: (QWidget | None, str, str, *QWidget, QWidget) -> None
        super().__init__(parent, WindowTypes.Window | WindowTypes.FramelessWindowHint)

        mainLayout = QVBoxLayout(self)

        def closeWindow(ev):
            self.close()

        # Set up and add header
        self._titleBarView = TitleBarView(
            self,
            mainText=titleBarViewMainText,
            subText=titleBarViewSubText,
            onCloseCallback=closeWindow,
        )

        self.__childViews = childViews
        mainLayout.addWidget(self._titleBarView, 0, AlignmentFlag.AlignTop)

        # Add mid section elements
        midSection = QFrame(self)
        bodyLayout = QVBoxLayout(midSection)
        midSection.setLayout(bodyLayout)
        for view in self.__childViews:
            if isinstance(view, QWidget):
                view.setParent(self)
                bodyLayout.addWidget(view)

        mainLayout.addWidget(midSection, 1, AlignmentFlag.AlignVCenter)

        # Add footer element
        if isinstance(footer, QWidget):
            mainLayout.addWidget(footer, 0, AlignmentFlag.AlignBottom)
            footer.setParent(self)

        self.setLayout(mainLayout)

        self.setBorderStyle(borderStyle=self.BorderStyle(radius=10, thickness=5))


class CustomSpacing(CustomQWidget):
    def __init__(self, parent, useVerticalSpacing, *widgets):
        # type: (QWidget| None, bool, *QWidget) -> None
        super().__init__(
            parent,
        )

        if useVerticalSpacing:
            layout = QVBoxLayout(self)
        else:
            layout = QHBoxLayout(self)

        for idx, widget in enumerate(widgets):
            if idx != 0:
                layout.addStretch(1)
            widget.setParent(self)
            layout.addWidget(widget)

        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)


class CustomHorizontalLayout(CustomSpacing):
    def __init__(self, parent, *widgets) -> None:
        # type: (QWidget | None, *QWidget) -> None
        super().__init__(parent, False, *widgets)


class CustomVerticalLayout(CustomSpacing):
    def __init__(self, parent, *widgets) -> None:
        # type: (QWidget | None, *QWidget) -> None
        super().__init__(parent, True, *widgets)


class CustomCheckBox(QCheckBox):
    def __init__(self, parent, onChangeHandler):
        # type: (QWidget | None, Callable[[Qt.CheckState], None]) -> None

        super().__init__("", parent)
        self.setTristate(False)
        self.stateChanged.connect(onChangeHandler)


class CustomSpinBox(QSpinBox):
    def __init__(self, parent, onChangeHandler, minValue=5):
        # type: (QWidget | None, Callable[[int], None], int) -> None

        super().__init__(parent)
        self.valueChanged.connect(onChangeHandler)
        self.setMinimum(minValue)


class ColorPickerTool(QWidget):
    def __init__(
        self,
        parent,
        onChangedHandler,
    ):
        # type: (QWidget | None, Callable[[QAction], None]) -> None

        super().__init__(parent)

        layout = QHBoxLayout(self)

        self._btn = QToolButton(self)
        self._btn.triggered.connect(onChangedHandler)
        self._btn.setIcon(
            QIcon(":/icons/Settings.svg")
        )  # TODO: Change icon to down arrow

        self._label = QLabel(self)
        self._label.setFixedSize(self._btn.height() - 5, self._btn.height() - 5)
        self._label.setAutoFillBackground(True)
        self._label.setStyleSheet("QLabel { background-color: red}")

        layout.addWidget(self._label)
        layout.addWidget(self._btn)

        self.__color = GlobalColor.white  # TODO: Load color from settings
        self.__setColor(self.__color)

        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.setLayout(layout)

    def __setColor(self, color):
        # type: (QColor | GlobalColor) -> None
        labelPalette = self._label.palette()
        labelPalette.setColor(QPalette.ColorRole.Window, color)
        self.__color = color

    def updateColor(self):

        color = QColorDialog.getColor()

        if color.isValid():
            self.__setColor(color)


class CustomImage(QLabel):
    def __init__(self, parent, src):
        # type: (QWidget | None, QPixmap | str | QImage) -> None
        super().__init__(parent)

        self.__currentSize = QSize(60, 60)
        self.setScaledContents(True)

        if isinstance(src, str):
            self.load_image_from_url(src)
        elif src is not None:
            self.setPixmap(src)
            self.resizeImage()

    def resetFixedSize(self):
        resetFixedSize(self)

    def resizeImage(self):
        pixmap = self.pixmap()
        if pixmap:
            self.setPixmap(
                pixmap.scaled(
                    self.__currentSize,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
            )

    @cache
    def networkManager(self):
        manager = QtNetwork.QNetworkAccessManager(self)
        manager.finished.connect(self._handle_reply)
        return manager

    def _handle_reply(self, reply):
        # type: (QtNetwork.QNetworkReply,) -> None

        if reply.error() == QtNetwork.QNetworkReply.NetworkError.NoError:

            response_data = reply.readAll()
            image = QImage()

            if image.loadFromData(response_data.data()):
                QtCore.qDebug("load_image_from_url: Image Loaded")

                self.setPixmap(QPixmap(image))
                self.resizeImage()

            else:
                QtCore.qDebug("load_image_from_url: Image Not Loaded")

        else:
            QtCore.qDebug("load_image_from_url: QNetworkReply Error!")

    def load_image_from_url(self, url_str, new_size=None):
        # type: (str, QSize | None) -> None
        url = QUrl(url_str)

        if url.isValid():
            QtCore.qDebug("load_image_from_url: url is valid => " + url.url())

            if not url.isLocalFile():
                QtCore.qDebug("load_image_from_url: url is not a local file")
                QtNetwork.QNetworkProxyFactory.setUseSystemConfiguration(True)
            else:
                QtCore.qDebug("load_image_from_url: url is a local file")

            if isinstance(new_size, QSize):
                self.__currentSize = new_size
            self.networkManager().get(QtNetwork.QNetworkRequest(url))
