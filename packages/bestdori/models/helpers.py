from typing import List, Dict, Union, TypeVar
from typing_extensions import Literal
from pydantic import BaseModel
from utils.pydantic_model_helpers import UnderscoreToCamelConfig

Number = Union[int, float]
T = TypeVar('T')
PossiblyNone = Union[T, None]
ServerListType = List[PossiblyNone[T]]


class UnderscoreToCamelModel(BaseModel):
    class Config(UnderscoreToCamelConfig):
        pass
