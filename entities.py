from dataclasses import dataclass, field
import pygame as pg
import state


class Camera:
    def __init__(self, x=0, y=0, z=1):
        self.x = x
        self.y = y
        self.z = z

    def move(self, dx, dy):
        self.x += dx * self.z
        self.y += dy * self.z

    def zoom(self, x_rel, y_rel, fac):
        self.x -= x_rel * fac
        self.y -= y_rel * fac
        self.z += fac

    def len_rel(self, len_abs):
        return len_abs / self.z

    def len_abs(self, len_rel):
        return len_rel * self.z

    def x_rel(self, x_abs):
        return round((x_abs - self.x) / self.z)

    def x_abs(self, x_rel):
        return round(self.x + (x_rel * self.z))

    def y_rel(self, y_abs):
        return round((y_abs - self.y) / self.z)

    def y_abs(self, y_rel):
        return round(self.y + (y_rel * self.z))


class AuxiliaryWorld:
    def __init__(self, wrld, data_program):
        self.data_program = data_program
        count = len(wrld.cards_id)
        self.cards_idmap = {id: i for i, id in enumerate(wrld.cards_id)}
        self.buffer_metrics = [list() for _ in range(count)]
        self.caches_render_card = []
        self.caches_render_text = []

        self.arrows_xi = []
        self.arrows_yi = []
        self.arrows_exit_xf = []
        self.arrows_exit_yf = []
        self.arrows_idmap = {}

        for xi, xf, yi, yf, ids_exit in zip(
                wrld.cards_xi, wrld.cards_xf, wrld.cards_yi,wrld.cards_yf,
                wrld.cards_id_exit
        ):
            size = (xf - xi, yf - yi)
            self.caches_render_card.append(pg.Surface(size, pg.SRCALPHA))
            self.caches_render_text.append(pg.Surface(size, pg.SRCALPHA))
            self.arrows_xi.append((xf + xi) / 2)
            self.arrows_yi.append((yf + yi) / 2)
            xf, yf = list(), list()
            for id_exit in ids_exit:
                i = self.cards_idmap[id_exit]
                xf.append((wrld.cards_xf[i] + wrld.cards_xi[i]) / 2)
                yf.append((wrld.cards_yf[i] + wrld.cards_yi[i]) / 2)
            self.arrows_exit_xf.append(xf)
            self.arrows_exit_yf.append(yf)


