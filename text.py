from dataclasses import dataclass
import pygame as pg
import gui
import state
from bisect import bisect_left


class HandlerText:
    def  __init__(self, data_program, camera=None, cards_xi=None, cards_xf=None, cards_yi=None, cards_yf=None, cards_buffer=None, buffer_metrics=None, caches_render=None):
        self.cam = Camera() if camera is None else camera
        self.cards_xi = [] if cards_xi is None else cards_xi
        self.cards_xf = [] if cards_xf is None else cards_xf
        self.cards_yi = [] if cards_yi is None else cards_yi
        self.cards_yf = [] if cards_yf is None else cards_yf
        self.cards_buffer = [] if cards_buffer is None else cards_buffer
        self.buffer_metrics = [] if buffer_metrics is None else buffer_metrics
        self.caches_render = [] if caches_render is None else caches_render
        self.font = pg.font.SysFont("Arial", 16)
        self.data_program = data_program
        self.mount = 0

    def set_mount(self, n):
        self.mount = n

    def listen(self, event):
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_BACKSPACE and self.cards_buffer[self.mount]:
                self.cards_buffer[self.mount] = self.cards_buffer[self.mount][:-1]
                del self.buffer_metrics[self.mount][-1]
            elif event.unicode:
                self.cards_buffer[self.mount] += event.unicode
                self.buffer_metrics[self.mount].append(self.font.size(self.cards_buffer[self.mount])[0])
            text = self.wrap_text(self.cards_buffer[self.mount], 200, 100, self.buffer_metrics[self.mount])
            self.caches_render[self.mount] = gui.draw_text(text, self.font, self.data_program.theme.text_card, 200, 100)

    def draw(self, screen):
        for xi, xf, yi, yf, surf in zip(self.cards_xi, self.cards_xf, self.cards_yi, self.cards_yf, self.caches_render):
            width = self.cam.x_rel(xf) - self.cam.x_rel(xi)
            height = self.cam.x_rel(yf) - self.cam.x_rel(yi)
            x = self.cam.x_rel(xi)
            y = self.cam.y_rel(yi)
            screen.blit(pg.transform.scale(surf, (width, height)), (x, y))

    @staticmethod
    def wrap_text(text, width_max, height_max, width_list) -> str:
        assert isinstance(text, str)
        assert isinstance(width_max, int)
        assert isinstance(height_max, int)
        assert isinstance(width_list, (list, tuple))
        assert all(isinstance(n, int) for n in width_list)
        output = []
        start = 0
        end = bisect_left(width_list, width_max)
        output.append(text[start:end])
        while end < len(text):
            start = end
            end = bisect_left(width_list, width_max, key=lambda t: t - width_list[end - 1])
            output.append(text[start:end])
        return '\n'.join(output)
        
