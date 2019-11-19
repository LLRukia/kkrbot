import os
import sys
import json
import time
import random
import sqlite3
import requests
from collections import OrderedDict

class Table:
    def __init__(self, database_path, table_name, **columns):
        self.conn = sqlite3.connect(database_path)
        self.name = table_name
        self.columns = OrderedDict(columns)
    
    def create(self):
        self.conn.execute(f'''
            create table {self.name} ({','.join([f"{column_name} {column_type}" for column_name, column_type in self.columns.items()])})
        ''')
    
    def drop(self):
        self.conn.execute(f'drop table {self.name}')

    def select_by_single_value(self, *column, **constraint):
        col_exp = '*' if not column else ','.join(column)
        if constraint:
            return self.conn.execute(f'''
                select {col_exp} from {self.name} where {' and '.join([k+'=?' for k in constraint.keys()])} order by id asc
            ''', tuple(constraint.values())).fetchall()
            return self.conn.execute(sql, tuple(values)).fetchall()
        else:
            return self.conn.execute(f'select {col_exp} from {self.name}').fetchall()
    
    def select(self, *column, **constraint):
        col_exp = '*' if not column else ','.join(column)
        if constraint:
            return self.conn.execute(f'''
                select {col_exp} from {self.name} where {' and '.join([k+' in ({})'.format(','.join('?'*len(constraint[k]))) for k in constraint.keys()])} order by id asc
            ''', [v for k, vs in constraint.items() for v in vs]).fetchall()
        else:
            return self.conn.execute(f'select {col_exp} from {self.name}').fetchall()
    
    def select_or(self, *column, **constraint):
        col_exp = '*' if not column else ','.join(column)
        if constraint:
            return self.conn.execute(f'''
                select {col_exp} from {self.name} where {' or '.join([k+' in ({})'.format(','.join('?'*len(constraint[k]))) for k in constraint.keys()])} order by id asc
            ''', [v for k, vs in constraint.items() for v in vs]).fetchall()
        else:
            return self.conn.execute(f'select {col_exp} from {self.name}').fetchall()

    def insert(self, *data):
        self.conn.execute(f'''
            insert into {self.name} ({','.join(self.columns.keys())}) values ({','.join('?'*len(self.columns))})
        ''', data)
        self.conn.commit()

    def close(self):
        self.conn.close()
    
    def __del__(self):
        self.close()

class CardTable(Table):
    def __init__(self, database_path, table_name='card'):
        super().__init__(database_path, table_name,
            id='int primary key not null',
            name='varchar(50) not null',
            characterId='tinyint not null',
            bandId='tinyint not null',
            rarity='tinyint not null',
            attribute='varchar(10) not null',
            skillId='smallint not null',
            performance='int not null',
            technique='int not null',
            visual='int not null',
            type='varchar(30) not null',
            resourceSetName='varchar(30) not null',
        )

class EventTable(Table):
    def __init__(self, database_path, table_name='event'):
        super().__init__(database_path, table_name,
            id='int primary key not null',
            attribute='varchar(10) not null',
            eventType='varchar(30) not null',
            eventName='varchar(100) not null',
            bannerAssetBundleName='varchar(30) not null',
        )

class GachaTable(Table):
    def __init__(self, database_path, table_name='gacha'):
        super().__init__(database_path, table_name,
            id='int primary key not null',
            resourceName='varchar(30) not null',
            type='varchar(30) not null',
            gachaName='varchar(100) not null',
            bannerAssetBundleName='varchar(30) not null',
            fixed4star='tinyint not null',
        )

resource_map = {
    'all_cards': 'https://bestdori.com/api/cards/all.5.json',
    'all_skills': 'https://bestdori.com/api/skills/all.5.json',
    'all_characters': 'https://bestdori.com/api/characters/all.2.json',
    'all_bands': 'https://bestdori.com/api/bands/all.1.json',
    'all_events': 'https://bestdori.com/api/events/all.5.json',
    'all_gachas': 'https://bestdori.com/api/gacha/all.5.json',
}

