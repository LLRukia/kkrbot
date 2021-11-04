import asyncio
import logging

_logger = logging.getLogger('quart.app')

class Timer:
    def __init__(self, timeout, callback, repeat=False, async_cb=True):
        self._timeout = timeout
        self._callback = callback
        self._task = asyncio.ensure_future(self._job())
        self._repeat = repeat
        self._async = async_cb

    async def _job(self):
        await asyncio.sleep(self._timeout)
        try:
            if self._async:
                await self._callback()
            else:
                self._callback()
        except Exception as e:
            _logger.error('when callback, error occured. %s', e)
        if self._repeat:
            self._task = asyncio.ensure_future(self._job(), loop=asyncio.get_event_loop())

    def cancel(self):
        self._task.cancel()
