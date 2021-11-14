from typing import List
from typing_extensions import Literal
from .helpers import UnderscoreToCamelModel, ServerListType, PossiblyNone


class PartialEvent(UnderscoreToCamelModel):
    class Attribute(UnderscoreToCamelModel):
        attribute: str
        percent: int

    class Character(UnderscoreToCamelModel):
        character_id: int
        percent: int

    event_type: Literal['story', 'challenge', 'versus', 'live_try', 'mission_live', 'festival', 'medley']
    event_name: ServerListType[str]
    banner_asset_bundle_name: str
    start_at: ServerListType[str]
    end_at: ServerListType[str]
    attributes: List[Attribute]
    characters: List[Character]
    reward_cards: List[int]

class Reward(UnderscoreToCamelModel):
    reward_type: Literal['star', 'coin', 'practice_ticket', 'item', 'situation', 'stamp']
    reward_id: PossiblyNone[int]
    reward_quantity: int


class PointReward(Reward):
    point: int

class Event(PartialEvent):
    

    class RankingReward(UnderscoreToCamelModel):
        from_rank: int
        to_rank: int
        reward_type: Literal['degree', 'item', 'star', 'practice_ticket']

    class Story(UnderscoreToCamelModel):
        scenario_id: str
        cover_image: str
        background_image: str
        release_pt: str
        rewards: List[Reward]
        caption: List[PossiblyNone[str]]
        title: List[PossiblyNone[str]]
        synopsis: List[PossiblyNone[str]]
        release_conditions: List[PossiblyNone[str]]

    asset_bundle_name: str
    enable_flag: List[PossiblyNone[bool]]
    public_start_at: List[PossiblyNone[str]]
    public_end_at: List[PossiblyNone[str]]
    distribution_start_at: List[PossiblyNone[str]]
    distribution_end_at: List[PossiblyNone[str]]
    bgm_asset_bundle_name: str
    bgm_file_name: str
    aggregate_end_at: List[PossiblyNone[str]]
    exchange_end_at: List[PossiblyNone[str]]
    point_rewards: List[PossiblyNone[List[PointReward]]]
    ranking_rewards: List[PossiblyNone[List[RankingReward]]]
    stories: List[Story]
