import re
import random
from collections import defaultdict

from MsgTypes import EmojiMsg, ImageMsg, MultiMsg, StringMsg
from handlers.CommonHandler import CommonGroupHandler, GroupChatState, OneNightState

class EasyGroupHandler(CommonGroupHandler):
    def __init__(self, bot, gid):
        super().__init__(bot, gid)
        self.state = {
            'chat': GroupChatState(self, gid),
            '1night': OneNightState(self, gid),
        }

class EasyGroupChatState(GroupChatState):
    def __init__(self, hdlr, gid=None):
        super().__init__(hdlr, gid)

    async def on_chat(self, context):
        if await self.game_judge(context):
            return
        
        if await self.fixed_reply(context):
            return
        
        if await self.query_card(context):
            return
        
        if await self.change_back_jpg(context):
            return

        if await self.query_pixiv(context):
            return

        if await self.handle_jpg(context):
            return
        
        if await self.handle_common_chat(context):
            return

        # await self.handle_repeat(context)
