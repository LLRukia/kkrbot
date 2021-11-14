from typing import List, Dict
from typing_extensions import Literal
from .helpers import UnderscoreToCamelModel, ServerListType, PossiblyNone

SeasonCostumeType = Literal[
    'CASUAL_SUMMER', 'CASUAL_WINTER', 'CASUAL_SPRING',
    'UNIFORM_SUMMER', 'UNIFORM_WINTER',
    'CASUAL_APRILFOOL', 'UNIFORM_APRILFOOL',
]


class SeasonCostume(UnderscoreToCamelModel):
    character_id: int
    basic_season_id: int
    costume_type: Literal['CASUAL', 'UNIFORM']
    season_costume_type: SeasonCostumeType
    sd_asset_bundle_name: str
    live2d_asset_bundle_name: str


class PartialCharacter(UnderscoreToCamelModel):
    character_name: ServerListType[str]
    first_name: ServerListType[str]
    last_name: ServerListType[str]
    nickname: ServerListType[str]
    band_id: PossiblyNone[int]
    season_costume_list: PossiblyNone[Dict[Literal['entries'], List[SeasonCostume]]]