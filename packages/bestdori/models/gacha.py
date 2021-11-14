from typing import List, Dict
from typing_extensions import Literal
from .helpers import UnderscoreToCamelModel, ServerListType, PossiblyNone

class PartialGacha(UnderscoreToCamelModel):
    resource_name: str
    banner_asset_bundle_name: PossiblyNone[str]
    gacha_name: ServerListType[str]
    published_at: ServerListType[str]
    closed_at: ServerListType[str]
    type: Literal['permanent', 'special', 'limited', 'dreamfes', 'miracle', 'free', 'birthday', 'kirafes']
    new_cards: List[int]


class DetailItem(UnderscoreToCamelModel):
    rarity_index: int
    weight: int
    pickup: bool


class RateItem(UnderscoreToCamelModel):
    rate: int
    weight_total: int


class PaymentMethod(UnderscoreToCamelModel):
    gacha_id: int
    payment_method: Literal['paid_star', 'free_star', 'normal_ticket', 'over_the_3_star_ticket']
    quantity: int
    payment_method_id: int
    count: int
    behavior: Literal['once_a_day', 'normal', 'over_the_3_star_once']
    pickup: bool
    cost_item_quantity: int


class Information(UnderscoreToCamelModel):
    description: ServerListType[str]
    new_member_info: ServerListType[str]
    notice: ServerListType[str]
    term: ServerListType[str]


class Gacha(PartialGacha):
    details: ServerListType[Dict[int, DetailItem]]
    rates: ServerListType[Dict[int, RateItem]]
    payment_methods: List[PaymentMethod]
    description: ServerListType[str]
    annotation: ServerListType[str]
    gacha_period: ServerListType[str]
    gacha_type: Literal['normal']
    information: Information
