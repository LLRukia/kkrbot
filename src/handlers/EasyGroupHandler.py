import re
import random
from collections import defaultdict

from MsgTypes import EmojiMsg, ImageMsg, MultiMsg, StringMsg
from handlers.CommonHandler import CommonGroupHandler, GroupChatState

class EasyGroupHandler(CommonGroupHandler):
    def __init__(self, bot, gid):
        super().__init__(bot, gid)
        self.state = EasyGroupChatState(self, gid)

class EasyGroupChatState(GroupChatState):
    def __init__(self, hdlr, gid=None):
        super().__init__(hdlr, gid)
        self.drive_regex = re.compile(r'^[0-9]{5,6}.*?[Qq=].*$')

    async def on_chat(self, context):
        if await self.fixed_reply(context):
            return
        
        if await self.query_card(context):
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
        uid = context['user_id']
        gid = context['group_id']
        if uid == 444351271 and self.drive_regex.match(msg):
            await self.hdlr.bot.send_group_msg(gid, StringMsg(msg))
            return True
        return await super().handle_common_chat(context)