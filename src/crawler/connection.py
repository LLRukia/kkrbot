import os
import json

from . import EventTable, GachaTable

def event_gacha(json_path, database_file, output_file, logger):
    event_table = EventTable(database_file)
    gacha_table = GachaTable(database_file)
    servers = ['jp', 'en', 'tw', 'cn', 'kr']
    if os.access(output_file, os.R_OK):
        with open(output_file, 'r', encoding='utf-8') as f:
            output = json.load(f)
    else:
        output = {'event2gacha': [{} for _ in servers], 'gacha2event': [{} for _ in servers]}

    
    event_start_at = [{} for _ in servers]
    event_end_at = [{} for _ in servers]
    start_at_event = [{} for _ in servers]
    end_at_event = [{} for _ in servers]
    gacha_start_at = [{} for _ in servers]
    gacha_end_at = [{} for _ in servers]
    start_at_gacha = [{} for _ in servers]
    end_at_gacha = [{} for _ in servers]

    for eid in set([str(r[0]) for r in event_table.select('id')]):
        with open(os.path.join(json_path, 'events', f'{eid}.json'), 'r', encoding='utf-8') as f:
            data = json.load(f)
            for i in range(len(servers)):
                if data['startAt'][i]:
                    event_start_at[i][eid] = data['startAt'][i]
                    if not start_at_event[i].get(data['startAt'][i]):
                        start_at_event[i][data['startAt'][i]] = []
                    start_at_event[i][data['startAt'][i]].append(eid)
                
                if data['endAt'][i]:
                    event_end_at[i][eid] = data['endAt'][i]
                    if not end_at_event[i].get(data['endAt'][i]):
                        end_at_event[i][data['endAt'][i]] = []
                    end_at_event[i][data['endAt'][i]].append(eid)

    for gid in set([str(r[0]) for r in gacha_table.select('id')]):
        with open(os.path.join(json_path, 'gachas', f'{gid}.json'), 'r', encoding='utf-8') as f:
            data = json.load(f)
            for i in range(len(servers)):
                if data['publishedAt'][i]:
                    gacha_start_at[i][gid] = data['publishedAt'][i]
                    if not start_at_gacha[i].get(data['publishedAt'][i]):
                        start_at_gacha[i][data['publishedAt'][i]] = []
                    start_at_gacha[i][data['publishedAt'][i]].append(gid)
            
                if data['closedAt'][i]:
                    gacha_end_at[i][gid] = data['closedAt'][i]
                    if not end_at_gacha[i].get(data['closedAt'][i]):
                        end_at_gacha[i][data['closedAt'][i]] = []
                    end_at_gacha[i][data['closedAt'][i]].append(gid)
    
    for i in range(len(servers)):
        for eid, start_at in event_start_at[i].items():
            if not output['event2gacha'][i].get(eid):
                output['event2gacha'][i][eid] = []
            for gid in start_at_gacha[i].get(start_at, []):
                if gid not in output['event2gacha'][i][eid]:
                    output['event2gacha'][i][eid].append(gid)
                    if not output['gacha2event'][i].get(gid):
                        output['gacha2event'][i][gid] = []
                    output['gacha2event'][i][gid].append(eid)
        
        for eid, end_at in event_end_at[i].items():
            if not output['event2gacha'][i].get(eid):
                output['event2gacha'][i][eid] = []
            for gid in end_at_gacha[i].get(end_at, []):
                if gid not in output['event2gacha'][i][eid]:
                    output['event2gacha'][i][eid].append(gid)
                    if not output['gacha2event'][i].get(gid):
                        output['gacha2event'][i][gid] = []
                    output['gacha2event'][i][gid].append(eid)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False)