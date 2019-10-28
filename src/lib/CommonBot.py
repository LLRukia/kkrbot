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
        # self.add_timer(5, self.get_status)
        # self.add_repeat_timer(60*30, self.get_status)
        self.add_handler(LoseliaGroupHandler(self, [Groups.LU]))
        self.add_handler(EasyGroupHandler(self, [Groups.ZOO, Groups.YISHANYISHAN]))
        self.begin()

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
                    try:
                        callback and await callback(context)
                    except Exception as e:
                        self.logger.error('on_group_increase, callback error, %s', e)
        return {}

    async def on_group_decrease(self, context):
        self.server.logger.info('on_group_decrease %s', context)
        for hdlr in self.handlers:
            for substype, callback in self._handler_callbacks[hdlr].items():
                if substype.on_group_decrease(context):
                    try:
                        callback and await callback(context)
                    except Exception as e:
                        self.logger.error('on_group_decrease, callback error, %s', e)
        return {}

    async def on_group_message(self, context):
        self.server.logger.info('on_group_message %s', context)
        for hdlr in self.handlers:
            for substype, callback in self._handler_callbacks[hdlr].items():
                if substype.on_group_message(context):
                    try:
                        callback and await callback(context)
                    except Exception as e:
                        self.logger.error('on_group_message, callback error, %s', e)
        return {}

    async def on_private_message(self, context):
        import Cards
        import sqlite3
        self.card_db = Cards.CardDB(sqlite3.connect(os.path.join(const.workpath, 'data', 'cards.db')))

        msg = context['raw_message'].strip()
        gid = context['user_id']
        if gid:# == 365181628:
            res = re.search(r'^无框(\d+)(\s+(特训前|特训后))?$', msg)
            if res:
                result = self.card_db.select_by_single_value('resourceSetName', id=int(res.group(1)))
                if result:
                    resource_set_name = result[0][0]
                    if res.group(3) == '特训前':
                        if os.access(os.path.join(const.datapath, 'image', 'assets', f'{resource_set_name}_card_normal.png'), os.R_OK):
                            file_path = f'assets/{resource_set_name}_card_normal.png'
                    elif res.group(3) == '特训后':
                        if os.access(os.path.join(const.datapath, 'image', 'assets', f'{resource_set_name}_card_after_training.png'), os.R_OK):
                            file_path = f'assets/{resource_set_name}_card_after_training.png'
                    else:
                        file_path = f'assets/{resource_set_name}_card_normal.png' \
                        if os.access(os.path.join(const.datapath, 'image', 'assets', f'{resource_set_name}_card_normal.png'), os.R_OK) \
                        else f'assets/{resource_set_name}_card_after_training.png' \
                        if os.access(os.path.join(const.datapath, 'image', 'assets', f'{resource_set_name}_card_after_training.png'), os.R_OK) \
                        else ''
                    if file_path:
                        await self.send_private_msg(gid, ImageMsg({'file': file_path}))
                else:
                    await self.send_private_msg(gid, StringMsg('无相关卡牌'))
                return True
            
            res = re.search(r'^查卡(\d+)(\s+(特训前|特训后))?$', msg)
            if res:
                description, resource_set_name, rarity, attribute, band_id = self.card_db.detail(cid=int(res.group(1)))
                if resource_set_name:
                    if res.group(3) == '特训前':
                        file_path = ImageProcesser.merge_image(resource_set_name, rarity, attribute, band_id, thumbnail=False, trained=False)
                    elif res.group(3) == '特训后':
                        file_path = ImageProcesser.merge_image(resource_set_name, rarity, attribute, band_id, thumbnail=False, trained=True)
                    else:
                        file_path = ImageProcesser.merge_image(resource_set_name, rarity, attribute, band_id, thumbnail=False, trained=False) \
                                or ImageProcesser.merge_image(resource_set_name, rarity, attribute, band_id, thumbnail=False, trained=True)
                    if file_path:
                        await self.send_private_msg(gid, MultiMsg([ImageMsg({'file': file_path}), StringMsg(description)]))
                else:
                    await self.send_private_msg(gid, StringMsg('无相关卡牌'))
                return True
            
            constraints = Cards.parse(msg.strip())
            if constraints:
                if constraints == '露佬':
                    await self.send_private_msg(gid, MultiMsg([StringMsg('再查露佬头都给你锤爆'), ImageMsg({'file':'kkr/lulao'})]))
                    return True
                results = self.card_db.select('id', 'resourceSetName', 'rarity', 'attribute', 'bandId', 'skillId', 'type', **constraints)
                if results:
                    images = [
                        ImageProcesser.merge_image(r[1], r[2], r[3], r[4]) or
                        ImageProcesser.white_padding(180, 180)
                        for r in results
                    ]
                    images_trained = [
                        ImageProcesser.merge_image(r[1], r[2], r[3], r[4], trained=True) or
                        ImageProcesser.white_padding(180, 180)
                        for r in results
                    ]
                    texts = [str(r[0]) + f'({Cards.skill_type.get(r[5], "未知")}, {Cards.types.get(r[6], "未知")})' for r in results]
                    # fragment
                    MAX_NUM = 32
                    file_names = [ImageProcesser.thumbnail2(
                        images[i * MAX_NUM: min((i + 1) * MAX_NUM, len(images_trained))], 
                        images_trained[i * MAX_NUM: min((i + 1) * MAX_NUM, len(images_trained))], 
                        texts[i * MAX_NUM: min((i + 1) * MAX_NUM, len(images_trained))]) for i in range((len(images_trained) - 1) // MAX_NUM + 1)]
                    [await self.send_private_msg(gid, ImageMsg({'file': f})) for f in file_names]
                else:
                    await self.send_private_msg(gid, StringMsg('无相关卡牌'))
                return True
            return False

        self.logger.info('on_private_message %s', context)
        if context['user_id'] not in [444351271, 365181628]: return {}
        if context['raw_message'].strip().startswith('/'):
            s = context['raw_message'][1:]
            try:
                d = json.loads(s)
            except:
                self.logger.error('exec command failed, %s', s)
            command = d['command']
            
            f = getattr(self, command)
            f and callable(f) and await f(context, d)
        
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
