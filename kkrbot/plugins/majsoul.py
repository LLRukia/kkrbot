from asyncio.subprocess import STDOUT
import os
import re
import subprocess

from loguru import logger

import globals
from nonebot import on_message, on_regex, on_startswith
from nonebot.adapters import Bot, Event
from nonebot.adapters.cqhttp import Message, MessageSegment
from nonebot.matcher import Matcher
from nonebot.rule import Rule
from nonebot.typing import T_State
from utils import ImageProcesser
from utils.Asset import ImageAsset
from utils import BestdoriAssets

def is_majsoul() -> Rule:
    pattern = re.compile(r'^麻雀 ([0-9zmpsZMPS\+#]+)([ 0-9zmps]*)?$')

    async def _regex(bot: "Bot", event: "Event", state: T_State) -> bool:
        if event.get_type() != "message":
            return False
        matched = pattern.search(event.get_plaintext().strip())
        if matched:
            state["_matched"] = matched.group(1)
            state["dora"] = matched.group(2)
            return True
        else:
            return False

    return Rule(_regex)


majsoul = on_message(is_majsoul(), block=True, priority=3)


@majsoul.handle()
async def handle_majsoul(bot: Bot, event: Event, state: T_State, matcher: Matcher):
    query_string = state["_matched"]
    dora = state["dora"]
    bin_path = os.path.join(globals.workpath, 'utils', 'mahjong-helper')
    if dora:
        query = [bin_path, f'-d={dora}', '-a', '-s', query_string]
    else:
        query = [bin_path, '-a', '-s', query_string]
    try:
        out = subprocess.check_output(query, stderr=STDOUT, timeout=5)
    except subprocess.TimeoutExpired:
        await matcher.send(Message.template("{}{}").format(
            MessageSegment.text('你看看你这叫牌吗？'),
            MessageSegment.image(ImageAsset.random_preset_image('憨批')),
        ))
        return
    await matcher.send(Message.template("{}").format(MessageSegment.image(ImageProcesser.str_to_pic(out.decode('utf8').strip().split('\n')))))
