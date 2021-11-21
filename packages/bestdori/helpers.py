from typing import List, Dict, Union
from typing_extensions import Literal
from .models import Card, Event, Gacha, PartialEvent, PartialGacha

Server = Literal['jp', 'en', 'tw', 'cn', 'kr']

servers = ['jp', 'en', 'tw', 'cn', 'kr']

server_index_map = {server: index for index, server in enumerate(servers)}


def get_card_asset_urls_from_metadata(metadata: Card):
    suffix = str(metadata.id // 50)
    group_id = '0' * (5 - len(suffix)) + suffix

    resource_set_name = metadata.resource_set_name

    urls = {
        'icon_normal': f'https://bestdori.com/assets/jp/thumb/chara/card{group_id}_rip/{resource_set_name}_normal.png',
        'card_normal': f'https://bestdori.com/assets/jp/characters/resourceset/{resource_set_name}_rip/card_normal.png',
    }

    if metadata.rarity > 2:
        urls = {
            **urls,
            'icon_after_training': f'https://bestdori.com/assets/jp/thumb/chara/card{group_id}_rip/{resource_set_name}_after_training.png',
            'card_after_training': f'https://bestdori.com/assets/jp/characters/resourceset/{resource_set_name}_rip/card_after_training.png',
        }
    
    return urls


def get_event_asset_urls_from_metadata(metadata: Event):
    banner_asset_bundle_name, asset_bundle_name = metadata.banner_asset_bundle_name, metadata.asset_bundle_name
    banner_urls = {server: f'https://bestdori.com/assets/{server}/homebanner_rip/{banner_asset_bundle_name}.png' for server in servers}
    banner_urls2 = {server: f'https://bestdori.com/assets/{server}/event/{asset_bundle_name}/images_rip/banner.png' for server in servers}
    trim_eventtop_urls = {server: f'https://bestdori.com/assets/{server}/event/{asset_bundle_name}/topscreen_rip/trim_eventtop.png' for server in servers}
    bg_event_top_urls = {server: f'https://bestdori.com/assets/{server}/event/{asset_bundle_name}/topscreen_rip/bg_eventtop.png' for server in servers}


def is_event_duration_intersected_with_gacha_duration(
    event: PartialEvent,
    gacha: PartialGacha,
    server: Server = 'jp',
) -> bool:
    server_index = server_index_map[server]
    if gacha.published_at[server_index] and gacha.closed_at[server_index] and event.start_at[server_index] and event.end_at[server_index]:
        return not (gacha.published_at[server_index] >= event.end_at[server_index] or gacha.closed_at[server_index] <= event.start_at[server_index])
    return False


def get_gacha_during_event(
    event: PartialEvent,
    gachas: Union[List[PartialGacha], Dict[int, PartialGacha]],
    server: Server = 'jp',
):
    if isinstance(gachas, list):
        return [gacha for gacha in gachas if is_event_duration_intersected_with_gacha_duration(event, gacha, server)]
    return {id: gacha for id, gacha in gachas.items() if is_event_duration_intersected_with_gacha_duration(event, gacha, server)}
        