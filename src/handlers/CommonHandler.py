import copy
import os
import functools
import random
from collections import defaultdict

import const
import Handler
import States
from const import Emojis, Images
from MsgTypes import EmojiMsg, ImageMsg, MultiMsg, RecordMsg, StringMsg
from OperationManager import OperationManager
from Subscribes import Any, Group, Nany, Private


class PrivateChatState(States.BaseState):
    def __init__(self, hdlr, uid=None):
        super().__init__(hdlr)
        self.private_subscribe = Private(uid)
        self.last_message = defaultdict(str)
        self.operator = hdlr.bot.operator

    async def on_chat(self, context):
        pass

    async def query_pixiv(self, context, enable_r18=False):
        msg = context['raw_message']
        uid = context['user_id']
        return await self.operator.query_pixiv(self.hdlr.bot.send_private_msg, msg, uid, enable_r18)

    def enter(self):
        self.hdlr.bot.logger.info(f'{self.__class__.__name__} entered')
        self.hdlr.subscribe(self.private_subscribe, self.on_chat)

    def leave(self, target):
        self.hdlr.ubsubscribe(self.private_subscribe)
        self.hdlr.on_state_changed(target)


class CommonPrivateHandler(Handler.Handler):
    def __init__(self, bot, uid):
        super().__init__(bot)
        self.state = {
            'chat': PrivateChatState(self, uid),
        }

    def begin(self):
        self.state['chat'].enter()


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
            '划': 'skateboard',
            '滑': 'skateboard',
            '我日你妈': 'worinima',
        }
        self.kkr_images = [n for n in os.listdir(os.path.join(
            const.datapath, 'image', 'kkr')) if os.path.isfile(os.path.join(const.datapath, 'image', 'kkr', n))]
        [self.kkr_images.remove(word) for word in ['welcome', 'tql', 'lulao']]
        self.operator = OperationManager(
            self.hdlr.bot, self.preset_keywords)

    async def on_chat(self, context):
        if await self.game_judge(context):
            return

        if await self.fixed_reply(context):
            return

        if await self.fixed_roomcode_reply(context):
            return

        if await self.query_pixiv(context):
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

    async def query_pixiv(self, context, enable_r18=False):
        msg = context['raw_message']
        gid = context['group_id']
        return await self.operator.query_pixiv(self.hdlr.bot.send_group_msg, msg, gid, enable_r18)


    async def game_judge(self, context):
        msg = context['raw_message']
        gid = context['group_id']
        if msg == '玩一夜狼':
            await self.hdlr.bot.send_group_msg(gid, StringMsg('输入"加入"加入游戏，输入"开始"开始游戏，输入"说明"查阅游戏规则，输入"退出"以退出游戏，输入"结束"以结束游戏，发言完毕后输入"查看结果"以结束游戏'))
            self.leave('1night')
            return True

    async def handle_common_chat(self, context):
        msg = context['raw_message']
        gid = context['group_id']
        if ('露佬' in msg and '唱歌' in msg):
            if not random.randint(0, 9):
                await self.hdlr.bot.send_group_msg(gid, RecordMsg({'file': 'auto_reply/xiaoxingxing.silk'}))
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
        await self.hdlr.bot.send_group_msg(gid, ImageMsg({'file': f'kkr/{random.choice(self.preset_keywords["憨批"])}'}))

    async def change_back_jpg(self, context):
        msg = context['raw_message']
        gid = context['group_id']
        uid = context['sender']['user_id']
        return await self.operator.change_back_jpg(self.hdlr.bot.send_group_msg, msg, gid, uid, self.hdlr.bot.logger)

    async def handle_jpg(self, context):
        msg = context['raw_message']
        gid = context['group_id']
        uid = context['sender']['user_id']
        return await self.operator.handle_jpg(self.hdlr.bot.send_group_msg, msg, gid, uid, self.hdlr.bot.logger)

    async def fixed_reply(self, context):
        msg = context['raw_message']
        gid = context['group_id']
        return await self.operator.fixed_reply(self.hdlr.bot.send_group_msg, msg, gid)

    async def fixed_roomcode_reply(self, context):
        msg = context['raw_message']
        gid = context['group_id']
        uid = context['sender']['user_id']
        return await self.operator.fixed_roomcode_reply(self.hdlr.bot.send_group_msg, msg, gid, uid, True, self.hdlr.bot.logger)

    async def query_user_gacha(self, context):
        msg = context['raw_message'].strip()
        gid = context['group_id']
        return await self.operator.query_user_gacha(self.hdlr.bot.send_group_msg, msg, gid, self.hdlr.bot.logger)

    async def query_card(self, context):
        msg = context['raw_message'].strip()
        gid = context['group_id']
        return await self.operator.query_card(self.hdlr.bot.send_group_msg, msg, gid)

    async def query_event(self, context):
        msg = context['raw_message'].strip()
        gid = context['group_id']
        return await self.operator.query_event(self.hdlr.bot.send_group_msg, msg, gid)

    async def query_gacha(self, context):
        msg = context['raw_message'].strip()
        gid = context['group_id']
        return await self.operator.query_gacha(self.hdlr.bot.send_group_msg, msg, gid)

    def enter(self):
        self.hdlr.bot.logger.info(f'{self.__class__.__name__} entered')
        self.hdlr.subscribe(self.group_subscribe, self.on_chat)

    def leave(self, target):
        self.hdlr.unsubscribe(self.group_subscribe)
        self.hdlr.on_state_changed(target)


