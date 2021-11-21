from typing import Callable, NoReturn, Dict, Union
from typing_extensions import Literal
from .rpc import Aria2RPC, GID
from .options import Options
from ..jsonrpc import WebsocketJSONRPC


Aria2Event = Literal[
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

Aria2EventHandler = Callable[[GID], NoReturn]

Aria2RPCWebsocketMessageHandlers = Dict[Aria2Event, Aria2EventHandler]

event_to_method_map: Dict[Aria2Event, Aria2RPCNotificationMessageMethod] = {
    'download_start': 'aria2.onDownloadStart',
    'download_pause': 'aria2.onDownloadPause',
    'download_stop': 'aria2.onDownloadStop',
    'download_complete': 'aria2.onDownloadComplete',
    'download_error': 'aria2.onDownloadError',
    'bt_download_complete': 'arai2.onBtDownloadComplete',
}


def wrap_aria2_event_handler(handler: Aria2EventHandler):
    def notification_handler(notification: Dict):
        return handler(notification['params'][0]['gid'])
    
    return notification_handler


class WSAria2RPC(WebsocketJSONRPC, Aria2RPC):
    def __init__(
        self,
        uri: str,
        secret = '',
        options: Options = None,
        initial_id: Union[str, int] = None,
        id_generator: Callable[[Union[str, int], Dict], Union[str, int]] = None,
        on_download_start: Aria2EventHandler = None,
        on_download_complete: Aria2EventHandler = None,
        on_download_pause: Aria2EventHandler = None,
        on_download_stop: Aria2EventHandler = None,
        on_download_error: Aria2EventHandler = None,
        on_bt_download_complete: Aria2EventHandler = None,
    ):
        WebsocketJSONRPC.__init__(self, uri=uri)
        Aria2RPC.__init__(self, secret=secret, options=options, initial_id=initial_id, id_generator=id_generator)
        self._handlers = {
            'aria2.onDownloadStart': [wrap_aria2_event_handler(on_download_start)] if on_download_start else [],
            'aria2.onDownloadPause': [wrap_aria2_event_handler(on_download_pause)] if on_download_pause else [],
            'aria2.onDownloadStop': [wrap_aria2_event_handler(on_download_stop)] if on_download_stop else [],
            'aria2.onDownloadComplete': [wrap_aria2_event_handler(on_download_complete)] if on_download_complete else [],
            'aria2.onDownloadError': [wrap_aria2_event_handler(on_download_error)] if on_download_error else [],
            'aria2.onBtDownloadComplete': [wrap_aria2_event_handler(on_bt_download_complete)] if on_bt_download_complete else [],
        }
        
    def add_event_listener(self, event: Aria2Event, handler: Aria2EventHandler):
        self.add_notification_handler(event_to_method_map[event], wrap_aria2_event_handler(handler))

