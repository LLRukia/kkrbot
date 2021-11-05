#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import globals
from nonebot.log import logger, default_format
import nonebot
from nonebot.adapters.cqhttp import Bot as CQHTTPBot

logger.add("app.log", rotation="04:00", diagnose=False, level="INFO", format=default_format)

nonebot.init()
app = nonebot.get_asgi()

driver = nonebot.get_driver()
driver.register_adapter("cqhttp", CQHTTPBot)

nonebot.load_builtin_plugins()
nonebot.load_from_toml("pyproject.toml")


globals.config = driver.config
globals.logger = logger

logger.info(f'datapath loaded from config: {globals.config.datapath}')

if __name__ == "__main__":
    nonebot.logger.warning("Always use `nb run` to start the bot instead of manually running!")
    nonebot.run(app="__mp_main__:app")
