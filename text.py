import pygame as pg
import gui
import state
from bisect import bisect_left


class HandlerText:
    def __init__(self, data_program, core, aux):
        self.font = pg.font.SysFont(data_program.font, 16)
        self.core = core
        self.aux = aux
        for xi, xf, yi, yf, buffer, metrics, id_enter, id_exit, surf_card, surf_text in zip(
                core.cards_xi, core.cards_xf, core.cards_yi, core.cards_yf, core.cards_buffer,
                aux.buffer_metrics, core.cards_id_enter, core.cards_id_exit,
                aux.caches_render_card, aux.caches_render_text
        ):
            surf_card.fill(core.get_color(len(id_enter), len(id_exit), aux))
            for i in range(len(buffer)):
                metrics.append(self.font.size(buffer[:i+1])[0])
            width = xf - xi
            height = yf - yi
            text = self.wrap_text(buffer, width * 0.90, height * 0.90, metrics)
            gui.draw_text(surf_text, width * 0.05, height * 0.05, text, self.font, data_program.theme.text_card)

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
            width_card = self.core.get_width(self.mount)
            height_card = self.core.get_height(self.mount)
            text = self.wrap_text(
                text=self.core.cards_buffer[self.mount],
                width_max=0.90 * width_card,
                height_max=0.90 * height_card,
                width_list=self.aux.buffer_metrics[self.mount]
            )
            surface = self.aux.caches_render_text[self.mount]
            surface.fill(0)
            gui.draw_text(surface, 0.05 * width_card, 0.05 * height_card, text, self.font, self.data_program.theme.text_card)

    def draw(self, screen):
        for xi, xf, yi, yf, surf in zip(self.core.cards_xi, self.core.cards_xf, self.core.cards_yi, self.core.cards_yf, self.aux.caches_render_text):
            xi_rel = self.core.camera.x_rel(xi)
            xf_rel = self.core.camera.x_rel(xf)
            yi_rel = self.core.camera.y_rel(yi)
            yf_rel = self.core.camera.y_rel(yf)
            if (not (0 <= xi_rel <= xf_rel <= self.data_program.width) and
                not (0 <= yi_rel <= yf_rel <= self.data_program.height)):
                continue
            scaled = pg.transform.scale(surf, (
                self.core.camera.len_rel(xf - xi),
                self.core.camera.len_rel(yf - yi)
            ))
            screen.blit(scaled, (xi_rel, yi_rel))

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
        
