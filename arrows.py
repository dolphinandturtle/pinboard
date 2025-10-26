import pygame as pg
import gui
import state


class HandlerArrows:
    def __init__(self, data_program, wrld, aux):
        self.arrows_xi = []
        self.arrows_xf = []
        self.arrows_yi = []
        self.arrows_yf = []
        for xi, xf, yi, yf, id, ids_exit in zip(
                wrld.cards_xi, wrld.cards_xf,
                wrld.cards_yi, wrld.cards_yf,
                wrld.cards_id, wrld.cards_id_exit
        ):
            for id_exit in ids_exit:
                i = aux.cards_idmap[id_exit]
                self.arrows_xi.append((
                    wrld.camera.x_rel(xf) + wrld.camera.x_rel(xi)
                ) / 2)
                self.arrows_yi.append((
                    wrld.camera.y_rel(yf) + wrld.camera.y_rel(yi)
                ) / 2)
                self.arrows_xf.append((
                    wrld.camera.x_rel(wrld.cards_xf[i]) +
                    wrld.camera.x_rel(wrld.cards_xi[i])
                ) / 2)
                self.arrows_yf.append((
                    wrld.camera.y_rel(wrld.cards_yf[i]) +
                    wrld.camera.y_rel(wrld.cards_yi[i])
                ) / 2)

        self.buttons = gui.ButtonsLine(self.arrows_xi, self.arrows_xf, self.arrows_yi, self.arrows_yf)
        self.data_program = data_program

    def listen(self, event):
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
