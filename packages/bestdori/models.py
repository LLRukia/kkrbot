from typing import List, Dict, Union, TypeVar
from typing_extensions import Literal
from pydantic import BaseModel
from utils.pydantic_model_helpers import UnderscoreToCamelConfig

T = TypeVar('T')

PossiblyNone = Union[T, None]


class CardStat(BaseModel):
    performance: int
    technique: int
    visual: int

    class Config(UnderscoreToCamelConfig):
        pass


class CardStatWithLevelLimitInfo(CardStat):
    level_limit: int


class AllCardItem(BaseModel):
    character_id: int
    rarity: int
    attribute: str
    levelLimit: int
    resource_set_name: str
    prefix: List[str]
    released_at: List[str]
    skill_id: int
    type: str
    stat: Dict[Union[int, Literal['episodes', 'training']], Union[CardStat, List[CardStat], CardStatWithLevelLimitInfo]]

    class Config(UnderscoreToCamelConfig):
        pass


class Card(BaseModel):
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
    character_id: int
    rarity: int
    attribute: str
    level_limit: int
    resource_set_name: str
    sd_resource_name: str
    episodes: Dict[Literal['entries'], List[CardEpisode]]
    costume_id: int
    gacha_text: List[PossiblyNone[str]]
    prefix: List[str]
    released_at: List[str]
    skill_name: List[str]
    skill_id: int
    source: List[Dict]
    type: str
    stat: Dict[Union[int, Literal['episodes', 'training']], Union[CardStat, List[CardStat], CardStatWithLevelLimitInfo]]

    class Config(UnderscoreToCamelConfig):
        pass
