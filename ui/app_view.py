from typing import Optional, Callable

import PySide6.QtCore

from ui.qt_imports import QEvent, QMouseEvent, QPaintEvent

from .qt_imports import *
from .custom_widgets import (
    QResizableWidget,
    ClickableSvgWidget,
    CustomQWidget,
    QMovableResizableWidget,
)
from .fonts_import import CUSTOM_FONT_ID
from .utils import fadeAnimation


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
            # print("Font couldn't load")
            pass
        else:
            families = QFontDatabase.applicationFontFamilies(self.FONTID)
            print(families, fontName)
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


class MainWindow(QMovableResizableWidget):
    def __init__(
        self,
        parent,
    ):
        # type: (QWidget | None,) -> None

        super().__init__(parent, WindowTypes.Window | WindowTypes.FramelessWindowHint)
        self.setAttribute(WidgetAttributes.WA_Hover, True)

        mainLayout = QVBoxLayout(self)

        def closeWindow(ev):
            self.close()

        self._titleBar = TitleBarGroup(
            self,
            mainText="Main Text",
            subText="Sub Text",
            onCloseCallback=closeWindow,
        )
        self._windowContent = WindowContent(
            self,
        )
        self._winControl = WindowControl(
            self,
        )

        mainLayout.addWidget(self._titleBar)
        mainLayout.addWidget(self._windowContent)
        mainLayout.addWidget(self._winControl)

        mainLayout.setStretch(0, 0)
        mainLayout.setStretch(2, 0)
        mainLayout.setStretch(1, 1)

        mainLayout.setSpacing(0)
        self.setLayout(mainLayout)
        self.resize(400, 180)

        self.setBorderStyle(
            borderStyle=self.BorderStyle(
                radius=10,
                thickness=5,
            )
        )


class TitleBarGroup(CustomQWidget):
    def __init__(self, parent, f=None, mainText="", subText="", onCloseCallback=None):
        # type: (QWidget | None, WindowTypes | None, str, str, Callable[[QEvent], None] | None) -> None

        if f is not None:
            super().__init__(parent, f)
        else:
            super().__init__(parent)

        self.mainTextLabel = AppLabel(mainText, self, pixelSize=20)
        self.subTextLabel = AppLabel(subText, self)

        closeSvg = ClickableSvgWidget(
            self, svgFilePath=":/icons/Close.svg", msBtnPressCallback=onCloseCallback
        )
        closeSvg.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.closeSVG = closeSvg

        grid = QGridLayout(self)
        grid.addWidget(
            self.mainTextLabel, 0, 0, AlignmentFlag.AlignLeft | AlignmentFlag.AlignTop
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
        grid.setSpacing(0)
        grid.setContentsMargins(0, 0, 0, 0)
        self.setAttribute(WidgetAttributes.WA_MouseTracking, True)

    def fadeIn(self, duration: int = 250) -> None:

        return super().fadeIn(duration)


class WindowContent(CustomQWidget):
    def __init__(self, parent, f=None) -> None:
        # type: (QWidget | None, WindowTypes) -> None
        if f is not None:
            super().__init__(parent, f)
        else:
            super().__init__(parent)

        # self.setAttribute(WidgetAttributes.WA_TransparentForMouseEvents, True)


class WindowControl(QWidget):
    def __init__(self, parent, f=None):
        # type: (QWidget | None, WindowTypes | None) -> None
        if f is not None:
            super().__init__(parent, f)
        else:
            super().__init__(parent)

        # self.setAutoFillBackground(True)
