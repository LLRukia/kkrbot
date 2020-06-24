import json
import os
import re

import const
from BaseBot import Bot
from const import Emojis, Groups, Images
from handlers.LoseliaGroupHandler import LoseliaGroupHandler
from handlers.EasyGroupHandler import EasyGroupHandler
from MsgTypes import EmojiMsg, ImageMsg, MultiMsg, StringMsg, RecordMsg
import ImageProcesser
from OperationManager import OperationManager

class CommonBot(Bot):
    def TO_SUBSCRIBE(self):
        return {
            'notice.group_increase': self.on_group_increase,
            'notice.group_decrease': self.on_group_decrease,
            'message.group': self.on_group_message,
            'message.private': self.on_private_message,
        }

    def __init__(self, server):
        super().__init__(server)
        self.operator = OperationManager(self)
        self.add_handler(LoseliaGroupHandler(self, [Groups.LU]))
        self.add_handler(EasyGroupHandler(self, [Groups.LSJJKX]))
        self.begin()
        self._inited = False

    def lazy_init(self):
        self._inited = True
        self.add_repeat_timer(30*60, self.operator.bilibili_drawcard_spider.fetch_once, False)
        for hdlr in self.handlers:
            hdlr.lazy_init()

    def begin(self):
        super().begin()
        self.logger.info('begin')
        # self.add_timer(5, self.get_status)
        # self.add_repeat_timer(60*30, self.get_status)

    async def get_status(self):
        self.logger.info('get_status')
        info = await self.server.get_status()
        self.logger.info('on_get_status %s', info)
        await self.send_private_msg(444351271, StringMsg(str(info)))

    async def on_group_increase(self, context):
        self.server.logger.info('on_group_increase %s', context)
        for hdlr in self.handlers:
            for substype, callback in self._handler_callbacks[hdlr].items():
                if substype.on_group_increase(context):
                    callback and await callback(context)
        return {}

    async def on_group_decrease(self, context):
        self.server.logger.info('on_group_decrease %s', context)
        for hdlr in self.handlers:
            for substype, callback in self._handler_callbacks[hdlr].items():
                if substype.on_group_decrease(context):
                    callback and await callback(context)
        return {}

    async def on_group_message(self, context):
        if not self._inited:
            self.lazy_init()
        self.server.logger.info('on_group_message %s', context)
        for hdlr in self.handlers:
            for substype, callback in self._handler_callbacks[hdlr].items():
                if substype.on_group_message(context):
                    callback and await callback(context)
        return {}

    async def on_private_message(self, context):
        if not self._inited:
            self.lazy_init()
        self.logger.info('on_private_message %s', context)
        sub_type = context['sub_type']
        if sub_type in ['friend']:
            for hdlr in self.handlers:
                for substype, callback in self._handler_callbacks[hdlr].items():
                    if substype.on_private_message(context):
                        callback and await callback(context)
        elif sub_type in ['group']:
            msg = context['raw_message'].strip()
            uid = context['user_id']
            if await self.operator.fixed_reply(self.send_private_msg, msg, uid):
                self.logger.info('query manual successful')
                return
            if await self.operator.change_back_jpg(self.send_private_msg, msg, uid, uid, self.logger):
                self.logger.info('change back jpg successful')
                return
            if await self.operator.handle_jpg(self.send_private_msg, msg, uid, uid, self.logger):
                self.logger.info('handle jpg successful')
                return
            if await self.operator.query_card(self.send_private_msg, msg, uid):
                self.logger.info('query card successful')
                return
            if await self.operator.query_event(self.send_private_msg, msg, uid):
                self.logger.info('query event successful')
                return
            if await self.operator.query_gacha(self.send_private_msg, msg, uid):
                self.logger.info('query gacha successful')
                return
            if await self.operator.query_user_gacha(self.send_private_msg, msg, uid, self.logger):
                self.logger.info('query user gacha successful')
                return
            if await self.operator.fixed_roomcode_reply(self.send_private_msg, msg, uid, uid, logger=self.logger):
                return

        # if context['raw_message'].strip().startswith('/'):
        #     s = context['raw_message'][1:]
        #     try:
        #         d = json.loads(s)
        #     except:
        #         self.logger.error('exec command failed, %s', s)
        #     command = d['command']
            
        #     f = getattr(self, command)
        #     f and callable(f) and await f(context, d)
        
        return {}

    async def save_pic(self, context, d):
        raw_pic = d['image']
        name = d['name']
        r = re.compile(r'\[CQ:image,file=(.*?\..{3})\]')
        pic = r.findall(raw_pic)[0]
        pic_dict = {
            'file': pic
        }
        setattr(Images, name, pic_dict)

        self.logger.info('Image: %s', ImageMsg(pic_dict).get())
        await self.send_private_msg(context['user_id'], ImageMsg(pic_dict))
