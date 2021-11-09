import collections
import datetime
import json
import os
import random
import re

import globals
from crawlers.bestdori import CardTable, EventTable, GachaTable
from nonebot.adapters.cqhttp import Message, MessageSegment

from utils import ImageProcesser
from utils.Asset import ImageAsset


class Card:
    def __init__(self):
        self.card_table = CardTable(os.path.join(globals.datapath, 'bestdori.db'))
        self._mapping = {
            'characterId': {
                '户山香澄': 1, '香澄': 1, 'kasumi': 1, 'ksm': 1,
                '花园多惠': 2, '多惠': 2, 'tae': 2, 'otae': 2, ''
                '牛込里美': 3, '里美': 3, 'rimi': 3,
                '山吹沙绫': 4, '沙绫': 4, 'saya': 4,
                '市谷有咲': 5, '有咲': 5, 'arisa': 5, 'ars': 5,
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

        with open(os.path.join(globals.datapath, 'json', 'all_skills.json'), 'r', encoding='utf-8') as f:
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
        if string[0] == '查卡' and len(string) > 1:  # avoid query of all cards
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
            name, skill_id, performance, technique, visual, type_, resource_set_name, rarity, attribute, band_id = self.card_table.select_by_single_value(
                'name', 'skillId', 'performance', 'technique', 'visual', 'type',
                'resourceSetName', 'rarity', 'attribute', 'bandId',
                id=cid)[0]
        except:
            return '', '', -1, '', -1
        else:
            skill_id = str(skill_id)
            skill_description = self._all_skills[skill_id]['simpleDescription'][3] or self._all_skills[skill_id]['simpleDescription'][
                0] or self._all_skills[skill_id]['simpleDescription'][2] or self._all_skills[skill_id]['simpleDescription'][1]
            skill_description = skill_description.replace('\n', '') + f' ({",".join([str(round(n, 1)) for n in self._all_skills[skill_id]["duration"]])})'
            overall = f'{performance}/{technique}/{visual}/{performance + technique + visual}'
            return f'\n标题: {name}\n种类: {self._types[type_]}\n三围: {overall}\n技能: {skill_description}', resource_set_name, rarity, attribute, band_id


class Event:
    def __init__(self, card_table):
        self.event_table = EventTable(os.path.join(globals.datapath, 'bestdori.db'))
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
        self._gacha_type = {
            'permanent': '无期限',
            'limited': '期间限定',
            'special': '特殊',
        }
        self._server = {
            '日服': 0,
            '国际服': 1,
            '台服': 2,
            '国服': 3,
            '韩服': 4,
        }
        self._server_name = {
            0: 'jp',
            1: 'en',
            2: 'tw',
            3: 'cn',
            4: 'kr',
        }
        with open(os.path.join(globals.datapath, 'json', 'event_gacha.json'), 'r', encoding='utf-8') as f:
            self._event_gacha = json.load(f)['event2gacha']

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

    def _detail_ver2(self, eid, server):
        res = self.event_table.select_by_single_value('bannerAssetBundleName', id=eid)
        if res:
            banner_asset_bundle_name, = res[0]
            if banner_asset_bundle_name:
                detail = Message()
                with open(os.path.join(globals.datapath, 'json', 'events', f'{eid}.json'), 'r', encoding='utf-8') as f:
                    event_data = json.load(f)
                if event_data["startAt"][server]:
                    file_path = os.path.join(globals.asset_event_path, self._server_name[server], f'{banner_asset_bundle_name}.png')
                    if os.access(file_path, os.R_OK):
                        detail.append(MessageSegment.image(ImageAsset.image_path(file_path)))
                    detail.append(MessageSegment.text('\n'.join([f'{key}: {value}' for key, value in {
                        '标题': event_data['eventName'][server],
                        '种类': self._type[event_data['eventType']],
                        '开始时间': f'{(datetime.datetime.utcfromtimestamp(int(event_data["startAt"][server]) // 1000) + datetime.timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")}(北京时间)',
                        '结束时间': f'{(datetime.datetime.utcfromtimestamp(int(event_data["endAt"][server]) // 1000) + datetime.timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")}(北京时间)',
                    }.items()])))

                    detail.append(MessageSegment.text('\n属性: '))

                    [(detail.append(MessageSegment.image(ImageAsset.image_path(os.path.join(globals.asset_resource_path, f'{a["attribute"]}.png')))),
                      detail.append(MessageSegment.text(f'+{a["percent"]}%'))) for a in event_data['attributes']]

                    detail.append(MessageSegment.text('\n角色: '))

                    images = [[
                        ImageProcesser.open_nontransparent(os.path.join(globals.asset_resource_path, f'chara_icon_{c["characterId"]}.png')) or
                        ImageProcesser.white_padding(420, 140),
                    ] for c in event_data['characters']]
                    texts = [f'+{c["percent"]}%' for c in event_data['characters']]
                    character_raw = ImageProcesser.thumbnail(
                        images=images,
                        labels=texts,
                        col_num=len(images),
                        row_space=5,
                    )
                    detail.append(MessageSegment.image(character_raw))

                    detail.append(MessageSegment.text('\n奖励: '))
                    cards = self.card_table.select('id', 'resourceSetName', 'rarity', 'attribute', 'bandId', id=event_data['rewardCards'])
                    rewards_raw = ImageProcesser.thumbnail(
                        images=[ImageProcesser.merge_image(c[1], c[2], c[3], c[4], thumbnail=True, trained=False) or
                                ImageProcesser.white_padding(420, 140)
                                for c in cards],
                        labels=[str(c[0]) for c in cards],
                        col_num=len(cards),
                        row_space=5,
                    )
                    detail.append(MessageSegment.image(rewards_raw))

                    if self._event_gacha[server].get(str(eid)):
                        detail.append(MessageSegment.text('\n关联卡池: '))
                        for gacha_id in self._event_gacha[server][str(eid)]:
                            with open(os.path.join(globals.datapath, 'json', 'gachas', f'{gacha_id}.json'), 'r', encoding='utf-8') as f:
                                gacha_data = json.load(f)
                            new_cards = [card for card in gacha_data['newCards'] if gacha_data['details'][server][str(card)]['pickup']]
                            if new_cards:
                                file_path = os.path.join(globals.asset_gacha_path, self._server_name[server], f'{gacha_data["bannerAssetBundleName"]}.png')
                                if os.access(file_path, os.R_OK):
                                    detail.append(MessageSegment.image(ImageAsset.image_path(file_path)))
                                detail.append(MessageSegment.text('\n'.join([f'{key}: {value}' for key, value in {
                                    '标题': gacha_data['gachaName'][server],
                                    '种类': self._gacha_type[gacha_data['type']],
                                    'ID': str(gacha_id),
                                }.items()])))
                                detail.append(MessageSegment.text('\nPICK UP: '))
                                cards = self.card_table.select('id', 'resourceSetName', 'rarity', 'attribute', 'bandId', id=new_cards)
                                pickups_raw = ImageProcesser.thumbnail(
                                    images=[ImageProcesser.merge_image(c[1], c[2], c[3], c[4], thumbnail=True, trained=False) or
                                            ImageProcesser.white_padding(420, 140)
                                            for c in cards],
                                    labels=[str(c[0]) for c in cards],
                                    col_num=len(cards),
                                    row_space=5,
                                )
                                detail.append(MessageSegment.image(pickups_raw))
                else:
                    detail.extend([MessageSegment.text('活动尚未开始，查查别的服务器吧'), MessageSegment.image(ImageAsset.static_image('kkr/amazed.gif'))])
            return detail


class Gacha:
    def __init__(self, card_table):
        self.gacha_table = GachaTable(os.path.join(globals.datapath, 'bestdori.db'))
        self.card_table = card_table
        self._mapping = {
            'type': {
                '常驻': 'permanent', '无期限': 'permanent',
                '限时': 'limited', '限定': 'limited', '期间限定': 'limited',
                '特殊': 'special',
            },
            'fixed4star': {
                '必4': 1, '必四': 1,
            }
        }
        self._type = {
            'permanent': '无期限',
            'limited': '期间限定',
            'special': '特殊',
        }
        self._event_type = {
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
            '韩服': 4,
        }
        self._server_name = {
            0: 'jp',
            1: 'en',
            2: 'tw',
            3: 'cn',
            4: 'kr',
        }
        with open(os.path.join(globals.datapath, 'json', 'event_gacha.json'), 'r', encoding='utf-8') as f:
            self._gacha_event = json.load(f)['gacha2event']

    def _parse_query_command(self, string):
        string = string.split()
        if string[0] == '卡池列表':
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
        res = self.gacha_table.select_by_single_value('bannerAssetBundleName', 'resourceName', id=eid)
        if res:
            detail = Message()
            banner_asset_bundle_name, resourceName = res[0]
            with open(os.path.join(globals.datapath, 'json', 'gachas', f'{eid}.json'), 'r', encoding='utf-8') as f:
                gacha_data = json.load(f)
            if gacha_data["publishedAt"][server]:
                file_path = os.path.join(globals.asset_gacha_path, self._server_name[server], f'{banner_asset_bundle_name}.png')
                if os.access(file_path, os.R_OK):
                    detail.append(MessageSegment.image(ImageAsset.image_path(file_path)))
                else:
                    file_path = os.path.join(globals.asset_gacha_path, resourceName, self._server_name[server], 'logo.png')
                    if os.access(file_path, os.R_OK):
                        detail.append(MessageSegment.image(ImageAsset.image_path(file_path)))
                detail.append(MessageSegment.text('\n'.join([f'{key}: {value}' for key, value in {
                    '标题': gacha_data['gachaName'][server],
                    '种类': self._type[gacha_data['type']],
                    '开始时间': f'{(datetime.datetime.utcfromtimestamp(int(gacha_data["publishedAt"][server]) // 1000) + datetime.timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")}(北京时间)',
                    '结束时间': f'{(datetime.datetime.utcfromtimestamp(int(gacha_data["closedAt"][server]) // 1000) + datetime.timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")}(北京时间)',
                }.items()])))
                new_cards = [card for card in gacha_data['newCards'] if gacha_data['details'][server][str(card)]['pickup']]
                if new_cards:
                    detail.append(MessageSegment.text('\nPICK UP: '))
                    cards = self.card_table.select('id', 'resourceSetName', 'rarity', 'attribute', 'bandId', id=gacha_data['newCards'])
                    rewards = ImageProcesser.thumbnail(
                        images=[ImageProcesser.merge_image(c[1], c[2], c[3], c[4], thumbnail=True, trained=False) for c in cards],
                        labels=[str(c[0]) for c in cards],
                        col_num=len(cards),
                        row_space=5,
                    )
                    detail.append(MessageSegment.image(rewards))

                detail.append(MessageSegment.text(f'\n描述: {gacha_data["description"][server]}'))

                if self._gacha_event[server].get(str(eid)):
                    detail.append(MessageSegment.text('\n关联活动: '))
                    for event_id in self._gacha_event[server][str(eid)]:
                        with open(os.path.join(globals.datapath, 'json', 'events', f'{event_id}.json'), 'r', encoding='utf-8') as f:
                            event_data = json.load(f)
                        file_path = os.path.join(globals.asset_event_path, self._server_name[server], f'{event_data["bannerAssetBundleName"]}.png')
                        if os.access(file_path, os.R_OK):
                            detail.append(MessageSegment.image(ImageAsset.image_path(file_path)))
                        detail.append(MessageSegment.text('\n'.join([f'{key}: {value}' for key, value in {
                            '标题': event_data['eventName'][server],
                            '种类': self._event_type[event_data['eventType']],
                            'ID': str(event_id),
                        }.items()])))
                        detail.append(MessageSegment.text('\n奖励: '))
                        cards = self.card_table.select('id', 'resourceSetName', 'rarity', 'attribute', 'bandId', id=event_data['rewardCards'])
                        rewards = ImageProcesser.thumbnail(
                            images=[ImageProcesser.merge_image(c[1], c[2], c[3], c[4], thumbnail=True, trained=False) for c in cards],
                            labels=[str(c[0]) for c in cards],
                            col_num=len(cards),
                            row_space=5,
                        )
                        detail.append(MessageSegment.image(rewards))
            else:
                detail.extend([MessageSegment.text('卡池未开放，查查别的服务器吧'), MessageSegment.image(ImageAsset.static_image('kkr/amazed.gif'))])
            return detail


card = None
event = None
gacha = None


def init():
    global card
    global event
    global gacha
    if not os.path.exists(os.path.join(globals.datapath, 'bestdori.db')):
        globals.logger.warning('please run `cd crawlers && python BestdoriCrawler.py init` first!')
    card = Card()
    event = Event(card.card_table)
    gacha = Gacha(card.card_table)
