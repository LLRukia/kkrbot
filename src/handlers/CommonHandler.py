import os
import re
import random
from collections import defaultdict
import sqlite3
import time
import requests

import const
import Handler
import ImageProcesser
import States
from const import Emojis, Images
from MsgTypes import EmojiMsg, ImageMsg, MultiMsg, StringMsg, RecordMsg
from Subscribes import Any, Group, Nany, Private
from BestdoriAssets import card
from bilibili_drawcard_spider import Bilibili_DrawCard_Spider

class GroupChatState(States.BaseState):
    def __init__(self, hdlr, gid=None):
        super().__init__(hdlr)
        self.group_subscribe = Group(gid)
        self.cur_back_jpg = defaultdict(dict)
        self.last_message = defaultdict(str)
        self.repeat_users = defaultdict(set)
        self.preset_keywords = {
            '粉键': 'pink_note',
            'gkd': 'gkd',
            '沉船': 'stop',
            '氪': ['stop', 'kejin'],
            '太强了': 'tql',
            '太强啦': 'tql',
            'tql': 'tql',
            '憨批': ['hanpi1', 'hanpi2', 'hanpi3'],
            '牛逼': 'nb',
            'nb': 'nb',
            '去世': 'tuxie',
            '吐血': 'tuxie',
        }
        self.change_back_pic_regex = re.compile(r'^底图([0-9]*)$')
        self.bilibili_drawcard_spider = Bilibili_DrawCard_Spider()
        self.hdlr.bot.add_repeat_timer(30*60, self.bilibili_drawcard_spider.fetch_once, False)
    
    async def on_chat(self, context):
        if await self.fixed_reply(context):
            return
       
        if await self.fixed_roomcode_reply(context):
            return
 
        if await self.query_gacha(context):
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
        gid = context['group_id']
        if ('露佬' in msg and '唱歌' in msg) and not random.randint(0, 9):
            await self.hdlr.bot.send_group_msg(gid, RecordMsg({'file': 'xiaoxingxing.silk'}))
            return True
        for kwd, fn in self.preset_keywords.items():
            if kwd in msg and not random.randint(0, 4):
                await self.hdlr.bot.send_group_msg(gid, ImageMsg({'file':f'kkr/{fn if type(fn) is str else random.choice(fn)}'}))
                return True
        if not random.randint(0, 9 if ('kkr' in msg.lower() or 'kokoro' in msg.lower()) else 49):
            await self.hdlr.bot.send_group_msg(gid, ImageMsg({'file': f'kkr/{random.randint(1, 16)}'}))
            return True

    async def handle_jpg(self, context):
        msg = context['raw_message']
        gid = context['group_id']
        uid = context['sender']['user_id']
        if not msg.endswith('.jpg') or '[' in msg:
            return False
        msg = msg[:-4]
        file_name = ImageProcesser.image_merge(self.cur_back_jpg[gid].get(uid, 31), msg)
        await self.hdlr.bot.send_group_msg(gid, ImageMsg({'file': file_name}))
        return True

    async def handle_repeat(self, context):
        msg = context['raw_message']
        gid = context['group_id']
        uid = context['sender']['user_id']
        
        if msg == self.last_message[gid]:
            self.repeat_users[gid].add(uid)
            if len(self.repeat_users[gid]) > 3:
                if random.randint(0,3)==1:
                    await self.break_repeat(context)
                else:
                    self.last_message[gid] = ''
                    self.repeat_users[gid].clear()
                    await self.hdlr.bot.server.send(context,message=context['message'])
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
        back_num = self.change_back_pic_regex.findall(msg)
        back_num = int(back_num[0]) if back_num else None
        if back_num and back_num in ImageProcesser.CUR_BACK_PIC_SET:
            self.hdlr.bot.logger.info(f'{uid} change back {back_num} success')
            self.cur_back_jpg[gid][uid] = int(back_num)
            await self.hdlr.bot.send_group_msg(gid, StringMsg('已修改'))
            return True

    async def fixed_reply(self, context):
        msg = context['raw_message']
        gid = context['group_id']
        uid = context['sender']['user_id']
        if msg == '使用说明':
            pass
        if msg == '底图目录':
            file_name = ImageProcesser.get_back_pics()
            await self.hdlr.bot.send_group_msg(gid, ImageMsg({'file': file_name}))
            return True

    async def fixed_roomcode_reply(self, context):
        msg = context['raw_message']
        gid = context['group_id']
        uid = context['sender']['user_id']
        if msg == 'ycm' or msg == '有车吗':
            rl = self._query_room_number()
            if rl is None:
                await self.hdlr.bot.send_group_msg(gid, StringMsg('查车失败，芽佬快看看怎么啦 QAQ'))
            elif rl:
                await self.hdlr.bot.send_group_msg(gid, StringMsg('\n\n'.join(rl)))
            else:
                await self.hdlr.bot.send_group_msg(gid, MultiMsg([ImageMsg({'file':f'kkr/{random.choice(self.preset_keywords["憨批"])}'}), StringMsg('哈哈，没车')]))
            return True
        else:
            res = re.search(r'^(.*?)([0-9]{5,6})(.*?)[Qq][0-4](.*)$', msg.strip())
            if res:
                room_code = res.group(2)
                flag, msg = self._submit_room_number(room_code, uid, msg)
                if flag:
                    await self.hdlr.bot.send_group_msg(gid, MultiMsg([ImageMsg({'file':f'kkr/nb'}), StringMsg('上传车牌啦！')]))
                else:
                    await self.hdlr.bot.send_group_msg(gid, StringMsg(f'kkr坏了，芽佬快看看QAQ  {msg}'))
                return True
        return False

    def _submit_room_number(self, number, user_id, raw_msg, source='kkrbot'):
        payload = {
            'function': 'submit_room_number',
            'number': number,
            'user_id': user_id,
            'raw_message': raw_msg,
            'source': source,
            'token': 'n59erYT4P',
        }
        r = requests.post('http://api.bandoristation.com/', params=payload)
        if r.status_code == 200:
            d = r.json()
            try:
                if d['status'] == 'failure':
                    return False, d['response']
                else:
                    return True, ''
            except Exception as e:
                return False, str(e)
        else:
            return False, 'bad_request'

    def _query_room_number(self):
        r = requests.get('http://api.bandoristation.com/?function=query_room_number')
        if r.status_code == 200:
            ret = []
            try:
                d = r.json()['response']
                for room in d:
                    t = int(room['time'])//1000
                    now = time.time()
                    dlts = int(now - t)
                    dltm = 0
                    if dlts > 59:
                        dltm = dlts // 60
                        dlts %= 60
                    if dltm:
                        s = f'{dltm}分{dlts}秒前  '
                    else:
                        s = f'{dlts}秒前  '
                    ret.append((s + room['raw_message']))
            except:
                self.hdlr.bot.logger.error('bad reply of bandoristation: %s', r)
            ret.reverse()
            return ret
        else:
            return None

    async def query_gacha(self, context):
        msg = context['raw_message'].strip()
        gid = context['group_id']
        if msg == '更新抽卡数据':
            l = self.bilibili_drawcard_spider.fetch_once()
            if not l is None:
                await self.hdlr.bot.send_group_msg(gid, MultiMsg([ImageMsg({'file':f'kkr/nb'}), StringMsg(f'又有新的{l}个出货记录了！')]))
            else:
                await self.hdlr.bot.send_group_msg(gid, StringMsg('更新失败，芽佬快看看怎么啦 QAQ'))
            return True
        else:
            res = re.search(r'^查抽卡名字 (.*?)$', msg)
            self.hdlr.bot.logger.info(f'{msg}, {res}')
            ret = []
            query = False
            if res:
                self.hdlr.bot.logger.info(f'query gacha {res.group(1)}')
                query = True
                ret = self.bilibili_drawcard_spider.get_data_by_username(res.group(1))
                
            else:
                res = re.search(r'^查抽卡id (.*?)$', msg)
                if res:
                    uid = int(res.group(1))
                    self.hdlr.bot.logger.info(f'query gacha {uid}')
                    query = True
                    
                    ret = self.bilibili_drawcard_spider.get_data_by_uid(uid)
            
            if not query:
                return False
            
            if not ret:
                await self.hdlr.bot.send_group_msg(gid, MultiMsg([ImageMsg({'file':f'kkr/{random.choice(self.preset_keywords["憨批"])}'}), StringMsg('没出货查什么查')]))
                return True

            images = []
            texts = []
            stringmsg = []
            self.hdlr.bot.logger.info(f'gacha result {ret}')
            too_large = False
            if len(ret) > 50:
                ret = ret[:50]
                too_large = True
            for (i, d) in enumerate(ret):
                card_id = d.situation_id
                r = card.card_db.select_by_single_value('id', 'resourceSetName', 'rarity', 'attribute', 'bandId', 'skillId', 'type', id=card_id)[0]
                if r:
                    images.append(ImageProcesser.merge_image(r[1], r[2], r[3], r[4]) or
                        ImageProcesser.white_padding(180, 180))
                    t = time.strftime('%Y/%m/%d %H:%M:%S', time.localtime(d.gacha_at // 1000))
                    s = f'{t}'
                    texts.append(s)
                    stringmsg.append(f'{t}: {d.user_name}({d.user_id}) ==< {d.gacha_name}')

                if (i+1) % 10 == 0:
                    file_name = ImageProcesser.thumbnail(images=images, labels=texts, col_space=40)
                    await self.hdlr.bot.send_group_msg(gid, MultiMsg([ImageMsg({'file': file_name}), StringMsg('\n'.join(stringmsg))]))
                    images = []
                    texts = []
                    stringmsg = []
            
            if images:
                file_name = ImageProcesser.thumbnail(images=images, labels=texts, col_space=40)
                await self.hdlr.bot.send_group_msg(gid, MultiMsg([ImageMsg({'file': file_name}), StringMsg('\n'.join(stringmsg))]))
            
            if too_large:
                await self.hdlr.bot.send_group_msg(gid, MultiMsg([ImageMsg({'file':f'kkr/nb'}), StringMsg('出货的也太多了，kkr好累！下次再查吧！')]))
            return True


    async def query_card(self, context):
        msg = context['raw_message'].strip()
        gid = context['group_id']
        return await card.query_card(self.hdlr.bot.send_group_msg, msg, gid)
    
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
