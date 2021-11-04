from MsgTypes import PrivateMsg, GroupMsg
from Timer import Timer
from collections import defaultdict


class Bot:
    def get_bind_dict(self):
        raise NotImplementedError

    def __init__(self, server):
        self.server = server
        self.logger = self.server.logger
        self.handlers = set()
        self._handler_callbacks = defaultdict(dict)
        self.init_subscribe()

    def init_subscribe(self):
        for e, f in self.get_bind_dict().items():
            self.logger.info('init_subscribe %s: %s', e, f)
            self.server.subscribe(e, f)

    def __del__(self):
        self._on_destroy()

    def _on_destroy(self):
        self.clear_subscribes()

    def add_timer(self, time, func, async_cb=True):
        return Timer(time, func, False, async_cb)

    def add_repeat_timer(self, time, func, async_cb=True):
        return Timer(time, func, True, async_cb)

    def clear_subscribes(self):
        for e, f in self.get_bind_dict().items():
            self.server.unsubscribe(e, f)

    def remove_handler(self, handler):
        if handler not in self.handlers:
            raise RuntimeError('Trying to remove a handler which has not been registered')
        # If this handler referenced by other, it will not call Handler._on_destroy, and may cause errors
        # so DO NOT reference handler except here
        self.handlers.remove(handler)

    def add_handler(self, handler):
        if handler in self.handlers:
            raise RuntimeError('Duplicated add handler')
        self.handlers.add(handler)

    def start(self):
        for handler in self.handlers:
            handler.start()

    def _handler_subscribe(self, handler, subs_type, callback):
        if handler not in self.handlers:
            raise RuntimeError('Trying to subscribe with a handler which is not registered')
        self._handler_callbacks[handler][subs_type] = callback

    def _handler_unsubscribe(self, handler, subs_type):
        if self._handler_callbacks[handler].pop(subs_type, None) is None:
            self.logger.error('Bad handler unsubscribe: %s', subs_type.__class__.__name__)

    async def send_msg_with_context(self, context, msg):
        await self.server.send(context, message=msg.get())
        return {}

    async def send_private_msg(self, user_id, msg):
        await self.server.send_msg(**PrivateMsg(user_id, msg).get())
        return {}

    async def send_group_msg(self, group_id, msg):
        await self.server.send_msg(**GroupMsg(group_id, msg).get())
        return {}
