import pygame as pg
import json
from dataclasses import dataclass, asdict
from toolbar import Toolbar
from world import HandlerWorld
import gui
import state
import pickle
from sys import argv


path_save = argv[1]


@dataclass(slots=True, order=True)
class DataProgram:
    width: int
    height: int
    font: str
    theme: gui.Theme
    action: state.Action
    environment: state.Environment


class Pinboard:
    def __init__(self, data_program, world):
        self.data_program = data_program
        self.screen = pg.display.set_mode((data_program.width, data_program.height))
        self.world = world
        self.toolbar = Toolbar(data_program)
        self.clock = pg.time.Clock()

    def run(self):
        while True:
            self.clock.tick(30)
            for event in pg.event.get():
                self.toolbar.listen(event)
                if not self.toolbar.activation:
                    self.world.listen(event)
                match self.data_program.action:
                    case state.Action.IDLE:
                        if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                            with open(path_save, "wb") as file:
                                pickle.dump(asdict(self.world.wrld), file)
                            pg.quit()
                            exit()
            self.screen.fill(self.data_program.theme.background)
            self.world.draw(self.screen)
            self.toolbar.draw(self.screen)
            pg.display.update()


if __name__ == "__main__":
    from entities import PersistentWorld
    pg.init()
    pg.font.init()
    pg.display.set_caption("pinboard")
    data_program = DataProgram(
        width=1280, height=720,
        font="Arial",
        theme=gui.DEFAULT_THEME,
        action=state.Action.IDLE,
        environment=state.Environment.GLOBAL
    )
    try:
        with open(path_save, "rb") as file:
            prog = Pinboard(data_program, HandlerWorld(data_program, PersistentWorld(**pickle.load(file))))
    except FileNotFoundError:
        prog = Pinboard(data_program, HandlerWorld(data_program))
    prog.run()
