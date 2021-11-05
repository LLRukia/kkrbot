import re

import globals
from nonebot import on_regex, on_startswith, require
from nonebot.adapters import Bot, Event, Message, MessageSegment
from nonebot.matcher import Matcher
from nonebot.typing import T_State

scheduler = require('nonebot_plugin_apscheduler').scheduler


@scheduler.scheduled_job('cron', hour='*/2', id='fetch_drawcard_data_hourly')
async def fetch_drawcard_data_hourly():
    from crawlers.BilibiliDrawcardCrawler import drawcard_crawler
    l = await drawcard_crawler.fetch_once()
    globals.logger.info(f'fetch_drawcard_data_hourly successfully get {l}')

drawcard_query = on_startswith('查抽卡名字')


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
        ret = drawcard_crawler.get_data_by_user(user_name)
        matcher.stop_propagation()
    else:
        matcher.block = False


drawcard_update = on_regex(r'^更新抽卡数据$')


@drawcard_update.handle()
async def handle_drawcard_query(bot: Bot, event: Event, state: T_State, matcher: Matcher):
    from crawlers.BilibiliDrawcardCrawler import drawcard_crawler
    l = await drawcard_crawler.fetch_once()
    if l != 0:
        msg = Message.template('{}{}').format(MessageSegment.image('file///kkr/nb'), f'又有新的{l}个出货记录了！')
        matcher.send(msg)
    else:
        msg = Message.template('{}').format('更新失败，芽佬快看看怎么啦 QAQ')
        matcher.send(msg)
    matcher.stop_propagation()
