import os
import asyncio
from packages.aria2 import Options, WSAria2RPC


async def main():
    async with WSAria2RPC(
        uri = os.environ.get('ARIA2RPC_URI') or 'ws://localhost:6800/jsonrpc',
        secret = os.environ.get('ARIA2RPC_SECRET') or '',
        on_download_start = lambda gid: print('🚀 download_start', gid),
        on_download_complete = lambda gid: print('✅ download_complete', gid),
    ) as aria2rpc:
        hasDownloaded = False
        while True:
            if not hasDownloaded:
                hasDownloaded = True
                gid = await aria2rpc.add_uri(
                    ['https://www.baidu.com'],
                    Options(
                        dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'tmp')),
                    ),
                )
                files = await aria2rpc.get_files(gid=gid)
                actives = await aria2rpc.tell_active()
                version = await aria2rpc.get_version()
                print(gid, files, actives, version)
            await asyncio.sleep(1)

try:
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
except KeyboardInterrupt:
    print('exit')