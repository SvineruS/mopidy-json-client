import asyncio
import logging
from collections import defaultdict

import websockets

from . import mopidy_api
from .messages import RequestMessage, ResponseMessage

logger = logging.getLogger('mopidy_async_client')


class MopidyClient:

    def __init__(self, url='ws://localhost:6680/mopidy/ws', loop=None, parse_results=False,
                 reconnect_attempts=5, reconnect_timeout=20):

        self.listener = MopidyListener()

        self.core = mopidy_api.CoreController(self._request)
        self.playback = mopidy_api.PlaybackController(self._request)
        self.mixer = mopidy_api.MixerController(self._request)
        self.tracklist = mopidy_api.TracklistController(self._request)
        self.playlists = mopidy_api.PlaylistsController(self._request)
        self.library = mopidy_api.LibraryController(self._request)
        self.history = mopidy_api.HistoryController(self._request)

        #

        self.ws_url = url

        if loop is None:
            loop = asyncio.get_event_loop()
        self._loop = loop

        #

        self.wsa = None
        self._request_queue = []
        self._consumer_task = None

        self._reconnect_attempts = reconnect_attempts
        self._reconnect_timeout = reconnect_timeout

        ResponseMessage.set_settings(
            on_msg_event=self._dispatch_event,
            on_msg_result=self._dispatch_result,
            parse_results=parse_results
        )

    # Connection public functions

    async def connect(self):
        if self.is_connected():
            raise RuntimeWarning("Connection already open")
        self.wsa = await websockets.connect(self.ws_url, loop=self._loop)
        self._consumer_task = self._loop.create_task(self._ws_consumer())
        logger.info("Connected")
        return self

    async def disconnect(self):
        logger.info("Connection closed")
        if self.is_connected():
            await self.wsa.close()
        if self._consumer_task is not None:
            self._consumer_task.cancel()
        self._request_queue.clear()
        self._consumer_task = None
        self.wsa = None

    async def _reconnect(self):
        async def _reconnect_():
            await self.disconnect()
            for i in range(self._reconnect_attempts - 1):
                try:
                    logging.info(f"try to reconnect. attempt {i} / {self._reconnect_attempts}")
                    await self.connect()
                    return
                except OSError:
                    logging.info(f"reconnect failed. new attempt in {self._reconnect_timeout} sec")
                    await asyncio.sleep(self._reconnect_timeout)
            await self.connect()  # not catching last attempt

        self._loop.create_task(_reconnect_())  # this task will be closed so creating new one

    def is_connected(self):
        return self.wsa and self.wsa.open

    #

    async def _request(self, method, **kwargs):
        if not self.is_connected():
            raise RuntimeError("Connect before making requests!")

        request = RequestMessage(method, **kwargs)
        self._request_queue.append(request)

        try:
            logging.debug(f"sending request {request}")
            await self.wsa.send(request.to_json())
            return await request.wait_for_result()
        except websockets.ConnectionClosed:
            await self._reconnect()
            await self._request(method, **kwargs)
        except Exception as ex:
            logger.exception(ex)
            return None

    async def _ws_consumer(self):
        try:
            async for message in self.wsa:
                try:
                    await ResponseMessage.parse_json_message(message)
                except Exception as ex:
                    logger.exception(ex)
        except websockets.ConnectionClosed:
            await self._reconnect()

    async def _dispatch_result(self, id_msg, result):
        for request in self._request_queue:
            if request.id_msg == id_msg:
                self._loop.create_task(request.unlock(result))
                self._request_queue.remove(request)
                return

    async def _dispatch_event(self, event, event_data):
        # noinspection PyProtectedMember
        self._loop.create_task(self.listener._on_event(event, event_data))

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
        'audio_message',  # extra event for gstreamer plugins like spectrum
        '*'  # all events
    )

    def __init__(self):
        self.bindings = defaultdict(list)

    async def _on_event(self, event, event_data):
        logger.debug(f"event {event} happened")
        for callback in self.bindings[event]:
            await callback(event_data)
        for callback in self.bindings['*']:
            await callback(event, event_data)

    def bind(self, event, callback):
        assert event in self.EVENTS, 'Event {} does not exist'.format(event)
        if callback not in self.bindings[event]:
            self.bindings[event].append(callback)

    def unbind(self, event, callback):
        for index, cb in enumerate(self.bindings[event]):
            if cb == callback:
                self.bindings[event].pop(index)
                return

    def clear(self):
        self.bindings = {}
