import os
import asyncio
import aiohttp
from motor.motor_asyncio import AsyncIOMotorClient
from packages.bestdori.crawler import Crawler
from packages.aria2.options import Options
from packages.aria2.ws_rpc import WSAria2RPC
from crawlers.Logger import Logger


async def main():
    async with \
            aiohttp.ClientSession() as session, \
            WSAria2RPC(
                uri = os.environ.get('ARIA2RPC_URI') or 'ws://localhost:6800/jsonrpc',
                options = Options(
                    https_proxy = os.environ.get('https_proxy'),
                ).dict(exclude_unset=True, exclude_none=True, by_alias=True),
                on_download_start = lambda gid: print('🚀 download_start', gid),
                on_download_complete = lambda gid: print('✅ download_complete', gid),
            ) as aria2rpc:

        crawler = Crawler(
            session = session,
            aria2rpc = aria2rpc,
            mongo = AsyncIOMotorClient(os.environ.get('MONGO_URI') or 'mongodb://localhost:27017'),
            asset_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'tmp')),
            logger = Logger(),
        )

        await crawler.download_assets(1)

try:
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
except KeyboardInterrupt:
    print('exit')
