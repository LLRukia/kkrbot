import os
import random
from collections import defaultdict

import const
import Handler
import ImageProcesser
import States
from const import Emojis, Images
from MsgTypes import EmojiMsg, ImageMsg, MultiMsg, StringMsg, RecordMsg
from Subscribes import Any, Group, Nany, Private
from BestdoriAssets import card, event, gacha
from bilibili_drawcard_spider import Bilibili_DrawCard_Spider
import func

class GroupChatState(States.BaseState):
    def __init__(self, hdlr, gid=None):
        super().__init__(hdlr)
        self.group_subscribe = Group(gid)
        self.last_message = defaultdict(str)
        self.repeat_users = defaultdict(set)
        self.preset_keywords = {
            '粉键': 'pink_note',
            'gkd': 'gkd',
            '沉船': 'stop',
            '氪': ['stop', 'starstone'],
            '太强了': 'tql',
            '太强啦': 'tql',
            'tql': 'tql',
            '憨批': ['hanpi1', 'hanpi2', 'hanpi3'],
            '牛逼': 'nb',
            'nb': 'nb',
            '去世': 'tuxie',
            '吐血': 'tuxie',
            '震撼': 'surprise',
            '想要': 'want',
        }
        self.kkr_images = [n for n in os.listdir(os.path.join(const.datapath, 'image', 'kkr')) if os.path.isfile(os.path.join(const.datapath, 'image', 'kkr', n))]
        [self.kkr_images.remove(word) for word in ['welcome', 'tql', 'lulao']]
        self.hdlr.bot.add_repeat_timer(30*60, func.bilibili_drawcard_spider.fetch_once, False)
    
    async def on_chat(self, context):
        if await self.fixed_reply(context):
            return
       
        if await self.fixed_roomcode_reply(context):
            return
 
        if await self.query_gacha(context):
            return

        if await self.query_card(context):
            return

        if await self.query_event(context):
            return

        if await self.change_back_jpg(context):
            return

        if await self.handle_jpg(context):
            return
        
        if await self.handle_common_chat(context):
            return

        await self.handle_repeat(context)

    async def handle_common_chat(self, context):
        msg = context['raw_message']
        gid = context['group_id']
        if ('露佬' in msg and '唱歌' in msg) and not random.randint(0, 9):
            await self.hdlr.bot.send_group_msg(gid, RecordMsg({'file': 'xiaoxingxing.silk'}))
            return True
        for kwd, fn in self.preset_keywords.items():
            if kwd in msg and not random.randint(0, 4):
                await self.hdlr.bot.send_group_msg(gid, ImageMsg({'file': f'kkr/{fn if type(fn) is str else random.choice(fn)}'}))
                return True
        if not random.randint(0, 9 if ('kkr' in msg.lower() or 'kokoro' in msg.lower()) else 49):
            await self.hdlr.bot.send_group_msg(gid, ImageMsg({'file': f'kkr/{random.choice(self.kkr_images)}'}))
            return True

    async def handle_repeat(self, context):
        msg = context['raw_message']
        gid = str(context['group_id'])
        uid = str(context['sender']['user_id'])
        
        if msg == self.last_message[gid]:
            self.repeat_users[gid].add(uid)
            if len(self.repeat_users[gid]) > 3:
                if random.randint(0, 3) == 1:
                    await self.break_repeat(context)
                else:
                    self.last_message[gid] = ''
                    self.repeat_users[gid].clear()
                    await self.hdlr.bot.server.send(context, message=context['message'])
                return True
        else:
            self.last_message[gid] = msg
            self.repeat_users[gid] = set([uid])
        return False

    async def break_repeat(self, context):
        gid = context['group_id']
        self.last_message[gid] = ''
        self.repeat_users[gid].clear()
        await self.hdlr.bot.send_group_msg(gid, ImageMsg({'file':f'kkr/{random.choice(self.preset_keywords["憨批"])}'}))

    async def change_back_jpg(self, context):
        msg = context['raw_message']
        gid = context['group_id']
        uid = context['sender']['user_id']
        return await func.change_back_jpg(self.hdlr.bot.send_group_msg, msg, gid, uid, func.cur_back_pic, self.hdlr.bot.logger)
    
    async def handle_jpg(self, context):
        msg = context['raw_message']
        gid = context['group_id']
        uid = context['sender']['user_id']
        return await func.handle_jpg(self.hdlr.bot.send_group_msg, msg, gid, uid, func.cur_back_pic, self.hdlr.bot.logger)
    
    async def fixed_reply(self, context):
        msg = context['raw_message']
        gid = context['group_id']
        uid = context['sender']['user_id']
        return await func.fixed_reply(self.hdlr.bot.send_group_msg, msg, gid)

    async def fixed_roomcode_reply(self, context):
        msg = context['raw_message']
        gid = context['group_id']
        uid = context['sender']['user_id']
        return await func.fixed_roomcode_reply(self.hdlr.bot.send_group_msg, msg, gid, uid, self.hdlr.bot.logger)

    async def query_user_gacha(self, context):
        msg = context['raw_message'].strip()
        gid = context['group_id']
        return await func.query_user_gacha(self.hdlr.bot.send_group_msg, msg, gid, self.hdlr.bot.logger)

    async def query_card(self, context):
        msg = context['raw_message'].strip()
        gid = context['group_id']
        return await func.query_card(self.hdlr.bot.send_group_msg, msg, gid)
    
    async def query_event(self, context):
        msg = context['raw_message'].strip()
        gid = context['group_id']
        return await func.query_event(self.hdlr.bot.send_group_msg, msg, gid)
    
    async def query_gacha(self, context):
        msg = context['raw_message'].strip()
        gid = context['group_id']
        return await func.query_gacha(self.hdlr.bot.send_group_msg, msg, gid)
    
    def enter(self):
        self.hdlr.subscribe(self.group_subscribe, self.on_chat)
    
    def leave(self):
        self.hdlr.ubsubscribe(self.group_subscribe)


class CommonGroupHandler(Handler.Handler):
    def __init__(self, bot, gid):
        super().__init__(bot)
        self.state = GroupChatState(self, gid)
    
    def begin(self):
        self.state.enter()
