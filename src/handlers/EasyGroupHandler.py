import re
import random
from collections import defaultdict

from MsgTypes import EmojiMsg, ImageMsg, MultiMsg, StringMsg
from handlers.CommonHandler import CommonGroupHandler, GroupChatState

class EasyGroupHandler(CommonGroupHandler):
    def __init__(self, bot, gid):
        super().__init__(bot, gid)
        self.state = {
            'chat': EasyGroupChatState(self, gid),
        }

class EasyGroupChatState(GroupChatState):
    def __init__(self, hdlr, gid=None):
        super().__init__(hdlr, gid)

    async def on_chat(self, context):
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
