from typing import Dict, TypeVar, Any, List
from typing_extensions import Literal
from pydantic import BaseModel
from utils.pydantic_model_helpers import UnderscoreToCamelConfig, AllOptional
from ..jsonrpc import unwrap_success_response_message
from .options import Options

T = TypeVar('T')
R = TypeVar('R')
E = TypeVar('E')

GID = str

class Uri(BaseModel):
    uri: str
    status: Literal['used', 'waiting']


class File(BaseModel):
    index: int
    path: str
    length: int
    completed_length: int
    selected: bool
    uris: List[Uri]

    class Config(UnderscoreToCamelConfig):
        pass


class BitTorrent(BaseModel, metaclass=AllOptional):
    announce_list: List[str]
    comment: str
    creation_date: str
    mode: Literal['single', 'multi']
    info: Dict[Literal['name'], str]

    class Config(UnderscoreToCamelConfig):
        pass


class Server(BaseModel):
    uri: str
    current_uri: str
    download_speed: int

    class Config(UnderscoreToCamelConfig):
        pass


class Servers(BaseModel):
    index: int
    servers: List[Server]


class Status(BaseModel, metaclass=AllOptional):
    gid: GID
    status: Literal['active', 'waiting', 'paused', 'error', 'complete', 'removed']
    total_length: int
    complete_length: int
    upload_length: int
    bitfield: str
    download_speed: int
    upload_speed: int
    info_hash: str
    num_seeders: str
    seeder: bool
    piece_length: int
    num_pieces: int
    connections: str
    error_code: str
    error_message: str
    followed_by: List[GID]
    following: List[GID]
    belong_to: List[GID]
    dir: str
    files: List[File]
    bittorrent: BitTorrent
    verified_length: int
    verify_integrity_pending: bool

    class Config(UnderscoreToCamelConfig):
        pass


class Stat(BaseModel):
    download_speed: int
    upload_speed: int
    num_active: int
    num_waiting: int
    num_stopped: int
    num_stopped_total: int

    class Config(UnderscoreToCamelConfig):
        pass


class Version(BaseModel):
    version: str
    enabledFeatures: List[str]

    class Config(UnderscoreToCamelConfig):
        pass


def trim_end_params(params: List[Any]):
    lastParamIndex = len(params) - 1
    while params[lastParamIndex] is None:
        lastParamIndex -= 1
    return params[0: lastParamIndex + 1]


