from typing import Iterable, Optional, Union, Dict
from typing_extensions import Literal


def escape(*code: Iterable[Union[int, str]]):
    return f'\x1b[{";".join([str(c) for c in code])}m'


def escape_foreground(code: int):
    return escape(38, 5, code)


def escape_background(code: int):
    return escape(48, 5, code)


class Color:
    RESET = 0
    BRIGHT = 1
    DIM = 2
    UNDERSCORE = 4
    BLINK = 5
    REVERSE = 7
    HIDDEN = 8

    FG_BLACK = 30
    FG_RED = 31
    FG_GREEN = 32
    FG_YELLOW = 33
    FG_BLUE = 34
    FG_MAGENTA = 35
    FG_CYAN = 36
    FG_WHITE = 37

    BG_BLACK = 40
    BG_RED = 41
    BG_GREEN = 42
    BG_YELLOW = 43
    BG_BLUE = 44
    BG_MAGENTA = 45
    BG_CYAN = 46
    BG_WHITE = 47

    FG_BRIGHT_BLACK = 90
    FG_BRIGHT_RED = 91
    FG_BRIGHT_GREEN = 92
    FG_BRIGHT_YELLOW = 93
    FG_BRIGHT_BLUE = 94
    FG_BRIGHT_MAGENTA = 95
    FG_BRIGHT_CYAN = 96
    FG_BRIGHT_WHITE = 97

    BG_BRIGHT_BLACK = 100
    BG_BRIGHT_RED = 101
    BG_BRIGHT_GREEN = 102
    BG_BRIGHT_YELLOW = 103
    BG_BRIGHT_BLUE = 104
    BG_BRIGHT_MAGENTA = 105
    BG_BRIGHT_CYAN = 106
    BG_BRIGHT_WHITE = 107

ColorOptions = Union[int, Iterable[int], str, Dict[Literal['foreground', 'background'], Optional[int]]]


def get_escaped_code(first_arg: ColorOptions, *codes: Iterable[int]):
    if isinstance(first_arg, int): return escape(first_arg, *codes)

    if isinstance(first_arg, str): return escape(first_arg)

    if isinstance(first_arg, Iterable): return escape(*first_arg)

    foreground, background = first_arg.get('foreground'), first_arg.get('background')
    return f'{escape_foreground(foreground) if foreground else ""}{escape_background(background) if background else ""}'

Message = Union[str, int]


def colored(message: Message, second_arg: ColorOptions, *codes: Iterable[int]):
    if isinstance(second_arg, int): return f'{get_escaped_code(second_arg, *codes)}{message}{escape(Color.RESET)}'

    return f'{get_escaped_code(second_arg)}{message}{escape(Color.RESET)}'


def colored_with_padding(message: Message, options: ColorOptions, *codes: Iterable[int]):
    if isinstance(options, int): return colored(f' {message} ', options, *codes)

    return colored(f' {message} ', options)


black = lambda message: colored(message, Color.FG_BLACK)
red = lambda message: colored(message, Color.FG_RED)
green = lambda message: colored(message, Color.FG_GREEN)
yellow = lambda message: colored(message, Color.FG_YELLOW)
blue = lambda message: colored(message, Color.FG_BLUE)
magenta = lambda message: colored(message, Color.FG_MAGENTA)
cyan = lambda message: colored(message, Color.FG_CYAN)
white = lambda message: colored(message, Color.FG_WHITE)