class OneNightState(States.BaseState):
    _RULE = """1、游戏准备：
所有玩家身份牌库中随机抽取游戏人数+3的身份牌，分发身份后将多余的3张身份牌暗置并编号。
2、游戏开始：
所有玩家确认自己的身份牌，然后暗置。特别注意，这之后除明确要求确认身份的技能效果外，任何玩家不得进行确认身份动作。
3、夜晚行动：
游戏日夜晚各身份依照【狼人-狼先知-爪牙-守夜人-预言家-学徒预言家-强盗-女巫-捣蛋鬼-酒鬼-失眠者-揭示者】的顺序进行行动，技能结算完成后夜晚结束。
4、白天行动：
游戏日白天所有玩家按顺序进行3轮有顺序的讨论，讨论完毕后进行投票，投票结束后进行胜负判定。得到票数最多的人被投出局。如果存在平票，则平票的人都算出局。
5、胜负判定
村民阵营：游戏结束时若至少有1名狼人出局，则村民阵营获得胜利。
狼人阵营：游戏结束时若没有狼人出局，则狼人获胜。爪牙有着特殊的胜利规则，请查看爪牙的具体规则。
"""
    _CHARS = {
        'default': None,
        'Seer': """预言家，在夜晚可以选择行使以下能力之一：
确认1名玩家的身份。
或者确认两张桌面中央卡牌的身份。
Tips:抽到预言家的玩家能够在晚上获取非常重要的信息，如果发现自己被换成狼人，还可以利用自己的信息游戏冒充其他游戏中的角色。""",
        'Werewolf': """狼人，在狼人的行动阶段，所有狼人互相确认身份。(我KKR会私聊告诉你狼人都是谁)
最终成为狼人的玩家要误导其他村民，不在白天被指认出来即为获胜。
Tips:和普通狼人杀不同的是，狼人并没有杀人的能力。抽到狼人卡牌的玩家有可能在晚上被换成村民阵营的身份卡牌，所以暴露自己原来是狼人的身份也不失为一种策略。""",
        'Robber': """强盗，在夜晚必须选择1名玩家并确认其身份，然后与该玩家交换身份牌。
Tips:强盗属于村民阵营，最终成为强盗的玩家需要在白天找出任意一名狼人。强盗在晚上可以知道一名玩家原有的身份，是非常重要的信息点哦""",
        'Troublemaker': """捣蛋鬼，在夜晚必须选择2名玩家，这2名玩家交换身份。
Tips:捣蛋鬼属于村民阵营，最终成为捣蛋鬼的玩家需要在白天找出任意一名狼人。原来是捣蛋鬼的玩家永远不可能在晚上被换成狼人，所以经常成为狼人玩家冒充的对象。""",
        'Villager': """村民，无特殊技能。
Tips:最终成为村民的玩家需要在白天找出任意一名狼人。"""
    }
    _FORMATION = {
        3: ['Seer', 'Robber', 'Troublemaker', 'Werewolf', 'Werewolf', 'Villager'],
        4: ['Seer', 'Robber', 'Troublemaker', 'Werewolf', 'Werewolf', 'Villager', 'Villager'],
    }

    _FLOW = ['Werewolf', 'Seer', 'Robber', 'Troublemaker']

    def __init__(self, hdlr, gid=None):
        super().__init__(hdlr)
        self.group_subscribe = Group(gid)
        self._send_g = functools.partial(self.hdlr.bot.send_group_msg, gid)
        self._send_p = self.hdlr.bot.send_private_msg
        self._confirm_quit = False

    def reset(self):
        self.pn = 0
        self.players = {}
        self.reverse_players = defaultdict(set)
        self._stage = 0
        self._sub_stage = 0
        self.formation = []
        self.private_subscribe = None

    @property
    def sub_stage(self):
        return self._sub_stage
    
    @sub_stage.setter
    def sub_stage(self, v):
        self._sub_stage = v
        while OneNightState._FLOW[self._sub_stage] not in self.reverse_players and self._sub_stage < len(OneNightState._FLOW):
            self._sub_stage += 1
        if self._sub_stage >= len(OneNightState._FLOW):
            self._stage += 1

    async def on_chat(self, context):
        if context['raw_message'] == '结束':
            if self._confirm_quit:
                self.leave('chat')
            else:
                await self._send_g(StringMsg('再次输入以确认结束'))
                self._confirm_quit = True
            return
        self._confirm_quit = False
        if self._stage == 0:
            await self._on_stage_0(context)
        elif self._stage == 2:
            await self._on_stage_2(context)

    async def on_p_chat(self, context):
        if self._stage != 1:
            return
        uid = str(context['sender']['user_id'])
        if uid not in self.players:
            return
        if self.players[uid] != OneNightState._FLOW[self.sub_stage]:
            return
        cur_char = OneNightState._FLOW[self.sub_stage]
        func = getattr(self, '_%s'%(cur_char.lower()))
        await func(context)

    async def _seer(self, context, first=None):
        if first:
            for p in first:
                await self._send_p(first, StringMsg('请给我一个你想查验的人的QQ号(查1名场上的玩家)或者2个1~3之间的数字(使用一个空格隔开)(查2张沉底的身份牌)'))
            return
        msg = context['raw_message']
        uid = str(context['sender']['user_id'])
        msg = msg.strip()
        if msg.find(' ') >= 0:
            msg = msg.split(' ')
            if len(msg) == 2:
                p1, p2 = int(msg[0]), int(msg[1])
                if p1 >=1 and p1 <= 3 and p2 >=1 and p2 <= 3:
                    p1 = self.formation[p1]
                    p2 = self.formation[p2]
                    await self._send_p(uid, StringMsg(f'身份1是{p1}: {OneNightState._CHARS[p1]}'))
                    await self._send_p(uid, StringMsg(f'身份2是{p2}: {OneNightState._CHARS[p2]}'))
                    self.sub_stage += 1
                    return
        else:
            if msg in self.players and msg != uid:
                p = self.players[msg]
                await self._send_p(uid, StringMsg(f'身份是{p}: {OneNightState._CHARS[p]}'))
                self.sub_stage += 1
                return
        await self._send_p(uid, StringMsg('您的输入不合法，请检查'))

    async def _robber(self, context, first=None):
        if first:
            for p in first:
                await self._send_p(first, StringMsg('请给我一个你想抢的人的QQ号'))
            return
        msg = context['raw_message']
        uid = str(context['sender']['user_id'])
        msg = msg.strip()
        
        if msg in self.players and msg != uid:
            p = self.players[msg]
            self.players[msg] = self.players[uid]
            self.players[uid] = p
            await self._send_p(uid, StringMsg(f'你抢来的身份是{p}: {OneNightState._CHARS[p]}'))
            if 'wolf' in p:
                await self._send_p(uid, StringMsg('注意你的胜利条件已经变化'))
            self.sub_stage += 1
            return
        await self._send_p(uid, StringMsg('您的输入不合法，请检查'))

    async def _troublemaker(self, context, first=None):
        if first:
            for p in first:
                await self._send_p(first, StringMsg('请给我2个你想交换身份的人的QQ号(使用一个空格隔开)'))
            return
        msg = context['raw_message']
        uid = str(context['sender']['user_id'])
        msg = msg.strip()
        
        if msg.find(' ') >= 0:
            msg = msg.split(' ')
            if len(msg) == 2:
                p1, p2 = msg[0], msg[1]
                if p1 in self.players and p2 in self.players:
                    p = self.players[p1]
                    self.players[p1] = self.players[p2]
                    self.players[p2] = p
                    await self._send_p(uid, StringMsg('交换成功'))
                    self.sub_stage += 1
                    return
        await self._send_p(uid, StringMsg('您的输入不合法，请检查'))

    async def _on_stage_0(self, context):
        msg = context['raw_message']
        uid = str(context['sender']['user_id'])
        if msg == '开始':
            if len(self.players) < 3:
                await self._send_g(StringMsg('人数不足无法开始游戏，需要至少3人'))
            else:
                await self.start()
        elif msg == '加入':
            if uid in self.players:
                await self._send_g(StringMsg('请勿重复加入'))
            else:
                self.players[uid] = 'default'
        elif msg == '退出':
            if uid not in self.players:
                await self._send_g(MultiMsg([StringMsg('没加入退个锤子'), ImageMsg({'file': f'kkr/worinima'})]))
            else:
                self.players.pop(uid)

    async def start(self):
        self.pn = len(self.players)
        self.formation = copy.deepcopy(OneNightState._FORMATION[self.pn])
        self.private_subscribe = Private(self.players.keys())
        self.hdlr.subscribe(self.private_subscribe, self.on_p_chat)
        wolves = []
        for p in self.players.keys():
            char = random.choice(self.formation)
            if 'wolf' in char:
                wolves.append(p)
            self.formation.remove(char)
            self.players[p] = char
            self.reverse_players[char].add(p)
            await self._send_p(p, StringMsg('你的身份是' + OneNightState._CHARS[char]))
        for p in wolves:
            await self._send_p(p, StringMsg('其他狼人玩家的QQ号是：%s' % (str(wolves))))
        self._stage = 1
        await self._send_g(StringMsg('身份发放完毕，现在天黑请闭眼'))
        self.sub_stage = 0
        self._on_stage_1()

    async def _on_stage_1(self):
        cur_char = OneNightState._FLOW[self.sub_stage]
        func = getattr(self, '_%s'%(cur_char.lower()))
        await func(None, self.reverse_players[cur_char])

    async def _on_stage_2(self, context):
        msg = context['raw_message']
        if msg == '查看结果':
            s = ''
            for k, v in self.players.items():
                s += f'{k}的身份是{v}\n'
            s += f'沉底的身份是:{str(self.formation)}'
            await self._send_g(StringMsg(s))
            self.leave('chat')

    def enter(self):
        self.reset()
        self.hdlr.subscribe(self.group_subscribe, self.on_chat)

    def leave(self, target):
        if self.private_subscribe:
            self.hdlr.ubsubscribe(self.private_subscribe)
        self.hdlr.ubsubscribe(self.group_subscribe)
        self.hdlr.on_state_changed(target)


class CommonGroupHandler(Handler.Handler):
    def __init__(self, bot, gid):
        super().__init__(bot)
        self.state = {
            'chat': GroupChatState(self, gid),
            '1night': OneNightState(self, gid),
        }

    def begin(self):
        self.state['chat'].enter()
