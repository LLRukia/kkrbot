import json
import os
import random
import re
import time
from collections import defaultdict

import globals
from nonebot import on_keyword, on_regex, require
from nonebot.adapters import Bot, Event
from nonebot.adapters.cqhttp import Message, MessageSegment
from nonebot.matcher import Matcher
from nonebot.plugin import on, on_endswith, on_message
from nonebot.rule import Rule, to_me
from nonebot.typing import T_State
from utils import ImageProcesser, is_group_message, is_poke_message
from utils.Asset import ImageAsset

scheduler = require('nonebot_plugin_apscheduler').scheduler


def is_fucking() -> Rule:
    pattern = re.compile(r'^(我){0,1}.*?([日草操]|cao|ri).*?([你]|kkr|kokoro){0,1}(.*)$')

    async def _regex(bot: "Bot", event: "Event", state: T_State) -> bool:
        if event.get_type() != "message":
            return False
        msg = event.get_plaintext().strip().lower()
        matched = pattern.findall(msg)
        if matched:
            state["matched"] = matched[0]
            return True
        else:
            return False

    return Rule(_regex)


at_kkr = on_message(is_fucking() & to_me(), block=True, priority=2)


@at_kkr.handle()
async def handle_at_kkr(bot: Bot, event: Event, state: T_State, matcher: Matcher):
    subj, verb, obj, obj2 = state["matched"]
    if not subj:
        subj = 'kkr也'
    if obj in ['kkr', 'kokoro']:
        subj = obj
        obj = '你'
    final_s = f'{subj}{verb}{obj}{obj2}'
    raw = ImageAsset.image_raw(ImageProcesser.bg_image_gen(47, final_s))
    await matcher.send(Message.template("{}").format(MessageSegment.image(raw)))

help = on_regex(r'^使用说明$', block=True, priority=1)


@help.handle()
async def handle_help(bot: Bot, event: Event, state: T_State, matcher: Matcher):
    await matcher.send(Message.template("{}").format(MessageSegment.image(ImageProcesser.str_to_pic([
            'ycm/有车吗: 查询车牌(来源: https://bandoristation.com/)',
            '底图目录: 查询底图目录(是的，不仅功能一样，连图都盗过来了，虽然还没更新。底图31，Tsugu！.jpg)',
            '底图+数字: 切换底图',
            'xx.jpg: 图片合成',
            '',
            '以下查询功能数据来源Bestdori',
            '查卡 [稀有度] [颜色] [人物] [乐团] [技能类型]: 按条件筛选符合要求的卡片，同类条件取并集，不同类条件取交集。例如: 查卡 4x pure ksm 分',
            '查卡+数字: 按id查询单卡信息',
            '无框+数字: 按id查询单卡无框卡面',
            '活动列表 [活动类型]: 按条件筛选符合要求的活动，活动类型包括“一般活动”，“竞演LIVE”或“对邦”，“挑战LIVE”或“CP”，“LIVE试炼”，“任务LIVE”',
            '活动+数字 [服务器]: 按id查询单活动信息，默认国服，可选“日服”，“国际服”，“台服”，“国服”，“韩服”',
            '卡池列表 [卡池类型]: 按条件筛选符合要求的卡池，卡池类型包括“常驻”或“无期限”，“限时”或“限定”或“期间限定”，“特殊”（该条件慎加，因为没啥特别的卡池），“必4”',
            '卡池+数字 [服务器]: 按id查询单卡池信息，默认国服，可选“日服”，“国际服”，“台服”，“国服”，“韩服”',
            '',
            '以下查询功能数据来源bilibili开放的豹跳接口，慎用',
            '查抽卡名字 名字: 查用户名称包含该名字的玩家出的4星',
        ], 'manual'))))

bg_query = on_regex(r'^底图目录$', block=True, priority=2)


@bg_query.handle()
async def handle_bg_query(bot: Bot, event: Event, state: T_State, matcher: Matcher):
    await matcher.send(Message.template("{}").format(MessageSegment.image(ImageProcesser.get_back_pics())))


@scheduler.scheduled_job('cron', hour='*/1', id='save_user_profile_hourly')
async def save_user_profile_hourly():
    with open(os.path.join(globals.user_profile_path, 'user_profile.json'), 'w', encoding='utf-8') as f:
        json.dump(globals.user_profile, f, ensure_ascii=False)
    globals.logger.info(f'save_user_profile_hourly successfully {len(globals.user_profile)}')

change_bg = on_regex(r'^底图([0-9]*)$', block=True, priority=2)


