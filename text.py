from dataclasses import dataclass
import pygame as pg
import gui
import state
from bisect import bisect_left


class HandlerText:
    def __init__(self, data_program, core, aux):
        self.font = pg.font.SysFont(data_program.font, 16)
        self.core = core
        self.aux = aux
        aux.buffer_metrics[:] = [
            [self.font.size(buffer[:i])[0] for i in range(len(buffer))]
            for buffer in core.cards_buffer
        ]
        for buffer, metrics, surface in zip(core.cards_buffer, aux.buffer_metrics, aux.caches_render):
            text = self.wrap_text(buffer, 200, 100, metrics)
            surface.fill(data_program.theme.card_isolated)
            gui.draw_text(surface, text, self.font, data_program.theme.text_card)
        self.data_program = data_program
        self.mount = 0

    def set_mount(self, n):
        self.mount = n

    def listen(self, event):
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_BACKSPACE and self.core.cards_buffer[self.mount]:
                self.core.cards_buffer[self.mount] = self.core.cards_buffer[self.mount][:-1]
                del self.aux.buffer_metrics[self.mount][-1]
            elif event.unicode:
                self.core.cards_buffer[self.mount] += event.unicode
                self.aux.buffer_metrics[self.mount].append(self.font.size(self.core.cards_buffer[self.mount])[0])
            text = self.wrap_text(self.core.cards_buffer[self.mount], 200, 100, self.aux.buffer_metrics[self.mount])
            surface = self.aux.caches_render[self.mount]
            surface.fill(self.data_program.theme.card_isolated)
            gui.draw_text(surface, text, self.font, self.data_program.theme.text_card)

    def draw(self, screen):
        for xi, xf, yi, yf, surf in zip(self.core.cards_xi, self.core.cards_xf, self.core.cards_yi, self.core.cards_yf, self.aux.caches_render):
            width = self.core.camera.x_rel(xf) - self.core.camera.x_rel(xi)
            height = self.core.camera.x_rel(yf) - self.core.camera.x_rel(yi)
            x = self.core.camera.x_rel(xi)
            y = self.core.camera.y_rel(yi)
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
        
