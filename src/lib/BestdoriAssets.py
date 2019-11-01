import os
import re
import sqlite3
import json
import collections
import datetime
from PIL import Image

import const
import ImageProcesser
from MsgTypes import EmojiMsg, ImageMsg, MultiMsg, StringMsg, RecordMsg

from crawler import CardTable

class CardDB:
    def __init__(self, conn):
        self.conn = conn
    
    def select_by_single_value(self, *column, **constraint):
        col_exp = '*' if not column else ','.join(column)
        if constraint:
            return self.conn.execute(f'''
                select {col_exp} from card where {' and '.join([k+'=?' for k in constraint.keys()])} order by id asc
            ''', tuple(constraint.values())).fetchall()
        else:
            return self.conn.execute(f'select {col_exp} from card').fetchall()

    def select(self, *column, **constraint):
        col_exp = '*' if not column else ','.join(column)
        if constraint:
            return self.conn.execute(f'''
                select {col_exp} from card where {' and '.join([k+' in ({})'.format(','.join('?'*len(constraint[k]))) for k in constraint.keys()])} order by id asc
            ''', [v for k, vs in constraint.items() for v in vs]).fetchall()
        else:
            return self.conn.execute(f'select {col_exp} from card').fetchall()

    def close(self):
        self.conn.close()
    
    def __del__(self):
        self.close()

