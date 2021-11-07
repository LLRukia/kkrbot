from typing import Optional, Union, List
from typing_extensions import Literal
from pydantic import BaseModel, Field
from pydantic.main import ModelMetaclass


class AllOptional(ModelMetaclass):
    """
    see https://stackoverflow.com/questions/67699451/make-every-fields-as-optional-with-pydantic#answer-67733889
    """

    def __new__(self, name, bases, namespaces, **kwargs):
        annotations = namespaces.get('__annotations__', {})
        for base in bases:
            annotations = {**annotations, **base.__annotations__}
        for field in annotations:
            if not field.startswith('__'):
                annotations[field] = Optional[annotations[field]]
        namespaces['__annotations__'] = annotations
        return super().__new__(self, name, bases, namespaces, **kwargs)


class UnderscoreToDashConfig:
    alias_generator = lambda str: str.replace('_', '-')


class _BasicOptions(BaseModel):
    """
    https://aria2.github.io/manual/en/html/aria2c.html#basic-options
    """

    dir: str
    "https://aria2.github.io/manual/en/html/aria2c.html#cmdoption-d"

    input_file: str
    "https://aria2.github.io/manual/en/html/aria2c.html#cmdoption-i"

    max_concurrent_downloads: int
    "https://aria2.github.io/manual/en/html/aria2c.html#cmdoption-j"

    check_integrity: bool
    "https://aria2.github.io/manual/en/html/aria2c.html#cmdoption-v"

    # Note: for derived model (like `BasicOptions`),
    # `continue_field: bool = Field(None, alias='continue')` will not override the alias_generator of `UnderscoreToDashConfig`.
    # This is a known bug, see https://github.com/samuelcolvin/pydantic/issues/1177.
    continue_field: bool = Field(alias='continue')
    "https://aria2.github.io/manual/en/html/aria2c.html#cmdoption-c"


class BasicOptions(_BasicOptions, metaclass=AllOptional):
    class Config(UnderscoreToDashConfig):
        fields = {'continue_field': 'continue'}


class _HttpFtpSftpOptions(BaseModel):
    """
    https://aria2.github.io/manual/en/html/aria2c.html#http-ftp-sftp-options
    """

    all_proxy: str
    "https://aria2.github.io/manual/en/html/aria2c.html#cmdoption-all-proxy"

    all_proxy_passwd: str
    "https://aria2.github.io/manual/en/html/aria2c.html#cmdoption-all-proxy-passwd"

    all_proxy_user: str
    "https://aria2.github.io/manual/en/html/aria2c.html#cmdoption-all-proxy-user"

    checksum: str
    "https://aria2.github.io/manual/en/html/aria2c.html#cmdoption-checksum"

    connection_timeout: int
    "https://aria2.github.io/manual/en/html/aria2c.html#cmdoption-connect-timeout"

    dry_run: bool
    "https://aria2.github.io/manual/en/html/aria2c.html#cmdoption-dry-run"

    lowest_speed_limit: Union[int, str]
    "https://aria2.github.io/manual/en/html/aria2c.html#cmdoption-lowest-speed-limit"

    max_connection_per_server: int
    "https://aria2.github.io/manual/en/html/aria2c.html#cmdoption-x"

    max_file_not_found: int
    "https://aria2.github.io/manual/en/html/aria2c.html#cmdoption-max-file-not-found"

    max_tries: int
    "https://aria2.github.io/manual/en/html/aria2c.html#cmdoption-m"

    min_split_size: str
    "https://aria2.github.io/manual/en/html/aria2c.html#cmdoption-k"

    netrc_path: str
    "https://aria2.github.io/manual/en/html/aria2c.html#cmdoption-netrc-path"

    no_netrc: bool
    "https://aria2.github.io/manual/en/html/aria2c.html#cmdoption-n"

    no_proxy: str
    "https://aria2.github.io/manual/en/html/aria2c.html#cmdoption-no-proxy"

    out: str
    "https://aria2.github.io/manual/en/html/aria2c.html#cmdoption-o"

    proxy_method: Literal['get', 'tunnel']
    "https://aria2.github.io/manual/en/html/aria2c.html#cmdoption-proxy-method"

    remote_time: bool
    "https://aria2.github.io/manual/en/html/aria2c.html#cmdoption-r"

    reuse_uri: bool
    "https://aria2.github.io/manual/en/html/aria2c.html#cmdoption-reuse-uri"

    retry_wait: int
    "https://aria2.github.io/manual/en/html/aria2c.html#cmdoption-retry-wait"

    server_stat_of: str
    "https://aria2.github.io/manual/en/html/aria2c.html#cmdoption-server-stat-of"

    server_stat_if: str
    "https://aria2.github.io/manual/en/html/aria2c.html#cmdoption-server-stat-if"

    server_stat_timeout: int
    "https://aria2.github.io/manual/en/html/aria2c.html#cmdoption-server-stat-timeout"

    split: int
    "https://aria2.github.io/manual/en/html/aria2c.html#cmdoption-s"

    stream_piece_selector: Literal['default', 'inorder', 'random', 'geom']
    "https://aria2.github.io/manual/en/html/aria2c.html#cmdoption-stream-piece-selector"

    timeout: int
    "https://aria2.github.io/manual/en/html/aria2c.html#cmdoption-t"

    uri_selector: Literal['feedback', 'inorder', 'adaptive']
    "https://aria2.github.io/manual/en/html/aria2c.html#cmdoption-uri-selector"


