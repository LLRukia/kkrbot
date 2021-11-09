import os
import random
import re
import time

import globals
import httpx
from nonebot import on_message, on_regex, on_startswith
from nonebot.adapters import Bot, Event
from nonebot.adapters.cqhttp import Message, MessageSegment
from nonebot.matcher import Matcher
from nonebot.rule import Rule
from nonebot.typing import T_State
from utils import ImageProcesser
from utils.Asset import ImageAsset
from utils import BestdoriAssets

ycm = on_regex(r'^(有车吗|ycm)$', block=True, priority=3)


@ycm.handle()
async def handle_query_roomdcode(bot: Bot, event: Event, state: T_State, matcher: Matcher):
    async def _query_room_number():
        async with httpx.AsyncClient() as client:
            r = await client.get('http://api.bandoristation.com/?function=query_room_number')
            try:
                r.raise_for_status()
            except:
                import sys
                sys.excepthook(*sys.exc_info())
                return None
            ret = []
            try:
                d = r.json()['response']
                for room in d:
                    t = int(room['time'])//1000
                    now = time.time()
                    dlts = int(now - t)
                    dltm = 0
                    if dlts > 59:
                        dltm = dlts // 60
                        dlts %= 60
                    if dltm:
                        s = f'{dltm}分{dlts}秒前  '
                    else:
                        s = f'{dlts}秒前  '
                    ret.append((s + room['raw_message']))
            except:
                import sys
                sys.excepthook(*sys.exc_info())
            ret.reverse()
            return ret
    rl = await _query_room_number()
    if rl is None:
        await matcher.send(Message.template("{}{}").format(
            MessageSegment.image(ImageAsset.static_image('kkr/frustrated.gif')),
            f'查车失败，{globals.admin_nickname}快看看怎么啦 QAQ'
        ))
    elif rl:
        await matcher.send(Message.template("{}").format(
            '\n\n'.join(rl)
        ))
    else:
        await matcher.send(Message.template("{}{}").format(
            MessageSegment.image(ImageAsset.random_preset_image('憨批')),
            '哈哈，没车'
        ))


def is_roomcode() -> Rule:
    pattern = re.compile(r'^([0-9]{5,6})(\s+.+)*(\s+[Qq][0-4])(\s+.+)*$')

    async def _regex(bot: "Bot", event: "Event", state: T_State) -> bool:
        if event.get_type() != "message":
            return False
        matched = pattern.search(event.get_plaintext().strip())
        if matched:
            state["_matched"] = matched.group(1)
            return True
        else:
            return False

    return Rule(_regex)


submit_roomcode = on_message(is_roomcode(), block=True, priority=3)


@submit_roomcode.handle()
async def handle_submit_roomdcode(bot: Bot, event: Event, state: T_State, matcher: Matcher):
    room_code = state["_matched"]

    async def _submit_room_number(number, user_id, raw_msg, source='kkrbot', logger=None):
        params = {
            'function': 'submit_room_number',
            'number': number,
            'user_id': user_id,
            'raw_message': raw_msg,
            'source': source,
            'token': 'n59erYT4P',  # This token is only used for kkrbot to submit roomcode
        }
        async with httpx.AsyncClient() as client:
            r = await client.get('http://api.bandoristation.com/', params=params)
            try:
                r.raise_for_status()
            except:
                import sys
                sys.excepthook(*sys.exc_info())
                return False, 'bad_request'
            d = r.json()
            try:
                if d['status'] == 'failure':
                    return False, d['response']
                else:
                    return True, ''
            except Exception as e:
                return False, str(e)

    flag, msg = await _submit_room_number(room_code, event.get_user_id(), event.get_plaintext())
    if flag:
        await matcher.send(Message.template("{}{}").format(
            MessageSegment.image(ImageAsset.static_image(f'kkr/nb.jpg')),
            '上传车牌啦！'
        ))
    else:
        await matcher.send(Message.template("{}{}").format(
            MessageSegment.image(ImageAsset.static_image(f'kkr/grey.jpg')),
            f'kkr坏了，{globals.admin_nickname}快看看QAQ  {msg}'
        ))


