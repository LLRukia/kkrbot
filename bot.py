#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from collections import defaultdict
import os
import sys
import json

import nonebot
from nonebot.adapters.cqhttp import Bot as CQHTTPBot
from nonebot.log import default_format, logger

import globals

logger.add("app.log", rotation="04:00", diagnose=False, level="INFO", format=default_format)

nonebot.init(_env_file='.env.dev')
app = nonebot.get_asgi()

driver = nonebot.get_driver()
driver.register_adapter("cqhttp", CQHTTPBot)

nonebot.load_builtin_plugins()
nonebot.load_from_toml("pyproject.toml")


globals.config = driver.config
globals.logger = logger
globals.workpath = os.path.split(os.path.realpath(__file__))[0]
globals.datapath = globals.config.datapath
globals.staticpath = os.path.join(globals.workpath, 'static')
globals.user_profile_path = os.path.join(globals.datapath, 'user_profile')
globals.asset_card_path = os.path.join(globals.datapath, 'image', 'assets', 'cards')
globals.asset_card_thumb_path = os.path.join(globals.datapath, 'image', 'assets', 'cards', 'thumb')
globals.asset_event_path = os.path.join(globals.datapath, 'image', 'assets', 'events')
globals.asset_gacha_path = os.path.join(globals.datapath, 'image', 'assets', 'gachas')
globals.asset_resource_path = os.path.join(globals.datapath, 'image', 'assets', 'res')
globals.kkr_id = os.environ.get('KKR_ID', None)
globals.admin_nickname = os.environ.get('ADMIN_NICKNAME', '')

logger.info(f'inited datapath: {globals.datapath} kkr_id: {globals.kkr_id}, admin_nickname: {globals.admin_nickname}')

if not os.path.exists(globals.datapath):
    os.mkdir(globals.datapath)
if not os.path.exists(globals.user_profile_path):
    os.mkdir(globals.user_profile_path)

from utils import BestdoriAssets  # noqa

BestdoriAssets.init()
globals.user_profile = defaultdict(dict)
try:
    with open(os.path.join(globals.user_profile_path, 'user_profile.json'), 'r', encoding='utf-8') as f:
        globals.user_profile.update(json.load(f))
except OSError:
    pass

if __name__ == "__main__":
    nonebot.logger.warning("Always use `nb run` to start the bot instead of manually running!")
    nonebot.run(app="__mp_main__:app")
