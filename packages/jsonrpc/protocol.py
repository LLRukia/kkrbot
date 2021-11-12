from typing import Optional, Union, Generic, TypeVar, Any, List, Dict
from typing_extensions import Literal
from pydantic import BaseModel
from pydantic.generics import GenericModel

T = TypeVar('T')
R = TypeVar('R')
E = TypeVar('E')

JSONRPCId = Union[int, str, None]
JSONRPCRequestParams = TypeVar('JSONRPCRequestParams', List[Any], Dict[str, Any])


class JSONRPCBaseData(BaseModel):
    jsonrpc: Literal['2.0']
    id: JSONRPCId


class JSONRPCSuccessResponse(GenericModel, JSONRPCBaseData, Generic[T]):
    result: T


class JSONRPCError(GenericModel, Generic[T]):
    code: int
    message: str
    data: Optional[T]


class JSONRPCErrorResponse(GenericModel, JSONRPCBaseData, Generic[R]):
    error: JSONRPCError[R]


JSONRPCResponse = Union[JSONRPCSuccessResponse, JSONRPCErrorResponse]


class JSONRPCNotification(GenericModel, Generic[JSONRPCRequestParams]):
    jsonrpc: Literal['2.0']
    method: str
    params: Optional[JSONRPCRequestParams]
