
class _BaseController:
    def __init__(self, request_handler):
        self._request_handler_ = request_handler

    async def mopidy_request(self, method, **kwargs):
        return await self._request_handler_(method, **kwargs)


class CoreController(_BaseController):

    async def get_uri_schemes(self, **options):
        """Get list of URI schemes we can handle"""
        return await self.mopidy_request('core.get_uri_schemes', **options)

    async def get_version(self, **options):
        """Get version of the Mopidy core API"""
        return await self.mopidy_request('core.get_version', **options)

    async def describe(self, **options):
        """Get all endpoints"""
        return await self.mopidy_request('core.describe', **options)

    
class HistoryController(_BaseController):

    async def get_history(self, **options):
        """Get the track history.
        The timestamps are milliseconds since epoch.
        :returns: the track history
        :rtype: list of (timestamp, :class:`mopidy.models.Ref`) tuples"""
        return await self.mopidy_request('core.history.get_history', **options)

    async def get_length(self, **options):
        """Get the number of tracks in the history.
        :returns: the history length
        :rtype: int"""
        return await self.mopidy_request('core.history.get_length', **options)

    
class LibraryController(_BaseController):

    async def browse(self, uri, **options):
        """Browse directories and tracks at the given ``uri``.
        ``uri`` is a string which represents some directory belonging to a
        backend. To get the intial root directories for backends pass
        :class:`None` as the URI.
        Returns a list of :class:`mopidy.models.Ref` objects for the
        directories and tracks at the given ``uri``.
        The :class:`~mopidy.models.Ref` objects representing tracks keep the
        track's original URI. A matching pair of objects can look like this::
            Track(uri='dummy:/foo.mp3', name='foo', artists=..., album=...)
            Ref.track(uri='dummy:/foo.mp3', name='foo')
        The :class:`~mopidy.models.Ref` objects representing directories have
        backend specific URIs. These are opaque values, so no one but the
        backend that created them should try and derive any meaning from them.
        The only valid exception to this is checking the scheme, as it is used
        to route browse requests to the correct backend.
        For example, the dummy library's ``/bar`` directory could be returned
        like this::
            Ref.directory(uri='dummy:directory:/bar', name='bar')
        :param string uri: URI to browse
        :rtype: list of :class:`mopidy.models.Ref`
        .. versionadded:: 0.18"""
        return await self.mopidy_request('core.library.browse', uri=uri, **options)

    async def get_distinct(self, field, query=None, **options):
        """List distinct values for a given field from the library.
        This has mainly been added to support the list commands the MPD
        protocol supports in a more sane fashion. Other frontends are not
        recommended to use this method.
        :param string field: One of ``track``, ``artist``, ``albumartist``,
            ``album``, ``composer``, ``performer``, ``date`` or ``genre``.
        :param dict query: Query to use for limiting results, see
            :meth:`search` for details about the query format.
        :rtype: set of values corresponding to the requested field type.
        .. versionadded:: 1.0"""
        return await self.mopidy_request('core.library.get_distinct', field=field, query=query, **options)

    async def get_images(self, uris, **options):
        """Lookup the images for the given URIs
        Backends can use this to return image URIs for any URI they know about
        be it tracks, albums, playlists. The lookup result is a dictionary
        mapping the provided URIs to lists of images.
        Unknown URIs or URIs the corresponding backend couldn't find anything
        for will simply return an empty list for that URI.
        :param uris: list of URIs to find images for
        :type uris: list of string
        :rtype: {uri: tuple of :class:`mopidy.models.Image`}
        .. versionadded:: 1.0"""
        return await self.mopidy_request('core.library.get_images', uris=uris, **options)

    async def lookup(self, uris, **options):
        """Lookup the given URIs.
        If the URI expands to multiple tracks, the returned list will contain
        them all.
        :param uris: track URIs
        :type uris: list of string
        :rtype: {uri: list of :class:`mopidy.models.Track`}"""
        return await self.mopidy_request('core.library.lookup', uris=uris, **options)

    async def refresh(self, uri=None, **options):
        """Refresh library. Limit to URI and below if an URI is given.
        :param uri: directory or track URI
        :type uri: string"""
        return await self.mopidy_request('core.library.refresh', uri=uri, **options)

    async def search(self, query, uris=None, exact=False, **options):
        """Search the library for tracks where ``field`` contains ``values``.
        ``field`` can be one of ``uri``, ``track_name``, ``album``, ``artist``,
        ``albumartist``, ``composer``, ``performer``, ``track_no``, ``genre``,
        ``date``, ``comment``, or ``any``.
        If ``uris`` is given, the search is limited to results from within the
        URI roots. For example passing ``uris=['file:']`` will limit the search
        to the local backend.
        Examples::
            # Returns results matching 'a' in any backend
            search({'any': ['a']})
            # Returns results matching artist 'xyz' in any backend
            search({'artist': ['xyz']})
            # Returns results matching 'a' and 'b' and artist 'xyz' in any
            # backend
            search({'any': ['a', 'b'], 'artist': ['xyz']})
            # Returns results matching 'a' if within the given URI roots
            # "file:///media/music" and "spotify:"
            search({'any': ['a']}, uris=['file:///media/music', 'spotify:'])
            # Returns results matching artist 'xyz' and 'abc' in any backend
            search({'artist': ['xyz', 'abc']})
        :param query: one or more queries to search for
        :type query: dict
        :param uris: zero or more URI roots to limit the search to
        :type uris: list of string or :class:`None`
        :param exact: if the search should use exact matching
        :type exact: :class:`bool`
        :rtype: list of :class:`mopidy.models.SearchResult`
        .. versionadded:: 1.0
            The ``exact`` keyword argument."""
        return await self.mopidy_request('core.library.search', query=query, uris=uris, exact=exact, **options)

    
