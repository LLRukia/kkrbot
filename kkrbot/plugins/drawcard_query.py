import re
import time

import globals
from nonebot import on_regex, on_startswith, require
from nonebot.adapters import Bot, Event
from nonebot.adapters.cqhttp import Message, MessageSegment
from nonebot.matcher import Matcher
from nonebot.typing import T_State
from utils import ImageProcesser
from utils.Asset import ImageAsset
from utils import BestdoriAssets

scheduler = require('nonebot_plugin_apscheduler').scheduler


@scheduler.scheduled_job('cron', hour='*/2', id='fetch_drawcard_data_hourly')
async def fetch_drawcard_data_hourly():
    from crawlers.BilibiliDrawcardCrawler import drawcard_crawler
    l = await drawcard_crawler.fetch_once()
    globals.logger.info(f'fetch_drawcard_data_hourly successfully get {l}')

drawcard_query = on_startswith('查抽卡名字', block=True, priority=3)


@drawcard_query.handle()
async def handle_drawcard_query(bot: Bot, event: Event, state: T_State, matcher: Matcher):
    from crawlers.BilibiliDrawcardCrawler import drawcard_crawler
    msg = event.get_plaintext()
    res = re.search(r'^查抽卡名字 (.*?)$', msg)
    globals.logger.debug(f'{msg}, {res}')
    ret = []
    query = False
    if res:
        user_name = res.group(1)
        globals.logger.info(f'query gacha user {user_name}')
        ret = drawcard_crawler.get_data_by_username(user_name)
    if not ret:
        await matcher.send(Message.template("{}{}").format(
            MessageSegment.image(ImageAsset.static_image('kkr/haha_hanpi.jpg')),
            '没出货查什么查'
        ))

    images = []
    texts = []
    stringmsg = []
    too_large = False
    if len(ret) > 50:
        ret = ret[:50]
        too_large = True
    for (i, d) in enumerate(ret):
        card_id = d.situation_id
        r = BestdoriAssets.card.card_table.select_by_single_value('id', 'resourceSetName', 'rarity', 'attribute', 'bandId', 'skillId', 'type', id=card_id)[0]
        if r:
            images.append(ImageProcesser.merge_image(r[1], r[2], r[3], r[4]) or
                          ImageProcesser.white_padding(180, 180))
            t = time.strftime('%Y/%m/%d %H:%M:%S', time.localtime(d.gacha_at // 1000))
            s = f'{t}'
            texts.append(s)
            stringmsg.append(f'{t}: {d.user_name}({d.user_id}) ==< {d.gacha_name}')

        if (i+1) % 10 == 0:
            thumb = ImageProcesser.thumbnail(images=images, labels=texts, col_space=40)
            await matcher.send(Message.template("{}{}").format(
                MessageSegment.image(thumb),
                '\n'.join(stringmsg)
            ))
            images = []
            texts = []
            stringmsg = []

    if images:
        thumb = ImageProcesser.thumbnail(images=images, labels=texts, col_space=40)
        await matcher.send(Message.template("{}{}").format(
            MessageSegment.image(thumb),
            '\n'.join(stringmsg)
        ))

    if too_large:
        await matcher.send(Message.template("{}{}").format(
            MessageSegment.image(ImageAsset.static_image('kkr/nb.jpg')),
            '出货的也太多了，kkr好累！下次再查吧！'
        ))


drawcard_update = on_regex(r'^更新抽卡数据$', block=True, priority=3)


@drawcard_update.handle()
async def handle_drawcard_update(bot: Bot, event: Event, state: T_State, matcher: Matcher):
    from crawlers.BilibiliDrawcardCrawler import drawcard_crawler
    l = await drawcard_crawler.fetch_once()
    if l != 0:
        await matcher.send(Message.template("{}{}").format(
            MessageSegment.image(ImageAsset.static_image('kkr/nb.jpg')),
            f'又有新的{l}个出货记录了！'
        ))
    else:
        await matcher.send(Message.template("{}").format(
            f'更新失败，{globals.admin_nickname}快看看怎么啦 QAQ'
        ))
