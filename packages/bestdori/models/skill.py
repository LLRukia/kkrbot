from typing import List
from .helpers import UnderscoreToCamelModel, ServerListType, Number

class PartialSkill(UnderscoreToCamelModel):
    simple_description: ServerListType[str]
    description: ServerListType[str]
    duration: List[Number]
