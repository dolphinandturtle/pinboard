import pygame as pg
import gui
import state


class HandlerArrows:
    def __init__(self, data_program, camera, xi=None, yi=None, xf=None, yf=None, id=None, id_exit=None, idmap=None):
        self.camera = camera
        self.xi = [] if xi is None else xi
        self.yi = [] if yi is None else yi
        self.list_xf = [] if xf is None else xf
        self.list_yf = [] if yf is None else yf
        self.id = [] if id is None else id
        self.id_exit = [] if id is None else id_exit
        self.idmap = {} if idmap is None else idmap
        self.data_program = data_program

    def probe(self, x, y):
        WIDTH = 10
        ids_intersect_x = [
            (id_parent, id_child)
            for id_parent, xi, list_xf, id_child in zip(self.id, self.xi, self.list_xf, self.id_exit)
            for xf in list_xf
            if xi < x < xf
        ]
        out = []
        for id_parent, id_child in ids_intersect_x:
            i = self.idmap[id_parent]
            xi, list_xf = self.xi[i], self.list_xf[i]
            yi, list_yf = self.yi[i], self.list_yf[i]
            for xf, yf in zip(list_xf, list_yf):
                m = (yf - yi) / (xf - xi)
                ey = m * (x - xi) + yi
                if ey - WIDTH <= y <= ey + WIDTH:
                    out.append((id_parent, id_child))
        return out

    def draw(self, screen):
        for xi, yi, list_xf, list_yf in zip(self.xi, self.yi, self.list_xf, self.list_yf):
            for xf, yf in zip(list_xf, list_yf):
                gui.draw_arrow(screen, self.data_program.theme.arrow_uni, (self.camera.x_rel(xi), self.camera.y_rel(yi)), (self.camera.x_rel(xf), self.camera.y_rel(yf)), width=3)
