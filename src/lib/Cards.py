import os
import sqlite3
import json
import math
import collections

import const

types = {
    'initial': '初始',
    'permanent': '无期限',
    'limited': '期间限定',
    'event': '活动',
    'campaign': '联名合作',
    'others': '其他',
}

with open(os.path.join(const.workpath, 'data', 'json', 'all_skills.json'), 'r', encoding='utf-8') as f:
    skills = json.load(f)

skill_type = {
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

mapping = {
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
}

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
    
    def insert(self, *data):
        self.conn.execute('''
            insert into card (id, name, characterId, rarity, attribute, resourceSetName, sdResourceName) values (?,?,?,?,?,?,?)
        ''', data)
        self.conn.commit()
    
    def detail(self, cid):
        try:
            name, skill_id, performance, technique, visual, type_, resource_set_name, rarity, attribute, band_id = self.select_by_single_value(
                'name', 'skillId', 'performance', 'technique', 'visual', 'type', 
                'resourceSetName', 'rarity', 'attribute', 'bandId',
                id=cid)[0]
        except:
            return '', '', -1, '', -1
        else:
            skill_id = str(skill_id)
            skill_description = skills[skill_id]['simpleDescription'][3] or skills[skill_id]['simpleDescription'][0] or skills[skill_id]['simpleDescription'][2] or skills[skill_id]['simpleDescription'][1]
            skill_description = skill_description.replace('\n', '') + f' ({",".join([str(round(n, 1)) for n in skills[skill_id]["duration"]])})'
            overall = f'{performance}/{technique}/{visual}/{performance + technique + visual}'
            return f'\n标题: {name}\n种类: {types[type_]}\n三围: {overall}\n技能: {skill_description}', resource_set_name, rarity, attribute, band_id

    def close(self):
        self.conn.close()
    
    def __del__(self):
        self.close()


def parse(string):
    string = string.split()
    if string[0] == '查卡' and len(string) > 1: # avoid query of all cards
        constraint = collections.OrderedDict()
        for c in string[1:]:
            valid_parameter = False
            if c == '露佬':
                return '露佬'
            for arribute, arribute2id in mapping.items():
                if c.lower() in arribute2id:
                    if constraint.get(arribute) is None:
                        constraint[arribute] = []
                    constraint[arribute].append(arribute2id[c.lower()])
                    valid_parameter = True
                    break
            if not valid_parameter:
                return {}
        return constraint
