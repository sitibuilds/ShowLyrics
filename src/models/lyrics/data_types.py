import enum
from dataclasses import dataclass, asdict, field

class LyricSource(enum.Enum):
    Musixmatch = enum.auto()
    LRCLib = enum.auto()
    MegaLobiz = enum.auto()
    NetEase = enum.auto()


class LRCEntry:
    __slots__ = ("lyric", "time")

    def __init__(self, lyric="", time=None) -> None:
        # type: (str, None | LyricTime) -> None
        self.lyric = lyric
        self.time = time

    def __str__(self):
        return str({"lyric": self.lyric, "time": str(self.time)})

    def __repr__(self):
        return f"LRCEntry(time={str(self.time)}, lyric={self.lyric})"


class LyricTime:
    """
    A class for representing playback time in mins,secs, and milliseconds format
    """

    __slots__ = ("mins", "secs", "ms", "__ms_cached")

    def __init__(self, mins, secs, ms):
        # type: (int, int, int) -> None

        self.validate_time(mins, secs, ms)
        self.mins = mins
        self.secs = secs
        self.ms = ms

    def __str__(self):
        return f"{self.mins}:{self.secs}.{self.ms}"

    def __repr__(self):
        return f"Time(mins={self.mins}, secs={self.secs}, ms={self.ms})"

    def __add__(self, other):
        # type: (LyricTime) -> LyricTime
        if isinstance(other, LyricTime):
            ms = self.to_milliseconds() + other.to_milliseconds()
            return LyricTime.convert_from_milliseconds(ms)
        raise TypeError("Cannot add to object of type %s" % type(other))

    def __sub__(self, other):
        # type: (LyricTime) -> LyricTime
        if isinstance(other, LyricTime):
            ms = abs(self.to_milliseconds() + other.to_milliseconds())
            return LyricTime.convert_from_milliseconds(ms)
        raise TypeError("Cannot subtract from object of type %s" % type(other))

    @staticmethod
    def strptime(time_str, format="%M:%S.%m"):
        # type: (str, str) -> LyricTime
        """Pass LyricTime from a given string.

        Placeholders are denoted by a '%' char and another character specifying the semantics of the time it represents.

        Accepted placeholders: %M - Minute, %S - Second, %m - millisecond, %% - Match the char '%'

        If a placeholder is not specifed, it is assumed to be 0.

        If no placeholder is specified, the function throws an exception.
        """

        valid_placeholders = ("%M", "%S", "%m", "%%")

        mins, secs, ms = -1, -1, -1

        time_str_idx = 0  # `time_str` has been validated upto this index as matching the provided format
        format_idx = 0  # `format` has been validated upto this index

        def find_non_numeric_idx(string, start=0):
            # type: (str, int) -> int

            nums = tuple(str(i) for i in range(10))
            for i, c in enumerate(string[start:], start):
                if c not in nums:
                    return i
            return -1

        while time_str_idx < len(time_str) and format_idx < len(format):
            t, f = time_str[time_str_idx], format[format_idx]

            if f != "%":
                if t != f:
                    raise ValueError(
                        f"Time string '{time_str}' does not match format '{format}'"
                    )
                else:
                    time_str_idx += 1
                    format_idx += 1
            else:
                # Look ahead to verify placeholder and check placeholder's value in time string
                if format_idx + 1 < len(format):
                    placeholder = format[format_idx : format_idx + 2]

                    if placeholder not in valid_placeholders:
                        raise ValueError(
                            "Invalid format. Unknown placeholder: %s" % placeholder
                        )

                    if placeholder == "%%":
                        if time_str_idx < len(time_str):
                            if time_str[time_str_idx] == "%":
                                time_str_idx += 1
                                format_idx += 2
                                continue

                        raise ValueError(
                            "Time string '{time_str}' does not match format '{format}'"
                        )

                    # Check placeholder value in time string
                    i = find_non_numeric_idx(time_str, time_str_idx)
                    if i == -1:
                        value_str = time_str[time_str_idx:]
                    else:
                        value_str = time_str[time_str_idx:i]

                    try:
                        value = int(value_str)

                        if placeholder == "%M":
                            if mins == -1:
                                mins = value
                            else:
                                raise ValueError(
                                    f"Invalid format. Multiple instances of placeholder '{placeholder}' not allowed"
                                )

                        elif placeholder == "%m":
                            if ms == -1:
                                ms = value
                            else:
                                raise ValueError(
                                    f"Invalid format. Multiple instances of placeholder '{placeholder}' not allowed"
                                )

                        elif placeholder == "%S":
                            if secs == -1:
                                secs = value
                            else:
                                raise ValueError(
                                    f"Invalid format. Multiple instances of placeholder '{placeholder}' not allowed"
                                )

                        else:
                            raise ValueError(f"Invalid format")

                        time_str_idx = i if i != -1 else len(time_str)
                        format_idx += 2

                    except ValueError:
                        raise ValueError(
                            f"Time string '{time_str}' does not match format '{format}'"
                        )
                else:
                    raise ValueError(
                        "Invalid format. '%' must be followed by another character"
                    )

        if time_str_idx >= len(time_str) and format_idx >= len(format):
            if mins == -1:
                mins = 0
            if secs == -1:
                secs = 0
            if ms == -1:
                ms = 0
        else:
            raise ValueError(
                f"Time string '{time_str}' does not match format '{format}'"
            )

        return LyricTime(mins, secs, ms)

    @staticmethod
    def validate_time(mins, secs, ms):

        assert 0 <= mins <= 59
        assert 0 <= secs <= 59
        assert 0 <= ms <= 999

    def to_milliseconds(self):
        # type: () -> int
        if self.__ms_cached is not None:
            return self.__ms_cached
        self.__ms_cached = ms = (self.mins * 60 * 1000) + (self.secs * 1000) + self.ms
        return ms

    @staticmethod
    def convert_from_milliseconds(ms):
        # type: (int) -> LyricTime

        _s = int(ms / 1000)
        secs = _s % 60
        mins = (_s // 60) % 60
        ms = int(ms) % 1000

        return LyricTime(mins, secs, ms)

    def __eq__(self, __value):
        # type: (object) -> bool
        if isinstance(__value, LyricTime):
            return (
                __value.mins == self.mins
                and __value.secs == self.secs
                and __value.ms == self.ms
            )
        return False

    def __lt__(self, __value):
        if isinstance(__value, LyricTime):
            return self.to_milliseconds() < __value.to_milliseconds()

        elif isinstance(__value, int):
            return self.to_milliseconds() < __value

        raise TypeError(
            f"Cannot compare object of type {type(self)} to object of type {type(__value)}"
        )

@dataclass
class CustomDataClass:

    def to_dict(self):
        return asdict(self)

@dataclass(kw_only=True, repr=True, init=True)
class TrackDetails(CustomDataClass):
    name: str # Name of the track
    artists: list[str] # List of artists who performed the track
    is_playing: bool
    track_type: str # Can be one of 'track', 'episode', 'ad', or 'unknown'
    duration_ms: int # Track duration
    ms_remote: int = -1  # Remote progress in milliseconds if song is currently playing. (-1 if not playing)
    popularity: float = -1 # Track popularity
    meta: dict = field(default_factory=dict) # Meta information which provides some context for the currently playing track
        
    def __eq__(self, val):
        if isinstance(val, TrackDetails):
            return val.name == self.name and self.track_type == val.track_type and val.artists == self.artists
        raise TypeError("Cannot compare object of type %s" % type(val) + " to obejct of type %s" % type(self))
    

if __name__ == "__main__":

    t = LyricTime.strptime("50:20.09", "%M:%S.%m")