class HttpFtpSftpOptions(_HttpFtpSftpOptions, metaclass=AllOptional):
    class Config(UnderscoreToDashConfig):
        pass


class _HTTPSpecificOptions(BaseModel):
    """
    https://aria2.github.io/manual/en/html/aria2c.html#http-specific-options
    """

    ca_certificate: str
    "https://aria2.github.io/manual/en/html/aria2c.html#cmdoption-ca-certificate"

    certificate: str
    "https://aria2.github.io/manual/en/html/aria2c.html#cmdoption-certificate"

    check_certificate: bool
    "https://aria2.github.io/manual/en/html/aria2c.html#cmdoption-check-certificate"

    http_accept_gzip: bool
    "https://aria2.github.io/manual/en/html/aria2c.html#cmdoption-http-accept-gzip"

    http_auth_challenge: bool
    "https://aria2.github.io/manual/en/html/aria2c.html#cmdoption-http-auth-challenge"

    http_no_cache: bool
    "https://aria2.github.io/manual/en/html/aria2c.html#cmdoption-http-no-cache"

    http_user: str
    "https://aria2.github.io/manual/en/html/aria2c.html#cmdoption-http-user"

    http_passwd: str
    "https://aria2.github.io/manual/en/html/aria2c.html#cmdoption-http-passwd"

    http_proxy: str
    "https://aria2.github.io/manual/en/html/aria2c.html#cmdoption-http-proxy"

    http_proxy_passwd: str
    "https://aria2.github.io/manual/en/html/aria2c.html#cmdoption-http-proxy-passwd"

    http_proxy_user: str
    "https://aria2.github.io/manual/en/html/aria2c.html#cmdoption-http-proxy-user"

    https_proxy: str
    "https://aria2.github.io/manual/en/html/aria2c.html#cmdoption-https-proxy"

    https_proxy_passwd: str
    "https://aria2.github.io/manual/en/html/aria2c.html#cmdoption-https-proxy-passwd"

    https_proxy_user: str
    "https://aria2.github.io/manual/en/html/aria2c.html#cmdoption-https-proxy-user"

    private_key: str
    "https://aria2.github.io/manual/en/html/aria2c.html#cmdoption-private-key"

    referer: str
    "https://aria2.github.io/manual/en/html/aria2c.html#cmdoption-referer"

    enable_http_keep_alive: bool
    "https://aria2.github.io/manual/en/html/aria2c.html#cmdoption-enable-http-keep-alive"

    enable_http_pipelining: bool
    "https://aria2.github.io/manual/en/html/aria2c.html#cmdoption-enable-http-pipelining"

    header: Union[str, List[str]]
    "https://aria2.github.io/manual/en/html/aria2c.html#cmdoption-header"

    load_cookie: str
    "https://aria2.github.io/manual/en/html/aria2c.html#cmdoption-load-cookies"

    save_cookie: str
    "https://aria2.github.io/manual/en/html/aria2c.html#cmdoption-save-cookies"

    use_head: bool
    "https://aria2.github.io/manual/en/html/aria2c.html#cmdoption-use-head"

    user_agent: str
    "https://aria2.github.io/manual/en/html/aria2c.html#cmdoption-use-head"


class HTTPSpecficOptions(_HTTPSpecificOptions, metaclass=AllOptional):
    class Config(UnderscoreToDashConfig):
        pass


class Options(HTTPSpecficOptions, HttpFtpSftpOptions, BasicOptions):
    pass


if __name__ == '__main__':
    options = Options(**{
        'dir': '1',
        'input-file': 'tt',
        'continue-field': True,
        'dry-run': False,
        'stream-piece-selector': 'default',
    })

    print(options.json(exclude_unset=True, exclude_none=True, by_alias=True))