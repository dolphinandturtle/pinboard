import pygame as pg
import json
from dataclasses import dataclass, asdict
from toolbar import Toolbar
from world import HandlerWorld
import gui
import state
import pickle


@dataclass(slots=True, order=True)
class DataProgram:
    width: int
    height: int
    theme: gui.Theme
    action: state.Action
    environment: state.Environment


class Pinboard:
    def __init__(self, data_program, world):
        self.data_program = data_program
        self.screen = pg.display.set_mode((data_program.width, data_program.height))
        self.world = world
        self.toolbar = Toolbar(data_program)

    def run(self):
        while True:
            for event in pg.event.get():
                self.toolbar.listen(event)
                if not self.toolbar.activation:
                    self.world.listen(event)
                match self.data_program.action:
                    case state.Action.IDLE:
                        if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                            #with open("saves/global.save", "wb") as file:
                            #    pickle.dump(self.world.dump(), file)
                            pg.quit()
                            exit()
            self.screen.fill(self.data_program.theme.background)
            self.world.draw(self.screen)
            self.toolbar.draw(self.screen)
            pg.display.update()
            


if __name__ == "__main__":
    pg.init()
    pg.font.init()
    pg.display.set_caption("pinboard")    
    data_program = DataProgram(
        width=1280, height=720,
        theme=gui.DEFAULT_THEME,
        action=state.Action.IDLE,
        environment=state.Environment.GLOBAL,
    )
    #try:
    #    with open("saves/global.save", "rb") as file:
    #        prog = Pinboard(data_program, HandlerWorld(data_program, *pickle.load(file)))
    #except FileNotFoundError:
    prog = Pinboard(data_program, HandlerWorld(data_program))
    prog.run()
