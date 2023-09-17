from PySide6.QtCore import QObject
from api import get_lrc_lyrics
from data_types import LRCEntry, LyricSource, LyricTime
from datetime import datetime

class LRCLyrics:
    def __init__(self, lrc_string, source):
        # type: (str, str) -> None
        pass
    
    @staticmethod
    def __process_lrc_string(lrc_string):
        # type: (str) -> LRCLyrics
        lyrics = lrc_string.splitlines()

        def process(lrc_lyric):
            # type: (str) -> tuple[datetime, str]

            time_format = "[%M:%S.%f]"

            i = lrc_lyric.find(']')
            lyric_str = lrc_lyric[i+1:].strip()
            time_str = lrc_lyric[:i+1].strip()

            t = LyricTime.strptime(time_str, time_format)

            # TODO: Continue Lyrics View Model
            

def get_lyrics(track_name, artist_name):
    # type: (str, str) -> LRCLyrics
    pass

    lrc = get_lrc_lyrics(track_name, artist_name)

    lyric = LRCLyrics()
class LyricsViewModel(QObject):
    """Manage lyrics information, providing endpoints for Views to retrieve time-synced lyrics and/or full lyrics for songs"""

    def __init__(self, track_name=None, artist_name=None, lyrics=None) -> None:
        # type: (str|None, str|None, LRCLyrics) -> None
        """Create a new LyricsViewModel instance

        Args:
            track_name (str, optional): Track Name. Defaults to None.
            artist_name (str, optional): Artist Name for the specified track. Defaults to None.
            lyrics (LRCLyrics, optional): Lyrics Data - Specifying this parameter 
                            prevents the object from making an API call. Defaults to None.
        """
        super().__init__()

