from dataclasses import dataclass
from typing import Callable
import pygame as pg


@dataclass(slots=True, frozen=True)
class Follower: # Crew
    buffer: list # Buffer
    encode: Callable # Job


@dataclass(slots=True, frozen=True)
class BufferRigged:
    pilot:      list
    followers:  list[Follower]

    @classmethod
    def init(cls, iterable=(), *args):
        pilot = list(iterable)
        for fol in args:
            fol.buffer = list(map(fol.encode, pilot))
        return cls(pilot, args)

    def __iter__(self):
        return self.pilot.__iter__()

    def __getitem__(self, key):
        if isinstance(key, int):
            return self.pilot.__getitem__(key)
        elif isinstance(key, slice):
            return BufferRigged(
                self.pilot.__getitem__(key),
                [fol.__getitem__(key) for fol in self.followers]
            )
        else:
            raise IndexError

    def __setitem__(self, key, value):
        for fol in self.followers:
            fol.buffer.__setitem__(key, fol.encode(value))
        return self.pilot.__setitem__(key, value)

    def __delitem__(self, key):
        for fol in self.followers:
            fol.buffer.__delitem__(key)
        self.pilot.__delitem__(key)

    def __add__(self, x, /):
        return BufferRigged(
            self.pilot.__add__(x.pilot),
            [fol.__add__(xfol) for fol, xfol in zip(self.followers, x.followers)]
        )


class Editor:
    def __init__(self, bindings, followers):
        self.bindings = bindings
        self.buffer = BufferRigged.init([], *followers)
        self.cur = 0

    def listen(self, mod, key, unicode):
        try:
            self.bindings[mod][key](self)
        except KeyError:
            self.insert(unicode)

    def get_buffer(self):
        return ''.join(buffer)

    def get_cursor(self):
        return cur

    def set_buffer(self, buffer):
        self.buffer = buffer
        self.cur = len(buffer)

    def move_left(self):
        if self.cur > 0:
            self.cur -= 1

    def move_right(self):
        if self.cur < len(self.buffer):
            self.cur += 1

    def insert(self, new):
        self.buffer = self.buffer[:self.cur] + new + self.buffer[self.cur:]

    def backspace(self):
        self.buffer = self.buffer[:self.cur-1] + self.buffer[self.cur:]


BINDINGS_EMACS = {
    pg.KMOD_NONE: {
        pg.K_BACKSPACE: Editor.backspace
    },
    pg.KMOD_LCTRL: {
        pg.K_f: Editor.move_right,
        pg.K_b: Editor.move_right
    }
}
