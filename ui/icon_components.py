from typing import Callable

from .qt_imports import (
    QWidget,
    QEvent,
    QSizePolicy,
    QFrame,
    WindowTypes,
    CursorShape,
    WidgetAttributes,
    QVBoxLayout,
    QSvgWidget,
    QMouseEvent,
    Qt,
)


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
