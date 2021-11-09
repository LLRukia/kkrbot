from typing import Optional, Union, List
from typing_extensions import Literal
from pydantic import BaseModel, Field
from utils.pydantic_model_helpers import AllOptional, UnderscoreToDashConfig


class BaseOptionsModel(BaseModel):
    def dict(self, **kwargs):
        """
        Change default kwargs for `dict` method
        """
        kwargs.setdefault('by_alias', True)
        kwargs.setdefault('exclude_unset', True)
        kwargs.setdefault('exclude_none', True)
        return super().dict(**kwargs)

    def json(self, **kwargs):
        """
        Change default kwargs for `json` method
        """
        kwargs.setdefault('by_alias', True)
        kwargs.setdefault('exclude_unset', True)
        kwargs.setdefault('exclude_none', True)
        return super().json(**kwargs)


class OptionsModelConfig(UnderscoreToDashConfig):
    allow_population_by_field_name = True
    """
    Allow using `Options` like this:

    ```
    options = Options(https_proxy='http://localhost:1080')
    ```

    Otherwise, we can only use `Options` by alias like this:

    ```
    options = Options(**{
        'https-proxy': 'http://localhost:1080',
    })
    ```
    """

class BasicOptions(BaseModel):
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

    continue_field: bool = Field(alias='continue')
    """
    https://aria2.github.io/manual/en/html/aria2c.html#cmdoption-c

    Convention: if the option name is a reserved keyword, we add the `_field` suffix to the name as the field

    Note: for derived model (like `BasicOptions`),
    `continue_field: bool = Field(None, alias='continue')` will not override the alias_generator of `UnderscoreToDashConfig`.
    This is a known bug, see https://github.com/samuelcolvin/pydantic/issues/1177.
    """

    class Config(OptionsModelConfig):
        fields = {'continue_field': 'continue'}


class HttpFtpSftpOptions(BaseModel):
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


class HTTPSpecificOptions(BaseModel):
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
    

class Options(BaseOptionsModel, HTTPSpecificOptions, HttpFtpSftpOptions, BasicOptions, metaclass=AllOptional):
    class Config(OptionsModelConfig):
        allow_population_by_field_name = True


if __name__ == '__main__':
    options = Options(
        dir= '1',
        input_file = 'tt',
        dry_run = False,
        stream_piece_selector = 'default',
        continue_field = 1,
    )

    print(options.json())