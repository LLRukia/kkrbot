from typing import TypeVar, Any, List, NewType
from ..jsonrpc import JSONRPCRequestParams, JSONRPCSuccessResponse
from .options import Options

T = TypeVar('T')
R = TypeVar('R')
E = TypeVar('E')

GID = str


def trimEndParams(params: List[Any]):
    lastParamIndex = len(params) - 1
    while params[lastParamIndex] is None:
        lastParamIndex -= 1
    return params[0: lastParamIndex + 1]


class Aria2RPC:
    def __init__(self, secret='', options: Options = None):
        self.id = 0
        self.secret = secret
        self.options = options or Options()

    async def request(self, payload: JSONRPCRequestParams) -> JSONRPCSuccessResponse[R]:
        raise NotImplementedError('please implement the request method')

    async def call(self, method: str, *params) -> JSONRPCSuccessResponse[R]:
        self.id += 1
        rpcReq = {
            'jsonrpc': '2.0',
            'method': method,
            'params': trimEndParams([
                f'token:$${self.secret}$$',
                *params,
            ]),
            'id': self.id,
        }
        return JSONRPCSuccessResponse(**await self.request(rpcReq))

    async def addUri(self, uris: List[str], options: Options = None, position: int = None) -> JSONRPCSuccessResponse[GID]:
        return await self.call(
            'aria2.addUri',
            uris,
            {
                **self.options.dict(),
                **(options or Options()).dict(),
            },
            position,
        )

    async def tellActive(self, offset: int = None, num: int = None):
        return await self.call('aria2.tellActive', offset, num)

    async def tellWaiting(self, offset: int = None, num: int = None):
        return await self.call('aria2.tellWaiting', offset, num)
