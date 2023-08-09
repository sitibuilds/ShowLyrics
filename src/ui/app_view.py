from .generic_view_components import *
from .icon_components import (
    AppIcon,
    CloseIcon,
    SettingsIcon,
    TwoStateIcon,
    PlayPauseIcon,
    ExpandShrinkIcon,
    RewindIcon,
)


class MainWindowView(GenericWindowView):
    def __init__(self, parent):
        # type: (QWidget | None) -> None
        super().__init__(
            parent,
            "Main Text",
            "Sub Text",
            LyricsView(None),
            footer=FooterView(None),
        )
        self.layout().setSpacing(0)
        self.resize(400, 180)


class LyricsView(QFrame):
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


class MediaControl(QFrame):
    def __init__(self, parent, f=None):
        if f is not None:
            super().__init__(parent, f)
        else:
            super().__init__(parent)

        layout = QHBoxLayout(self)

        playPause = PlayPauseIcon(
            self, lambda x: print("play", x), lambda y: print("pause", y)
        )
        playPause.setFixedSizeAppIcons(20, 20)

        rewindBackward = RewindIcon(self, lambda x: print("rewind back", x), False)
        rewindBackward.setFixedSize(20, 20)
        rewindForward = RewindIcon(self, lambda x: print("rewind forward", x), True)
        rewindForward.setFixedSize(20, 20)

        layout.addWidget(rewindBackward)
        layout.addWidget(playPause)
        layout.addWidget(rewindForward)

        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)


class FooterView(QFrame):
    def __init__(self, parent, f=None):
        # type: (QWidget | None, WindowTypes | None) -> None
        if f is not None:
            super().__init__(parent, f)
        else:
            super().__init__(parent)

        # self.setAutoFillBackground(True)
        mediaControl = MediaControl(self)
        image = CustomImage(self, "https://www.python.org/static/img/python-logo.png")
        settings = SettingsIcon(self, lambda x: print("settings"))

        settings.setFixedSize(20, 20)

        layout = QHBoxLayout()
        layout.addWidget(image)
        layout.addStretch(1)
        layout.addWidget(mediaControl)
        layout.addStretch(1)
        layout.addWidget(settings)
        layout.setContentsMargins(0, 0, 0, 0)

        self.setLayout(layout)

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
