from typing import List, Dict, Union, TypeVar
from typing_extensions import Literal
from pydantic import BaseModel
from utils.pydantic_model_helpers import UnderscoreToCamelConfig

T = TypeVar('T')

PossiblyNone = Union[T, None]
Number = Union[int, float]


class CardStat(BaseModel):
    performance: int
    technique: int
    visual: int

    class Config(UnderscoreToCamelConfig):
        pass


class CardStatWithLevelLimitInfo(CardStat):
    level_limit: int


class PartialCard(BaseModel):
    character_id: int
    rarity: int
    attribute: str
    level_limit: int
    resource_set_name: str
    prefix: List[str]
    released_at: List[str]
    skill_id: int
    type: str
    stat: Dict[Union[int, Literal['episodes', 'training']], Union[CardStat, List[CardStat], CardStatWithLevelLimitInfo]]

    class Config(UnderscoreToCamelConfig):
        pass


class Card(PartialCard):
    class CardEpisode(BaseModel):
        class CardEpisodeCost(BaseModel):
            resource_id: int
            resource_type: str
            quantity: int
            lb_bonus: int
            
            class Config(UnderscoreToCamelConfig):
                pass

        episode_id: int
        episode_type: str
        situation_id: int
        scenario_id: str
        append_performance: int
        append_technique: int
        append_visual: int
        release_level: int
        costs: Dict[Literal['entries'], List[CardEpisodeCost]]
        
        class Config(UnderscoreToCamelConfig):
            pass

    id: int
    sd_resource_name: str
    episodes: Dict[Literal['entries'], List[CardEpisode]]
    costume_id: int
    gacha_text: List[PossiblyNone[str]]
    skill_name: List[str]
    source: List[Dict]

    class Config(UnderscoreToCamelConfig):
        pass

SeasonCostumeType = Literal[
    'CASUAL_SUMMER', 'CASUAL_WINTER', 'CASUAL_SPRING',
    'UNIFORM_SUMMER', 'UNIFORM_WINTER',
    'CASUAL_APRILFOOL', 'UNIFORM_APRILFOOL',
]


class SeasonCostume(BaseModel):
    character_id: int
    basic_season_id: int
    costume_type: Literal['CASUAL', 'UNIFORM']
    season_costume_type: SeasonCostumeType
    sd_asset_bundle_name: str
    live2d_asset_bundle_name: str

    class Config(UnderscoreToCamelConfig):
        pass


class PartialCharacter(BaseModel):
    character_name: List[str]
    first_name: List[str]
    last_name: List[str]
    nickname: List[PossiblyNone[str]]
    band_id: PossiblyNone[int]
    season_costume_list: PossiblyNone[Dict[Literal['entries'], List[SeasonCostume]]]

    class Config(UnderscoreToCamelConfig):
        pass


class PartialBand(BaseModel):
    band_name: List[PossiblyNone[str]]

    class Config(UnderscoreToCamelConfig):
        pass


class PartialSkill(BaseModel):
    simple_description: List[PossiblyNone[str]]
    description: List[PossiblyNone[str]]
    duration: List[Number]

    class Config(UnderscoreToCamelConfig):
        pass


class PartialEvent(BaseModel):
    class Attribute(BaseModel):
        attribute: str
        percent: int

    class Character(BaseModel):
        character_id: int
        percent: int

        class Config(UnderscoreToCamelConfig):
            pass

    event_type: Literal['story', 'challenge', 'versus', 'live_try', 'mission_live', 'festival', 'medley']
    event_name: List[PossiblyNone[str]]
    banner_asset_bundle_name: str
    start_at: List[PossiblyNone[str]]
    end_at: List[PossiblyNone[str]]
    attributes: List[Attribute]
    characters: List[Character]
    reward_cards: List[int]

    class Config(UnderscoreToCamelConfig):
        pass


class PartialGacha(BaseModel):
    resource_name: str
    banner_asset_bundle_name: PossiblyNone[str]
    gacha_name: List[PossiblyNone[str]]
    published_at: List[PossiblyNone[str]]
    closed_at: List[PossiblyNone[str]]
    type: Literal['permanent', 'special', 'limited', 'dreamfes', 'miracle', 'free', 'birthday', 'kirafes']
    new_cards: List[int]

    class Config(UnderscoreToCamelConfig):
        pass