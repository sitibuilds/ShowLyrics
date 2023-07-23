from typing import Optional, Callable

from ui.qt_imports import QEvent, QMouseEvent, QPaintEvent, QWidget, WindowTypes

from .qt_imports import *
from .custom_widgets import (
    FramelessRoundedBorderWidget,
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


class GenericMainWindow(QMovableResizableWidget):
    def __init__(self, parent, titleBarViewMainText, titleBarViewSubText, *childViews):
        # type: (QWidget | None, str, str, *QWidget) -> None
        super().__init__(parent, WindowTypes.Window | WindowTypes.FramelessWindowHint)

        mainLayout = QVBoxLayout(self)

        def closeWindow(ev):
            self.close()

        self._titleBarView = TitleBarView(
            self,
            mainText=titleBarViewMainText,
            subText=titleBarViewSubText,
            onCloseCallback=closeWindow,
        )

        self.__childViews = childViews
        mainLayout.addWidget(self._titleBarView)

        for view in self.__childViews:
            if isinstance(view, QWidget):
                mainLayout.addStretch(1)
                view.setParent(self)
                mainLayout.addWidget(view)

        self.setLayout(mainLayout)
        self.setBorderStyle(borderStyle=self.BorderStyle(radius=10, thickness=5))


class MainWindow(GenericMainWindow):
    def __init__(self, parent):
        # type: (QWidget | None) -> None
        super().__init__(
            parent,
            "Main Text",
            "Sub Text",
            WindowContentView(None),
            LyricsViewControl(None),
        )
        self.layout().setSpacing(0)
        self.resize(400, 180)


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


class WindowContentView(CustomQWidget):
    def __init__(self, parent, f=None) -> None:
        # type: (QWidget | None, WindowTypes) -> None
        if f is not None:
            super().__init__(parent, f)
        else:
            super().__init__(parent)

        layout = QHBoxLayout()


class LyricsViewControl(QFrame):
    def __init__(self, parent, f=None):
        # type: (QWidget | None, WindowTypes | None) -> None
        if f is not None:
            super().__init__(parent, f)
        else:
            super().__init__(parent)

        # self.setAutoFillBackground(True)
        playPause = PlayPauseIcon(
            self, lambda x: print("play", x), lambda y: print("pause", y)
        )
        settings = SettingsIcon(self, lambda x: print("settings"))
        expandShrink = ExpandShrinkIcon(
            self, lambda x: print("expand", x), lambda y: print("shrink", y)
        )

        expandShrink.setFixedSizeAppIcons(20, 20)
        playPause.setFixedSizeAppIcons(20, 20)
        settings.setFixedSize(20, 20)

        layout = QHBoxLayout()
        layout.addWidget(settings)
        layout.addStretch(1)
        layout.addWidget(playPause)
        layout.addStretch(1)
        layout.addWidget(expandShrink)
        layout.setContentsMargins(0, 0, 0, 0)

        self.setLayout(layout)

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)


class AppIcon(ClickableSvgWidget):
    def __init__(self, parent, svgFilePath, callback):
        # type: (QWidget | None, str | None, Callable[[QEvent], None]) -> None
        super().__init__(parent, None, svgFilePath, callback)


class CloseIcon(AppIcon):
    def __init__(
        self, parent: QWidget | None, callback: Callable[[QEvent], None]
    ) -> None:
        super().__init__(parent, ":/icons/Close.svg", callback)


class TwoStateIcon(AppIcon):
    def __init__(self, parent, stateAIcon, stateBIcon, stateACallback, stateBCallback):
        # type: (QWidget| None, str | None, str | None, Callable[[QEvent], None], Callable[[QEvent], None]) -> None

        super().__init__(parent, "", None)

        self.__stateACallback = stateACallback
        self.__stateBCallback = stateBCallback

        def _stateACallback(ev):
            # type: (QEvent | None) -> None
            self.__stateACallback(ev)
            self.__changeState(False)

        def _stateBCallback(ev):
            # type: (QEvent | None) -> None
            self.__stateBCallback(ev)
            self.__changeState(True)

        self.__iconA = AppIcon(self, stateAIcon, _stateACallback)
        self.__iconB = AppIcon(self, stateBIcon, _stateBCallback)

        self.__is_state_A = None
        self.__iconA.hide()
        self.__iconB.hide()

        self.__changeState(True)

    def __changeState(self, to_state_A):
        # type: (bool) -> None

        if self.__is_state_A != to_state_A:
            self.__is_state_A = to_state_A

            prev_widget = None
            if to_state_A:
                prev_widget = self._replaceInnerWidget(self.__iconA)
            else:
                prev_widget = self._replaceInnerWidget(self.__iconB)

            if prev_widget:
                prev_widget.hide()

            curr_widget = self.svgWidget()
            if curr_widget:
                curr_widget.show()

    def setFixedSizeAppIcons(self, width, height):
        # type: (int, int) -> None
        self.__iconA.setFixedSize(width, height)
        self.__iconB.setFixedSize(width, height)


class PlayPauseIcon(TwoStateIcon):
    def __init__(self, parent, playStateCallback, pauseStateCallback):
        # type: (QWidget | None, Callable[[QEvent], None], Callable[[QEvent], None]) -> None
        super().__init__(
            parent,
            ":/icons/Play.svg",
            ":/icons/Pause.svg",
            playStateCallback,
            pauseStateCallback,
        )


class ExpandShrinkIcon(TwoStateIcon):
    def __init__(self, parent, expandStateCallback, shrinkStateCallback):
        # type: (QWidget | None, Callable[[QEvent], None], Callable[[QEvent], None]) -> None
        super().__init__(
            parent,
            ":/icons/Expand.svg",
            ":/icons/Shrink.svg",
            expandStateCallback,
            shrinkStateCallback,
        )
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)


class SettingsIcon(AppIcon):
    def __init__(self, parent, callback):
        # type: (QWidget | None, Callable[[QEvent], None]) -> None
        super().__init__(parent, ":/icons/Settings.svg", callback)
