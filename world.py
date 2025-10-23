import pygame as pg
import gui
import state


class HandlerWorld:
    def __init__(
            self, data_program, cards_xi=None, cards_xf=None, cards_yi=None, cards_yf=None,
            cards_state_enter=None, cards_state_local=None, cards_state_exit=None,
            cards_buffer=None, cards_id=None, cards_id_enter=None, cards_id_exit=None
    ):
        # Position
        self.cards_xi = [] if cards_xi is None else cards_xi
        self.cards_xf = [] if cards_xf is None else cards_xf
        self.cards_yi = [] if cards_yi is None else cards_yi
        self.cards_yf = [] if cards_yf is None else cards_yf
        # Arrows
        self.cards_state_enter = [] if cards_state_enter is None else cards_state_enter
        self.cards_state_local = [] if cards_state_local is None else cards_state_local
        self.cards_state_exit  = [] if cards_state_exit is None else cards_state_exit
        # Text
        self.cards_buffer = [] if cards_buffer is None else cards_buffer
        # Ids
        self.cards_id       = [] if cards_id is None else cards_id
        self.cards_id_enter = [] if cards_id_enter is None else cards_id_enter
        self.cards_id_exit  = [] if cards_id_exit is None else cards_id_exit
        # Auxiliary
        self.xi = 0
        self.yi = 0
        self.cam = gui.Camera()
        self.data_program = data_program
        self.cards_idmap = {id: i for i, id in enumerate(self.cards_id)}
        self.buttons_rect = gui.ButtonsRect(
            self.cards_xi, self.cards_yi,
            self.cards_xf, self.cards_yf,
            self.cards_id, self.cards_idmap
        )
        # TODO:
        # BoxesOfText will handle all the text processing, rename to HandlerText.
        self.buffer_metrics = []
        self.boxes_of_text = gui.BoxesOfText(data_program)
        # TODO:
        # surface_text and surface_card need to be loaded
        self.surface_text = []
        self.surface_card = []
        self.stage = 0
        self.focused = 0
        self.id_base = 0

    def dump(self) -> list:
        return [
            self.cards_xi, self.cards_xf, self.cards_yi, self.cards_yf,
            self.cards_state_enter, self.cards_state_local, self.cards_state_exit,
            self.cards_buffer, self.cards_id, self.cards_id_enter, self.cards_id_exit
        ]

    def spawn(self, xi, xf, yi, yf) -> int:
        self.cards_xi.append(xi)
        self.cards_xf.append(xf)
        self.cards_yi.append(yi)
        self.cards_yf.append(yf)
        self.cards_state_enter.append(list())
        self.cards_state_local.append(state.StateCard.ISOLATED)
        self.cards_state_exit.append(list())
        self.cards_id_enter.append(list())
        self.cards_id_exit.append(list())
        self.cards_buffer.append(str())
        self.buffer_metrics.append(list())
        id = max(self.cards_id) + 1 if self.cards_id else 0
        # Order matters for the following two operations.
        self.cards_idmap[id] = len(self.cards_id)
        self.cards_id.append(id)
        return id

    def kill(self, id):
        idel = self.cards_idmap[id]
        for id2 in self.cards_id_enter[idel]:
            idel2 = self.cards_idmap[id2]
            self.cards_id_exit[idel2].remove(id)
        for id3 in self.cards_id_exit[idel]:
            idel3 = self.cards_idmap[id3]
            self.cards_id_enter[idel3].remove(id)
        del self.cards_xi[idel]
        del self.cards_xf[idel]
        del self.cards_yi[idel]
        del self.cards_yf[idel]
        del self.cards_state_enter[idel]
        del self.cards_state_local[idel]
        del self.cards_state_exit[idel]
        del self.cards_buffer[idel]
        del self.buffer_metrics[idel]
        del self.cards_id[idel]
        del self.cards_id_enter[idel]
        del self.cards_id_exit[idel]
        del self.surface_card[idel]
        del self.surface_text[idel]

        # Update dictionary
        '''Every index gt. than that of the deleted id's
        is going to move back by 1.'''
        inf = self.cards_idmap[id]
        del self.cards_idmap[id]
        for id in self.cards_id[inf:]:
            self.cards_idmap[id] -= 1

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
                        self.cam.move(-dx, -dy)
                elif event.type == pg.MOUSEBUTTONUP and self.stage == 1:
                    self.stage = 0
                elif event.type == pg.MOUSEWHEEL:
                    self.cam.zoom(self.xi, self.yi, -0.1 * event.y)

    def listen_arrows(self, event):
        match self.data_program.action:
            case state.Action.CREATE:
                if event.type in {pg.MOUSEBUTTONDOWN, pg.MOUSEBUTTONUP} and event.button == 1:
                    x, y = event.pos
                    x = self.cam.x_abs(x)
                    y = self.cam.y_abs(y)
                    ids = self.buttons_rect.probe(x, y)
                    if ids == []:
                        self.stage = 0
                        print("Not a valid node...")
                        return
                    elif self.stage == 0:
                        self.id_base = ids[-1]
                        index = self.cards_idmap[self.id_base]
                        self.xi = (self.cards_xf[index] + self.cards_xi[index]) / 2
                        self.yi = (self.cards_yf[index] + self.cards_yi[index]) / 2
                        self.stage = 1
                    elif self.stage == 2:
                        id_final = ids[-1]
                        index_base = self.cards_idmap[self.id_base]
                        index_final = self.cards_idmap[id_final]
                        self.cards_id_enter
                        self.cards_id_exit[index_base].append(id_final)
                        self.cards_id_enter[index_final].append(self.id_base)
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
                    self.spawn(
                        self.cam.x_abs(self.xi),
                        self.cam.x_abs(xf),
                        self.cam.y_abs(self.yi),
                        self.cam.y_abs(yf)
                    )
                    surf_card = pg.Surface((200, 100), pg.SRCALPHA)
                    surf_card.fill(self.data_program.theme.card_isolated)
                    self.surface_card.append(surf_card)
                    self.surface_text.append(surf_card)
                    self.stage = 0

        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1 and self.stage == 0:
            x, y = event.pos
            x = self.cam.x_abs(x)
            y = self.cam.y_abs(y)
            ids = self.buttons_rect.probe(x, y)
            if ids == []:
                self.stage = 0
                print("Not a valid node...")
                return
            match self.data_program.action:
                case state.Action.REMOVE:
                    id_del = ids[-1]
                    self.kill(id_del)
                case state.Action.EDIT:
                    self.focused = self.cards_idmap[ids[0]]
                case state.Action.MOVE:
                    self.id_base = ids[-1]
                    self.stage = 1

        match self.data_program.action:
            case state.Action.EDIT:
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_BACKSPACE and self.cards_buffer[self.focused]:
                        self.cards_buffer[self.focused] = self.cards_buffer[self.focused][:-1]
                        del self.buffer_metrics[self.focused][-1]
                        self.surface_text[self.focused] = self.boxes_of_text.render(self.cards_buffer[self.focused], 200, 100, self.buffer_metrics[self.focused])
                    elif event.unicode:
                        self.cards_buffer[self.focused] += event.unicode
                        self.buffer_metrics[self.focused].append(self.boxes_of_text.font.size(self.cards_buffer[self.focused])[0])
                        self.surface_text[self.focused] = self.boxes_of_text.render(self.cards_buffer[self.focused], 200, 100, self.buffer_metrics[self.focused])

            case state.Action.MOVE:
                if event.type == pg.MOUSEMOTION and self.stage == 1:
                    dx, dy = event.rel
                    index = self.cards_idmap[self.id_base]
                    self.cards_xf[index] += dx * self.cam.z
                    self.cards_xi[index] += dx * self.cam.z
                    self.cards_yf[index] += dy * self.cam.z
                    self.cards_yi[index] += dy * self.cam.z
                elif event.type == pg.MOUSEBUTTONUP and event.button == 1 and self.stage == 1:
                    self.stage = 0

    def draw(self, screen):
        self.draw_arrows(screen)
        self.draw_cards(screen)

    def draw_cards(self, screen):
        for xi, xf, yi, yf, id, ids_exit, surf_card, surf_text in zip(self.cards_xi, self.cards_xf, self.cards_yi, self.cards_yf, self.cards_id, self.cards_id_exit, self.surface_card, self.surface_text):
            width = self.cam.x_rel(xf) - self.cam.x_rel(xi)
            height = self.cam.x_rel(yf) - self.cam.x_rel(yi)
            x = self.cam.x_rel(xi)
            y = self.cam.y_rel(yi)
            screen.blit(pg.transform.scale(surf_card, (width, height)), (x, y))
            screen.blit(pg.transform.scale(surf_text, (width, height)), (x, y))

    def draw_arrows(self, screen):
        for xi, xf, yi, yf, id, ids_exit, surf_card, surf_text in zip(self.cards_xi, self.cards_xf, self.cards_yi, self.cards_yf, self.cards_id, self.cards_id_exit, self.surface_card, self.surface_text):
            # Coordinates of parent card's center
            xci = (self.cam.x_rel(xf) + self.cam.x_rel(xi)) / 2
            yci = (self.cam.y_rel(yf) + self.cam.y_rel(yi)) / 2
            for id_exit in ids_exit:
                i = self.cards_idmap[id_exit]
                # Coordinates of child card's center
                xcf = (
                    self.cam.x_rel(self.cards_xf[i]) +
                    self.cam.x_rel(self.cards_xi[i])
                ) / 2
                ycf = (
                    self.cam.y_rel(self.cards_yf[i]) +
                    self.cam.y_rel(self.cards_yi[i])
                ) / 2
                gui.draw_arrow(screen, self.data_program.theme.arrow_uni, (xci, yci), (xcf, ycf), width=3)
