import random
from collections import defaultdict

from MsgTypes import EmojiMsg, ImageMsg, MultiMsg, StringMsg, RecordMsg
from handlers.CommonHandler import CommonGroupHandler, GroupChatState
from Subscribes import GroupEx

class LoseliaGroupHandler(CommonGroupHandler):
    def __init__(self, bot, gid):
        super().__init__(bot, gid)
        self.state = LoseliaGroupChatState(self, gid)
        

class LoseliaGroupChatState(GroupChatState):
    def __init__(self, hdlr, gid=None):
        super().__init__(hdlr, gid)
        self.group_subscribe_ex = GroupEx(gid)
        

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

    async def handle_lavish_loselia(self, context):
        msg = context['raw_message']
        gid = context['group_id']
        if ('屁话' in msg or '人话' in msg or '放屁' in msg or '狗话' in msg) and random.randint(0, 1) == 1:
            await self.hdlr.bot.send_group_msg(gid, MultiMsg([StringMsg('你是说这样的吗'), ImageMsg({'file':f'll_fangpi{random.choice(["","1"])}.png'})]))
            return True
        if '撸' in msg and random.randint(0, 7) == 1:
            await self.hdlr.bot.send_group_msg(gid, ImageMsg({'file':'ll_love.jpg'}))
            return True
        if ('白给' in msg or '差点' in msg) and random.randint(0, 1) == 1:
            await self.hdlr.bot.send_group_msg(gid, ImageMsg({'file':'ll_give.jpg'}))
            return True
        # if ('妹子' in msg or '女人' in msg or '女的' in msg) and random.randint(0, 1) == 1:
        #    await self.hdlr.bot.send_group_msg(gid, ImageMsg({'file':'ll_girl.jpg'}))
        #    return True
        if ('gay' in msg or '基友' in msg or '搞基' in msg) and random.randint(0, 1) == 1:
            await self.hdlr.bot.send_group_msg(gid, ImageMsg({'file':'ll_gay.jpg'}))
            return True
        if ('自虐' in msg or 'SM' in msg.upper()) and random.randint(0, 1) == 1:
            await self.hdlr.bot.send_group_msg(gid, ImageMsg({'file':'ll_sm.jpg'}))
            return True
        if '草' in msg and random.randint(0, 10) == 1:
            await self.hdlr.bot.send_group_msg(gid, StringMsg('草'))
            return True

    async def handle_common_chat(self, context):
        if await self.handle_lavish_loselia(context):
            return True
        
        return await super().handle_common_chat(context)

    async def break_repeat(self, context):
        gid = context['group_id']
        # await self.hdlr.bot.send_group_msg(gid, MultiMsg([StringMsg('别整天复读啦，我要看到露佬smile！'), ImageMsg({'file':'露佬！.jpg'})]))
        self.last_message[gid] = ''
        # self.repeat_times[gid] = 0
        self.repeat_users[gid].clear()
        await self.hdlr.bot.send_group_msg(gid, StringMsg('别整天复读啦，我要看到露佬smile！'))
        await self.hdlr.bot.send_group_msg(gid, RecordMsg({'file':'are_you_smiling.mp3'})) 

    async def on_group_increase(self, context):
        # await self.send_msg_with_context(context, '欢迎新露佬吹！')
        await self.hdlr.bot.send_group_msg(context['group_id'], MultiMsg([StringMsg('欢迎新露佬吹！'), ImageMsg({'file': 'kkr/welcome'})]))
        return {}

    def enter(self):
        self.hdlr.subscribe(self.group_subscribe_ex, self.on_group_increase)
        super().enter()
    
    def leave(self):
        self.hdlr.ubsubscribe(self.group_subscribe_ex)
        super().leave()
