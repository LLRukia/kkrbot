class Any:
    __slots__ = []
    def on_group_message(self, context):
        return True

    def on_private_message(self, context):
        return True

    def on_group_decrease(self, context):
        return True
    
    def on_group_increase(self, context):
        return True

class Nany:
    __slots__ = []
    def on_group_message(self, context):
        return False

    def on_private_message(self, context):
        return False

    def on_group_decrease(self, context):
        return False
    
    def on_group_increase(self, context):
        return False

class Group(Nany):
    __slots__ = ['gid']
    def __init__(self, gid: int):
        self.gid = gid

    def on_group_message(self, context):
        return context['group_id'] == self.gid if self.gid else True

class Private(Nany):
    __slots__ = ['uid']
    def __init__(self, uid: int):
        self.uid = uid

    def on_private_message(self, context):
        return context['user_id'] == self.uid if self.uid else True

class GroupEx(Nany):
    __slots__ = ['gid']
    def __init__(self, gid: int):
        self.gid = gid

    def on_group_decrease(self, context):
        return context['group_id'] == self.gid if self.gid else True

    def on_group_increase(self, context):
        return context['group_id'] == self.gid if self.gid else True