import asyncio
import os
from typing import Dict, Union
from aiohttp import ClientSession
from motor.motor_asyncio import AsyncIOMotorClient
from packages.aria2.options import Options
from packages.aria2.ws_rpc import WSAria2RPC
from utils.logger import Logger
from .models import Card, PartialCard, PartialCharacter, PartialEvent, PartialGacha, PartialBand, PartialSkill
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

    async def fetch_all_cards_metadata(self) -> Dict[int, PartialCard]:
        res = await self.session.get('https://bestdori.com/api/cards/all.5.json')
        all_cards_metadata: Dict = await res.json()
        await self.mongo.bestdori.all.update_one({
            'cards': {'$exists': True}},
            {'$set': {'cards': all_cards_metadata}},
            upsert=True
        )
        return {id: PartialCard(**all_card_item) for id, all_card_item in all_cards_metadata.items()}

    async def fetch_all_characters_metadata(self) -> Dict[int, PartialCharacter]:
        res = await self.session.get('https://bestdori.com/api/characters/all.5.json')
        all_characters_metadata: Dict = await res.json()
        await self.mongo.bestdori.all.update_one(
            {'characters': {'$exists': True}},
            {'$set': {'characters': all_characters_metadata}},
            upsert=True,
        )
        return {id: PartialCharacter(**all_character_item) for id, all_character_item in all_characters_metadata.items()}

    async def fetch_all_bands_metadata(self) -> Dict[int, PartialBand]:
        res = await self.session.get('https://bestdori.com/api/bands/all.1.json')
        all_bands_metadata: Dict = await res.json()
        await self.mongo.bestdori.all.update_one(
            {'bands': {'$exists': True}},
            {'$set': {'bands': all_bands_metadata}},
            upsert=True,
        )
        return {id: PartialBand(**all_band_item) for id, all_band_item in all_bands_metadata.items()}

    async def fetch_all_skills_metadata(self) -> Dict[int, PartialSkill]:
        res = await self.session.get('https://bestdori.com/api/skills/all.5.json')
        all_skills_metadata: Dict = await res.json()
        await self.mongo.bestdori.all.update_one(
            {'skills': {'$exists': True}},
            {'$set': {'skills': all_skills_metadata}},
            upsert=True,
        )
        return {id: PartialSkill(**all_skill_item) for id, all_skill_item in all_skills_metadata.items()}

    async def fetch_all_events_metadata(self) -> Dict[int, PartialEvent]:
        res = await self.session.get('https://bestdori.com/api/events/all.5.json')
        all_events_metadata: Dict = await res.json()
        await self.mongo.bestdori.all.update_one(
            {'events': {'$exists': True}},
            {'$set': {'events': all_events_metadata}},
            upsert=True,
        )
        return {id: PartialEvent(**all_event_item) for id, all_event_item in all_events_metadata.items()}

    async def fetch_all_gachas_metadata(self) -> Dict[int, PartialGacha]:
        res = await self.session.get('https://bestdori.com/api/gacha/all.5.json')
        all_gachas_metadata: Dict = await res.json()
        await self.mongo.bestdori.all.update_one(
            {'gachas': {'$exists': True}},
            {'$set': {'gachas': all_gachas_metadata}},
            upsert=True,
        )
        return {id: PartialGacha(**all_gacha_item) for id, all_gacha_item in all_gachas_metadata.items()}

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
        