class Aria2RPC:
    def __init__(self, secret='', options: Options = None):
        self.id = 0
        self.secret = secret
        self.options = options or Options()

    async def request(self, *args, **kwargs):
        raise NotImplementedError('please implement the request method')

    async def call(self, method: str, *params):
        self.id += 1
        rpcReq = {
            'jsonrpc': '2.0',
            'method': method,
            'params': trim_end_params([
                f'token:$${self.secret}$$',
                *params,
            ]),
            'id': self.id,
        }
        return await self.request(rpcReq)

    @unwrap_success_response_message
    async def add_uri(self, uris: List[str], options: Options = None, position: int = None) -> GID:
        return await self.call(
            'aria2.addUri',
            uris,
            {
                **self.options.dict(),
                **(options or Options()).dict(),
            },
            position,
        )

    @unwrap_success_response_message
    async def tell_status(self, gid: GID, keys: List[str] = None) -> Status:
        """
        https://aria2.github.io/manual/en/html/aria2c.html#aria2.tellStatus
        """
        return await self.call('aria2.tellStatus', gid, keys)

    @unwrap_success_response_message
    async def get_uris(self, gid: GID) -> List[Uri]:
        """
        https://aria2.github.io/manual/en/html/aria2c.html#aria2.getUris
        """
        return await self.call('aria2.getUris', gid)

    @unwrap_success_response_message
    async def get_files(self, gid: GID) -> List[File]:
        """
        https://aria2.github.io/manual/en/html/aria2c.html#aria2.getFiles
        """
        return await self.call('aria2.getFiles', gid)

    async def get_peers(self):
        """
        https://aria2.github.io/manual/en/html/aria2c.html#aria2.getPeers
        """
        raise NotImplementedError('TODO')

    @unwrap_success_response_message
    async def get_servers(self, gid: GID) -> Servers:
        """
        https://aria2.github.io/manual/en/html/aria2c.html#aria2.getServers
        """
        return await self.call('aria2.getServers', gid)

    @unwrap_success_response_message
    async def tell_active(self, keys: List[str] = None) -> List[Status]:
        """
        https://aria2.github.io/manual/en/html/aria2c.html#aria2.tellActive
        """
        return await self.call('aria2.tellActive', keys)

    @unwrap_success_response_message
    async def tell_waiting(self, offset: int, num = int, keys: List[str] = None) -> List[Status]:
        """
        https://aria2.github.io/manual/en/html/aria2c.html#aria2.tellWaiting
        """
        return await self.call('aria2.tellWaiting', offset, num, keys)

    @unwrap_success_response_message
    async def tell_stopped(self, offset: int, num = int, keys: List[str] = None) -> List[Status]:
        """
        https://aria2.github.io/manual/en/html/aria2c.html#aria2.tellStopped
        """
        return await self.call('aria2.tellStopped', offset, num, keys)

    @unwrap_success_response_message
    async def change_position(self, gid: GID, pos: int, how: Literal['POS_CUR', 'POS_SET']) -> int:
        """
        https://aria2.github.io/manual/en/html/aria2c.html#aria2.changePosition
        """
        return await self.call('aria2.changePosition', gid, pos, how)
    
    @unwrap_success_response_message
    async def change_uris(self, gid: GID, fileindex: int, delUris: List[str], addUris: List[str], position: int = None) -> List[int]:
        """
        https://aria2.github.io/manual/en/html/aria2c.html#aria2.changePosition
        """
        return await self.call('aria2.changeUris', gid, fileindex, delUris, addUris, position)

    @unwrap_success_response_message
    async def get_option(self, gid: GID) -> Options:
        """
        https://aria2.github.io/manual/en/html/aria2c.html#aria2.getOption
        """
        return await self.call('aria2.getOption', gid)

    @unwrap_success_response_message
    async def change_option(self, gid: GID, options: Options) -> Literal['OK']:
        """
        https://aria2.github.io/manual/en/html/aria2c.html#aria2.changeOption
        """
        return await self.call('aria2.changeOption', gid, options)

    @unwrap_success_response_message
    async def get_global_option(self) -> Options:
        """
        https://aria2.github.io/manual/en/html/aria2c.html#aria2.getGlobalOption
        """
        return await self.call('aria2.getGlobalOption')
    
    @unwrap_success_response_message
    async def change_global_option(self, options: Options) -> Literal['OK']:
        """
        https://aria2.github.io/manual/en/html/aria2c.html#aria2.changeGlobalOption
        """
        return await self.call('aria2.changeGlobalOption', options)

    @unwrap_success_response_message
    async def get_global_stat(self) -> Stat:
        """
        https://aria2.github.io/manual/en/html/aria2c.html#aria2.getGlobalStat
        """
        return await self.call('aria2.getGlobalStat')

    @unwrap_success_response_message
    async def purge_download_result(self) -> Literal['OK']:
        """
        https://aria2.github.io/manual/en/html/aria2c.html#aria2.purgeDownloadResult
        """
        return await self.call('aria2.purgeDownloadResult')

    @unwrap_success_response_message
    async def remove_download_result(self, gid: GID) -> Literal['OK']:
        """
        https://aria2.github.io/manual/en/html/aria2c.html#aria2.removeDownloadResult
        """
        return await self.call('aria2.removeDownloadResult', gid)

    @unwrap_success_response_message
    async def get_version(self) -> Version:
        """
        https://aria2.github.io/manual/en/html/aria2c.html#aria2.getVersion
        """
        return await self.call('aria2.getVersion')

    @unwrap_success_response_message
    async def get_session_info(self) -> str:
        """
        https://aria2.github.io/manual/en/html/aria2c.html#aria2.getSessionInfo
        """
        return await self.call('aria2.getSessionInfo')
