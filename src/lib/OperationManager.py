import json
import os
import random
import re
import time
from collections import defaultdict

import requests

import const
import Handler
import ImageProcesser
import States
from BestdoriAssets import card, event, gacha
from bilibili_drawcard_spider import Bilibili_DrawCard_Spider
from const import Emojis, Images
from MsgTypes import EmojiMsg, ImageMsg, MultiMsg, RecordMsg, StringMsg
from Subscribes import Any, Group, Nany, Private
from pixiv_crawler import PixivCursor

bds = Bilibili_DrawCard_Spider()

COMPRESS_IMAGE = True

if os.access(os.path.join(const.user_profile_path, 'user_profile.json'), os.R_OK):
    with open(os.path.join(const.user_profile_path, 'user_profile.json'), 'r', encoding='utf-8') as f:
        user_profile = defaultdict(dict)
        user_profile.update(json.load(f))
else:
    user_profile = defaultdict(dict)
    user_profile.update({str(qq_id): {'authority': 'admin'} for qq_id in [444351271, 365181628]})

class OperationManager:

    def __init__(self, bot, preset_keywords={}):
        self.bilibili_drawcard_spider = bds
        self.logger = bot.logger
        self.bot = bot
        self.preset_keywords = preset_keywords or {
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

    async def query_pixiv(self, send_handler, msg, receiver_id):
        res = re.search(r'^看看(.*)?图$', msg.strip())
        if res:
            mmap = {
                '帅': 'female',
                '妹子': 'male',
                '露佬': 'kyaru',
            }
            file_path, meta = PixivCursor.get_one({'mode': mmap.get(res.group(1), 'daily')})
            
            global COMPRESS_IMAGE
            msg = []
            if isinstance(file_path, list):
                if file_path:
                    for file in file_path[:3]:
                        if COMPRESS_IMAGE:
                            f = ImageProcesser.compress(os.path.join('/root/pixiv/', file), isabs=True)
                        msg.append(ImageMsg({'file': f}))
            elif file_path:
                if COMPRESS_IMAGE:
                    file_path = ImageProcesser.compress(os.path.join('/root/pixiv/', file_path), isabs=True)
                msg.append(ImageMsg({'file': file_path}))
            if msg:
                msg.insert(0, StringMsg(f'id: {meta['id']}\nauthor: {meta['user']['id']}, {meta['user']['name']}'))
                await send_handler(receiver_id, MultiMsg(msg))
            else:
                await send_handler(receiver_id, MultiMsg([StringMsg('kkr找不到'), ImageMsg({'file': f'kkr/tuxie'})]))
                return True
        else:
            return False

    async def query_card(self, send_handler, msg, receiver_id):   # send_handler: Bot send handler
        res = re.search(r'^无框(\d+)(\s+(特训前|特训后))?$', msg.strip())
        if res:
            result = card.card_table.select_by_single_value('resourceSetName', id=int(res.group(1)))
            if result:
                resource_set_name = result[0][0]
                if res.group(3) == '特训前':
                    if os.access(os.path.join(const.asset_card_path, f'{resource_set_name}_card_normal.png'), os.R_OK):
                        file_path = f'assets/cards/{resource_set_name}_card_normal.png'
                elif res.group(3) == '特训后':
                    if os.access(os.path.join(const.asset_card_path, f'{resource_set_name}_card_after_training.png'), os.R_OK):
                        file_path = f'assets/cards/{resource_set_name}_card_after_training.png'
                else:
                    file_path = f'assets/cards/{resource_set_name}_card_normal.png' \
                    if os.access(os.path.join(const.asset_card_path, f'{resource_set_name}_card_normal.png'), os.R_OK) \
                    else f'assets/cards/{resource_set_name}_card_after_training.png' \
                    if os.access(os.path.join(const.asset_card_path, f'{resource_set_name}_card_after_training.png'), os.R_OK) \
                    else ''
                if file_path:
                    global COMPRESS_IMAGE
                    if COMPRESS_IMAGE:
                        file_path = ImageProcesser.compress(file_path, 600)

                    await send_handler(receiver_id, ImageMsg({'file': file_path}))
            else:
                await send_handler(receiver_id, MultiMsg([StringMsg('没有这张卡'), ImageMsg({'file': f'kkr/{random.choice(self.preset_keywords["憨批"])}'})]))
            return True
        
        res = re.search(r'^查卡(\d+)(\s+(特训前|特训后))?$', msg.strip())
        if res:
            description, resource_set_name, rarity, attribute, band_id = card._detail(cid=int(res.group(1)))
            if resource_set_name:
                if res.group(3) == '特训前':
                    file_path = ImageProcesser.merge_image(resource_set_name, rarity, attribute, band_id, thumbnail=False, trained=False)
                elif res.group(3) == '特训后':
                    file_path = ImageProcesser.merge_image(resource_set_name, rarity, attribute, band_id, thumbnail=False, trained=True)
                else:
                    file_path = ImageProcesser.merge_image(resource_set_name, rarity, attribute, band_id, thumbnail=False, trained=False) \
                            or ImageProcesser.merge_image(resource_set_name, rarity, attribute, band_id, thumbnail=False, trained=True)
                if file_path:
                    if COMPRESS_IMAGE:
                        file_path = ImageProcesser.compress(file_path, 600)
                    await send_handler(receiver_id, MultiMsg([ImageMsg({'file': file_path}), StringMsg(description)]))
            else:
                await send_handler(receiver_id, MultiMsg([StringMsg('没有这张卡'), ImageMsg({'file': f'kkr/{random.choice(self.preset_keywords["憨批"])}'})]))
            return True
        
        constraints = card._parse_query_command(msg.strip())
        if constraints:
            if constraints == '露佬':
                await send_handler(receiver_id, MultiMsg([StringMsg('再查露佬头都给你锤爆\n'), ImageMsg({'file':'kkr/lulao'})]))
                return True
            results = card.card_table.select('id', 'resourceSetName', 'rarity', 'attribute', 'bandId', 'skillId', 'type', **constraints)
            if results:
                images = [[
                    ImageProcesser.merge_image(r[1], r[2], r[3], r[4]) or
                    ImageProcesser.white_padding(180, 180),
                    ImageProcesser.merge_image(r[1], r[2], r[3], r[4], trained=True) or
                    ImageProcesser.white_padding(180, 180)
                ] for r in results]
                # images = [ImageProcesser.merge_image(r[1], r[2], r[3], r[4]) or ImageProcesser.white_padding(180, 180) for r in results]
                texts = [str(r[0]) + f'({card._skill_types.get(r[5], "未知")}, {card._types.get(r[6], "未知")})' for r in results]
                # fragment
                MAX_NUM = 32
                file_names = [ImageProcesser.thumbnail(
                    images=images[i * MAX_NUM: min((i + 1) * MAX_NUM, len(images))],
                    labels=texts[i * MAX_NUM: min((i + 1) * MAX_NUM, len(images))],
                    label_style={'font_size': 20},
                    col_space=20,
                    row_space=20,
                ) for i in range((len(images) - 1) // MAX_NUM + 1)]
                [await send_handler(receiver_id, ImageMsg({'file': f})) for f in file_names]
            else:
                await send_handler(receiver_id, MultiMsg([StringMsg('kkr找不到'), ImageMsg({'file': f'kkr/tuxie'})]))
            return True
        return False

    async def query_event(self, send_handler, msg, receiver_id):
        res = re.search(r'^活动(\d+)(\s+(日服|国际服|台服|国服|韩服))?$', msg.strip())
        if res:
            detail = event._detail_ver2(int(res.group(1)), event._server[res.group(3) or '国服'])
            if detail is not None:
                await send_handler(receiver_id, MultiMsg(detail))
            else:
                await send_handler(receiver_id, MultiMsg([StringMsg('没有这个活动'), ImageMsg({'file': f'kkr/{random.choice(self.preset_keywords["憨批"])}'})]))
            return True
        
        constraints = event._parse_query_command(msg.strip())
        if constraints is not None:
            results = event.event_table.select('id', 'eventType', 'eventName', 'bannerAssetBundleName', **constraints)
            if results:
                images = [[
                    ImageProcesser.open_nontransparent(os.path.join(const.asset_event_path, 'jp', f'{r[3]}.png')) or
                    ImageProcesser.white_padding(420, 140),
                ] for r in results]
                texts = [f'{r[0]}: {r[2]}' for r in results]
                MAX_NUM = 32
                file_names = [ImageProcesser.thumbnail(images=images[i * MAX_NUM: min((i + 1) * MAX_NUM, len(images))],
                    labels=texts[i * MAX_NUM: min((i + 1) * MAX_NUM, len(images))],
                    label_style={'font_size': 20, 'font_type': 'default_font.ttf'},
                    col_space=20,
                    row_space=20
                ) for i in range((len(images) - 1) // MAX_NUM + 1)]
                [await send_handler(receiver_id, ImageMsg({'file': f})) for f in file_names]
            else:
                await send_handler(receiver_id, MultiMsg([StringMsg('kkr找不到'), ImageMsg({'file': f'kkr/tuxie'})]))
            return True
        return False

    async def query_gacha(self, send_handler, msg, receiver_id):
        res = re.search(r'^卡池(\d+)(\s+(日服|国际服|台服|国服|韩服))?$', msg.strip())
        if res:
            detail = gacha._detail(int(res.group(1)), gacha._server[res.group(3) or '国服'])
            if detail is not None:
                await send_handler(receiver_id, MultiMsg(detail))
            else:
                await send_handler(receiver_id, MultiMsg([StringMsg('没有这个卡池'), ImageMsg({'file': f'kkr/{random.choice(self.preset_keywords["憨批"])}'})]))
            return True
        
        constraints = gacha._parse_query_command(msg.strip())
        if constraints is not None:
            if constraints == {}:
                results = gacha.gacha_table.select_or('id', 'type', 'gachaName', 'bannerAssetBundleName', 'resourceName', type=['permanent', 'limited'], fixed4star=[1])
            else:
                results = gacha.gacha_table.select('id', 'type', 'gachaName', 'bannerAssetBundleName', 'resourceName', **constraints) 
            if results:
                images = [[
                    ImageProcesser.open_nontransparent(os.path.join(const.asset_gacha_path, 'jp', f'{r[3]}.png')) or
                    ImageProcesser.open_nontransparent(os.path.join(const.asset_gacha_path, r[4], 'jp', 'logo.png')) or
                    ImageProcesser.white_padding(420, 140),
                ] for r in results]
                texts = [f'{r[0]}: {r[2]} ({gacha._type[r[1]]})' for r in results]
                MAX_NUM = 32
                file_names = [ImageProcesser.thumbnail(images=images[i * MAX_NUM: min((i + 1) * MAX_NUM, len(images))],
                    image_style={'height': 140},
                    labels=texts[i * MAX_NUM: min((i + 1) * MAX_NUM, len(images))],
                    label_style={'font_size': 20, 'font_type': 'default_font.ttf'},
                    col_space=20,
                    row_space=20
                ) for i in range((len(images) - 1) // MAX_NUM + 1)]
                [await send_handler(receiver_id, ImageMsg({'file': f})) for f in file_names]
            else:
                await send_handler(receiver_id, MultiMsg([StringMsg('kkr找不到'), ImageMsg({'file': f'kkr/tuxie'})]))
            return True
        return False

    async def query_user_gacha(self, send_handler, msg, receiver_id, logger=None):
        if msg == '更新抽卡数据':
            l = self.bilibili_drawcard_spider.fetch_once()
            if not l is None:
                await send_handler(receiver_id, MultiMsg([ImageMsg({'file': f'kkr/nb'}), StringMsg(f'又有新的{l}个出货记录了！')]))
            else:
                await send_handler(receiver_id, StringMsg('更新失败，芽佬快看看怎么啦 QAQ'))
            return True
        else:
            res = re.search(r'^查抽卡名字 (.*?)$', msg)
            self.logger.info(f'{msg}, {res}')
            ret = []
            query = False
            if res:
                self.logger.info(f'query gacha user {res.group(1)}')
                query = True
                ret = self.bilibili_drawcard_spider.get_data_by_username(res.group(1))
                
            else:
                res = re.search(r'^查抽卡id (.*?)$', msg)
                if res:
                    uid = int(res.group(1))
                    self.logger.info(f'query gacha user {uid}')
                    query = True
                    
                    ret = self.bilibili_drawcard_spider.get_data_by_uid(uid)
            
            if not query:
                return False
            
            if not ret:
                await send_handler(receiver_id, MultiMsg([ImageMsg({'file':f'kkr/{random.choice(self.preset_keywords["憨批"])}'}), StringMsg('没出货查什么查')]))
                return True

            images = []
            texts = []
            stringmsg = []
            # self.logger.info(f'gacha result {ret}')
            too_large = False
            if len(ret) > 50:
                ret = ret[:50]
                too_large = True
            for (i, d) in enumerate(ret):
                card_id = d.situation_id
                r = card.card_table.select_by_single_value('id', 'resourceSetName', 'rarity', 'attribute', 'bandId', 'skillId', 'type', id=card_id)[0]
                if r:
                    images.append(ImageProcesser.merge_image(r[1], r[2], r[3], r[4]) or
                        ImageProcesser.white_padding(180, 180))
                    t = time.strftime('%Y/%m/%d %H:%M:%S', time.localtime(d.gacha_at // 1000))
                    s = f'{t}'
                    texts.append(s)
                    stringmsg.append(f'{t}: {d.user_name}({d.user_id}) ==< {d.gacha_name}')

                if (i+1) % 10 == 0:
                    file_name = ImageProcesser.thumbnail(images=images, labels=texts, col_space=40)
                    await send_handler(receiver_id, MultiMsg([ImageMsg({'file': file_name}), StringMsg('\n'.join(stringmsg))]))
                    images = []
                    texts = []
                    stringmsg = []
            
            if images:
                file_name = ImageProcesser.thumbnail(images=images, labels=texts, col_space=40)
                await send_handler(receiver_id, MultiMsg([ImageMsg({'file': file_name}), StringMsg('\n'.join(stringmsg))]))
            
            if too_large:
                await send_handler(receiver_id, MultiMsg([ImageMsg({'file': f'kkr/nb'}), StringMsg('出货的也太多了，kkr好累！下次再查吧！')]))
            return True

    def _submit_room_number(self, number, user_id, raw_msg, source='kkrbot', logger=None):
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

    def _query_room_number(self, logger=None):
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
                self.logger.error('bad reply of bandoristation: %s', r)
            ret.reverse()
            return ret
        else:
            return None

    async def fixed_roomcode_reply(self, send_handler, msg, receiver_id, sender_id, submit_permission=False, logger=None):
        if msg == 'ycm' or msg == '有车吗':
            rl = self._query_room_number()
            if rl is None:
                await send_handler(receiver_id, StringMsg('查车失败，芽佬快看看怎么啦 QAQ'))
            elif rl:
                await send_handler(receiver_id, StringMsg('\n\n'.join(rl)))
            else:
                await send_handler(receiver_id, MultiMsg([ImageMsg({'file':f'kkr/{random.choice(self.preset_keywords["憨批"])}'}), StringMsg('哈哈，没车')]))
            return True
        else:
            if submit_permission or user_profile[str(sender_id)].get('authority') == 'admin':
                res = re.search(r'^([0-9]{5,6})(\s+.+)*(\s+[Qq][0-4])(\s+.+)*$', msg.strip())
                if res:
                    room_code = res.group(1)
                    flag, msg = self._submit_room_number(room_code, sender_id, msg)
                    if flag:
                        await send_handler(receiver_id, MultiMsg([ImageMsg({'file':f'kkr/nb'}), StringMsg('上传车牌啦！')]))
                    else:
                        await send_handler(receiver_id, StringMsg(f'kkr坏了，芽佬快看看QAQ  {msg}'))
                    return True
        return False

    async def fixed_reply(self, send_handler, msg, receiver_id, logger=None):
        be_at = False
        if '[CQ:at,qq=2807901929]' in msg:
            be_at = True
        if msg == '使用说明':
            await send_handler(receiver_id, ImageMsg({'file': ImageProcesser.manual()}))
            return True
        if msg == '底图目录':
            file_name = ImageProcesser.get_back_pics()
            await send_handler(receiver_id, ImageMsg({'file': file_name}))
            return True
        if be_at:
            m = re.compile(r'^(我){0,1}.*?([日草操]|cao|ri).*?([你]|kkr|kokoro){0,1}(.*)$').findall(msg.strip().lower())
            self.logger.info('be_at %s', m)
            if m:
                m = m[0]
                verb = m[1]
                obj = m[2]
                subj = m[0]
                obj2 = m[3]
                if not subj:
                    subj = 'kkr也'
                if obj in ['kkr', 'kokoro']:
                    subj = obj
                    obj = '你'
                final_s = f'{subj}{verb}{obj}{obj2}'
                fn = ImageProcesser.image_merge(47, final_s)
                await send_handler(receiver_id, ImageMsg({'file': fn}))
            else:
                file_path, meta = PixivCursor.get_one({'mode': 'kkr'})
                global COMPRESS_IMAGE
                if isinstance(file_path, list):
                    if file_path:
                        for file in file_path[:3]:
                            if COMPRESS_IMAGE:
                                f = ImageProcesser.compress(os.path.join('/root/pixiv/', file), isabs=True)
                            await send_handler(receiver_id, ImageMsg({'file': f}))
                        return True
                else:
                    if COMPRESS_IMAGE:
                        file_path = ImageProcesser.compress(os.path.join('/root/pixiv/', file_path), isabs=True)
                    await send_handler(receiver_id, ImageMsg({'file': file_path}))
                    return True
        return False

    async def change_back_jpg(self, send_handler, msg, receiver_id, sender_id, logger=None):
        sender_id = str(sender_id)
        back_num = re.compile(r'^底图([0-9]*)$').findall(msg)
        back_num = int(back_num[0]) if back_num else None
        if back_num and back_num in ImageProcesser.CUR_BACK_PIC_SET:
            self.logger.info(f'{sender_id} change back {back_num} success')
            user_profile[sender_id]['cur_back_pic'] = int(back_num)
            await send_handler(receiver_id, StringMsg('已修改'))
            with open(os.path.join(const.user_profile_path, 'user_profile.json'), 'w', encoding='utf-8') as f:
                json.dump(user_profile, f, ensure_ascii=False)
            return True

    async def handle_jpg(self, send_handler, msg, receiver_id, sender_id, logger=None):
        sender_id = str(sender_id)
        if not msg.endswith('.jpg') or '[' in msg:
            return False
        msg = msg[:-4]
        file_name = ImageProcesser.image_merge(user_profile[sender_id].get('cur_back_pic', 31), msg)
        await send_handler(receiver_id, ImageMsg({'file': file_name}))
        return True
