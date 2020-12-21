import asyncio
import logging

import websockets

from . import mopidy_api
from .messages import RequestMessage, ResponseMessage


logger = logging.getLogger('mopidy_async_client')


class MopidyClient:

    def __init__(self, ws_url='ws://localhost:6680/mopidy/ws', loop=None):

        self.listener = MopidyListener()

        self.core = mopidy_api.CoreController(self._request)
        self.playback = mopidy_api.PlaybackController(self._request)
        self.mixer = mopidy_api.MixerController(self._request)
        self.tracklist = mopidy_api.TracklistController(self._request)
        self.playlists = mopidy_api.PlaylistsController(self._request)
        self.library = mopidy_api.LibraryController(self._request)
        self.history = mopidy_api.HistoryController(self._request)

        #

        self.ws_url = ws_url

        if loop is None:
            loop = asyncio.get_event_loop()
        self._loop = loop

        #

        self.wsa = None
        self._request_queue = []
        self._connected = False
        self._consumer_task = None

        ResponseMessage.set_handlers(
            on_msg_event=self._dispatch_event,
            on_msg_result=self._dispatch_result
        )

    # Connection public functions

    async def connect(self):
        if self.wsa:
            raise Exception("Connection already open")
        self.wsa = await websockets.connect(self.ws_url, loop=self._loop)
        self._consumer_task = self._loop.create_task(self._ws_consumer())
        return self

    async def disconnect(self):
        self._consumer_task.cancel()
        await self.wsa.close()
        self.wsa = None

    #

    async def _request(self, method, **kwargs):
        request = RequestMessage(method, **kwargs)
        self._request_queue.append(request)

        try:
            await self.wsa.send(request.json_message)
            return await request.wait_for_result()
        except Exception as ex:
            logger.exception(ex)
            return None

    async def _ws_consumer(self):
        async for message in self.wsa:
            try:
                await ResponseMessage.parse_json_message(message)
            except Exception as ex:
                logger.exception(ex)

    async def _dispatch_result(self, id_msg, result):
        for request in self._request_queue:
            if request.id_msg == id_msg:
                await request.callback(result)
                self._request_queue.remove(request)
                return

    async def _dispatch_event(self, event, event_data):
        await self.listener.on_event(event, **event_data)

    async def __aenter__(self):
        return await self.connect()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.disconnect()


class MopidyListener:
    EVENTS = (
       'track_playback_paused',
       'track_playback_resumed',
       'track_playback_started',
       'track_playback_ended',
       'playback_state_changed',
       'tracklist_changed',
       'playlists_loaded',
       'playlist_changed',
       'playlist_deleted',
       'options_changed',
       'volume_changed',
       'mute_changed',
       'seeked',
       'stream_title_changed',
       'audio_message'  # extra event for gstreamer plugins like spectrum
    )

    def __init__(self):
        self.bindings = {}

    async def on_event(self, event, **event_data):
        if event in self.bindings:
            for callback in self.bindings[event]:
                await callback(**event_data)

    def bind(self, event, callback):
        assert event in self.EVENTS, 'Event {} does not exist'.format(event)
        if event not in self.bindings:
            self.bindings[event] = []

        if callback not in self.bindings[event]:
            self.bindings[event].append(callback)

    def unbind(self, event, callback):
        if event not in self.bindings:
            return
        for index, cb in enumerate(self.bindings[event]):
            if cb == callback:
                self.bindings[event].pop(index)
                return

    def clear(self):
        self.bindings = {}
