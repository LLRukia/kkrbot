import json
from typing import Sequence


class Msg:
    def __init__(self):
        self.type = self.data = None
    
    def get(self)-> dict:
        return {
            'type': self.type,
            'data': self.data
        }

MSGS = Sequence[Msg]

class StringMsg(Msg):
    def __init__(self, msg: str):
        self.type = 'text'
        self.data = {'text': msg}
    
class ImageMsg(Msg):
    def __init__(self, info: dict):
        self.type = 'image'
        self.data = info

class RecordMsg(Msg):
    def __init__(self, info: dict):
        self.type = 'record'
        self.data = info

class EmojiMsg(Msg):
    def __init__(self, eid: int):
        self.type = 'face'
        self.data = {'id': eid}

class MultiMsg:
    def __init__(self, msgs: MSGS):
        self.data = msgs

    def get(self)-> list:
        return [x.get() for x in self.data]

class PrivateMsg:
    def __init__(self, user_id: int, msg: Msg):
        self.user_id = user_id
        self.msg = msg

    def get(self)-> dict:
        return {
            'user_id': self.user_id,
            'message': self.msg.get(),
        }

class GroupMsg:
    def __init__(self, group_id: int, msg: Msg):
        self.group_id = group_id
        self.msg = msg

    def get(self)-> dict:
        return {
            'group_id': self.group_id,
            'message': self.msg.get(),
        }