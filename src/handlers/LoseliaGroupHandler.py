import random
from collections import defaultdict

from MsgTypes import EmojiMsg, ImageMsg, MultiMsg, StringMsg, RecordMsg
from handlers.CommonHandler import CommonGroupHandler, GroupChatState, OneNightState
from Subscribes import GroupEx
from string import Template

class LoseliaGroupHandler(CommonGroupHandler):
    def __init__(self, bot, gid):
        super().__init__(bot, gid)
        self.state = {
            'chat': LoseliaGroupChatState(self, gid),
            '1night': OneNightState(self, gid),
        }


class LoseliaGroupChatState(GroupChatState):
    def __init__(self, hdlr, gid=None):
        super().__init__(hdlr, gid)
        self.group_subscribe_ex = GroupEx(gid)
        self.members = {
            444351271: {'nn': ['露露', '露露佬'], 'tpl': [
                Template('${nn}放屁'),
                Template('${nn}哭哭'),
                Template('${nn}摘星了吗'),
                Template('${nn}今年几岁'),
            ], 'prob': 0.02},
            272001610: {'nn': ['露佬'], 'tpl': [Template('${nn}放屁'), Template('${nn}唱歌')], 'prob': 0.04},
            510553691: {'nn': ['秃哥'], 'tpl': [Template('${nn}上班了吗'), Template('${nn}下班了吗')], 'prob': 0.02},
            839867673: {'nn': ['汐酱'], 'tpl': [Template('${nn}凶凶QAQ')], 'prob': 0.01},
            921255023: {'nn': ['ru佬'], 'tpl': [Template('${nn}单手p歌'), Template('${nn}太强啦')], 'prob': 0.02},
            1762262568: {'nn': ['紫苑神仙'], 'tpl': [Template('${nn}出勤了吗')], 'prob': 0.02},
            1589443608: {'nn': ['r佬'], 'tpl': [Template('${nn}摘星了吗')], 'prob': 0.02},
            137127931: {'nn': ['喵喵'], 'tpl': [Template('${nn}快一键变蠢')], 'prob': 0.02},
            985460698: {'nn': ['小花'], 'tpl': [Template('${nn}又飞升了')], 'prob': 0.02},
            2695671482: {'nn': ['神乐'], 'tpl': [Template('${nn}女装'), Template('${nn}快发瑟图')], 'prob': 0.03},
            1119671753: {'nn': ['兔兔'], 'tpl': [Template('${nn}富婆')], 'prob': 0.02},
            1066379234: {'nn': ['小黑'], 'tpl': [Template('${nn}快发瑟图')], 'prob': 0.03},
            365181628: {'nn': ['鸭锤', '芽佬', '放屁神鸭', '紫苑老公', '渣男鸭'], 'tpl': [
                Template('${nn}泡妞了吗'),
                Template('${nn}好强呀'),
                Template('${nn}真帅，啊我死啦'),
                Template('${nn}放屁好臭'),
                Template('${nn}凶凶QAQ'),
                Template('${nn}贴贴露佬了吗'),
            ], 'prob': 0.04},
            3521953035: {'nn': ['屁股肉大师', '栗子'], 'tpl': [
                Template('${nn}屁股了吗'),
                Template('${nn}怎么还不学习'),
            ], 'prob': 0.03},
            752277065: {'nn': ['千朝'], 'tpl': [Template('${nn}快更专栏')], 'prob': 0.02},
            2308860434: {'nn': ['秃哥粉丝'], 'tpl': [Template('${nn}迫害秃哥了吗')], 'prob': 0.02},
        }
        self.COUNT_PERIOD = 60
        self.prob_decay = 1
        self.chat_count = 0
        self.hdlr.bot.add_repeat_timer(self.COUNT_PERIOD, self.update_prob_decay, False)

    async def on_chat(self, context):
        self.chat_count += 1
        if await self.game_judge(context):
            return
        
        if await self.fixed_reply(context):
            return

        if await self.fixed_roomcode_reply(context):
            return
        
        if await self.query_pixiv(context):
            return

        if await self.query_user_gacha(context):
            return

        if await self.query_card(context):
            return
        
        if await self.query_event(context):
            return
        
        if await self.query_gacha(context):
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
        sender_id = context['sender']['user_id']
        if random.random() < self.members.get(sender_id, {'prob': 0}).get('prob', 0.01) * self.prob_decay:
            s = random.choice([Template('${nn}别放屁啦，快去屁歌吧！')] + self.members[sender_id].get('tpl', []))
            nn = random.choice(self.members[sender_id]['nn'])
            await self.hdlr.bot.send_group_msg(gid, StringMsg(s.substitute(nn=nn)))
            return True
        if ('屁话' in msg or '人话' in msg or '放屁' in msg or '狗话' in msg) and random.randint(0, 1) == 1:
            await self.hdlr.bot.send_group_msg(gid, ImageMsg({'file': f'snapshot/ll_fangpi{random.choice(["","1"])}.png'}))
            return True
        if '撸' in msg and random.randint(0, 7) == 1:
            await self.hdlr.bot.send_group_msg(gid, ImageMsg({'file': 'snapshot/ll_love.jpg'}))
            return True
        if ('白给' in msg or '差点' in msg) and random.randint(0, 1) == 1:
            await self.hdlr.bot.send_group_msg(gid, ImageMsg({'file': 'snapshot/ll_give.jpg'}))
            return True
        if ('妹子' in msg or '女人' in msg or '女的' in msg) and random.randint(0, 3) == 1:
           await self.hdlr.bot.send_group_msg(gid, ImageMsg({'file':'snapshot/ll_girl.jpg'}))
           return True
        if ('gay' in msg or '基友' in msg or '搞基' in msg) and random.randint(0, 1) == 1:
            await self.hdlr.bot.send_group_msg(gid, ImageMsg({'file': 'snapshot/ll_gay.jpg'}))
            return True
        if ('自虐' in msg or 'SM' in msg.upper()) and random.randint(0, 1) == 1:
            await self.hdlr.bot.send_group_msg(gid, ImageMsg({'file': 'snapshot/ll_sm.jpg'}))
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
        self.last_message[gid] = ''
        self.repeat_users[gid].clear()
        await self.hdlr.bot.send_group_msg(gid, StringMsg('别整天复读啦，我要看到露佬smile！'))
        await self.hdlr.bot.send_group_msg(gid, RecordMsg({'file': 'auto_reply/are_you_smiling.mp3'})) 

    async def on_group_changed(self, context, flag):
        if flag:
            await self.hdlr.bot.send_group_msg(context['group_id'], MultiMsg([StringMsg('欢迎新露佬吹！'), ImageMsg({'file': 'kkr/welcome'})]))
        else:
            await self.hdlr.bot.send_group_msg(context['group_id'], StringMsg('露佬吹又少了一个...哭哭QAQ'))
        return {}

    def update_prob_decay(self):
        count_per_second = self.chat_count / self.COUNT_PERIOD
        THRESHOLD = 0.1
        if count_per_second < THRESHOLD:
            self.prob_decay = 1
        else:
            self.prob_decay = THRESHOLD / count_per_second
        self.chat_count = 0

    def enter(self):
        self.hdlr.subscribe(self.group_subscribe_ex, self.on_group_changed)
        super().enter()
    
    def leave(self, target):
        self.hdlr.unsubscribe(self.group_subscribe_ex)
        super().leave(target)
