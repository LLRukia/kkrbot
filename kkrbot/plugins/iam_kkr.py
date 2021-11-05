import random
import re
import time

import globals
from nonebot import on_keyword, on_regex, on_startswith
from nonebot.adapters import Bot, Event
from nonebot.adapters.cqhttp import Message, MessageSegment
from nonebot.matcher import Matcher
from nonebot.typing import T_State
from utils import ImageProcesser
from utils.Asset import ImageAsset
from utils.BestdoriAssets import card, event, gacha

if globals.kkr_id:
    at_kkr = on_keyword(f'[CQ:at,qq={globals.kkr_id}', block=True, priority=1)

    @at_kkr.handle()
    async def handle_drawcard_query(bot: Bot, event: Event, state: T_State, matcher: Matcher):
        msg = event.get_plaintext()
        m = re.compile(r'^(我){0,1}.*?([日草操]|cao|ri).*?([你]|kkr|kokoro){0,1}(.*)$').findall(msg.strip().lower())
        if m:
            m = m[0]
            verb = m[1]
            obj = m[2]
            subj = m[0]
            obj2 = m[3]
            if not subj:
                subj = 'kkr也'
            if obj in ['kkr', 'kokoro']:
                subj = obj
                obj = '你'
            final_s = f'{subj}{verb}{obj}{obj2}'
            raw = ImageProcesser.bg_image_gen(47, final_s)
            await matcher.send(Message.template("{}").format(MessageSegment.image(raw)))

help = on_regex(r'^使用说明$', block=True, priority=1)


@help.handle()
async def handle_drawcard_query(bot: Bot, event: Event, state: T_State, matcher: Matcher):
    await matcher.send(Message.template("{}").format(MessageSegment.image(ImageProcesser.manual())))

bg_query = on_regex(r'^底图目录$', block=True, priority=1)


@bg_query.handle()
async def handle_drawcard_query(bot: Bot, event: Event, state: T_State, matcher: Matcher):
    await matcher.send(Message.template("{}").format(MessageSegment.image(ImageProcesser.get_back_pics())))

kkr = on_keyword({'kkr', 'kokoro', 'KKR', 'Kokoro'})
kkr_images = []


@kkr.handle()
async def handle_calling_me(bot: Bot, event: Event, state: T_State, matcher: Matcher):
    if not kkr_images:
        import os
        for _, _, files in os.walk(os.path.join(globals.staticpath, 'kkr')):
            for f in files:
                if f.endswith('.jpg') or f.endswith('.gif'):
                    kkr_images.append(f'kkr/{f}')

    await matcher.send(Message.template("{}").format(MessageSegment.image(ImageAsset.image_path(random.choice(kkr_images)))))
