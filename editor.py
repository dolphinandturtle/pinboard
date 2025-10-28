from dataclasses import dataclass
from typing import Callable
import pygame as pg


@dataclass(slots=True, frozen=True)
class CoBuffer:
    buffer: list
    encoder: Callable


class Editor:
    def __init__(self, bindings, *cobuffers):
        self.bindings = bindings
        self.cobuffers = cobuffers
        self.buffer = ""
        self.cur = 0

    def listen(self, mod, key, unicode):
        try:
            self.bindings[mod][key](self)
        except KeyError:
            self.insert(unicode)

    def get_buffer(self):
        return buffer

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
        for cobuf in self.cobuffers:
            cobuf.buffer = cobuf.buffer[:self.cur] + list(map(cobuf.encoder, new)) + cobuf.buffer[self.cur:]

    def backspace(self):
        self.buffer = self.buffer[:self.cur-1] + self.buffer[self.cur:]
        for cobuf in self.cobuffers:
            cobuf.buffer = cobuf.buffer[:cobuf.cur-1] + cobuf.buffer[cobuf.cur:]


BINDINGS_EMACS = {
    pg.KMOD_NONE: {
        pg.K_BACKSPACE: Editor.backspace
    },
    pg.KMOD_LCTRL: {
        pg.K_f: Editor.move_right,
        pg.K_b: Editor.move_right
    }
}