class Card:
    def __init__(self):
        # self.card_db = CardDB(sqlite3.connect(os.path.join(const.workpath, 'data', 'bestdori.db')))
        self.card_db = CardTable(os.path.join(const.workpath, 'data', 'bestdori.db'))
        self._mapping = {
            'characterId': {
                '户山香澄': 1,'香澄': 1, 'kasumi': 1, 'ksm': 1,
                '花园多惠': 2, '多惠': 2, 'tae': 2, 'otae': 2, ''
                '牛込里美': 3, '里美': 3, 'rimi': 3,
                '山吹沙绫': 4, '沙绫': 4, 'saya': 4,
                '市谷有咲': 5,'有咲': 5, 'arisa': 5, 'ars': 5,
                '美竹兰': 6, '兰': 6, 'ran': 6,
                '青叶摩卡': 7, '摩卡': 7, 'moca': 7,
                '上原绯玛丽': 8, '绯玛丽': 8, 'hmr': 8, 'himari': 8,
                '宇田川巴': 9, '巴': 9, 'tomoe': 9,
                '羽泽鸫': 10, '鸫': 10, 'tsugumi': 10, 'tgm': 10, 
                '弦卷心': 11, '心': 11, 'kkr': 11, 'kokoro': 11,
                '濑田薰': 12, '薰': 12, 'kaoru': 12, 'kor': 12,
                '北泽育美': 13, '育美': 13, 'hagumi': 13, 'hgm': 13,
                '松原花音': 14, '花音': 14, 'kanon': 14,
                '奥泽美咲': 15, '米歇尔': 15, '美咲': 15, 'misaki': 15, 'msk': 15,
                '丸山彩': 16, '彩': 16, 'aya': 16,
                '冰川日菜': 17, '日菜': 17, 'hina': 17,
                '白鹭千圣': 18, '千圣': 18, 'chisato': 18, 'cst': 18,
                '大和麻弥': 19, '麻弥': 19, 'maya': 19,
                '若宫伊芙': 20, '伊芙': 20, 'eve': 20,
                '凑友希那': 21, '友希那': 21, 'yukina': 21, 'ykn': 21,
                '冰川纱夜': 22, '纱夜': 22, 'sayo': 22,
                '今井莉莎': 23, '莉莎': 23, 'lisa': 23,
                '宇田川亚子': 24, '亚子': 24, 'ako': 24,
                '白金燐子': 25, '燐子': 25, 'rinko': 25,
            },
            'bandId': {
                'ppp': 1,
                'ag': 2, 'afterglow': 2,
                'hhw': 3,
                'pp': 4,
                'roselia': 5
            },
            'rarity': {
                '1x': 1, '一星': 1, '1星': 1,
                '2x': 2, '二星': 2, '2星': 2,
                '3x': 3, '三星': 3, '3星': 3,
                '4x': 4, '四星': 4, '4星': 4,
            },
            'attribute': {
                'powerful': 'powerful', '红': 'powerful',
                'cool': 'cool', '蓝': 'cool',
                'happy': 'happy', '橙': 'happy',
                'pure': 'pure', '绿': 'pure',
            },
            'type': {
                '初始': 'initial',
                '无期限': 'permanent',
                '限定': 'limited', '期间限定': 'limited',
                '活动': 'event',
                '联名合作': 'campaign',
                '其他': 'others',
            },
            'skillId': {
                '分': [1, 2, 3, 4, 17, 18, 20, 21, 22, 25, 26], '分卡': [1, 2, 3, 4, 17, 18, 20, 21, 22, 25, 26],
                '奶': [8, 9, 10, 13, 14, 15, 16], '奶卡': [8, 9, 10, 13, 14, 15, 16], 
                '判': [5, 6, 7, 11, 12, 15, 16], '判卡': [5, 6, 7, 11, 12, 15, 16],
                '盾': [23, 24], '盾卡': [23, 24],
                '115': 20, '115分': 20,
                '110': [18, 26], '110分': [18, 26],
                '100': 4, '100分': 4,
            }
        }

        with open(os.path.join(const.workpath, 'data', 'json', 'all_skills.json'), 'r', encoding='utf-8') as f:
            self._all_skills = json.load(f)
        
        self._types = {
            'initial': '初始',
            'permanent': '无期限',
            'limited': '期间限定',
            'event': '活动',
            'campaign': '联名合作',
            'others': '其他',
        }

        self._skill_types = {
            1: '10%分',
            2: '30%分',
            3: '60%分',
            4: '100%分',
            5: 'great判&10%分',
            6: 'good判&20%分',
            7: 'bad判&40%分',
            8: '300奶&10%分',
            9: '450奶&20%分',
            10: '750奶&40%分',
            11: 'great判&30%分',
            12: 'good判&60%分',
            13: '300奶&30%分',
            14: '450奶&60%分',
            15: '300奶&great判',
            16: '450奶&good判',
            17: '65%分|55%分(900)',
            18: '110%分|90%分(900)',
            20: '115%分',
            21: '40%分|450奶(600)',
            22: '80%分|500奶(600)',
            23: '盾|10%分',
            24: '盾|30%分',
            25: '65%分|55%分(great)',
            26: '110%分|90%分(great)',
        }
    
    def _parse_query_command(self, string):
        string = string.split()
        if string[0] == '查卡' and len(string) > 1: # avoid query of all cards
            constraint = collections.OrderedDict()
            for c in string[1:]:
                valid_parameter = False
                if c == '露佬':
                    return '露佬'
                for attribute, attribute2id in self._mapping.items():
                    if c.lower() in attribute2id:
                        if constraint.get(attribute) is None:
                            constraint[attribute] = []
                        if type(attribute2id[c.lower()]) is list:
                            constraint[attribute] += attribute2id[c.lower()]
                        else:
                            constraint[attribute].append(attribute2id[c.lower()])
                        valid_parameter = True
                        break
                if not valid_parameter:
                    return {}
            return constraint
    
    def _detail(self, cid):
        try:
            name, skill_id, performance, technique, visual, type_, resource_set_name, rarity, attribute, band_id = self.card_db.select_by_single_value(
                'name', 'skillId', 'performance', 'technique', 'visual', 'type', 
                'resourceSetName', 'rarity', 'attribute', 'bandId',
                id=cid)[0]
        except:
            return '', '', -1, '', -1
        else:
            skill_id = str(skill_id)
            skill_description = self._all_skills[skill_id]['simpleDescription'][3] or self._all_skills[skill_id]['simpleDescription'][0] or self._all_skills[skill_id]['simpleDescription'][2] or self._all_skills[skill_id]['simpleDescription'][1]
            skill_description = skill_description.replace('\n', '') + f' ({",".join([str(round(n, 1)) for n in self._all_skills[skill_id]["duration"]])})'
            overall = f'{performance}/{technique}/{visual}/{performance + technique + visual}'
            return f'\n标题: {name}\n种类: {self._types[type_]}\n三围: {overall}\n技能: {skill_description}', resource_set_name, rarity, attribute, band_id
    
    async def query_card(self, send_handler, msg, receiver_id):   # send_handler: Bot send handler
        res = re.search(r'^无框(\d+)(\s+(特训前|特训后))?$', msg.strip())
        if res:
            result = self.card_db.select_by_single_value('resourceSetName', id=int(res.group(1)))
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
                    await send_handler(receiver_id, ImageMsg({'file': file_path}))
            else:
                await send_handler(receiver_id, StringMsg('无相关卡牌'))
            return True
        
        res = re.search(r'^查卡(\d+)(\s+(特训前|特训后))?$', msg.strip())
        if res:
            description, resource_set_name, rarity, attribute, band_id = self._detail(cid=int(res.group(1)))
            if resource_set_name:
                if res.group(3) == '特训前':
                    file_path = ImageProcesser.merge_image(resource_set_name, rarity, attribute, band_id, thumbnail=False, trained=False)
                elif res.group(3) == '特训后':
                    file_path = ImageProcesser.merge_image(resource_set_name, rarity, attribute, band_id, thumbnail=False, trained=True)
                else:
                    file_path = ImageProcesser.merge_image(resource_set_name, rarity, attribute, band_id, thumbnail=False, trained=False) \
                            or ImageProcesser.merge_image(resource_set_name, rarity, attribute, band_id, thumbnail=False, trained=True)
                if file_path:
                    await send_handler(receiver_id, MultiMsg([ImageMsg({'file': file_path}), StringMsg(description)]))
            else:
                await send_handler(receiver_id, StringMsg('无相关卡牌'))
            return True
        
        constraints = self._parse_query_command(msg.strip())
        if constraints:
            if constraints == '露佬':
                await send_handler(receiver_id, MultiMsg([StringMsg('再查露佬头都给你锤爆'), ImageMsg({'file':'kkr/lulao'})]))
                return True
            results = self.card_db.select('id', 'resourceSetName', 'rarity', 'attribute', 'bandId', 'skillId', 'type', **constraints)
            if results:
                images = [[
                    ImageProcesser.merge_image(r[1], r[2], r[3], r[4]) or
                    ImageProcesser.white_padding(180, 180),
                    ImageProcesser.merge_image(r[1], r[2], r[3], r[4], trained=True) or
                    ImageProcesser.white_padding(180, 180)
                ] for r in results]
                # images = [ImageProcesser.merge_image(r[1], r[2], r[3], r[4]) or ImageProcesser.white_padding(180, 180) for r in results]
                texts = [str(r[0]) + f'({self._skill_types.get(r[5], "未知")}, {self._types.get(r[6], "未知")})' for r in results]
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
                await send_handler(receiver_id, StringMsg('无相关卡牌'))
            return True
        return False

