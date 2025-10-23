import pygame as pg
import gui
import state


class Toolbar:
    PATH_ICON_CREATE = "assets/icons/create.png"
    PATH_ICON_REMOVE = "assets/icons/remove.png"
    PATH_ICON_EDIT   = "assets/icons/edit.png"
    PATH_ICON_MOVE   = "assets/icons/move.png"
    PATH_ICON_GLOBAL = "assets/icons/global.png"
    PATH_ICON_CARD   = "assets/icons/card.png"
    PATH_ICON_ARROW  = "assets/icons/arrow.png"
    def __init__(self, data_program):
        self.data_program = data_program

        self.icon_create    = pg.transform.scale(pg.image.load(self.PATH_ICON_CREATE),  (self.data_program.width * 0.05, self.data_program.width * 0.05)).convert_alpha()
        self.icon_remove    = pg.transform.scale(pg.image.load(self.PATH_ICON_REMOVE),  (self.data_program.width * 0.05, self.data_program.width * 0.05)).convert_alpha()
        self.icon_edit      = pg.transform.scale(pg.image.load(self.PATH_ICON_EDIT),    (self.data_program.width * 0.05, self.data_program.width * 0.05)).convert_alpha()
        self.icon_move      = pg.transform.scale(pg.image.load(self.PATH_ICON_MOVE),    (self.data_program.width * 0.05, self.data_program.width * 0.05)).convert_alpha()
        self.icon_global    = pg.transform.scale(pg.image.load(self.PATH_ICON_GLOBAL),  (self.data_program.width * 0.05, self.data_program.width * 0.05)).convert_alpha()
        self.icon_card      = pg.transform.scale(pg.image.load(self.PATH_ICON_CARD),    (self.data_program.width * 0.05, self.data_program.width * 0.05)).convert_alpha()
        self.icon_arrow     = pg.transform.scale(pg.image.load(self.PATH_ICON_ARROW),   (self.data_program.width * 0.05, self.data_program.width * 0.05)).convert_alpha()
        self.icon_highlight = pg.Surface((self.data_program.width * 0.05, self.data_program.width * 0.05), pg.SRCALPHA)
        self.icon_highlight.fill(self.data_program.theme.button_hover)
        self.icon_highlight.set_alpha(60)

        self.envmap = [state.Environment.GLOBAL, state.Environment.CARD, state.Environment.ARROW]
        self.highlight_environment = self.envmap.index(self.data_program.environment)
        self.buttons_environment = gui.ButtonsRect(
            xi=[self.data_program.width * 0.95, self.data_program.width * 0.95, self.data_program.width * 0.95],
            yi=[self.data_program.width * 0.00, self.data_program.width * 0.05, self.data_program.width * 0.10],
            xf=[self.data_program.width * 1.00, self.data_program.width * 1.00, self.data_program.width * 1.00],
            yf=[self.data_program.width * 0.05, self.data_program.width * 0.10, self.data_program.width * 0.15],
            id=[0                             , 1                             , 2                             ],
            idmap={0: 0, 1: 1, 2: 2}
        )

        self.actmap = [state.Action.CREATE, state.Action.REMOVE, state.Action.EDIT, state.Action.MOVE, state.Action.IDLE]
        self.highlight_action = self.actmap.index(self.data_program.action)
        self.buttons_action = gui.ButtonsRect(
            xi=[self.data_program.width * 0.95, self.data_program.width * 0.95, self.data_program.width * 0.95, self.data_program.width * 0.95],
            yi=[self.data_program.width * 0.15, self.data_program.width * 0.20, self.data_program.width * 0.25, self.data_program.width * 0.30],
            xf=[self.data_program.width * 1.00, self.data_program.width * 1.00, self.data_program.width * 1.00, self.data_program.width * 1.00],
            yf=[self.data_program.width * 0.20, self.data_program.width * 0.25, self.data_program.width * 0.30, self.data_program.width * 0.35],
            id=[0                             , 1                             , 2                             , 3                             ],
            idmap={0: 0, 1: 1, 2: 2, 3: 3}
        )
        self.environment_queued = self.data_program.environment
        self.action_queued = self.data_program.action
        self.activation = False

    def draw(self, screen):
        screen.blit(self.icon_global, (self.data_program.width * 0.95, self.data_program.width * 0.00))
        screen.blit(self.icon_card,   (self.data_program.width * 0.95, self.data_program.width * 0.05))
        screen.blit(self.icon_arrow,  (self.data_program.width * 0.95, self.data_program.width * 0.10))
        screen.blit(self.icon_create, (self.data_program.width * 0.95, self.data_program.width * 0.15))
        screen.blit(self.icon_remove, (self.data_program.width * 0.95, self.data_program.width * 0.20))
        screen.blit(self.icon_edit,   (self.data_program.width * 0.95, self.data_program.width * 0.25))
        screen.blit(self.icon_move,   (self.data_program.width * 0.95, self.data_program.width * 0.30))

        screen.blit(self.icon_highlight, (self.data_program.width * 0.95, self.data_program.width * (0.00 + self.highlight_environment * 0.05)))
        if self.highlight_action < len(self.actmap) - 1:
            screen.blit(self.icon_highlight, (self.data_program.width * 0.95, self.data_program.width * (0.15 + self.highlight_action * 0.05)))
        pg.draw.rect(screen, self.data_program.theme.text_widget, (
            self.data_program.width * 0.95, self.data_program.width * 0.00,
            self.data_program.width * 0.05, self.data_program.width * 0.05
        ), width=3)
        pg.draw.rect(screen, self.data_program.theme.text_widget, (
            self.data_program.width * 0.95, self.data_program.width * 0.05,
            self.data_program.width * 0.05, self.data_program.width * 0.05
        ), width=3)
        pg.draw.rect(screen, self.data_program.theme.text_widget, (
            self.data_program.width * 0.95, self.data_program.width * 0.10,
            self.data_program.width * 0.05, self.data_program.width * 0.05
        ), width=3)
        pg.draw.rect(screen, self.data_program.theme.text_widget, (
            self.data_program.width * 0.95, self.data_program.width * 0.15,
            self.data_program.width * 0.05, self.data_program.width * 0.05
        ), width=3)
        pg.draw.rect(screen, self.data_program.theme.text_widget, (
            self.data_program.width * 0.95, self.data_program.width * 0.20,
            self.data_program.width * 0.05, self.data_program.width * 0.05
        ), width=3)
        pg.draw.rect(screen, self.data_program.theme.text_widget, (
            self.data_program.width * 0.95, self.data_program.width * 0.25,
            self.data_program.width * 0.05, self.data_program.width * 0.05
        ), width=3)
        pg.draw.rect(screen, self.data_program.theme.text_widget, (
            self.data_program.width * 0.95, self.data_program.width * 0.30,
            self.data_program.width * 0.05, self.data_program.width * 0.05
        ), width=3)

    def listen(self, event):
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            ids_environment = self.buttons_environment.probe(*event.pos)
            ids_action = self.buttons_action.probe(*event.pos)
            if ids_environment:
                self.activation = True
                self.environment_queued = self.envmap[ids_environment[0]]
                self.highlight_environment = self.envmap.index(self.environment_queued)
            elif ids_action:
                self.activation = True
                if self.data_program.action != self.actmap[ids_action[0]]:
                    self.action_queued = self.actmap[ids_action[0]]
                    self.highlight_action = self.actmap.index(self.action_queued)
                else:
                    self.action_queued = state.Action.IDLE
                    self.highlight_action = len(self.actmap)
        elif event.type == pg.MOUSEBUTTONUP and event.button == 1 and self.activation:
            ids_environment = self.buttons_environment.probe(*event.pos)
            ids_action = self.buttons_action.probe(*event.pos)
            self.activation = False
            if ids_environment:
                self.data_program.environment = self.environment_queued
            else:
                self.highlight_environment = self.envmap.index(self.data_program.environment)
            if ids_action:
                self.data_program.action = self.action_queued
            else:
                self.highlight_action = self.actmap.index(self.data_program.action)
            print(self.data_program.environment, self.data_program.action)
