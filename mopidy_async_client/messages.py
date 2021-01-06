import asyncio
import json
from itertools import count


class RequestMessage(object):
    msg_counter = count(0)

    def __init__(self, method, timeout=20, **params):
        self.id_msg = next(self.msg_counter)
        self.method = method
        self.params = params

        self._timeout = timeout
        self._on_result_event = asyncio.Event()
        self._result = None

    async def unlock(self, result):
        self._result = result
        self._on_result_event.set()

    async def wait_for_result(self):
        await asyncio.wait_for(
            self._on_result_event.wait(),
            self._timeout
        )
        return self._result

    def to_json(self):
        return json.dumps({
            'jsonrpc': '2.0',
            'id': self.id_msg,
            'method': self.method,
            'params': self.params
        })

    def __str__(self):
        return f"<RequestMessage id:{self.id_msg} method:'{self.method}' params:{self.params}>"


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
                raise ImportError("if you want to parse results pls install mopidy (pip install mopidy)")

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



