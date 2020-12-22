import asyncio
import time
import json
from itertools import count


class RequestTimeoutError(Exception):
    def __init__(self, method, timeout, *args):
        super(RequestTimeoutError, self).__init__(*args)
        self.method = method
        self.timeout = timeout

    def __repr__(self):
        return '[TIMEOUT] On request: {0} ({1:d} secs)'.format(self.method, self.timeout)


class RequestMessage(object):
    msg_counter = count(0)

    def __init__(self, method, on_result=None, timeout=20, **params):
        self.id_msg = next(self.msg_counter)
        self.method = method
        self.params = params
        self.callback = on_result if on_result else self.unlock

        self._locked = False if on_result or not timeout else True
        self._start_time = time.time()
        self._timeout = timeout

        self.result = None
        self.json_message = self.compose_json_msg()

    async def unlock(self, result):
        self.result = result
        self._locked = False

    def compose_json_msg(self):
        return json.dumps({
            'jsonrpc': '2.0',
            'id': self.id_msg,
            'method': self.method,
            'params': self.params
        })

    async def wait_for_result(self):
        while self._locked:
            if time.time() - self._start_time > self._timeout:
                raise RequestTimeoutError(self.method, self._timeout)
            await asyncio.sleep(0.1)
        return self.result

    def __repr__(self):
        return "<RequestMessage id:{0.id_msg} method:'{0.method}'>".format(self)


class ResponseMessage(object):
    _on_event = None
    _on_result = None
    _decoder = None

    @classmethod
    def set_settings(cls, on_msg_event=None, on_msg_result=None, parse_results=False):
        cls._on_event = on_msg_event
        cls._on_result = on_msg_result

        if parse_results:
            try:
                from mopidy import models
                cls._decoder = models.model_json_decoder
            except ImportError:
                raise Exception("if you want to parse results pls install mopidy (pip install mopidy)")

    @classmethod
    async def parse_json_message(cls, message):
        msg_data = json.loads(message, object_hook=cls._decoder)

        if 'jsonrpc' in msg_data:
            return await cls._json_message(msg_data)
        if 'event' in msg_data:
            return await cls._event_message(msg_data)

    @classmethod
    async def _json_message(cls, msg_data):
        assert msg_data['jsonrpc'] == '2.0', 'Wrong JSON-RPC version: %s' % msg_data['jsonrpc']
        assert 'id' in msg_data, 'JSON-RPC message has no id'

        msg_id = msg_data.get('id')
        error_data = msg_data.get('error')
        result_data = msg_data.get('result')

        if error_data:
            return await cls._on_result(id_msg=msg_id, result=error_data)
        await cls._on_result(id_msg=msg_id, result=result_data)

    @classmethod
    async def _event_message(cls, msg_data):
        if cls._on_event:
            event = msg_data.pop('event')
            await cls._on_event(event=event, event_data=msg_data)