class MixerController(_BaseController):

    async def get_mute(self, **options):
        """Get mute state.
        :class:`True` if muted, :class:`False` unmuted, :class:`None` if
        unknown."""
        return await self.mopidy_request('core.mixer.get_mute', **options)

    async def get_volume(self, **options):
        """Get the volume.
        Integer in range [0..100] or :class:`None` if unknown.
        The volume scale is linear."""
        return await self.mopidy_request('core.mixer.get_volume', **options)

    async def set_mute(self, mute, **options):
        """Set mute state.
        :class:`True` to mute, :class:`False` to unmute.
        Returns :class:`True` if call is successful, otherwise :class:`False`."""
        return await self.mopidy_request('core.mixer.set_mute', mute=mute, **options)

    async def set_volume(self, volume, **options):
        """Set the volume.
        The volume is defined as an integer in range [0..100].
        The volume scale is linear.
        Returns :class:`True` if call is successful, otherwise :class:`False`."""
        return await self.mopidy_request('core.mixer.set_volume', volume=volume, **options)

    
class PlaybackController(_BaseController):

    async def get_current_tl_track(self, **options):
        """Get the currently playing or selected track.
        Returns a :class:`mopidy.models.TlTrack` or :class:`None`."""
        return await self.mopidy_request('core.playback.get_current_tl_track', **options)

    async def get_current_tlid(self, **options):
        """Get the currently playing or selected TLID.
        Extracted from :meth:`get_current_tl_track` for convenience.
        Returns a :class:`int` or :class:`None`.
        .. versionadded:: 1.1"""
        return await self.mopidy_request('core.playback.get_current_tlid', **options)

    async def get_current_track(self, **options):
        """Get the currently playing or selected track.
        Extracted from :meth:`get_current_tl_track` for convenience.
        Returns a :class:`mopidy.models.Track` or :class:`None`."""
        return await self.mopidy_request('core.playback.get_current_track', **options)

    async def get_state(self, **options):
        """Get The playback state."""
        return await self.mopidy_request('core.playback.get_state', **options)

    async def get_stream_title(self, **options):
        """Get the current stream title or :class:`None`."""
        return await self.mopidy_request('core.playback.get_stream_title', **options)

    async def get_time_position(self, **options):
        """Get time position in milliseconds."""
        return await self.mopidy_request('core.playback.get_time_position', **options)

    async def next(self, **options):
        """Change to the next track.
        The current playback state will be kept. If it was playing, playing
        will continue. If it was paused, it will still be paused, etc."""
        return await self.mopidy_request('core.playback.next', **options)

    async def pause(self, **options):
        """Pause playback."""
        return await self.mopidy_request('core.playback.pause', **options)

    # DEPRECATED The ``tl_track`` argument. Use ``tlid`` instead.
    async def play(self, tl_track=None, tlid=None, **options):
        """Play the given track, or if the given tl_track and tlid is
        :class:`None`, play the currently active track.
        Note that the track **must** already be in the tracklist.
        .. deprecated:: 3.0
            The ``tl_track`` argument. Use ``tlid`` instead.
        :param tl_track: track to play
        :type tl_track: :class:`mopidy.models.TlTrack` or :class:`None`
        :param tlid: TLID of the track to play
        :type tlid: :class:`int` or :class:`None`"""
        return await self.mopidy_request('core.playback.play', tl_track=tl_track, tlid=tlid, **options)

    async def previous(self, **options):
        """Change to the previous track.
        The current playback state will be kept. If it was playing, playing
        will continue. If it was paused, it will still be paused, etc."""
        return await self.mopidy_request('core.playback.previous', **options)

    async def resume(self, **options):
        """If paused, resume playing the current track."""
        return await self.mopidy_request('core.playback.resume', **options)

    async def seek(self, time_position, **options):
        """Seeks to time position given in milliseconds.
        :param time_position: time position in milliseconds
        :type time_position: int
        :rtype: :class:`True` if successful, else :class:`False`"""
        return await self.mopidy_request('core.playback.seek', time_position=time_position, **options)

    async def set_state(self, new_state, **options):
        """Set the playback state.
        Must be :attr:`PLAYING`, :attr:`PAUSED`, or :attr:`STOPPED`.
        Possible states and transitions:
        .. digraph:: state_transitions
            "STOPPED" -> "PLAYING" [ label="play" ]
            "STOPPED" -> "PAUSED" [ label="pause" ]
            "PLAYING" -> "STOPPED" [ label="stop" ]
            "PLAYING" -> "PAUSED" [ label="pause" ]
            "PLAYING" -> "PLAYING" [ label="play" ]
            "PAUSED" -> "PLAYING" [ label="resume" ]
            "PAUSED" -> "STOPPED" [ label="stop" ]"""
        return await self.mopidy_request('core.playback.set_state', new_state=new_state, **options)

    async def stop(self, **options):
        """Stop playing."""
        return await self.mopidy_request('core.playback.stop', **options)

    
