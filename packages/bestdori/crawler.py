import asyncio
import os
from typing import Dict, Union, List, Callable, NoReturn
from pydantic import BaseModel
from aiohttp import ClientSession
from motor.motor_asyncio import AsyncIOMotorClient
from packages.aria2 import Options, GID
from packages.aria2.ws_rpc import WSAria2RPC
from utils.logger import Logger
from .models import *
from .helpers import get_card_asset_urls_from_metadata, get_event_asset_urls_from_metadata, servers

class AssetDownloadInfo(BaseModel):
    filename: str

class Crawler:
    def __init__(
        self,
        session: ClientSession,
        aria2rpc: WSAria2RPC,
        mongo: AsyncIOMotorClient,
        asset_dir: str,
        logger: Logger,
        on_asset_download_start: Callable[[AssetDownloadInfo], NoReturn] = None,
        on_asset_download_complete: Callable[[AssetDownloadInfo], NoReturn] = None,
        on_asset_download_error: Callable[[AssetDownloadInfo], NoReturn] = None,
    ) -> None:
        self.session = session
        self.aria2rpc = aria2rpc
        self.mongo = mongo
        self.asset_dir = asset_dir
        self.logger = logger
        self.gid2info: Dict[GID, AssetDownloadInfo] = {}

        if on_asset_download_start:
            # TODO: 不知道为什么，监听这个事件就跑不起来了。
            # self.aria2rpc.add_event_listener('download_start', lambda gid: on_asset_download_start(self.gid2info[gid]))
            raise NotImplementedError('not support "asset_download_start" event yet!')
        if on_asset_download_complete:
            self.aria2rpc.add_event_listener('download_complete', lambda gid: on_asset_download_complete(self.gid2info[gid]))
        if on_asset_download_error:
            self.aria2rpc.add_event_listener('download_error', lambda gid: on_asset_download_error(self.gid2info[gid]))

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
        return {int(id): PartialEvent(**all_event_item) for id, all_event_item in all_events_metadata.items()}

    async def fetch_all_gachas_metadata(self) -> Dict[int, PartialGacha]:
        res = await self.session.get('https://bestdori.com/api/gacha/all.5.json')
        all_gachas_metadata: Dict = await res.json()
        await self.mongo.bestdori.all.update_one(
            {'gachas': {'$exists': True}},
            {'$set': {'gachas': all_gachas_metadata}},
            upsert=True,
        )
        return {int(id): PartialGacha(**all_gacha_item) for id, all_gacha_item in all_gachas_metadata.items()}

    async def fetch_card_metadata(self, id: int, save_to_mongo=True) -> Card:
        res = await self.session.get(f'https://bestdori.com/api/cards/{id}.json')
        metadata = {'id': id, **(await res.json())}
        if save_to_mongo:
            await self.mongo.bestdori.card.update_one(
                {'id': id},
                {'$set': metadata},
                upsert=True,
            )
        return Card(**metadata)

    async def load_card_metadata(self, id: int) -> Card:
        metadata = await self.mongo.bestdori.card.find_one({'id': id})
        if not metadata:
            return await self.fetch_card_metadata(id)
        return Card(**metadata)

    async def fetch_event_metadata(self, id: int) -> Event:
        res = await self.session.get(f'https://bestdori.com/api/events/{id}.json')
        metadata = {'id': id, **(await res.json())}
        await self.mongo.bestdori.event.update_one(
            {'id': id},
            {'$set': metadata},
            upsert=True,
        )
        return Event(**metadata)

    async def load_event_metadata(self, id: int) -> Event:
        metadata = await self.mongo.bestdori.event.find_one({'id': id})
        if not metadata:
            return await self.fetch_event_metadata(id)
        return Event(**metadata)

    async def fetch_gacha_medadata(self, id: int) -> Gacha:
        res = await self.session.get(f'https://bestdori.com/api/gacha/{id}.json')
        metadata = {'id': id, **(await res.json())}
        await self.mongo.bestdori.gacha.update_one(
            {'id': id},
            {'$set': metadata},
            upsert=True,
        )
        return Gacha(**metadata)

    async def load_gacha_metadata(self, id: int) -> Gacha:
        metadata = await self.mongo.bestdori.gacha.find_one({'id': id})
        if not metadata:
            return await self.fetch_gacha_metadata(id)
        return Gacha(**metadata)

    async def download_asset(self, url: str, filename: str, overwrite=False, subdir=''):
        if os.path.isfile(os.path.join(self.asset_dir, subdir, filename)) and not overwrite:
            self.logger.info(f'{url} already exists')
            return

        if not os.path.exists(os.path.join(self.asset_dir, subdir)):
            os.makedirs(os.path.join(self.asset_dir, subdir))

        gid = await self.aria2rpc.add_uri([url], Options(
            out = filename,
            dir = os.path.abspath(os.path.join(self.asset_dir, subdir)),
        ))

        self.gid2info[gid] = AssetDownloadInfo(filename=os.path.join(subdir, filename))

    async def download_card_assets(self, id_or_metadata: Union[int, Card], overwrite=False):
        metadata = await self.load_card_metadata(id_or_metadata) if isinstance(id_or_metadata, int) else id_or_metadata
        resource_set_name = metadata.resource_set_name

        urls = get_card_asset_urls_from_metadata(metadata)

        await asyncio.gather(
            self.download_asset(urls['card_normal'], f'{resource_set_name}_card_normal.png', overwrite, 'cards'),
            self.download_asset(urls['icon_normal'], f'{resource_set_name}_normal.png', overwrite, os.path.join('cards', 'thumb')),
        )

        if metadata.rarity > 2:
            await asyncio.gather(
                self.download_asset(urls['card_after_training'], f'{resource_set_name}_card_after_training.png', overwrite, 'cards'),
                self.download_asset(urls['icon_after_training'], f'{resource_set_name}_after_training.png', overwrite, os.path.join('cards', 'thumb')),
            )

    async def download_event_assets(self, id_or_metadata: Union[int, Event], overwrite=False):
        metadata = await self.load_event_metadata(id_or_metadata) if isinstance(id_or_metadata, int) else id_or_metadata
        banner_asset_bundle_name, asset_bundle_name = metadata.banner_asset_bundle_name, metadata.asset_bundle_name

        # TODO: 国服活动的 banner url 有点问题
        # await asyncio.gather(*[
        #     self.download_asset(
        #         f'https://bestdori.com/assets/{server}/homebanner_rip/{banner_asset_bundle_name}.png',
        #         f'{banner_asset_bundle_name}.png',
        #         overwrite,
        #         server,
        #     ) for i, server in enumerate(servers) if metadata.start_at[i]
        # ])

        # await asyncio.gather(*[
        #     self.download_asset(
        #         f'https://bestdori.com/assets/{server}/event/{asset_bundle_name}/images_rip/banner.png',
        #         'banner.png',
        #         overwrite,
        #         server,
        #     ) for i, server in enumerate(servers) if metadata.start_at[i]
        # ])

        await self.download_asset(
            f'https://bestdori.com/assets/jp/event/{asset_bundle_name}/topscreen_rip/trim_eventtop.png',
            'trim_eventtop.png',
            overwrite,
            os.path.join('events', asset_bundle_name),
        )

        await self.download_asset(
            f'https://bestdori.com/assets/jp/event/{asset_bundle_name}/topscreen_rip/bg_eventtop.png',
            'bg_eventtop.png',
            overwrite,
            os.path.join('events', asset_bundle_name),
        )

    async def download_gacha_assets(self, id_or_metadata: Union[int, Event], overwrite=False) -> Gacha:
        metadata = await self.load_gacha_metadata(id_or_metadata) if isinstance(id_or_metadata, int) else id_or_metadata
        banner_asset_bundle_name, resource_name = metadata.banner_asset_bundle_name, metadata.resource_name

        await asyncio.gather(*[
            self.download_asset(
                f'https://bestdori.com/assets/{server}/homebanner_rip/{banner_asset_bundle_name}.png',
                f'{banner_asset_bundle_name}.png',
                overwrite,
                os.path.join('gachas', server),
            ) for i, server in enumerate(servers) if metadata.published_at[i]
        ])

        await asyncio.gather(*[
            self.download_asset(
                f'https://bestdori.com/assets/{server}/gacha/screen/{resource_name}_rip/logo.png',
                'logo.png',
                overwrite,
                os.path.join('gachas', resource_name, server),
            ) for i, server in enumerate(servers) if metadata.published_at[i]
        ])

        await asyncio.gather(*[
            self.download_asset(
                f'https://bestdori.com/assets/{server}/gacha/screen/{resource_name}_rip/pickup.png',
                'pickup.png',
                overwrite,
                os.path.join('gachas', resource_name, server),
            ) for i, server in enumerate(servers) if metadata.published_at[i]
        ])

    async def diff_card(self) -> List[int]:
        local_cards = set([card['id'] for card in await (self.mongo.bestdori.card.find({})).to_list(None)])
        return [int(id) for id in (await self.fetch_all_cards_metadata()).keys() if int(id) not in local_cards]

    async def diff_event(self) -> List[int]:
        local_events = set([event['id'] for event in await (self.mongo.bestdori.event.find({})).to_list(None)])
        return [int(id) for id in (await self.fetch_all_events_metadata()).keys() if int(id) not in local_events]

    async def diff_gacha(self) -> List[int]:
        local_gachas = set([gacha['id'] for gacha in await (self.mongo.bestdori.gacha.find({})).to_list(None)])
        return [int(id) for id in (await self.fetch_all_events_metadata()).keys() if int(id) not in local_gachas]
