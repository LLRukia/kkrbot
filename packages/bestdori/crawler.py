import os
from typing import Dict, Union
from aiohttp import ClientSession
from motor.motor_asyncio import AsyncIOMotorClient
from packages.aria2.ws_rpc import WSAria2RPC
from crawlers.Logger import Logger
from .models import Card


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
        all_cards_metadata_by_dict: Dict[int, Card] = await res.json()
        all_card_metadata_by_list = [{'id': int(id_), **card} for id_, card in all_cards_metadata_by_dict.items()]
        await self.mongo.bestdori.card.insert_many(all_card_metadata_by_list)
        return all_card_metadata_by_list

    async def fetch_metadata(self, id: int, save_to_mongo=True):
        res = await self.session.get(f'https://bestdori.com/api/cards/{id}.json')
        metadata = {'id': id, **await res.json()}
        if save_to_mongo: await self.mongo.bestdori.card.insert_one(metadata)
        return metadata

    async def load_metadata(self, id: int):
        metadata = await self.mongo.bestdori.card.find_one({'id': id})
        if not metadata:
            return await self.fetch_metadata(id)
        return metadata

    async def download_asset(self, url: str, filename: str, overwrite=False, subdir=''):
        if os.path.isfile(os.path.join(self.asset_dir, subdir, filename)) and not overwrite:
            self.logger.info(f'{url} already exists')
            return
        
        return await self.aria2rpc.addUri([url], {
            'out': filename,
            'dir': os.path.abspath(os.path.join(self.asset_dir, subdir)),
        })
 
    async def download_assets(self, id_or_metadata: Union[int, Card], overwrite=False):
        metadata = Card(**(await self.load_metadata(id_or_metadata) if isinstance(id_or_metadata, int) else id_or_metadata))
        id_ = metadata.id

        resource_set_name = metadata.resource_set_name

        # Cards
        card_normal = f'https://bestdori.com/assets/jp/characters/resourceset/{resource_set_name}_rip/card_normal.png'
        card_after_training = f'https://bestdori.com/assets/jp/characters/resourceset/{resource_set_name}_rip/card_after_training.png'

        # Icons
        temp = str(id_ // 50)
        s = '0' * (5 - len(temp)) + temp
        icon_normal = f'https://bestdori.com/assets/jp/thumb/chara/card{s}_rip/{resource_set_name}_normal.png'
        icon_after_training = f'https://bestdori.com/assets/jp/thumb/chara/card{s}_rip/{resource_set_name}_after_training.png'

        await self.download_asset(card_normal, f'{resource_set_name}_card_normal.png', overwrite)
        await self.download_asset(icon_normal, f'{resource_set_name}_normal.png', overwrite, 'thumb')

        if metadata.rarity > 2:
            await self.download_asset(card_after_training, f'{resource_set_name}_card_after_training.png', overwrite)
            await self.download_asset(icon_after_training, f'{resource_set_name}_after_training.png', overwrite, 'thumb')
        