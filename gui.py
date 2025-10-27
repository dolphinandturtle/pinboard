import pygame as pg
from dataclasses import dataclass
from math import cos, sin, hypot
from math import pi


@dataclass(slots=True, frozen=True)
class Theme:
    background: str
    button_hover: str
    arrow_uni: str
    arrow_bi: str
    card_isolated: str
    card_axiom: str
    card_theorem: str
    card_thesis: str
    card_focused: str
    text_card: str
    text_widget: str

DEFAULT_THEME = Theme(
    background="#333344",
    button_hover="#ffffff",
    arrow_uni="#dddddd",
    arrow_bi="#ffffff",
    card_isolated="#ffffff",
    card_axiom="#ffbbbb",
    card_theorem="#ffffaa",
    card_thesis="#aaff33",
    card_focused="#ffffaa",
    text_card="#000000",
    text_widget="#777799"
)

class ButtonsRect:
    def __init__(self, xi=None, yi=None, xf=None, yf=None, id=None, idmap=None):
        self.xi = [] if xi is None else xi
        self.yi = [] if yi is None else yi
        self.xf = [] if xf is None else xf
        self.yf = [] if yf is None else yf
        self.id = [] if id is None else id
        self.idmap = {} if idmap is None else idmap

    def probe(self, x, y) -> int:
        ids_intersect_x = [id for id, xi, xf in zip(self.id, self.xi, self.xf) if xi < x < xf]
        return [id for id in ids_intersect_x if self.yi[self.idmap[id]] < y < self.yf[self.idmap[id]]]


def draw_text(surface, x, y, text, font, color):
    for dy, line in enumerate(text.split('\n')):
        surface.blit(font.render(line, True, color), (
            x, y + font.get_height() * dy
        ))
    
def draw_arrow(screen, color, pos_i, pos_f, width):
    c = cos(0.8*pi)
    s = sin(0.8*pi)
    xi, yi = pos_i
    xf, yf = pos_f
    xc, yc = (xf + xi) / 2, (yf + yi) / 2
    xp, yp = xf*.55 + xi*.45, yf*.55 + yi*.45
    dx, dy = xp - xc, yp - yc
    xl, yl = (+dx*c - dy*s) + xc, (+dx*s + dy*c) + yc
    xr, yr = (+dx*c + dy*s) + xc, (-dx*s + dy*c) + yc
    pg.draw.line(screen, color, pos_i, pos_f, width=width)
    pg.draw.polygon(screen, color, ((xp, yp), (xl, yl), (xr, yr)))
