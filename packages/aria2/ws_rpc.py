import asyncio
import json
from typing import Callable, NoReturn, Dict
from typing_extensions import Literal
import functools
import websockets
from websockets.legacy.protocol import WebSocketCommonProtocol
from .rpc import Aria2RPC, GID
from .options import Options


Aria2RPCNotificationEvent = Literal[
    'download_start',
    'download_pause',
    'download_stop',
    'download_complete',
    'download_error',
    'bt_download_complete',
]

Aria2RPCNotificationMessageMethod = Literal[
    'aria2.onDownloadStart',
    'aria2.onDownloadPause',
    'aria2.onDownloadStop',
    'aria2.onDownloadComplete',
    'aria2.onDownloadError',
    'arai2.onBtDownloadComplete',
]

Aria2RPCWebsocketMessageHandler = Callable[[GID], NoReturn]

Aria2RPCWebsocketMessageHandlers = Dict[Aria2RPCNotificationEvent, Aria2RPCWebsocketMessageHandler]

message_method_to_event_name_map: Dict[Aria2RPCNotificationMessageMethod, Aria2RPCNotificationEvent] = {
    'aria2.onDownloadStart': 'download_start',
    'aria2.onDownloadPause': 'download_pause',
    'aria2.onDownloadStop': 'download_stop',
    'aria2.onDownloadComplete': 'download_complete',
    'aria2.onDownloadError': 'download_error',
    'arai2.onBtDownloadComplete': 'bt_download_complete',
}


async def on_message(websocket: WebSocketCommonProtocol, message_queue: asyncio.Queue, handlers: Aria2RPCWebsocketMessageHandlers):
    try:
        while True:
            message = json.loads(await websocket.recv())

            # If `id` is not `None`, the message should be the reponse of a request.
            if message.get('id') is not None:
                await message_queue.put(message)

            # Otherwise the message should be a notification
            else:
                event = message_method_to_event_name_map.get(message.get('method'))
                if event:
                    for handler in handlers[event]:
                        handler(message['params'][0]['gid'])

    except asyncio.CancelledError:
        pass


class WSAria2RPC(Aria2RPC):
    def __init__(
        self,
        uri: str,
        secret = '',
        options: Options = None,
        on_download_start: Aria2RPCWebsocketMessageHandler = None,
        on_download_complete: Aria2RPCWebsocketMessageHandler = None,
        on_download_pause: Aria2RPCWebsocketMessageHandler = None,
        on_download_stop: Aria2RPCWebsocketMessageHandler = None,
        on_download_error: Aria2RPCWebsocketMessageHandler = None,
        on_bt_download_complete: Aria2RPCWebsocketMessageHandler = None,
    ):
        super().__init__(secret=secret, options=options)
        self.uri = uri
        self.websocket: WebSocketCommonProtocol = None
        self._on_message_task: asyncio.Task = None
        self._message_queue = asyncio.Queue()
        self._handlers = {
            'download_start': [on_download_start] if on_download_start else [],
            'download_complete': [on_download_complete] if on_download_complete else [],
            'download_pause': [on_download_pause] if on_download_pause else [],
            'download_stop': [on_download_stop] if on_download_stop else [],
            'download_error': [on_download_error] if on_download_error else [],
            'bt_download_complete': [on_bt_download_complete] if on_bt_download_complete else [],
        }
        self._id = 0
        
    def add_handler(self, event: Aria2RPCNotificationEvent, handler: Aria2RPCWebsocketMessageHandler):
        self._handlers[event].append(handler)

    async def request(self, payload):
        self._id += 1

        # Intercept the request and set the jsonrpc `id`
        payload['id'] = self._id

        # Send request
        await self.websocket.send(json.dumps(payload))
        
        while True:
            message = await self._message_queue.get()
            
            # Check if `id` matches
            if message['id'] == payload['id']:
                return message
            
            # If `id` does not match, the message should be the response of some other request 
            self._message_queue.put(message)

    async def __aenter__(self):
        self.websocket = await websockets.connect(
            self.uri,
            ping_interval = None,
            close_timeout = 10,
        )
        self._on_message_task = asyncio.create_task(on_message(self.websocket, self._message_queue, self._handlers))
        return self

    async def __aexit__(self, exe_type, exc, tb):
        if self._on_message_task: self._on_message_task.cancel()
        asyncio.create_task(self.websocket.close()).add_done_callback(functools.partial(print, 'websocket closed'))
