import syncedlyrics
import spotipy
from data_types import TrackDetails
from dotenv import load_dotenv
import os


# TODO: Allow caller to specify these values; Remove load_dotenv from this module
SCRIPT_PATH = os.path.abspath(os.path.realpath(__file__))
dotenv_path = os.path.abspath(os.path.join(SCRIPT_PATH, "..", "..", "..", "..", ".env"))
load_dotenv(dotenv_path)

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")

SPOTIFY_SCOPE_READ_PLAYBACK_STATE = "user-read-playback-state"
SPOTIFY_SCOPE_MODIFY_PLAYBACK_STATE = "user-modify-playback-state"
SPOTIFY_SCOPE_READ_CURRENTLY_PLAYING = "user-read-currently-playing"
SCOPES = [
    SPOTIFY_SCOPE_READ_PLAYBACK_STATE,
    SPOTIFY_SCOPE_MODIFY_PLAYBACK_STATE,
    SPOTIFY_SCOPE_READ_CURRENTLY_PLAYING,
]


def get_lrc_lyrics(track_name, artist_name):
    # type: (str, str) -> dict[str, str | None]
    """
    Retrieves the lyric for the track specified in the search term in LRC format.

    search_term: `[TRACK_NAME] [ARTIST_NAME]`
    """

    transform_str = lambda s: s.strip().replace(" ", "_")
    search_term = transform_str(track_name) + " " + transform_str(artist_name)

    _providers = [
        syncedlyrics.Lrclib(),
        syncedlyrics.Musixmatch(),
        syncedlyrics.NetEase(),
        syncedlyrics.Megalobiz(),
    ]

    result = {
        "lrc": None,
        "source": None,
    }

    for provider in _providers:

        lrc_lyrics = provider.get_lrc(search_term)

        if syncedlyrics.is_lrc_valid(lrc_lyrics):
            result["lrc"] = lrc_lyrics
            result["source"] = provider.__class__.__name__
            break

    return result


def spotify_acquire_token_info(cached_token_info=None):
    # type: (dict | None) -> dict
    """
    Retrieve token info for authenticated user

    This function will take the user to the Spotify authentication page on their web browser.
    The token info is not stored locally, within this function

    """

    cache_handler = spotipy.cache_handler.MemoryCacheHandler(cached_token_info)
    oauth = spotipy.oauth2.SpotifyOAuth(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        scope=SCOPES,
        cache_handler=cache_handler,
    )

    # Validate cached token. If expired, refresh token info
    token_info = oauth.validate_token(cache_handler.get_cached_token())

    if token_info is None:  # No token exists

        token_info = oauth.get_access_token(None, as_dict=True)

        # Note: This is only for future versions of spotipy which may not support as_dict in get_access_token
        if isinstance(token_info, (str,)):
            return cache_handler.get_cached_token()

        return token_info

    else:
        return token_info


def get_currently_playing_song(cached_token_info=None):

    token_info = spotify_acquire_token_info(cached_token_info)

    token = token_info["access_token"]

    try:
        spotify_obj = spotipy.Spotify(auth=token)

        track = spotify_obj.currently_playing()
    except:
        # TODO: Log error
        return None

    if track is not None:
        track_type = track["currently_playing_type"]
        meta = {
            "actions": track["actions"],
        }

        item = track["item"]
        name = ""
        artists = []
        is_playing = track["is_playing"]
        progress_ms = track["progress_ms"] if track["progress_ms"] else -1
        duration_ms = -1
        popularity = -1

        if item:
            name = item["name"]
            popularity = item["popularity"] / 100
            duration_ms = item["duration_ms"]
            artists = list(map(lambda x: x["name"], item["artists"]))

        return TrackDetails(
            name=name,
            artists=artists,
            is_playing=is_playing,
            ms_remote=progress_ms,
            duration_ms=duration_ms,
            popularity=popularity,
            meta=meta,
            track_type=track_type,
        )

    return track


if __name__ == "__main__":
    from pprint import pprint

    pprint(get_currently_playing_song())
