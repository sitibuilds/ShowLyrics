import enum
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
    QObject
)


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

    def __init__(
        self,
        parent,
    ):
        super().__init__(parent, WindowTypes.FramelessWindowHint)

        self.setObjectName("Frameless-Widget")

        # Resizing support
        # self.setAttribute(Qt.WidgetAttribute.WA_Hover, True)
        self.setMouseTracking(True)

        self._borderThickness = 5
        self.__resizeActive = False
        self._offendingBorder = self.__ResizableWidgetBorder.UNSET
    
    def setBorderThickness(self, thickness):
        # type: (float) -> None
        val = max(5, thickness)
        self.setContentsMargins(*(val,)*4)

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
        if relPosX <= 0 + self._borderThickness:
            border |= self.__ResizableWidgetBorder.LEFT
        elif w - self._borderThickness <= relPosX <= w or relPosX > w:
            border |= self.__ResizableWidgetBorder.RIGHT
        
        if relPosY <= 0 + self._borderThickness:
            border |= self.__ResizableWidgetBorder.TOP
        elif h - self._borderThickness <= relPosY <= h or relPosY > h:
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
                    cursorGlobalX, cursorGlobalY = globalPosition.x(), globalPosition.y()

                    y1, y2, x1, x2 = y, y+oldH, x, x+oldW

                    if self.__ResizableWidgetBorder.TOP in self._offendingBorder:
                        y1 = cursorGlobalY

                    elif self.__ResizableWidgetBorder.BOTTOM in self._offendingBorder:
                        y2 = cursorGlobalY
                    
                    if self.__ResizableWidgetBorder.LEFT in self._offendingBorder:
                        x1 = cursorGlobalX
                    
                    elif self.__ResizableWidgetBorder.RIGHT in self._offendingBorder:
                        x2 = cursorGlobalX
                    
                    newX, newY =  x1, y1
                    newW, newH = max(0, x2 - x1), max(0, y2 - y1)

                    self.setGeometry(newX, newY, newW, newH)
                
                return True
        return False
