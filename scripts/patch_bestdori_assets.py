import os
import sys
import argparse
import asyncio
from typing import Awaitable
import aiohttp
from motor.motor_asyncio import AsyncIOMotorClient
from packages.bestdori import Crawler
from packages.aria2 import Options, WSAria2RPC
from utils.logger import Logger
from flow_controller import FlowController

directory = os.path.dirname(__file__)

parser = argparse.ArgumentParser(description='patcher for Bestdori assets')
parser.add_argument('-d', '--datapath', type=str, help='static resource path', default=os.path.abspath(os.path.join(directory, 'assets', 'images')))
parser.add_argument('-w', '--watch', help='if enabled, the patch process will keep running to receive notification push', default=False, action='store_true')


async def watch(task: Awaitable):
    hasStarted = False
    while True:
        if not hasStarted:
            hasStarted = True
            await task()
        await asyncio.sleep(1)


async def main(args):
    async with \
        aiohttp.ClientSession(
            connector = aiohttp.TCPConnector(
                limit = 30,
                limit_per_host = 10,
            ),
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36',
            },
            trace_configs=[
                FlowController(
                    interval = (1, 2),
                ),
            ],
        ) as session, \
        WSAria2RPC(
            uri = os.environ.get('ARIA2RPC_URI') or 'ws://localhost:6800/jsonrpc',
            options = Options(
                https_proxy = os.environ.get('https_proxy'),
                header = [
                    'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36',
                ],
            ),
        ) as aria2rpc:
            logger = Logger('bestdori-crawler')
            crawler = Crawler(
                session = session,
                aria2rpc = aria2rpc,
                mongo = AsyncIOMotorClient(os.environ.get('MONGO_URI') or 'mongodb://localhost:27017'),
                asset_dir = args.datapath,
                logger = logger,
                # on_asset_download_start = (lambda info: logger.info('🚀 download start', info.filename)) if args.watch else None,
                on_asset_download_complete = (lambda info: logger.info('✅ download complete', info.filename)) if args.watch else None,
                on_asset_download_error = (lambda info: logger.error(f'❌ download error', info.filename)) if args.watch else None,
            )

            async def task():
                card_diffs = await crawler.diff_card()
                logger.info(f'{len(card_diffs)} diffs found')
                for id in card_diffs[:2]:
                    logger.info(f'process card {id}')
                    await crawler.download_card_assets(id)
                    logger.info(f'assets of card {id} has been added to downloading queue')

            if args.watch:
                await watch(task)
            else:
                await task()


if __name__ == '__main__':
    if sys.platform == 'win32':
        os.system('cls')

    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main(parser.parse_args()))
    except KeyboardInterrupt:
        print('bye')

