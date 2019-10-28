import os
import sys
import json
import time
import random
import requests

class CardDB:
    def __init__(self, conn):
        self.conn = conn

    def create_table(self):
        self.conn.execute('''
            create table card (
                id int primary key not null,
                name varchar(50) not null,
                characterId tinyint not null,
                bandId tinyint not null,
                rarity tinyint not null,
                attribute varchar(10) not null,
                skillId smallint not null,
                performance int not null,
                technique int not null,
                visual int not null,
                type varchar(30) not null,
                resourceSetName varchar(30) not null
            )''')
    
    def select_by_single_value(self, *column, **constraint):
        col_exp = '*' if not column else ','.join(column)
        if constraint:
            return self.conn.execute(f'''
                select {col_exp} from card where {' and '.join([k+'=?' for k in constraint.keys()])} order by id asc
            ''', tuple(constraint.values())).fetchall()
            return self.conn.execute(sql, tuple(values)).fetchall()
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
            insert into card (id, name, characterId, bandId, rarity, attribute, skillId, performance, technique, visual, type, resourceSetName) values (?,?,?,?,?,?,?,?,?,?,?,?)
        ''', data)
        self.conn.commit()

    def close(self):
        self.conn.close()
    
    def __del__(self):
        self.close()

    def detail(self, cid):
        name, skill_id, performance, technique, visual, type_, resource_set_name = self.select_by_single_value('name', 'skillId', 'performance', 'technique', 'visual', 'type', 'resourceSetName', id=cid)[0]
        skill_id = str(skill_id)
        skill_description = skills[skill_id]['description'][3] or skills[skill_id]['description'][0] or skills[skill_id]['description'][2] or skills[skill_id]['description'][1]
        skill_description = skill_description.replace(r'{0}', 'x') + f' (x:{", ".join([str(round(n, 1)) for n in skills[skill_id]["duration"]])})'
        overall = f'{performance}/{technique}/{visual}/{performance + technique + visual}'
        return f'标题: {name}\n种类: {types[type_]}\n三围: {overall}\n技能: {skill_description}', resource_set_name

class Crawler:
    def __init__(self, logger, json_savedir, asset_savedir):
        self.logger = logger
        self.json_savedir = json_savedir
        self.asset_savedir = asset_savedir
        self.resource_map = {
            'all_cards': 'https://bestdori.com/api/cards/all.5.json',
            'all_skills': 'https://bestdori.com/api/skills/all.5.json',
            'all_characters': 'https://bestdori.com/api/characters/all.2.json',
            'all_bands': 'https://bestdori.com/api/bands/all.1.json',
        }
        if not os.path.exists(self.json_savedir): os.makedirs(self.json_savedir)
        if not os.path.exists(self.json_savedir): os.makedirs(self.asset_savedir)
        if not os.path.exists(os.path.join(self.json_savedir, 'cards')): os.makedirs(os.path.join(self.json_savedir, 'cards'))
        if not os.path.exists(os.path.join(self.asset_savedir, 'thumbnail')): os.makedirs(os.path.join(self.asset_savedir, 'thumbnail'))

    def load_json(self, cid):
        if type(cid) is int:
            filename = f'{os.path.join(self.json_savedir, "cards", str(cid))}.json'
        else:
            filename = f'{os.path.join(self.json_savedir, cid)}.json'
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            self.logger.error(exc_info=sys.exc_info())
            return {}

    def _save_json(self, data, filename):
        with open(f'{os.path.join(self.json_savedir, filename)}', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False)

    def _save_asset(self, asset, filename):
        with open(f'{os.path.join(self.asset_savedir, filename)}', 'wb') as f:
            f.write(asset)

    def request_json(self, cid=0):
        if type(cid) is int:
            url = f'https://bestdori.com/api/cards/{cid}.json'
            save_path = f'cards/{cid}.json'
        else:
            assert cid in self.resource_map
            url = self.resource_map[cid]
            save_path = f'{cid}.json'
        res = requests.get(url)
        if res.status_code == 200:
            data = res.json()
            self._save_json(data, save_path)
            return data
        return {}

    def request_asset(self, url, filename, overwrite=False):
        if os.path.isfile(os.path.join(self.asset_savedir, filename)) and not overwrite:
            self.logger.info(f'{url} already exists')
            return 1
        else:
            try:
                res = requests.get(url, timeout=5)
                if res.status_code == 404 or res.encoding:
                    self.logger.info(f'{url} not found')
                    return -1
                if res.status_code == 200:
                    self._save_asset(res.content, filename)
                    self.logger.info(f'request {url} successfully')
                    return 0
            except:
                try:
                    res = requests.get(url, timeout=5)
                    if res.status_code == 404 or res.encoding:
                        self.logger.info(f'{url} not found')
                        return -1
                    if res.status_code == 200:
                        self._save_asset(res.content, filename)
                        self.logger.info(f'request {url} successfully')
                        return 0
                except:
                    self.logger.error(exc_info=sys.exc_info())
                    return -1

    def request_assets(self, cid):
        try:
            json_data = self.load_json(cid) or self.request_json(cid)
        except:
            self.logger.error(exc_info=sys.exc_info())
        else:
            resource_set_name = json_data['resourceSetName']

            # card
            card_normal = f'https://bestdori.com/assets/jp/characters/resourceset/{resource_set_name}_rip/card_normal.png'
            card_after_training = f'https://bestdori.com/assets/jp/characters/resourceset/{resource_set_name}_rip/card_after_training.png'

            # icon
            temp = str(cid // 50)
            s = '0' * (5 - len(temp)) + temp
            normal = f'https://bestdori.com/assets/jp/thumb/chara/card{s}_rip/{resource_set_name}_normal.png'
            after_training = f'https://bestdori.com/assets/jp/thumb/chara/card{s}_rip/{resource_set_name}_after_training.png'
            
            if self.request_asset(card_normal, f'{resource_set_name}_card_normal.png') == 0:
                time.sleep(random.uniform(1, 2))
            temp_status = self.request_asset(normal, f'thumbnail/{resource_set_name}_normal.png')

            if json_data['rarity'] <= 2:
                return temp_status
            else:
                if temp_status == 0:
                    time.sleep(random.uniform(1, 2))
                if self.request_asset(card_after_training, f'{resource_set_name}_card_after_training.png') == 0:
                    time.sleep(random.uniform(1, 2))
                return self.request_asset(after_training, f'thumbnail/{resource_set_name}_after_training.png')
        return -1

    def request_data(self, cid):
        if self.request_json(cid):
            return self.request_assets(cid)