class PlaylistsController(_BaseController):

    async def as_list(self, **options):
        """Get a list of the currently available playlists.
        Returns a list of :class:`~mopidy.models.Ref` objects referring to the
        playlists. In other words, no information about the playlists' content
        is given.
        :rtype: list of :class:`mopidy.models.Ref`
        .. versionadded:: 1.0"""
        return await self.mopidy_request('core.playlists.as_list', **options)

    async def create(self, name, uri_scheme=None, **options):
        """Create a new playlist.
        If ``uri_scheme`` matches an URI scheme handled by a current backend,
        that backend is asked to create the playlist. If ``uri_scheme`` is
        :class:`None` or doesn't match a current backend, the first backend is
        asked to create the playlist.
        All new playlists must be created by calling this method, and **not**
        by creating new instances of :class:`mopidy.models.Playlist`.
        :param name: name of the new playlist
        :type name: string
        :param uri_scheme: use the backend matching the URI scheme
        :type uri_scheme: string
        :rtype: :class:`mopidy.models.Playlist` or :class:`None`"""
        return await self.mopidy_request('core.playlists.create', name=name, uri_scheme=uri_scheme, **options)

    async def delete(self, uri, **options):
        """Delete playlist identified by the URI.
        If the URI doesn't match the URI schemes handled by the current
        backends, nothing happens.
        Returns :class:`True` if deleted, :class:`False` otherwise.
        :param uri: URI of the playlist to delete
        :type uri: string
        :rtype: :class:`bool`
        .. versionchanged:: 2.2
            Return type defined."""
        return await self.mopidy_request('core.playlists.delete', uri=uri, **options)

    async def get_items(self, uri, **options):
        """Get the items in a playlist specified by ``uri``.
        Returns a list of :class:`~mopidy.models.Ref` objects referring to the
        playlist's items.
        If a playlist with the given ``uri`` doesn't exist, it returns
        :class:`None`.
        :rtype: list of :class:`mopidy.models.Ref`, or :class:`None`
        .. versionadded:: 1.0"""
        return await self.mopidy_request('core.playlists.get_items', uri=uri, **options)

    async def get_uri_schemes(self, **options):
        """Get the list of URI schemes that support playlists.
        :rtype: list of string
        .. versionadded:: 2.0"""
        return await self.mopidy_request('core.playlists.get_uri_schemes', **options)

    async def lookup(self, uri, **options):
        """Lookup playlist with given URI in both the set of playlists and in any
        other playlist sources. Returns :class:`None` if not found.
        :param uri: playlist URI
        :type uri: string
        :rtype: :class:`mopidy.models.Playlist` or :class:`None`"""
        return await self.mopidy_request('core.playlists.lookup', uri=uri, **options)

    async def refresh(self, uri_scheme=None, **options):
        """Refresh the playlists in :attr:`playlists`.
        If ``uri_scheme`` is :class:`None`, all backends are asked to refresh.
        If ``uri_scheme`` is an URI scheme handled by a backend, only that
        backend is asked to refresh. If ``uri_scheme`` doesn't match any
        current backend, nothing happens.
        :param uri_scheme: limit to the backend matching the URI scheme
        :type uri_scheme: string"""
        return await self.mopidy_request('core.playlists.refresh', uri_scheme=uri_scheme, **options)

    async def save(self, playlist, **options):
        """Save the playlist.
        For a playlist to be saveable, it must have the ``uri`` attribute set.
        You must not set the ``uri`` atribute yourself, but use playlist
        objects returned by :meth:`create` or retrieved from :attr:`playlists`,
        which will always give you saveable playlists.
        The method returns the saved playlist. The return playlist may differ
        from the saved playlist. E.g. if the playlist name was changed, the
        returned playlist may have a different URI. The caller of this method
        must throw away the playlist sent to this method, and use the
        returned playlist instead.
        If the playlist's URI isn't set or doesn't match the URI scheme of a
        current backend, nothing is done and :class:`None` is returned.
        :param playlist: the playlist
        :type playlist: :class:`mopidy.models.Playlist`
        :rtype: :class:`mopidy.models.Playlist` or :class:`None`"""
        return await self.mopidy_request('core.playlists.save', playlist=playlist, **options)

    