@dataclass(slots=True, frozen=True)
class PersistentWorld:
    # Position
    # TODO: Remove camera from PersistentWorld
    camera:             Camera = field(default_factory=Camera)
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

    def get_width(self, i):
        return self.cards_xf[i] - self.cards_xi[i]

    def get_height(self, i):
        return self.cards_yf[i] - self.cards_yi[i]

    def spawn(self, xi, xf, yi, yf, aux) -> int:
        # Position
        self.cards_xi.append(xi)
        self.cards_xf.append(xf)
        self.cards_yi.append(yi)
        self.cards_yf.append(yf)
        aux.arrows_xi.append((xf + xi) / 2)
        aux.arrows_yi.append((yf + yi) / 2)
        # State
        self.cards_state_enter.append(list())
        self.cards_state_local.append(state.StateCard.ISOLATED)
        self.cards_state_exit.append(list())
        # Relations
        id = max(self.cards_id) + 1 if self.cards_id else 0
        self.add_id(id, self.cards_id, aux.cards_idmap)
        self.cards_id_enter.append(list())
        self.cards_id_exit.append(list())
        aux.arrows_exit_xf.append(list())
        aux.arrows_exit_yf.append(list())
        # Text
        self.cards_buffer.append(str())
        aux.buffer_metrics.append(list())
        # Render
        size = (xf - xi, yf - yi)
        aux.caches_render_card.append(pg.Surface(size, pg.SRCALPHA))
        aux.caches_render_text.append(pg.Surface(size, pg.SRCALPHA))
        return id

    def kill(self, id, aux):
        idel = aux.cards_idmap[id]
        # Remove position
        del self.cards_xi[idel]
        del self.cards_xf[idel]
        del self.cards_yi[idel]
        del self.cards_yf[idel]
        del aux.arrows_xi[idel]
        del aux.arrows_yi[idel]
        # Remove states
        del self.cards_state_enter[idel]
        del self.cards_state_local[idel]
        del self.cards_state_exit[idel]
        # Remove buffer
        del self.cards_buffer[idel]
        del aux.buffer_metrics[idel]
        # Remove relations globally
        for id_child in self.cards_id_exit[idel]:
            ichild = aux.cards_idmap[id_child]
            self.cards_id_enter[ichild].remove(id)
            aux.caches_render_card[ichild].fill(self.get_color(
                count_arrows_in=len(self.cards_id_enter[ichild]),
                count_arrows_out=len(self.cards_id_exit[ichild]),
                aux=aux
            ))
        for id_parent in self.cards_id_enter[idel]:
            iparent = aux.cards_idmap[id_parent]
            i = self.cards_id_exit[iparent].index(id)
            del self.cards_id_exit[iparent][i]
            del aux.arrows_exit_xf[iparent][i]
            del aux.arrows_exit_yf[iparent][i]
            aux.caches_render_card[iparent].fill(self.get_color(
                count_arrows_in=len(self.cards_id_enter[iparent]),
                count_arrows_out=len(self.cards_id_exit[iparent]),
                aux=aux
            ))

        # Remove relations locally
        del self.cards_id_exit[idel]
        del self.cards_id_enter[idel]
        del aux.arrows_exit_xf[idel]
        del aux.arrows_exit_yf[idel]
        # Remove render caches
        del aux.caches_render_card[idel]
        del aux.caches_render_text[idel]
        # Update cards_idmap
        self.del_id(id, self.cards_id, aux.cards_idmap)

    def link(self, id_parent, id_child, aux):
        iparent = aux.cards_idmap[id_parent]
        ichild = aux.cards_idmap[id_child]
        self.cards_id_exit[iparent].append(id_child)
        self.cards_id_enter[ichild].append(id_parent)
        aux.arrows_exit_xf[iparent].append((self.cards_xf[ichild] + self.cards_xi[ichild]) / 2)
        aux.arrows_exit_yf[iparent].append((self.cards_yf[ichild] + self.cards_yi[ichild]) / 2)
        aux.caches_render_card[iparent].fill(self.get_color(
            count_arrows_in=len(self.cards_id_enter[iparent]),
            count_arrows_out=len(self.cards_id_exit[iparent]),
            aux=aux
        ))
        aux.caches_render_card[ichild].fill(self.get_color(
            count_arrows_in=len(self.cards_id_enter[ichild]),
            count_arrows_out=len(self.cards_id_exit[ichild]),
            aux=aux
        ))

    def unlink(self, id_parent, id_child, aux):
        ichild = self.cards_idmap[id_child]
        iparent = self.cards_idmap[id_parent]
        # Positions
        del aux.arrows_exit_xf[iparent]
        del aux.arrows_exit_yf[iparent]
        # Relations
        self.cards_id_exit[ichild].remove(id_parent)
        self.cards_id_enter[iparent].remove(id_child)

    @staticmethod
    def add_id(id, /, list_id, idict_id):
        idict_id[id] = len(list_id)
        list_id.append(id)

    @staticmethod
    def del_id(id, /, list_id, idict_id):
        '''Every index gt. than that of the deleted id's
        is going to move back by 1.'''
        inf = idict_id.pop(id)
        del list_id[inf]
        for id in list_id[inf:]:
            idict_id[id] -= 1

    @staticmethod
    def get_color(count_arrows_in, count_arrows_out, aux):
        if count_arrows_in == 0 and count_arrows_out == 0:
            return aux.data_program.theme.card_isolated
        elif count_arrows_in > 0 and count_arrows_out > 0:
            return aux.data_program.theme.card_theorem
        elif count_arrows_in > 0 and count_arrows_out == 0:
            return aux.data_program.theme.card_thesis
        elif count_arrows_in == 0 and count_arrows_out > 0:
            return aux.data_program.theme.card_axiom