@change_bg.handle()
async def handle_change_bg(bot: Bot, event: Event, state: T_State, matcher: Matcher):
    sender_id = event.get_user_id()
    back_num = state['_matched_groups'][0]
    globals.user_profile[sender_id]['cur_back_pic'] = int(back_num)
    raw = ImageAsset.image_raw(ImageProcesser.bg_image_gen(back_num, '改好啦'), f'change_{back_num}_done')
    await matcher.send(Message.template("{}").format(MessageSegment.image(raw)))
    return True


gen_bg_image = on_endswith('.jpg', block=True, priority=2)


@gen_bg_image.handle()
async def handle_gen_bg_image(bot: Bot, event: Event, state: T_State, matcher: Matcher):
    msg = event.get_plaintext()[:-4]
    back_num = globals.user_profile[event.get_user_id()].get('cur_back_pic', 31)
    raw = ImageAsset.image_raw(ImageProcesser.bg_image_gen(back_num, msg), f'bg_{back_num}_{msg}_done')
    await matcher.send(Message.template("{}").format(MessageSegment.image(raw)))

kkr = on_keyword({'kkr', 'kokoro', 'KKR', 'Kokoro'}, priority=10)
kkr_images = []


@kkr.handle()
async def handle_calling_me(bot: Bot, event: Event, state: T_State, matcher: Matcher):
    global kkr_images
    if not kkr_images:
        import os
        for _, _, files in os.walk(os.path.join(globals.staticpath, 'kkr')):
            for f in files:
                if f.endswith('.jpg') or f.endswith('.gif') or f.endswith('.png'):
                    kkr_images.append(os.path.abspath(os.path.join(globals.staticpath, 'kkr', f)))

    if not random.randint(0, 9):
        await matcher.send(Message.template("{}").format(MessageSegment.image(f"file:///{random.choice(kkr_images)}")))
        matcher.stop_propagation()
    else:
        matcher.block = False


repeat_breaker = on_message(is_group_message(), priority=100)

message_cache = {
    'last_message': defaultdict(str),
    'repeat_users': defaultdict(set)
}


@repeat_breaker.handle()
async def handle_repeat_breaker(bot: Bot, event: Event, state: T_State, matcher: Matcher):
    global message_cache

    async def break_repeat():
        message_cache['last_message'][gid] = ''
        message_cache['repeat_users'][gid].clear()
        await matcher.send(Message.template("{}{}").format(
            '别憨了，还搁这当复读机呢',
            MessageSegment.image(ImageAsset.random_preset_image('憨批')),
        ))

    gid = event.group_id
    msg = event.get_plaintext()
    uid = event.get_user_id()
    if msg == message_cache['last_message'][gid]:
        message_cache['repeat_users'][gid].add(uid)
        if len(message_cache['repeat_users'][gid]) > 3:
            if not random.randint(0, 3):
                await break_repeat()
            else:
                message_cache['last_message'][gid] = ''
                message_cache['repeat_users'][gid].clear()
                await matcher.send(event.get_message())
    else:
        message_cache['last_message'][gid] = msg
        message_cache['repeat_users'][gid] = set([uid])


preset_keywords_trigger = on_keyword(ImageAsset.preset.keys(), priority=99)


@preset_keywords_trigger.handle()
async def handle_preset_keywords(bot: Bot, event: Event, state: T_State, matcher: Matcher):
    msg = event.get_plaintext()
    hit_list = []
    for keyword in ImageAsset.preset.keys():
        if keyword in msg:
            hit_list.extend(ImageAsset.preset[keyword])

    if not random.randint(0, 9):
        await matcher.send(Message.template("{}").format(
            MessageSegment.image(ImageAsset.static_image(random.choice(list(set(hit_list))))),
        ))
        matcher.stop_propagation()
    else:
        matcher.block = False


poke = on(rule=is_poke_message() & to_me(), priority=2, block=True)


@poke.handle()
async def handle_poke(bot: Bot, event: Event, state: T_State, matcher: Matcher):
    who = event.get_user_id()

    msg = Message()
    msg.append(MessageSegment.at(who))
    sub_msg = [
        Message([MessageSegment.text('你也想上天？'), MessageSegment.image(ImageAsset.random_preset_image('tql'))]),
        Message([MessageSegment.text('吃我一炮'), MessageSegment.image(ImageAsset.static_image('kkr/rocket.gif'))]),
        Message([MessageSegment.text('欧拉欧拉'), MessageSegment.image(ImageAsset.static_image('kkr/poke.gif'))]),
    ]
    msg.extend(random.choice(sub_msg))
    await matcher.send(msg)
