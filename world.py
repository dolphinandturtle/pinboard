from dataclasses import dataclass, field
import pygame as pg
import gui
import state
from entities import Camera, AuxiliaryWorld, PersistentWorld
from text import HandlerText


class HandlerWorld:
    def __init__(self, data_program, wrld=None):
        self.wrld = PersistentWorld() if wrld is None else wrld
        self.aux = AuxiliaryWorld(self.wrld, data_program)
        # Auxiliary
        self.xi = 0
        self.yi = 0
        self.data_program = data_program
        self.buttons_rect = gui.ButtonsRect(
            self.wrld.cards_xi, self.wrld.cards_yi,
            self.wrld.cards_xf, self.wrld.cards_yf,
            self.wrld.cards_id, self.aux.cards_idmap
        )
        self.hnd_txt = HandlerText(self.data_program, self.wrld, self.aux)
        self.stage = 0
        self.id_base = 0

    def listen(self, event):
        match self.data_program.environment:
            case state.Environment.GLOBAL:
                self.listen_world(event)
            case state.Environment.CARD:
                self.listen_cards(event)
            case state.Environment.ARROW:
                self.listen_arrows(event)

    def listen_world(self, event):
        match self.data_program.action:
            case state.Action.MOVE:
                if event.type == pg.MOUSEBUTTONDOWN and self.stage == 0:
                    self.stage = 1
                if event.type == pg.MOUSEMOTION:
                    self.xi, self.yi = event.pos
                    if self.stage == 1:
                        dx, dy = event.rel
                        self.wrld.camera.move(-dx, -dy)
                elif event.type == pg.MOUSEBUTTONUP and self.stage == 1:
                    self.stage = 0
                elif event.type == pg.MOUSEWHEEL:
                    self.wrld.camera.zoom(self.xi, self.yi, -0.1 * event.y)

    def listen_arrows(self, event):
        match self.data_program.action:
            case state.Action.CREATE:
                if event.type in {pg.MOUSEBUTTONDOWN, pg.MOUSEBUTTONUP} and event.button == 1:
                    x, y = event.pos
                    x = self.wrld.camera.x_abs(x)
                    y = self.wrld.camera.y_abs(y)
                    ids = self.buttons_rect.probe(x, y)
                    if ids == []:
                        self.stage = 0
                        print("Not a valid node...")
                        return
                    elif self.stage == 0:
                        self.id_base = ids[-1]
                        index = self.aux.cards_idmap[self.id_base]
                        self.xi = (self.wrld.cards_xf[index] + self.wrld.cards_xi[index]) / 2
                        self.yi = (self.wrld.cards_yf[index] + self.wrld.cards_yi[index]) / 2
                        self.stage = 1
                    elif self.stage == 2:
                        id_final = ids[-1]
                        self.wrld.link(self.id_base, id_final, self.aux)
                        self.stage = 0
                elif event.type == pg.MOUSEMOTION and self.stage == 1:
                    self.stage = 2

    def listen_cards(self, event):
        match self.data_program.action:
            case state.Action.CREATE:
                if event.type == pg.MOUSEBUTTONDOWN and event.button == 1 and self.stage == 0:
                    self.xi, self.yi = event.pos
                    self.stage = 1
                elif event.type == pg.MOUSEMOTION and self.stage == 1:
                    self.stage = 2
                elif event.type == pg.MOUSEBUTTONUP and event.button == 1 and self.stage == 2:
                    xf, yf = event.pos
                    if (xf - self.xi) < 0:
                        self.xi, xf = xf, self.xi
                    if (yf - self.yi) < 0:
                        self.yi, yf = yf, self.yi
                    id_spawn = self.wrld.spawn(
                        self.wrld.camera.x_abs(self.xi),
                        self.wrld.camera.x_abs(xf),
                        self.wrld.camera.y_abs(self.yi),
                        self.wrld.camera.y_abs(yf),
                        self.aux
                    )
                    self.aux.caches_render_card[self.aux.cards_idmap[id_spawn]].fill(self.data_program.theme.card_isolated)
                    self.stage = 0

        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1 and self.stage == 0:
            x, y = event.pos
            x = self.wrld.camera.x_abs(x)
            y = self.wrld.camera.y_abs(y)
            ids = self.buttons_rect.probe(x, y)
            if ids == []:
                self.stage = 0
                print("Not a valid node...")
                return
            match self.data_program.action:
                case state.Action.REMOVE:
                    id_del = ids[-1]
                    self.wrld.kill(id_del, self.aux)
                case state.Action.EDIT:
                    self.hnd_txt.set_mount(self.aux.cards_idmap[ids[0]])
                case state.Action.MOVE:
                    self.id_base = ids[-1]
                    self.stage = 1

        match self.data_program.action:
            case state.Action.EDIT:
                self.hnd_txt.listen(event)

            case state.Action.MOVE:
                if event.type == pg.MOUSEMOTION and self.stage == 1:
                    dx, dy = event.rel
                    index = self.aux.cards_idmap[self.id_base]
                    self.wrld.cards_xf[index] += round(dx * self.wrld.camera.z)
                    self.wrld.cards_xi[index] += round(dx * self.wrld.camera.z)
                    self.wrld.cards_yf[index] += round(dy * self.wrld.camera.z)
                    self.wrld.cards_yi[index] += round(dy * self.wrld.camera.z)
                elif event.type == pg.MOUSEBUTTONUP and event.button == 1 and self.stage == 1:
                    self.stage = 0

    def draw(self, screen):
        self.draw_arrows(screen)
        self.draw_cards(screen)
        self.hnd_txt.draw(screen)

    def draw_cards(self, screen):
        for xi, xf, yi, yf, surf in zip(self.wrld.cards_xi, self.wrld.cards_xf, self.wrld.cards_yi, self.wrld.cards_yf, self.aux.caches_render_card):
            xi_rel = self.wrld.camera.x_rel(xi)
            xf_rel = self.wrld.camera.x_rel(xf)
            yi_rel = self.wrld.camera.y_rel(yi)
            yf_rel = self.wrld.camera.y_rel(yf)
            if (not (0 <= xi_rel <= xf_rel <= self.data_program.width) and
                not (0 <= yi_rel <= yf_rel <= self.data_program.height)):
                continue
            scaled = pg.transform.scale(surf, (
                self.wrld.camera.len_rel(xf - xi),
                self.wrld.camera.len_rel(yf - yi)
            ))
            screen.blit(scaled, (xi_rel, yi_rel))

    def draw_arrows(self, screen):
        for xi, xf, yi, yf, id, ids_exit in zip(self.wrld.cards_xi, self.wrld.cards_xf, self.wrld.cards_yi, self.wrld.cards_yf, self.wrld.cards_id, self.wrld.cards_id_exit):
            # Coordinates of parent card's center
            xci = (self.wrld.camera.x_rel(xf) + self.wrld.camera.x_rel(xi)) / 2
            yci = (self.wrld.camera.y_rel(yf) + self.wrld.camera.y_rel(yi)) / 2
            for id_exit in ids_exit:
                i = self.aux.cards_idmap[id_exit]
                # Coordinates of child card's center
                xcf = (
                    self.wrld.camera.x_rel(self.wrld.cards_xf[i]) +
                    self.wrld.camera.x_rel(self.wrld.cards_xi[i])
                ) / 2
                ycf = (
                    self.wrld.camera.y_rel(self.wrld.cards_yf[i]) +
                    self.wrld.camera.y_rel(self.wrld.cards_yi[i])
                ) / 2
                gui.draw_arrow(screen, self.data_program.theme.arrow_uni, (xci, yci), (xcf, ycf), width=3)
