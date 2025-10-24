from dataclasses import dataclass, field
import pygame as pg
import gui
import state
from text import HandlerText


class AuxiliaryWorld:
    def __init__(self, program_data, wrld):
        self.cards_idmap = {id: i for i, id in enumerate(wrld.cards_buffer)}
        self.buffer_metrics = []
        self.caches_render_card = []
        self.caches_render_text = []


@dataclass(slots=True, frozen=True)
class PersistentWorld:
    # Position
    camera:             gui.Camera = field(default_factory=gui.Camera)
    cards_xi:           list[int]  = field(default_factory=list)
    cards_xf:           list[int]  = field(default_factory=list)
    cards_yi:           list[int]  = field(default_factory=list)
    cards_yf:           list[int]  = field(default_factory=list)
    # Arrows
    cards_state_enter:  list[list[state.FlowArrow]] = field(default_factory=list)
    cards_state_local:  list[state.StateCard]       = field(default_factory=list)
    cards_state_exit:   list[list[state.FlowArrow]] = field(default_factory=list)
    # Text
    cards_buffer:       list[str] = field(default_factory=list)
    # Relations
    cards_id:           list[int]       = field(default_factory=list)
    cards_id_enter:     list[list[int]] = field(default_factory=list)
    cards_id_exit:      list[list[int]] = field(default_factory=list)

    def spawn(self, xi, xf, yi, yf, aux) -> int:
        id = max(self.cards_id) + 1 if self.cards_id else 0
        # Position
        self.cards_xi.append(xi)
        self.cards_xf.append(xf)
        self.cards_yi.append(yi)
        self.cards_yf.append(yf)
        # State
        self.cards_state_enter.append(list())
        self.cards_state_local.append(state.StateCard.ISOLATED)
        self.cards_state_exit.append(list())
        # Relations
        aux.cards_idmap[id] = len(self.cards_id)
        self.cards_id.append(id)
        self.cards_id_enter.append(list())
        self.cards_id_exit.append(list())
        # Text
        self.cards_buffer.append(str())
        aux.buffer_metrics.append(list())
        # Render
        surf = pg.Surface((200, 100), pg.SRCALPHA)
        surf.fill("#ffffff")
        aux.caches_render_card.append(surf)
        aux.caches_render_text.append(pg.Surface((200, 100), pg.SRCALPHA))
        return id

    def kill(self, id, aux):
        idel = aux.cards_idmap[id]
        # Remove position
        del self.cards_xi[idel]
        del self.cards_xf[idel]
        del self.cards_yi[idel]
        del self.cards_yf[idel]
        # Remove states
        del self.cards_state_enter[idel]
        del self.cards_state_local[idel]
        del self.cards_state_exit[idel]
        # Remove buffer
        del self.cards_buffer[idel]
        del aux.buffer_metrics[idel]
        # Remove relations globally
        for id_parent in self.cards_id_exit[idel]:
            self.cards_id_enter[aux.cards_idmap[id_parent]].remove(id)
        for id_child in self.cards_id_enter[idel]:
            self.cards_id_exit[aux.cards_idmap[id_child]].remove(id)
        # Remove relations locally
        del self.cards_id[idel]
        del self.cards_id_exit[idel]
        del self.cards_id_enter[idel]
        # Remove render caches
        del aux.caches_render_card[idel]
        del aux.caches_render_text[idel]
        # Update idmap
        '''Every index gt. than that of the deleted id's
        is going to move back by 1.'''
        inf = aux.cards_idmap[id]
        del aux.cards_idmap[id]
        for id in self.cards_id[inf:]:
            aux.cards_idmap[id] -= 1

    def link(self, id_parent, id_child, aux):
        self.cards_id_exit[aux.cards_idmap[id_parent]].append(id_child)
        self.cards_id_enter[aux.cards_idmap[id_child]].append(id_parent)


class HandlerWorld:
    def __init__(self, data_program, wrld=None):
        self.wrld = PersistentWorld() if wrld is None else wrld
        self.aux = AuxiliaryWorld(data_program, self.wrld)
        # Auxiliary
        self.xi = 0
        self.yi = 0
        #self.cam = gui.Camera()
        self.data_program = data_program
        #self.cards_idmap = {id: i for i, id in enumerate(self.cards_id)}
        self.buttons_rect = gui.ButtonsRect(
            self.wrld.cards_xi, self.wrld.cards_yi,
            self.wrld.cards_xf, self.wrld.cards_yf,
            self.wrld.cards_id, self.aux.cards_idmap
        )
        self.hnd_txt = HandlerText(
            data_program,
            self.wrld.camera, self.wrld.cards_xi, self.wrld.cards_xf, self.wrld.cards_yi, self.wrld.cards_yf,
            self.wrld.cards_buffer, self.aux.buffer_metrics, self.aux.caches_render_text
        )
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
                    self.wrld.spawn(
                        self.wrld.camera.x_abs(self.xi),
                        self.wrld.camera.x_abs(xf),
                        self.wrld.camera.y_abs(self.yi),
                        self.wrld.camera.y_abs(yf),
                        self.aux
                    )
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
                    self.wrld.cards_xf[index] += dx * self.wrld.camera.z
                    self.wrld.cards_xi[index] += dx * self.wrld.camera.z
                    self.wrld.cards_yf[index] += dy * self.wrld.camera.z
                    self.wrld.cards_yi[index] += dy * self.wrld.camera.z
                elif event.type == pg.MOUSEBUTTONUP and event.button == 1 and self.stage == 1:
                    self.stage = 0

    def draw(self, screen):
        self.draw_arrows(screen)
        self.draw_cards(screen)
        self.hnd_txt.draw(screen)

    def draw_cards(self, screen):
        for xi, xf, yi, yf, surf in zip(self.wrld.cards_xi, self.wrld.cards_xf, self.wrld.cards_yi, self.wrld.cards_yf, self.aux.caches_render_card):
            width = self.wrld.camera.x_rel(xf) - self.wrld.camera.x_rel(xi)
            height = self.wrld.camera.x_rel(yf) - self.wrld.camera.x_rel(yi)
            x = self.wrld.camera.x_rel(xi)
            y = self.wrld.camera.y_rel(yi)
            screen.blit(pg.transform.scale(surf, (width, height)), (x, y))

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
