from typing import Callable, Union

from BaseBot import Bot
from States import NonState
from Subscribes import Any, Nany


class Handler:
    def __init__(self, bot: Bot):
        self.bot = bot
        self.subscribes = set()
        self.state = {
            None: NonState
        }

    def __del__(self):
        self._on_destroy()

    def _on_destroy(self):
        map(lambda subs_type: self.bot._handler_unsubscribe(self, subs_type), self.subscribes)

    def subscribe(self, subs_type: Union[Any, Nany], callback: Callable):
        self.subscribes.add(subs_type)
        self.bot._handler_subscribe(self, subs_type, callback)

    def unsubscribe(self, subs_type: Union[Any, Nany]):
        self.subscribes.discard(subs_type)
        self.bot._handler_unsubscribe(self, subs_type)

    def on_state_changed(self, new):
        self.state[new].enter()

    def lazy_init(self):
        pass
