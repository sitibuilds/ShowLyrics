from .generic_view_components import *
from .icon_components import (
    AppIcon,
    CloseIcon,
    SettingsIcon,
    TwoStateIcon,
    PlayPauseIcon,
    ExpandShrinkIcon,
)


class MainWindowView(GenericWindowView):
    def __init__(self, parent):
        # type: (QWidget | None) -> None
        super().__init__(
            parent,
            "Main Text",
            "Sub Text",
            WindowContentView(None),
            footer=LyricsViewControl(None),
        )
        self.layout().setSpacing(0)
        self.resize(400, 180)


class WindowContentView(QFrame):
    def __init__(self, parent, f=None) -> None:
        # type: (QWidget | None, WindowTypes) -> None
        if f is not None:
            super().__init__(parent, f)
        else:
            super().__init__(parent)

        layout = QHBoxLayout(self)
        self.setLayout(layout)

        # self.setFixedSize(50, 50)
        self.setStyleSheet("background-color: green")


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