from crawler import EventTable

class Event:
    def __init__(self, card_table):
        self.event_table = EventTable(os.path.join(const.workpath, 'data', 'bestdori.db'))
        self.card_table = card_table
        self._mapping = {
            'attribute': {
                'powerful': 'powerful', '红': 'powerful',
                'cool': 'cool', '蓝': 'cool',
                'happy': 'happy', '橙': 'happy',
                'pure': 'pure', '绿': 'pure',
            },
            'eventType': {
                '一般活动': 'story',
                '竞演LIVE': 'versus', '对邦': 'versus',
                '挑战LIVE': 'challenge', 'cp': 'challenge',
                'LIVE试炼': 'live_try',
                '任务LIVE': 'mission_live',
            },
        }
        self._type = {
            'story': '一般活动',
            'versus': '竞演LIVE',
            'challenge': '挑战LIVE',
            'live_try': 'LIVE试炼',
            'mission_live': '任务LIVE',
        }
        self._server = {
            '日服': 0,
            '国际服': 1,
            '台服': 2,
            '国服': 3,
        }
        self._server_name = {
            0: 'jp',
            1: 'en',
            2: 'tw',
            3: 'cn',
        }

    def _parse_query_command(self, string):
        string = string.split()
        if string[0] == '活动列表':
            constraint = collections.OrderedDict()
            for c in string[1:]:
                valid_parameter = False
                for attribute, attribute2id in self._mapping.items():
                    if c.lower() in attribute2id:
                        if constraint.get(attribute) is None:
                            constraint[attribute] = []
                        if type(attribute2id[c.lower()]) is list:
                            constraint[attribute] += attribute2id[c.lower()]
                        else:
                            constraint[attribute].append(attribute2id[c.lower()])
                        valid_parameter = True
                        break
                if not valid_parameter:
                    return None
            return constraint
    
    def _detail(self, eid, server):
        banner_asset_bundle_name, = self.event_table.select_by_single_value('bannerAssetBundleName', id=eid)[0]
        if banner_asset_bundle_name:
            detail = []
            with open(os.path.join(const.workpath, 'data', 'json', 'events', f'{eid}.json'), 'r', encoding='utf-8') as f:
                event_data = json.load(f)
            if event_data["startAt"][server]:
                file_path = f'assets/events/{self._server_name[server]}/{banner_asset_bundle_name}.png'
                if os.access(os.path.join(const.asset_event_path, self._server_name[server], f'{banner_asset_bundle_name}.png'), os.R_OK):
                    detail.append(ImageMsg({'file': file_path}))
                detail.append(StringMsg('\n' + '\n'.join([f'{key}: {value}' for key, value in {
                    '标题': event_data['eventName'][server],
                    '种类': self._type[event_data['eventType']],
                    '开始时间': f'{(datetime.datetime.utcfromtimestamp(int(event_data["startAt"][server]) // 1000) + datetime.timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")}(北京时间)',
                    '结束时间': f'{(datetime.datetime.utcfromtimestamp(int(event_data["endAt"][server]) // 1000) + datetime.timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")}(北京时间)',
                }.items()])))

                detail.append(StringMsg('\n属性: '))
                [(detail.append(ImageMsg({'file': f'assets/res/{a["attribute"]}.png'})), detail.append(StringMsg(f'+{a["percent"]}%'))) for a in event_data['attributes']]
                
                detail.append(StringMsg('\n角色: '))
                c0 = event_data['characters'][0]
                for c in event_data['characters'][1:]:
                    if c['percent'] != c0['percent']:
                        [(detail.append(ImageMsg({'file': f'assets/res/chara_icon_{c["characterId"]}.png'})), detail.append(StringMsg(f'+{c["percent"]}%'))) for c in event_data['characters']]
                        c0 = None
                        break
                else:
                    [detail.append(ImageMsg({'file': f'assets/res/chara_icon_{c["characterId"]}.png'})) for c in event_data['characters']]
                    detail.append(StringMsg(f'+{c0["percent"]}%'))
                
                detail.append(StringMsg('\n奖励: '))
                cards = self.card_table.select('resourceSetName', 'rarity', 'attribute', 'bandId', id=event_data['rewardCards'])
                filenames = [ImageProcesser.merge_image(c[0], c[1], c[2], c[3], thumbnail=True, trained=False, return_fn=True) for c in cards]
                [detail.append(ImageMsg({'file': f})) for f in filenames]
                [detail.append(StringMsg(f'(卡牌id: {",".join([str(i) for i in event_data["rewardCards"]])})'))]
            else:
                detail.append(StringMsg('活动尚未开始'))
            return detail
    
    def _detail_ver2(self, eid, server):
        res = self.event_table.select_by_single_value('bannerAssetBundleName', id=eid)
        if res:
            banner_asset_bundle_name, = res[0]
            if banner_asset_bundle_name:
                detail = []
                with open(os.path.join(const.workpath, 'data', 'json', 'events', f'{eid}.json'), 'r', encoding='utf-8') as f:
                    event_data = json.load(f)
                if event_data["startAt"][server]:
                    file_path = f'assets/events/{self._server_name[server]}/{banner_asset_bundle_name}.png'
                    if os.access(os.path.join(const.asset_event_path, self._server_name[server], f'{banner_asset_bundle_name}.png'), os.R_OK):
                        detail.append(ImageMsg({'file': file_path}))
                    detail.append(StringMsg('\n' + '\n'.join([f'{key}: {value}' for key, value in {
                        '标题': event_data['eventName'][server],
                        '种类': self._type[event_data['eventType']],
                        '开始时间': f'{(datetime.datetime.utcfromtimestamp(int(event_data["startAt"][server]) // 1000) + datetime.timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")}(北京时间)',
                        '结束时间': f'{(datetime.datetime.utcfromtimestamp(int(event_data["endAt"][server]) // 1000) + datetime.timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")}(北京时间)',
                    }.items()])))

                    detail.append(StringMsg('\n属性: '))
                    [(detail.append(ImageMsg({'file': f'assets/res/{a["attribute"]}.png'})), detail.append(StringMsg(f'+{a["percent"]}%'))) for a in event_data['attributes']]
                    
                    detail.append(StringMsg('\n角色: '))
                    
                    images = [[
                        ImageProcesser.open_nontransparent(os.path.join(const.asset_resource_path, f'chara_icon_{c["characterId"]}.png'))
                    ] for c in event_data['characters']]
                    texts = [f'+{c["percent"]}%' for c in event_data['characters']]
                    character_filename = ImageProcesser.thumbnail(
                        images=images,
                        labels=texts,
                        col_num=len(images),
                        row_space=5,
                    )
                    detail.append(ImageMsg({'file': character_filename}))
        
                    
                    detail.append(StringMsg('\n奖励: '))
                    cards = self.card_table.select('resourceSetName', 'rarity', 'attribute', 'bandId', id=event_data['rewardCards'])
                    rewards_filename = ImageProcesser.thumbnail(
                        images=[ImageProcesser.merge_image(c[0], c[1], c[2], c[3], thumbnail=True, trained=False) for c in cards],
                        labels=[str(i) for i in event_data["rewardCards"]],
                        col_num=len(cards),
                        row_space=5,
                    )
                    detail.append(ImageMsg({'file': rewards_filename}))
                else:
                    detail.append(StringMsg('活动尚未开始'))
            return detail
    
    async def query(self, send_handler, msg, receiver_id):
        res = re.search(r'^活动(\d+)(\s+(日服|国际服|台服|国服))?$', msg.strip())
        if res:
            detail = self._detail_ver2(int(res.group(1)), self._server[res.group(3) or '国服'])
            if detail is not None:
                await send_handler(receiver_id, MultiMsg(detail))
            else:
                await send_handler(receiver_id, StringMsg('无相关活动'))
            return True
        
        constraints = self._parse_query_command(msg.strip())
        if constraints is not None:
            results = self.event_table.select('id', 'eventType', 'eventName', 'bannerAssetBundleName', **constraints)
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
            return True
        return False

card = Card()
event = Event(card.card_db)
