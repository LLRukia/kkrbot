from PIL import Image
import math


config = {
    'Lane': './assets/lane.png',
    'SkillNote': './assets/note_skill.png',
}

class Lane:
    _im = Image.open(config['Lane'])
    UNIT = 5.0

    def __init__(self):
        self.im = Image.new('RGB', (_im.width, _im.height), (255,255,255))
        self.im.paste(self._im)
    
    def apply(self, note):
        y_per = math.fmod(note.time, self.UNIT)
        y = y_per * self.im.height
        x = self._get_x(note.lane)

    def _get_x(self, ln):
        return self.width / 7



class Note:
    _im = None
    BOX = (0, 0)

    @classmethod
    def _im_src(cls):
        return cls._im

    def __init__(self):
        self.time = 0
        self.lane = 0

    @property
    def image(self):
        return self._im_src()

    def apply(self, lane):


class BPM(Note):
