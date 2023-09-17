import syncedlyrics

def get_lrc_lyrics(track_name, artist_name):
    # type: (str, str) -> dict[str, str | None]
    """
    Inspired by the `syncedlyrics.search` function

    Retrieves the lyric for the track specified in the search term in LRC format.
    
    search_term: `[TRACK_NAME] [ARTIST_NAME]`
    """
    
    transform_str = lambda s : s.strip().replace(" ", "_")
    search_term = transform_str(track_name) + " " + transform_str(artist_name)

    print(search_term)

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

