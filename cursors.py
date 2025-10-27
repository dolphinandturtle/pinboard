import pygame as pg
from dataclasses import dataclass
from enum import Enum, auto
import gui


class Stage(Enum):
    INIT = auto()
    SET = auto()


@dataclass(slots=True, frozen=True)
class Rect:
    xi: int
    xf: int
    yi: int
    yf: int


class CursorRect:

    def __init__(self):
        self.__xi__ = 0
        self.__yi__ = 0
        self.xi = 0
        self.xf = 0
        self.yi = 0
        self.yf = 0
        self.stage = Stage.INIT
        self.buffer = []

    def pull(self) -> Rect:
        return self.buffer.pop()

    def listen(self, event) -> bool:
        match self.stage:
            case Stage.INIT:
                if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                    self.__xi__, self.__yi__ = event.pos
                    self.xi, self.yi = event.pos
                    self.xf, self.yf = event.pos
                    self.stage = Stage.SET
            case Stage.SET:
                if event.type == pg.MOUSEMOTION:
                    xf, yf = event.pos
                    self.xi, self.xf = (self.__xi__, xf) if (xf - self.__xi__) > 0 else (xf, self.__xi__)
                    self.yi, self.yf = (self.__yi__, yf) if (yf - self.__yi__) > 0 else (yf, self.__yi__)
                elif event.type == pg.MOUSEBUTTONUP and event.button == 1:
                    self.stage = Stage.INIT
                    self.buffer.append(Rect(self.xi, self.xf, self.yi, self.yf))
                    return True
        return False

    def draw(self, screen):
        THICK = 3
        match self.stage:
            case Stage.SET:
                pg.draw.rect(screen, "#999999", (
                    self.xi, self.yi,
                    self.xf - self.xi,  # width
                    self.yf - self.yi   # height
                ), width=THICK)
        for rect in self.buffer:
            pg.draw.rect(screen, "#ffffff", (
                rect.xi, rect.yi,
                rect.xf - rect.xi,  # width
                rect.yf - rect.yi   # height
            ), width=THICK)


@dataclass(slots=True, frozen=True)
class Arrow:
    xi: int
    xf: int
    yi: int
    yf: int


class CursorArrow:

    def __init__(self):
        self.xi = 0
        self.xf = 0
        self.yi = 0
        self.yf = 0
        self.stage = Stage.INIT
        self.buffer = []

    def pull(self) -> Arrow:
        return self.buffer.pop()

    def listen(self, event) -> bool:
        match self.stage:
            case Stage.INIT:
                if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                    self.xi, self.yi = event.pos
                    self.xf, self.yf = event.pos
                    self.stage = Stage.SET
            case Stage.SET:
                if event.type == pg.MOUSEMOTION:
                    self.xf, self.yf = event.pos
                elif event.type == pg.MOUSEBUTTONUP and event.button == 1:
                    self.stage = Stage.INIT
                    self.buffer.append(Arrow(self.xi, self.xf, self.yi, self.yf))
                    return True
        return False

    def draw(self, screen):
        THICK = 3
        match self.stage:
            case Stage.SET:
                gui.draw_arrow(screen, "#999999", (self.xi, self.yi), (self.xf, self.yf), THICK)
        for arrow in self.buffer:
            gui.draw_arrow(screen, "#ffffff", (arrow.xi, arrow.yi), (arrow.xf, arrow.yf), THICK)
