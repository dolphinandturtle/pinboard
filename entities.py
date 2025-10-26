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
        for xi, xf, yi, yf in zip(wrld.cards_xi, wrld.cards_xf, wrld.cards_yi, wrld.cards_yf):
            size = (xf - xi, yf - yi)
            self.caches_render_card.append(pg.Surface(size, pg.SRCALPHA))
            self.caches_render_text.append(pg.Surface(size, pg.SRCALPHA))


@dataclass(slots=True, frozen=True)
class PersistentWorld:
    # Position
    camera:             Camera = field(default_factory=Camera)   # TODO: Remove camera from PersistentWorld
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
            self.cards_id_exit[iparent].remove(id)
            aux.caches_render_card[iparent].fill(self.get_color(
                count_arrows_in=len(self.cards_id_enter[iparent]),
                count_arrows_out=len(self.cards_id_exit[iparent]),
                aux=aux
            ))
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
        iparent = aux.cards_idmap[id_parent]
        ichild = aux.cards_idmap[id_child]
        self.cards_id_exit[iparent].append(id_child)
        self.cards_id_enter[ichild].append(id_parent)
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
