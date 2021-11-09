from .models import Card


def get_asset_urls_from_metadata(metadata: Card):
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