def is_querygacha() -> Rule:
    pattern = re.compile(r'^卡池(\d+)(\s+(日服|国际服|台服|国服|韩服))?$')

    async def _regex(bot: "Bot", event: "Event", state: T_State) -> bool:
        if event.get_type() != "message":
            return False
        raw_msg = event.get_plaintext().strip()
        if not raw_msg:
            return False
        matched = pattern.search(raw_msg)
        if matched:
            state["eid"] = int(matched.group(1))
            state["server"] = matched.group(3) or '国服'
            return True
        constraints = BestdoriAssets.gacha._parse_query_command(raw_msg)
        if constraints is not None:
            state["constraints"] = constraints
            return True
        else:
            return False

    return Rule(_regex)


query_gacha = on_message(is_querygacha(), block=True, priority=4)


@query_gacha.handle()
async def handle_query_gacha(bot: Bot, event: Event, state: T_State, matcher: Matcher):
    if 'eid' in state:
        detail = BestdoriAssets.gacha._detail(state['eid'], BestdoriAssets.gacha._server[state['server']])
        if detail is not None:
            await matcher.send(detail)
        else:
            await matcher.send(Message.template("{}{}").format(
                '没有这个卡池',
                MessageSegment.image(ImageAsset.random_preset_image('憨批')),
            ))
    elif 'constraints' in state:
        constraints = state["constraints"]
        if constraints == {}:
            results = BestdoriAssets.gacha.gacha_table.select_or('id', 'type', 'gachaName', 'bannerAssetBundleName', 'resourceName', type=['permanent', 'limited'], fixed4star=[1])
        else:
            results = BestdoriAssets.gacha.gacha_table.select('id', 'type', 'gachaName', 'bannerAssetBundleName', 'resourceName', **constraints)
        if results:
            images = [[
                ImageProcesser.open_nontransparent(os.path.join(globals.asset_gacha_path, 'jp', f'{r[3]}.png')) or
                ImageProcesser.open_nontransparent(os.path.join(globals.asset_gacha_path, r[4], 'jp', 'logo.png')) or
                ImageProcesser.white_padding(420, 140),
            ] for r in results]
            texts = [f'{r[0]}: {r[2]} ({BestdoriAssets.gacha._type[r[1]]})' for r in results]
            MAX_NUM = 32
            thumbnails = [ImageProcesser.thumbnail(images=images[i * MAX_NUM: min((i + 1) * MAX_NUM, len(images))],
                                                   image_style={'height': 140},
                                                   labels=texts[i * MAX_NUM: min((i + 1) * MAX_NUM, len(images))],
                                                   label_style={'font_size': 20, 'font_type': 'default_font.ttf'},
                                                   col_space=20,
                                                   row_space=20
                                                   ) for i in range((len(images) - 1) // MAX_NUM + 1)]
            msg = Message()
            msg.extend([MessageSegment.image(thumbnail) for thumbnail in thumbnails])
            await matcher.send(msg)
        else:
            await matcher.send(Message.template("{}{}").format(
                'kkr找不到',
                MessageSegment.image(ImageAsset.static_image(f'kkr/frustrated.gif'))
            ))


def is_querycard() -> Rule:
    pattern1 = re.compile(r'^无框(\d+)(\s+(特训前|特训后))?$')
    pattern2 = re.compile(r'^查卡(\d+)(\s+(特训前|特训后))?$')

    async def _regex(bot: "Bot", event: "Event", state: T_State) -> bool:
        if event.get_type() != "message":
            return False
        raw_msg = event.get_plaintext().strip()
        if not raw_msg:
            return False
        matched = pattern1.search(raw_msg)
        if matched:
            state["card_id"] = int(matched.group(1))
            if matched.group(3) == '特训前':
                state["is_after_training"] = True
            elif matched.group(3) == '特训后':
                state["is_after_training"] = False
            else:
                state["is_after_training"] = None
            state["is_need_merge"] = False
            return True
        matched = pattern2.search(raw_msg)
        if matched:
            state["card_id"] = int(matched.group(1))
            if matched.group(3) == '特训前':
                state["is_after_training"] = True
            elif matched.group(3) == '特训后':
                state["is_after_training"] = False
            else:
                state["is_after_training"] = None
            state["is_need_merge"] = True
            return True
        constraints = BestdoriAssets.card._parse_query_command(raw_msg)
        if constraints:
            state["constraints"] = constraints
            return True
        else:
            return False

    return Rule(_regex)


query_card = on_message(is_querycard(), block=True, priority=4)


@query_card.handle()
async def handle_query_card(bot: Bot, event: Event, state: T_State, matcher: Matcher):
    if 'card_id' in state:
        if not state['is_need_merge']:
            result = BestdoriAssets.card.card_table.select_by_single_value('resourceSetName', id=state["card_id"])
            if result:
                resource_set_name = result[0][0]
                if state["is_after_training"] is False:
                    if os.access(os.path.join(globals.asset_card_path, f'{resource_set_name}_card_normal.png'), os.R_OK):
                        file_path = f'assets/cards/{resource_set_name}_card_normal.png'
                elif state["is_after_training"] is True:
                    if os.access(os.path.join(globals.asset_card_path, f'{resource_set_name}_card_after_training.png'), os.R_OK):
                        file_path = f'assets/cards/{resource_set_name}_card_after_training.png'
                else:
                    file_path = f'assets/cards/{resource_set_name}_card_normal.png' \
                        if os.access(os.path.join(globals.asset_card_path, f'{resource_set_name}_card_normal.png'), os.R_OK) \
                        else f'assets/cards/{resource_set_name}_card_after_training.png' \
                        if os.access(os.path.join(globals.asset_card_path, f'{resource_set_name}_card_after_training.png'), os.R_OK) \
                        else ''
                if file_path:
                    file_path = ImageProcesser.compress(file_path, 600)
                    await matcher.send(Message.template("{}").format(
                        MessageSegment.image(ImageAsset.image_path(file_path)),
                    ))
                else:
                    await matcher.send(Message.template("{}{}").format(
                        f'好像Bestdori数据不同步啦，{globals.admin_nickname}快看看',
                        MessageSegment.image(ImageAsset.random_preset_image('震惊')),
                    ))
            else:
                await matcher.send(Message.template("{}{}").format(
                    '没有这个卡',
                    MessageSegment.image(ImageAsset.random_preset_image('憨批')),
                ))
        else:
            description, resource_set_name, rarity, attribute, band_id = BestdoriAssets.card._detail(cid=state["card_id"])
            if resource_set_name:
                if state["is_after_training"] is False:
                    file_path = ImageProcesser.merge_image(resource_set_name, rarity, attribute, band_id, thumbnail=False, trained=False)
                if state["is_after_training"] is True:
                    file_path = ImageProcesser.merge_image(resource_set_name, rarity, attribute, band_id, thumbnail=False, trained=True)
                else:
                    file_path = ImageProcesser.merge_image(resource_set_name, rarity, attribute, band_id, thumbnail=False, trained=False) \
                        or ImageProcesser.merge_image(resource_set_name, rarity, attribute, band_id, thumbnail=False, trained=True)
                if file_path:
                    file_path = ImageProcesser.compress(file_path, 600)
                    await matcher.send(Message.template("{}{}").format(
                        MessageSegment.image(ImageAsset.image_path(file_path)),
                        description
                    ))
                else:
                    await matcher.send(Message.template("{}{}").format(
                        f'好像Bestdori数据不同步啦，{globals.admin_nickname}快看看',
                        MessageSegment.image(ImageAsset.random_preset_image('震惊')),
                    ))
            else:
                await matcher.send(Message.template("{}{}").format(
                    '没有这个卡',
                    MessageSegment.image(ImageAsset.random_preset_image('憨批')),
                ))
    elif 'constraints' in state:
        constraints = state["constraints"]
        if constraints == '露佬':
            await matcher.send(Message.template("{}{}").format(
                '再查露佬头都给你锤爆',
                MessageSegment.image(ImageAsset.static_image('kkr/lulao.png')),
            ))
        else:
            results = BestdoriAssets.card.card_table.select('id', 'resourceSetName', 'rarity', 'attribute', 'bandId', 'skillId', 'type', **constraints)
            if results:
                images = [[
                    ImageProcesser.merge_image(r[1], r[2], r[3], r[4]) or
                    ImageProcesser.white_padding(180, 180),
                    ImageProcesser.merge_image(r[1], r[2], r[3], r[4], trained=True) or
                    ImageProcesser.white_padding(180, 180)
                ] for r in results]
                # images = [ImageProcesser.merge_image(r[1], r[2], r[3], r[4]) or ImageProcesser.white_padding(180, 180) for r in results]
                texts = [str(r[0]) + f'({BestdoriAssets.card._skill_types.get(r[5], "未知")}, {BestdoriAssets.card._types.get(r[6], "未知")})' for r in results]
                # fragment
                MAX_NUM = 32
                raw_images = [ImageProcesser.thumbnail(
                    images=images[i * MAX_NUM: min((i + 1) * MAX_NUM, len(images))],
                    labels=texts[i * MAX_NUM: min((i + 1) * MAX_NUM, len(images))],
                    label_style={'font_size': 20},
                    col_space=20,
                    row_space=20,
                ) for i in range((len(images) - 1) // MAX_NUM + 1)]
                [await matcher.send(Message.template("{}").format(MessageSegment.image(x))) for x in raw_images]
            else:
                await matcher.send(Message.template("{}{}").format(
                    'kkr找不到',
                    MessageSegment.image(ImageAsset.random_preset_image('吐血')),
                ))


def is_queryevent() -> Rule:
    pattern = re.compile(r'^活动(\d+)(\s+(日服|国际服|台服|国服|韩服))?$')

    async def _regex(bot: "Bot", event: "Event", state: T_State) -> bool:
        if event.get_type() != "message":
            return False
        raw_msg = event.get_plaintext().strip()
        if not raw_msg:
            return False
        matched = pattern.search(raw_msg)
        if matched:
            state["eid"] = int(matched.group(1))
            state["server"] = matched.group(3) or '国服'
            return True
        constraints = BestdoriAssets.event._parse_query_command(raw_msg)
        if constraints is not None:
            state["constraints"] = constraints
            return True
        else:
            return False

    return Rule(_regex)


query_event = on_message(is_queryevent(), block=True, priority=4)


@query_event.handle()
async def handle_query_event(bot: Bot, event: Event, state: T_State, matcher: Matcher):
    if 'eid' in state:
        detail = BestdoriAssets.event._detail_ver2(state['eid'], BestdoriAssets.gacha._server[state['server']])
        if detail is not None:
            await matcher.send(detail)
        else:
            await matcher.send(Message.template("{}{}").format(
                '没有这个活动',
                MessageSegment.image(ImageAsset.random_preset_image('憨批')),
            ))
    elif 'constraints' in state:
        results = BestdoriAssets.event.event_table.select('id', 'eventType', 'eventName', 'bannerAssetBundleName', **state['constraints'])
        if results:
            images = [[
                ImageProcesser.open_nontransparent(os.path.join(globals.asset_event_path, 'jp', f'{r[3]}.png')) or
                ImageProcesser.white_padding(420, 140),
            ] for r in results]
            texts = [f'{r[0]}: {r[2]}' for r in results]
            MAX_NUM = 32
            raw_images = [ImageProcesser.thumbnail(images=images[i * MAX_NUM: min((i + 1) * MAX_NUM, len(images))],
                                                   labels=texts[i * MAX_NUM: min((i + 1) * MAX_NUM, len(images))],
                                                   label_style={'font_size': 20, 'font_type': 'default_font.ttf'},
                                                   col_space=20,
                                                   row_space=20
                                                   ) for i in range((len(images) - 1) // MAX_NUM + 1)]
            [await matcher.send(Message.template("{}").format(MessageSegment.image(x))) for x in raw_images]
        else:
            await matcher.send(Message.template("{}{}").format(
                'kkr找不到',
                MessageSegment.image(ImageAsset.random_preset_image('吐血')),
            ))
