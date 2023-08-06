from typing import Optional
from PySide6.QtCore import QObject
from typing import TypedDict, TypeAlias

class LyricEntry(TypedDict):
    lyricText: str
    time: float # Start time of lyric in milliseconds

class LyricsViewModel(QObject):
    """Self manages api calls, lyrics information, ..."""
    
    def __init__(self, ) -> None:
        # type: () -> None
        super().__init__()