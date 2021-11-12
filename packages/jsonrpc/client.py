import asyncio
import json
from typing import Iterable, Any, Callable, Union, Dict
import websockets
from websockets.legacy.protocol import WebSocketCommonProtocol
import functools


async def on_message(websocket: WebSocketCommonProtocol, message_queue: asyncio.Queue, handlers: Dict[str, Callable]):
    try:
        while True:
            message = json.loads(await websocket.recv())

            # If `id` is not `None`, the message should be the response of a request.
            if message.get('id') is not None:
                await message_queue.put(message)

            # Otherwise the message should be a notification
            else:
                method = message.get('method')
                if method and method in handlers:
                    for handler in handlers[method]:
                        handler(message)

    except asyncio.CancelledError:
        pass


class WebsocketJSONRPC:
    def __init__(
        self,
        uri: str,
    ) -> None:
        self.uri = uri
        self._websocket: WebSocketCommonProtocol = None
        self._on_message_task: asyncio.Task = None
        self._message_queue = asyncio.Queue()
        self._handlers = {}

    async def request(self, payload):
        await self._websocket.send(json.dumps(payload))
        
        while True:
            message = await self._message_queue.get()
            
            # Check if `id` matches
            if message['id'] == payload['id']:
                return message
            
            # If `id` does not match, the message should be the response of some other request 
            self._message_queue.put(message)
 
    def add_notification_handler(self, method: str, handler: Callable):
        if method not in self._handlers:
            self._handlers[method] = []
        self._handlers[method].append(handler)

    def remove_notification_handler(self, method: str, handler: Callable):
        if method in self._handlers and handler in self._handlers[method]:
            self._handlers[method].remove(handler)

    async def __aenter__(self):
        self._websocket = await websockets.connect(
            self.uri,
            ping_interval = None,
            close_timeout = 10,
        )
        self._on_message_task = asyncio.create_task(on_message(self._websocket, self._message_queue, self._handlers))
        return self

    async def __aexit__(self, exe_type, exc, tb):
        if self._on_message_task: self._on_message_task.cancel()
        asyncio.create_task(self._websocket.close()).add_done_callback(functools.partial(print, 'websocket closed'))