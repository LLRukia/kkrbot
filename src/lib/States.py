class BaseState:
    def __init__(self, hdlr):
        self.hdlr = hdlr

    def enter(self):
        raise RuntimeError('Not implement')

    def leave(self, target):
        raise RuntimeError('Not implement')


class NonState(BaseState):
    def __init__(self, hdlr):
        super().__init__(hdlr)

    def enter(self):
        pass

    def leave(self, target):
        pass
