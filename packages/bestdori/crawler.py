import asyncio
import os
from typing import Dict, Union
from aiohttp import ClientSession
from motor.motor_asyncio import AsyncIOMotorClient
from packages.aria2.options import Options
from packages.aria2.ws_rpc import WSAria2RPC
from utils.logger import Logger
from .models import Card
from .helpers import get_asset_urls_from_metadata


class Crawler:
    def __init__(
        self,
        session: ClientSession,
        aria2rpc: WSAria2RPC,
        mongo: AsyncIOMotorClient,
        asset_dir: str,
        logger: Logger,
    ) -> None:
        self.session = session
        self.aria2rpc = aria2rpc
        self.mongo = mongo
        self.asset_dir = asset_dir
        self.logger = logger

    async def fetch_all_cards_metadata(self):
        res = await self.session.get('https://bestdori.com/api/cards/all.5.json')
        all_cards_metadata: Dict[int, Card] = await res.json()
        await self.mongo.bestdori.all.insert_one({'cards': all_cards_metadata})
        return all_cards_metadata

    async def fetch_metadata(self, id: int, save_to_mongo=True) -> Card:
        res = await self.session.get(f'https://bestdori.com/api/cards/{id}.json')
        metadata = {'id': id, **(await res.json())}
        if save_to_mongo: await self.mongo.bestdori.card.insert_one(metadata)
        return Card(**metadata)

    async def load_metadata(self, id: int) -> Card:
        metadata = await self.mongo.bestdori.card.find_one({'id': id})
        if not metadata:
            return await self.fetch_metadata(id)
        return Card(**metadata)

    async def download_asset(self, url: str, filename: str, overwrite=False, subdir=''):
        if os.path.isfile(os.path.join(self.asset_dir, subdir, filename)) and not overwrite:
            self.logger.info(f'{url} already exists')
            return
        
        await self.aria2rpc.add_uri([url], Options(
            out = filename,
            dir = os.path.abspath(os.path.join(self.asset_dir, subdir)),
        ))

        return filename
 
    async def download_assets(self, id_or_metadata: Union[int, Card], overwrite=False):
        metadata = await self.load_metadata(id_or_metadata) if isinstance(id_or_metadata, int) else id_or_metadata

        resource_set_name = metadata.resource_set_name

        urls = get_asset_urls_from_metadata(metadata)

        await asyncio.gather(*[
            self.download_asset(urls['card_normal'], f'{resource_set_name}_card_normal.png', overwrite),
            self.download_asset(urls['icon_normal'], f'{resource_set_name}_normal.png', overwrite, 'thumb'),
        ])

        if metadata.rarity > 2:
            await asyncio.gather(*[
                self.download_asset(urls['card_after_training'], f'{resource_set_name}_card_after_training.png', overwrite),
                self.download_asset(urls['icon_after_training'], f'{resource_set_name}_after_training.png', overwrite, 'thumb'),
            ])
        