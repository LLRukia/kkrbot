import asyncio
import random
import time
from types import SimpleNamespace
from typing import Union, List, Tuple
import aiohttp
from aiohttp import ClientSession, TraceRequestStartParams, TraceRequestEndParams

Number = Union[int, float]


class FlowController(aiohttp.TraceConfig):
    def __init__(self,
        interval: Union[Number, List[Number], Tuple[Number, Number]] = 1,
        ctx_key = 'host',
    ):
        super().__init__()
        self.interval = interval
        self.ctx_key = ctx_key
        self.store = {}

        self.on_request_start.append(self.__on_request_start)
        self.on_request_end.append(self.__on_request_end)

    def _get_key(self, trace_config_ctx: SimpleNamespace, params: Union[TraceRequestStartParams, TraceRequestEndParams]):
        key = trace_config_ctx.trace_request_ctx and trace_config_ctx.trace_request_ctx.get(self.ctx_key)
        return key or params.url.host

    async def __on_request_start(self, session: ClientSession, trace_config_ctx: SimpleNamespace, params: TraceRequestStartParams):
        key = self._get_key(trace_config_ctx, params)

        if key:
            if not self.store.get(key):
                self.store[key] = {
                    'last_start_time': time.time(),
                    'last_end_time': None,
                }
            else:
                interval = self.interval if isinstance(self.interval, (int, float)) else random.uniform(*self.interval)
                start_time = time.time()
                while True:
                    store = self.store[key]
                    if store.get('last_end_time') and store.get('last_start_time') < store.get('last_end_time') and store.get('last_end_time') + interval < time.time():
                        store['last_start_time'] = time.time()
                        break

                    # set max interval, avoid endless loop on some condition when error occurs
                    if time.time() - start_time > 10 * interval:
                        print(f'warning: "{key}" store may not be set properly (url: {params.url})')
                        store['last_start_time'] = time.time()
                        break

                    await asyncio.sleep(min(1, interval / 5))

    async def __on_request_end(self, session: ClientSession, trace_config_ctx: SimpleNamespace, params: TraceRequestEndParams):
        key = self._get_key(trace_config_ctx, params)
        if key:
            assert self.store[key] is not None
            self.store[key]['last_end_time'] = time.time()

