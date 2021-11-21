import os
import sys

if sys.platform == 'win32':
    os.system('cls')

import asyncio
import aiohttp
from motor.motor_asyncio import AsyncIOMotorClient
from packages.bestdori import Crawler, get_gacha_during_event
from packages.aria2 import Options, WSAria2RPC
from utils.logger import Logger


async def main():
    async with \
            aiohttp.ClientSession() as session, \
            WSAria2RPC(
                uri = os.environ.get('ARIA2RPC_URI') or 'ws://localhost:6800/jsonrpc',
                options = Options(
                    https_proxy = os.environ.get('https_proxy'),
                    header = [
                        'user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36',
                    ],
                ),
                on_download_start = lambda gid: print('🚀 download_start', gid),
                on_download_complete = lambda gid: print('✅ download_complete', gid),
            ) as aria2rpc:

        crawler = Crawler(
            session = session,
            aria2rpc = aria2rpc,
            mongo = AsyncIOMotorClient(os.environ.get('MONGO_URI') or 'mongodb://localhost:27017'),
            asset_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'tmp')),
            logger = Logger('bestdori-crawler'),
        )
        hasDownloaded = False
        while True:
            if not hasDownloaded:
                hasDownloaded = True
                # await crawler.download_card_assets(502)
                # await crawler.download_gacha_assets(1)
                # await crawler.download_event_assets(1)
                events = await crawler.fetch_all_events_metadata()
                gachas = await crawler.fetch_all_gachas_metadata()
                event = events[1]
                index = 0
                print(event.event_name[index])
                for gacha in get_gacha_during_event(event, gachas, 'jp').values():
                    print(gacha.gacha_name[index])
            await asyncio.sleep(1)

try:
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
except KeyboardInterrupt:
    print('exit')