class Crawler:
    def __init__(self, logger, table, savedir_config, json_api):
        self.logger = logger
        self.table = table
        self.savedir_config = savedir_config
        for _, path in self.savedir_config.items():
            if not os.path.exists(path): os.makedirs(path)
        self.json_api = json_api

    def request_overall_json(self, resource_type):  
        save_name = f'{resource_type}.json'
        res = requests.get(resource_map[resource_type])
        if res.status_code == 200:
            data = res.json()
            with open(f'{os.path.join(self.savedir_config["overall_json"], save_name)}', 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False)
            return data
        return {}
        
    def load_json(self, id_):
        try:
            with open(f'{os.path.join(self.savedir_config["json"], str(id_))}.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            self.logger.error(exc_info=sys.exc_info())
            return {}

    def _save_json(self, data, id_):
        with open(f'{os.path.join(self.savedir_config["json"], str(id_))}.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False)

    def _save_asset(self, asset, filename):
        with open(f'{os.path.join(self.savedir_config["assets"], filename)}', 'wb') as f:
            f.write(asset)

    def request_json(self, id_=0):  
        url = self.json_api + f'{id_}.json'
        res = requests.get(url)
        if res.status_code == 200:
            data = res.json()
            self._save_json(data, id_)
            return data
        return {}

    def request_asset(self, url, filename, overwrite=False):
        if os.path.isfile(os.path.join(self.savedir_config['assets'], filename)) and not overwrite:
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

class CardCrawler(Crawler):
    def __init__(self, logger, table, savedir_config, json_api):
        super().__init__(logger, table, savedir_config, json_api)
        self.thumb_savedirname = 'thumb'
        if not os.path.exists(os.path.join(self.savedir_config['assets'], self.thumb_savedirname)): os.makedirs(os.path.join(self.savedir_config['assets'], self.thumb_savedirname))

    def request_assets(self, id_):
        try:
            json_data = self.load_json(id_) or self.request_json(id_)
        except:
            self.logger.error(exc_info=sys.exc_info())
        else:
            resource_set_name = json_data['resourceSetName']

            # card
            card_normal = f'https://bestdori.com/assets/jp/characters/resourceset/{resource_set_name}_rip/card_normal.png'
            card_after_training = f'https://bestdori.com/assets/jp/characters/resourceset/{resource_set_name}_rip/card_after_training.png'

            # icon
            temp = str(id_ // 50)
            s = '0' * (5 - len(temp)) + temp
            normal = f'https://bestdori.com/assets/jp/thumb/chara/card{s}_rip/{resource_set_name}_normal.png'
            after_training = f'https://bestdori.com/assets/jp/thumb/chara/card{s}_rip/{resource_set_name}_after_training.png'
            
            if self.request_asset(card_normal, f'{resource_set_name}_card_normal.png') == 0:
                time.sleep(random.uniform(1, 2))
            temp_status = self.request_asset(normal, f'{self.thumb_savedirname}/{resource_set_name}_normal.png')

            if json_data['rarity'] <= 2:
                return temp_status
            else:
                if temp_status == 0:
                    time.sleep(random.uniform(1, 2))
                if self.request_asset(card_after_training, f'{resource_set_name}_card_after_training.png') == 0:
                    time.sleep(random.uniform(1, 2))
                return self.request_asset(after_training, f'{self.thumb_savedirname}/{resource_set_name}_after_training.png')
        return -1

    def request_data(self, id_):
        if self.request_json(id_):
            return self.request_assets(id_)

    def init(self):
        try:
            self.table.drop()
        except:
            pass
        finally:
            self.table.create()
        all_data = self.request_overall_json('all_cards')

        for id_, data in all_data.items():
            overall = {}
            if data['rarity'] < 3:
                for s in ['performance', 'technique', 'visual']:
                    if data['stat'].get('episodes'):
                        overall[s] = data['stat'][str(data['levelLimit'])][s] + data['stat']['episodes'][0][s] + data['stat']['episodes'][1][s]
                    else:
                        overall[s] = data['stat'][str(data['levelLimit'])][s]
            else:
                for s in ['performance', 'technique', 'visual']:
                    if data['stat'].get('episodes'):
                        overall[s] = data['stat'][str(data['levelLimit'] + 10)][s] + data['stat']['episodes'][0][s] + data['stat']['episodes'][1][s] + data['stat']['training'][s]
                    else:
                        overall[s] = data['stat'][str(data['levelLimit'] + 10)][s] + data['stat']['training'][s]
            
            if self.request_data(int(id_)) == 0:
                time.sleep(random.uniform(4, 5))

            self.table.insert(
                int(id_), 
                data['prefix'][0] or data['prefix'][1] or data['prefix'][2] or data['prefix'][3],
                data['characterId'],
                (data['characterId'] - 1) // 5 + 1,
                data['rarity'],
                data['attribute'],
                data['skillId'],
                overall['performance'],
                overall['technique'],
                overall['visual'],
                data['type'],
                data['resourceSetName']
            )
    
    def update(self):
        local_all_cards = set([str(r[0]) for r in self.table.select('id')])
        all_data = self.request_overall_json('all_cards')
        all_cards = set(all_data.keys())

        for id_ in all_cards - local_all_cards:
            data = all_data[id_]
            overall = {}
            if data['rarity'] < 3:
                for s in ['performance', 'technique', 'visual']:
                    if data['stat'].get('episodes'):
                        overall[s] = data['stat'][str(data['levelLimit'])][s] + data['stat']['episodes'][0][s] + data['stat']['episodes'][1][s]
                    else:
                        overall[s] = data['stat'][str(data['levelLimit'])][s]
            else:
                for s in ['performance', 'technique', 'visual']:
                    if data['stat'].get('episodes'):
                        overall[s] = data['stat'][str(data['levelLimit'] + 10)][s] + data['stat']['episodes'][0][s] + data['stat']['episodes'][1][s] + data['stat']['training'][s]
                    else:
                        overall[s] = data['stat'][str(data['levelLimit'] + 10)][s] + data['stat']['training'][s]
            
            if self.request_data(int(id_)) == 0:
                time.sleep(random.uniform(4, 5))

            self.table.insert(
                int(id_), 
                data['prefix'][0] or data['prefix'][1] or data['prefix'][2] or data['prefix'][3],
                data['characterId'],
                (data['characterId'] - 1) // 5 + 1,
                data['rarity'],
                data['attribute'],
                data['skillId'],
                overall['performance'],
                overall['technique'],
                overall['visual'],
                data['type'],
                data['resourceSetName']
            )

class EventCrawler(Crawler):
    def __init__(self, logger, table, savedir_config, json_api):
        super().__init__(logger, table, savedir_config, json_api)
        self.servers = ['jp', 'en', 'tw', 'cn', 'kr'] 
        for server in self.servers:
            if not os.path.exists(os.path.join(self.savedir_config['assets'], server)): os.makedirs(os.path.join(self.savedir_config['assets'], server))
    
    def request_assets(self, id_):
        try:
            json_data = self.load_json(id_) or self.request_json(id_)
        except:
            self.logger.error(exc_info=sys.exc_info())
        else:
            banner_asset_bundle_name = json_data['bannerAssetBundleName']
            asset_bundle_name = json_data['assetBundleName']

            for i, server in enumerate(self.servers):
                if json_data['startAt'][i]:
                    banner = f'https://bestdori.com/assets/{server}/homebanner_rip/{banner_asset_bundle_name}.png'
                    if self.request_asset(banner, f'{server}/{banner_asset_bundle_name}.png') == 0:
                        time.sleep(random.uniform(1, 2))
            
            character = f'https://bestdori.com/assets/jp/event/{asset_bundle_name}/topscreen_rip/trim_eventtop.png'
            background = f'https://bestdori.com/assets/jp/event/{asset_bundle_name}/topscreen_rip/bg_eventtop.png'
            if not os.path.exists(os.path.join(self.savedir_config['assets'], asset_bundle_name)): os.makedirs(os.path.join(self.savedir_config['assets'], asset_bundle_name))
            if self.request_asset(character, f'{asset_bundle_name}/trim_eventtop.png') == 0:
                time.sleep(random.uniform(1, 2))
            return self.request_asset(background, f'{asset_bundle_name}/bg_eventtop.png')
        return -1
    
    def request_data(self, id_):
        if self.request_json(id_):
            return self.request_assets(id_)

    def init(self):
        try:
            self.table.drop()
        except:
            pass
        finally:
            self.table.create()
        all_data = self.request_overall_json('all_events')

        for id_, data in all_data.items():
            if self.request_data(int(id_)) == 0:
                time.sleep(random.uniform(4, 5))

            self.table.insert(
                int(id_),
                data['attributes'][0]['attribute'],
                data['eventType'],
                data['eventName'][0] or data['eventName'][1] or data['eventName'][2] or data['eventName'][3],
                data['bannerAssetBundleName'],
            )

    def update(self):
        all_data = self.request_overall_json('all_events')
        local_all_events = set([str(r[0]) for r in self.table.select('id')])
        all_events = set(all_data.keys())

        for id_ in all_events - local_all_events:
            data = all_data[id_]
            if self.request_data(int(id_)) == 0:
                time.sleep(random.uniform(4, 5))

            self.table.insert(
                int(id_),
                data['attributes'][0]['attribute'],
                data['eventType'],
                data['eventName'][0] or data['eventName'][1] or data['eventName'][2] or data['eventName'][3] or data['eventName'][4],
                data['bannerAssetBundleName'],
            )

        for id_ in local_all_events:
            local_data = self.load_json(id_)
            for i, server in enumerate(self.servers[1:]):
                if not local_data['startAt'][i]:
                    if self.request_data(id_) == 0:
                        time.sleep(random.uniform(4, 5))
                    break

class GachaCrawler(Crawler):
    def __init__(self, logger, table, savedir_config, json_api):
        super().__init__(logger, table, savedir_config, json_api)
        self.servers = ['jp', 'en', 'tw', 'cn', 'kr']
        for server in self.servers:
            if not os.path.exists(os.path.join(self.savedir_config['assets'], server)): os.makedirs(os.path.join(self.savedir_config['assets'], server))

    def init(self):
        try:
            self.table.drop()
        except:
            pass
        finally:
            self.table.create()
        all_data = self.request_overall_json('all_gachas')

        for id_, data in all_data.items():
            if self.request_data(int(id_)) == 0:
                time.sleep(random.uniform(4, 5))

            self.table.insert(
                int(id_),
                data['resourceName'],
                data['type'],
                data['gachaName'][0] or data['gachaName'][1] or data['gachaName'][2] or data['gachaName'][3] or data['gachaName'][4],
                data.get('bannerAssetBundleName') or '',
                1 if self.load_json(id_)['paymentMethods'][0]['behavior'] == 'fixed_4_star_once' else 0
            )
    
    def update(self):
        all_data = self.request_overall_json('all_gachas')
        local_all_gachas = set([str(r[0]) for r in self.table.select('id')])
        all_gachas = set(all_data.keys())

        for id_ in all_gachas - local_all_gachas:
            data = all_data[id_]
            if self.request_data(int(id_)) == 0:
                time.sleep(random.uniform(4, 5))

            self.table.insert(
                int(id_),
                data['resourceName'],
                data['type'],
                data['gachaName'][0] or data['gachaName'][1] or data['gachaName'][2] or data['gachaName'][3] or data['gachaName'][4],
                data.get('bannerAssetBundleName') or '',
                1 if self.load_json(id_)['paymentMethods'][0]['behavior'] == 'fixed_4_star_once' else 0
            )

        for id_ in local_all_gachas:
            local_data = self.load_json(id_)
            for i, server in enumerate(self.servers[1:]):
                if not local_data['publishedAt'][i]:
                    if self.request_data(id_) == 0:
                        time.sleep(random.uniform(4, 5))
                    break
    
    def request_assets(self, id_):
        try:
            json_data = self.load_json(id_) or self.request_json(id_)
        except:
            self.logger.error(exc_info=sys.exc_info())
        else:
            banner_asset_bundle_name = json_data.get('bannerAssetBundleName')
            resourceName = json_data['resourceName']
            final_status = 0
            for i, server in enumerate(self.servers):
                if json_data['publishedAt'][i]:
                    if banner_asset_bundle_name:
                        banner = f'https://bestdori.com/assets/{server}/homebanner_rip/{banner_asset_bundle_name}.png'
                        if self.request_asset(banner, f'{server}/{banner_asset_bundle_name}.png') == 0:
                            time.sleep(random.uniform(1, 2))
                
                    logo = f'https://bestdori.com/assets/{server}/gacha/screen/{resourceName}_rip/logo.png'
                    pickup = f'https://bestdori.com/assets/{server}/gacha/screen/{resourceName}_rip/pickup.png'
                    if not os.path.exists(os.path.join(self.savedir_config['assets'], resourceName, server)): os.makedirs(os.path.join(self.savedir_config['assets'], resourceName, server))
                    if self.request_asset(logo, f'{resourceName}/{server}/logo.png', overwrite=server=='cn') == 0:
                        time.sleep(random.uniform(1, 2))
                    final_status = self.request_asset(pickup, f'{resourceName}/{server}/pickup.png', overwrite=server=='cn')
                    if server != self.servers[-1] and final_status == 0:
                        time.sleep(random.uniform(1, 2))
            return final_status
        return -1
    
    def request_data(self, id_):
        if self.request_json(id_):
            return self.request_assets(id_)
