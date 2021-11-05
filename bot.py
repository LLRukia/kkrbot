#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import nonebot
from nonebot.adapters.cqhttp import Bot as CQHTTPBot
from nonebot.log import default_format, logger

import globals

logger.add("app.log", rotation="04:00", diagnose=False, level="INFO", format=default_format)

nonebot.init()
app = nonebot.get_asgi()

driver = nonebot.get_driver()
driver.register_adapter("cqhttp", CQHTTPBot)

nonebot.load_builtin_plugins()
nonebot.load_from_toml("pyproject.toml")


globals.config = driver.config
globals.logger = logger
globals.workpath = os.path.split(os.path.realpath(__file__))[0]

if not os.path.exists(globals.config.datapath):
    os.mkdir(globals.config.datapath)
logger.info(f'datapath loaded from config: {globals.config.datapath}')

globals.datapath = globals.config.datapath
globals.staticpath = os.path.join(globals.workpath, 'static')
globals.user_profile_path = os.path.join(globals.datapath, 'user_profile')
globals.asset_card_path = os.path.join(globals.datapath, 'image', 'assets', 'cards')
globals.asset_card_thumb_path = os.path.join(globals.datapath, 'image', 'assets', 'cards', 'thumb')
globals.asset_event_path = os.path.join(globals.datapath, 'image', 'assets', 'events')
globals.asset_gacha_path = os.path.join(globals.datapath, 'image', 'assets', 'gachas')
globals.asset_resource_path = os.path.join(globals.datapath, 'image', 'assets', 'res')
globals.kkr_id = os.environ.get('KKR_ID', None)

from utils import BestdoriAssets  # noqa
BestdoriAssets.init()

if __name__ == "__main__":
    nonebot.logger.warning("Always use `nb run` to start the bot instead of manually running!")
    nonebot.run(app="__mp_main__:app")
