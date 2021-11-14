from typing import List, Dict, Union
from typing_extensions import Literal
from .helpers import UnderscoreToCamelModel, ServerListType


class CardStat(UnderscoreToCamelModel):
    performance: int
    technique: int
    visual: int


class CardStatWithLevelLimitInfo(CardStat):
    level_limit: int


class PartialCard(UnderscoreToCamelModel):
    character_id: int
    rarity: int
    attribute: str
    level_limit: int
    resource_set_name: str
    prefix: List[str]
    released_at: List[str]
    skill_id: int
    type: str
    stat: Dict[
        Union[int, Literal['episodes', 'training']],
        Union[CardStat, List[CardStat], CardStatWithLevelLimitInfo]
    ]


class Card(PartialCard):
    class CardEpisode(UnderscoreToCamelModel):
        class CardEpisodeCost(UnderscoreToCamelModel):
            resource_id: int
            resource_type: str
            quantity: int
            lb_bonus: int


        episode_id: int
        episode_type: str
        situation_id: int
        scenario_id: str
        append_performance: int
        append_technique: int
        append_visual: int
        release_level: int
        costs: Dict[Literal['entries'], List[CardEpisodeCost]]

    id: int
    sd_resource_name: str
    episodes: Dict[Literal['entries'], List[CardEpisode]]
    costume_id: int
    gacha_text: ServerListType[str]
    skill_name: List[str]
    source: List[Dict]