class TracklistController(_BaseController):

    # DEPRECATED The ``tracks`` argument. Use ``uris``.
    async def add(self, tracks=None, at_position=None, uris=None, **options):
        """Add tracks to the tracklist.
        If ``uris`` is given instead of ``tracks``, the URIs are
        looked up in the library and the resulting tracks are added to the
        tracklist.
        If ``at_position`` is given, the tracks are inserted at the given
        position in the tracklist. If ``at_position`` is not given, the tracks
        are appended to the end of the tracklist.
        Triggers the :meth:`mopidy.core.CoreListener.tracklist_changed` event.
        :param tracks: tracks to add
        :type tracks: list of :class:`mopidy.models.Track` or :class:`None`
        :param at_position: position in tracklist to add tracks
        :type at_position: int or :class:`None`
        :param uris: list of URIs for tracks to add
        :type uris: list of string or :class:`None`
        :rtype: list of :class:`mopidy.models.TlTrack`
        .. versionadded:: 1.0
            The ``uris`` argument.
        .. deprecated:: 1.0
            The ``tracks`` argument. Use ``uris``."""
        return await self.mopidy_request('core.tracklist.add', tracks=tracks, at_position=at_position, uris=uris, **options)

    async def clear(self, **options):
        """Clear the tracklist.
        Triggers the :meth:`mopidy.core.CoreListener.tracklist_changed` event."""
        return await self.mopidy_request('core.tracklist.clear', **options)

    # DEPRECATED Use :meth:`get_eot_tlid` instead.
    async def eot_track(self, tl_track, **options):
        """The track that will be played after the given track.
        Not necessarily the same track as :meth:`next_track`.
        .. deprecated:: 3.0
            Use :meth:`get_eot_tlid` instead.
        :param tl_track: the reference track
        :type tl_track: :class:`mopidy.models.TlTrack` or :class:`None`
        :rtype: :class:`mopidy.models.TlTrack` or :class:`None`"""
        return await self.mopidy_request('core.tracklist.eot_track', tl_track=tl_track, **options)

    async def filter(self, criteria, **options):
        """Filter the tracklist by the given criteria.
        Each rule in the criteria consists of a model field and a list of
        values to compare it against. If the model field matches any of the
        values, it may be returned.
        Only tracks that match all the given criteria are returned.
        Examples::
            # Returns tracks with TLIDs 1, 2, 3, or 4 (tracklist ID)
            filter({'tlid': [1, 2, 3, 4]})
            # Returns track with URIs 'xyz' or 'abc'
            filter({'uri': ['xyz', 'abc']})
            # Returns track with a matching TLIDs (1, 3 or 6) and a
            # matching URI ('xyz' or 'abc')
            filter({'tlid': [1, 3, 6], 'uri': ['xyz', 'abc']})
        :param criteria: one or more rules to match by
        :type criteria: dict, of (string, list) pairs
        :rtype: list of :class:`mopidy.models.TlTrack`"""
        return await self.mopidy_request('core.tracklist.filter', criteria=criteria, **options)

    async def get_consume(self, **options):
        """Get consume mode.
        :class:`True`
            Tracks are removed from the tracklist when they have been played.
        :class:`False`
            Tracks are not removed from the tracklist."""
        return await self.mopidy_request('core.tracklist.get_consume', **options)

    async def get_eot_tlid(self, **options):
        """The TLID of the track that will be played after the current track.
        Not necessarily the same TLID as returned by :meth:`get_next_tlid`.
        :rtype: :class:`int` or :class:`None`
        .. versionadded:: 1.1"""
        return await self.mopidy_request('core.tracklist.get_eot_tlid', **options)

    async def get_length(self, **options):
        """Get length of the tracklist."""
        return await self.mopidy_request('core.tracklist.get_length', **options)

    async def get_next_tlid(self, **options):
        """The tlid of the track that will be played if calling
        :meth:`mopidy.core.PlaybackController.next()`.
        For normal playback this is the next track in the tracklist. If repeat
        is enabled the next track can loop around the tracklist. When random is
        enabled this should be a random track, all tracks should be played once
        before the tracklist repeats.
        :rtype: :class:`int` or :class:`None`
        .. versionadded:: 1.1"""
        return await self.mopidy_request('core.tracklist.get_next_tlid', **options)

    async def get_previous_tlid(self, **options):
        """Returns the TLID of the track that will be played if calling
        :meth:`mopidy.core.PlaybackController.previous()`.
        For normal playback this is the previous track in the tracklist. If
        random and/or consume is enabled it should return the current track
        instead.
        :rtype: :class:`int` or :class:`None`
        .. versionadded:: 1.1"""
        return await self.mopidy_request('core.tracklist.get_previous_tlid', **options)

    async def get_random(self, **options):
        """Get random mode.
        :class:`True`
            Tracks are selected at random from the tracklist.
        :class:`False`
            Tracks are played in the order of the tracklist."""
        return await self.mopidy_request('core.tracklist.get_random', **options)

    async def get_repeat(self, **options):
        """Get repeat mode.
        :class:`True`
            The tracklist is played repeatedly.
        :class:`False`
            The tracklist is played once."""
        return await self.mopidy_request('core.tracklist.get_repeat', **options)

    async def get_single(self, **options):
        """Get single mode.
        :class:`True`
            Playback is stopped after current song, unless in ``repeat`` mode.
        :class:`False`
            Playback continues after current song."""
        return await self.mopidy_request('core.tracklist.get_single', **options)

    async def get_tl_tracks(self, **options):
        """Get tracklist as list of :class:`mopidy.models.TlTrack`."""
        return await self.mopidy_request('core.tracklist.get_tl_tracks', **options)

    async def get_tracks(self, **options):
        """Get tracklist as list of :class:`mopidy.models.Track`."""
        return await self.mopidy_request('core.tracklist.get_tracks', **options)

    async def get_version(self, **options):
        """Get the tracklist version.
        Integer which is increased every time the tracklist is changed. Is not
        reset before Mopidy is restarted."""
        return await self.mopidy_request('core.tracklist.get_version', **options)

    async def index(self, tl_track=None, tlid=None, **options):
        """The position of the given track in the tracklist.
        If neither *tl_track* or *tlid* is given we return the index of
        the currently playing track.
        :param tl_track: the track to find the index of
        :type tl_track: :class:`mopidy.models.TlTrack` or :class:`None`
        :param tlid: TLID of the track to find the index of
        :type tlid: :class:`int` or :class:`None`
        :rtype: :class:`int` or :class:`None`
        .. versionadded:: 1.1
            The *tlid* parameter"""
        return await self.mopidy_request('core.tracklist.index', tl_track=tl_track, tlid=tlid, **options)

    async def move(self, start, end, to_position, **options):
        """Move the tracks in the slice ``[start:end]`` to ``to_position``.
        Triggers the :meth:`mopidy.core.CoreListener.tracklist_changed` event.
        :param start: position of first track to move
        :type start: int
        :param end: position after last track to move
        :type end: int
        :param to_position: new position for the tracks
        :type to_position: int"""
        return await self.mopidy_request('core.tracklist.move', start=start, end=end, to_position=to_position, **options)

    # DEPRECATED Use :meth:`get_next_tlid` instead.
    async def next_track(self, tl_track, **options):
        """The track that will be played if calling
        :meth:`mopidy.core.PlaybackController.next()`.
        For normal playback this is the next track in the tracklist. If repeat
        is enabled the next track can loop around the tracklist. When random is
        enabled this should be a random track, all tracks should be played once
        before the tracklist repeats.
        .. deprecated:: 3.0
            Use :meth:`get_next_tlid` instead.
        :param tl_track: the reference track
        :type tl_track: :class:`mopidy.models.TlTrack` or :class:`None`
        :rtype: :class:`mopidy.models.TlTrack` or :class:`None`"""
        return await self.mopidy_request('core.tracklist.next_track', tl_track=tl_track, **options)

    # DEPRECATED Use :meth:`get_previous_tlid` instead.
    async def previous_track(self, tl_track, **options):
        """Returns the track that will be played if calling
        :meth:`mopidy.core.PlaybackController.previous()`.
        For normal playback this is the previous track in the tracklist. If
        random and/or consume is enabled it should return the current track
        instead.
        .. deprecated:: 3.0
            Use :meth:`get_previous_tlid` instead.
        :param tl_track: the reference track
        :type tl_track: :class:`mopidy.models.TlTrack` or :class:`None`
        :rtype: :class:`mopidy.models.TlTrack` or :class:`None`"""
        return await self.mopidy_request('core.tracklist.previous_track', tl_track=tl_track, **options)

    async def remove(self, criteria, **options):
        """Remove the matching tracks from the tracklist.
        Uses :meth:`filter()` to lookup the tracks to remove.
        Triggers the :meth:`mopidy.core.CoreListener.tracklist_changed` event.
        :param criteria: one or more rules to match by
        :type criteria: dict, of (string, list) pairs
        :rtype: list of :class:`mopidy.models.TlTrack` that were removed"""
        return await self.mopidy_request('core.tracklist.remove', criteria=criteria, **options)

    async def set_consume(self, value, **options):
        """Set consume mode.
        :class:`True`
            Tracks are removed from the tracklist when they have been played.
        :class:`False`
            Tracks are not removed from the tracklist."""
        return await self.mopidy_request('core.tracklist.set_consume', value=value, **options)

    async def set_random(self, value, **options):
        """Set random mode.
        :class:`True`
            Tracks are selected at random from the tracklist.
        :class:`False`
            Tracks are played in the order of the tracklist."""
        return await self.mopidy_request('core.tracklist.set_random', value=value, **options)

    async def set_repeat(self, value, **options):
        """Set repeat mode.
        To repeat a single track, set both ``repeat`` and ``single``.
        :class:`True`
            The tracklist is played repeatedly.
        :class:`False`
            The tracklist is played once."""
        return await self.mopidy_request('core.tracklist.set_repeat', value=value, **options)

    async def set_single(self, value, **options):
        """Set single mode.
        :class:`True`
            Playback is stopped after current song, unless in ``repeat`` mode.
        :class:`False`
            Playback continues after current song."""
        return await self.mopidy_request('core.tracklist.set_single', value=value, **options)

    async def shuffle(self, start=None, end=None, **options):
        """Shuffles the entire tracklist. If ``start`` and ``end`` is given only
        shuffles the slice ``[start:end]``.
        Triggers the :meth:`mopidy.core.CoreListener.tracklist_changed` event.
        :param start: position of first track to shuffle
        :type start: int or :class:`None`
        :param end: position after last track to shuffle
        :type end: int or :class:`None`"""
        return await self.mopidy_request('core.tracklist.shuffle', start=start, end=end, **options)

    async def slice(self, start, end, **options):
        """Returns a slice of the tracklist, limited by the given start and end
        positions.
        :param start: position of first track to include in slice
        :type start: int
        :param end: position after last track to include in slice
        :type end: int
        :rtype: :class:`mopidy.models.TlTrack`"""
        return await self.mopidy_request('core.tracklist.slice', start=start, end=end, **options)

    