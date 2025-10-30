from dataclasses import dataclass, field
import pygame as pg
import gui
import state
from entities import Camera, AuxiliaryWorld, PersistentWorld
from text import HandlerText
from arrows import HandlerArrows
import cursors


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
        self.hnd_arr = HandlerArrows(
            self.data_program, self.wrld.camera,
            self.aux.arrows_xi, self.aux.arrows_yi,
            self.aux.arrows_exit_xf, self.aux.arrows_exit_yf,
            self.wrld.cards_id, self.wrld.cards_id_exit, self.aux.cards_idmap
        )
        self.cursor_rect = cursors.CursorRect()
        self.cursor_arrow = cursors.CursorArrow()
        self.stage = 0
        self.id_base = []

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
                if self.cursor_arrow.listen(event):
                    arrow = self.cursor_arrow.pull()
                    try:
                        id_parent = self.buttons_rect.probe(
                            self.wrld.camera.x_abs(arrow.xi),
                            self.wrld.camera.y_abs(arrow.yi)
                        )[-1]
                        id_child = self.buttons_rect.probe(
                            self.wrld.camera.x_abs(arrow.xf),
                            self.wrld.camera.y_abs(arrow.yf)
                        )[-1]
                        if id_parent != id_child:
                            self.wrld.link(id_parent, id_child, self.aux)
                    except IndexError:
                        pass

    def listen_cards(self, event):
        match self.data_program.action:
            case state.Action.IDLE:
                if self.cursor_rect.listen(event):
                    rect = self.cursor_rect.pull()
                    ids_intersect_x = [id for id, xi, xf in zip(self.wrld.cards_id, self.wrld.cards_xi, self.wrld.cards_xf) if self.wrld.camera.x_abs(rect.xi) < xi < xf < self.wrld.camera.x_abs(rect.xf)]
                    self.id_base = [id for id in ids_intersect_x if self.wrld.camera.y_abs(rect.yi) < self.wrld.cards_yi[self.aux.cards_idmap[id]] < self.wrld.cards_yf[self.aux.cards_idmap[id]] < self.wrld.camera.y_abs(rect.yf)]

            case state.Action.CREATE:
                if self.cursor_rect.listen(event):
                    rect = self.cursor_rect.pull()
                    id_spawn = self.wrld.spawn(
                        self.wrld.camera.x_abs(rect.xi),
                        self.wrld.camera.x_abs(rect.xf),
                        self.wrld.camera.y_abs(rect.yi),
                        self.wrld.camera.y_abs(rect.yf),
                        self.aux
                    )
                    self.aux.caches_render_card[self.aux.cards_idmap[id_spawn]].fill(self.data_program.theme.card_isolated)

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
                    #self.id_base = [ids[-1]]
                    self.stage = 1

        match self.data_program.action:
            case state.Action.EDIT:
                self.hnd_txt.listen(event)

            case state.Action.MOVE:
                if event.type == pg.MOUSEMOTION and self.stage == 1:
                    dx, dy = event.rel
                    #for index in map(self.aux.cards_idmap.__getitem__, self.id_base):
                    for id_child in self.id_base:
                        index = self.aux.cards_idmap[id_child]
                        self.wrld.cards_xi[index] += round(dx * self.wrld.camera.z)
                        self.wrld.cards_xf[index] += round(dx * self.wrld.camera.z)
                        self.wrld.cards_yi[index] += round(dy * self.wrld.camera.z)
                        self.wrld.cards_yf[index] += round(dy * self.wrld.camera.z)
                        self.aux.arrows_xi[index] += round(dx * self.wrld.camera.z)
                        self.aux.arrows_yi[index] += round(dy * self.wrld.camera.z)
                        for id_parent in self.wrld.cards_id_enter[index]:
                            iparent = self.aux.cards_idmap[id_parent]
                            for i, id in enumerate(self.wrld.cards_id_exit[iparent]):
                                if id == id_child:
                                    self.aux.arrows_exit_xf[iparent][i] += round(dx * self.wrld.camera.z)
                                    self.aux.arrows_exit_yf[iparent][i] += round(dy * self.wrld.camera.z)

                elif event.type == pg.MOUSEBUTTONUP and event.button == 1 and self.stage == 1:
                    self.stage = 0

    def draw(self, screen):
        self.hnd_arr.draw(screen)
        self.hnd_txt.draw(screen)
        self.cursor_rect.draw(screen)
        self.cursor_arrow.draw(screen)
