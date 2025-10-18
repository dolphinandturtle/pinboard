import pygame as pg
from enum import Enum, auto
from bisect import bisect_left, bisect_right
from dataclasses import dataclass
from math import log2
import pickle


@dataclass(slots=True, frozen=True)
class Theme:
    background: str
    thread: str
    frame_focused: str
    frame_unfocused: str
    text: str

default_theme = Theme(
    background="#333344",
    thread="#880000",
    frame_focused="#ffffaa",
    frame_unfocused="#ffffff",
    text="#000000"
)


SIZE = WIDTH, HEIGHT = 1280, 720
pg.init()
pg.font.init()
pg.display.set_caption("pinboard")
screen = pg.display.set_mode(SIZE)
font = pg.font.SysFont("Arial", 16)


class State(Enum):
    IDLE = auto()
    PANNING = auto()
    LINK = auto()
    SELECTION = auto()
    FOCUSED = auto()

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

    def x_rel(self, x_abs):
        return round((x_abs - self.x) / self.z)

    def x_abs(self, x_rel):
        return round(self.x + (x_rel * self.z))

    def y_rel(self, y_abs):
        return round((y_abs - self.y) / self.z)

    def y_abs(self, y_rel):
        return round(self.y + (y_rel * self.z))

class Nodes:
    def __init__(self, id_max=0, idmap=None, id=None, xi=None, yi=None, xf=None, yf=None, buffer=None, slave=None, master=None):
        self.id_max = id_max
        self.idmap = {} if idmap is None else idmap
        self.id = [] if id is None else id
        self.xi = [] if xi is None else xi
        self.yi = [] if yi is None else yi
        self.xf = [] if xf is None else xf
        self.yf = [] if yf is None else yf
        self.buffer = [] if buffer is None else buffer
        self.slave = [] if slave is None else slave
        self.master = [] if master is None else master

    def spawn(self, xi, yi, xf, yf) -> int:
        id = self.id_max
        self.idmap[id] = len(self.id)
        self.id.append(id)
        self.xi.append(xi)
        self.xf.append(xf)
        self.yi.append(yi)
        self.yf.append(yf)
        self.buffer.append('')
        self.master.append([])
        self.slave.append([])
        self.id_max += 1
        return id

    def link(self, id_master, id_slave):
        self.slave[self.idmap[id_master]].append(id_slave)
        self.master[self.idmap[id_slave]].append(id_master)

    def probe(self, x, y) -> int:
        ids_intersect_x = [id for id, xi, xf in zip(self.id, self.xi, self.xf) if xi < x < xf]
        return [id for id in ids_intersect_x if self.yi[self.idmap[id]] < y < self.yf[self.idmap[id]]]

class State(Enum):
    IDLE = auto()
    PANNING = auto()
    CREATING = auto()
    EDITING = auto()

class Tool(Enum):
    BUILDER = auto()
    LINKER = auto()

class User:
    def __init__(self, focused=0, state=State.IDLE, tool=Tool.BUILDER):
        self.focused = focused
        self.state = state
        self.tool = tool
        self.args = []

def wrap_text(text, width_max, height_max, width_list) -> str:
    assert isinstance(text, str)
    assert isinstance(width_max, int)
    assert isinstance(height_max, int)
    assert isinstance(width_list, (list, tuple))
    assert all(isinstance(n, int) for n in width_list)
    output = []
    start = 0
    end = bisect_left(width_list, width_max)
    output.append(text[start:end])
    while end < len(text):
        start = end
        end = bisect_left(width_list, width_max, key=lambda t: t - width_list[end - 1])
        output.append(text[start:end])
    return '\n'.join(output)

try:
    with open("saves/global.save", "rb") as file:
        camera, nodes, user, font_metrics = pickle.load(file)
except FileNotFoundError:
    camera = Camera()
    nodes = Nodes()
    user = User()
    font_metrics = {}

def push_idle(event, user, camera):
    # Quit
    if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
        with open("saves/global.save", "wb") as file:
            pickle.dump([camera, nodes, user, font_metrics], file)
        pg.quit()
        exit()
    # Enter state
    if event.type == pg.MOUSEBUTTONDOWN:
        if event.button == 1:
            x_rel, y_rel = event.pos
            x_abs, y_abs = camera.x_abs(x_rel), camera.y_abs(y_rel)
            # Creating
            match user.tool:
                case Tool.BUILDER:
                    if ids := nodes.probe(x_abs, y_abs):
                        user.focused = ids[-1]
                        user.state = State.EDITING
                    else:
                        user.args.append(x_abs)
                        user.args.append(y_abs)
                        user.args.append(x_abs)
                        user.args.append(y_abs)
                        user.state = State.CREATING
                case Tool.LINKER:
                    if ids := nodes.probe(x_abs, y_abs):
                        user.args.append(x_abs)
                        user.args.append(y_abs)
                        user.args.append(x_abs)
                        user.args.append(y_abs)
                        user.args.append(ids[-1])
                        user.state = State.CREATING
        # Panning
        elif event.button == 2:
            user.state = State.PANNING

def push_panning(event, user, camera):
    if event.type == pg.MOUSEMOTION:
        dx, dy = event.rel
        camera.move(-dx, -dy)
    elif event.type == pg.MOUSEBUTTONUP and event.button == 2:
        user.state = State.IDLE

def push_creating(event, user, camera):
    if event.type == pg.MOUSEMOTION:
        xi, yi = event.pos
        user.args[2] = camera.x_abs(xi)
        user.args[3] = camera.y_abs(yi)
    elif event.type == pg.MOUSEBUTTONUP and event.button == 1:
        match user.tool:
            case Tool.BUILDER:
                id = nodes.spawn(*user.args)
                font_metrics[id] = []
                user.focused = id
                user.state = State.EDITING
            case Tool.LINKER:
                nodes.link(user.args[4], nodes.probe(user.args[2], user.args[3])[-1])
                user.state = State.IDLE
        user.args.clear()

x_cur, y_cur = 0, 0
while True:
    for event in pg.event.get():
        if event.type == pg.MOUSEMOTION:
            x_cur, y_cur = event.pos
        if event.type == pg.MOUSEWHEEL:
            camera.zoom(x_cur, y_cur, -0.1 * event.y)
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_b:
                user.tool = Tool.BUILDER
            elif event.key == pg.K_l:
                user.tool = Tool.LINKER
        match user.state:
            case State.IDLE:
                push_idle(event, user, camera)
            case State.PANNING:
                push_panning(event, user, camera)
            case State.CREATING:
                push_creating(event, user, camera)
            case State.EDITING:
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_BACKSPACE and nodes.buffer[user.focused]:
                        nodes.buffer[user.focused] = nodes.buffer[user.focused][:-1]
                        del font_metrics[user.focused][-1]
                    elif event.key == pg.K_ESCAPE:
                        user.state = State.IDLE
                    elif event.unicode:
                        nodes.buffer[user.focused] += event.unicode
                        font_metrics[user.focused].append(font.size(nodes.buffer[user.focused])[0])

    screen.fill(default_theme.background)
    match user.state:
        case State.CREATING:
            match user.tool:
                case Tool.BUILDER:
                    xi_abs, yi_abs, xf_abs, yf_abs = user.args
                    pg.draw.rect(screen, default_theme.frame_focused, (
                        camera.x_rel(xi_abs),
                        camera.y_rel(yi_abs),
                        camera.x_rel(xf_abs) - camera.x_rel(xi_abs),
                        camera.y_rel(yf_abs) - camera.y_rel(yi_abs)
                    ))
                case Tool.LINKER:
                    xi_abs, yi_abs, xf_abs, yf_abs, *_ = user.args
                    pg.draw.line(
                        screen, default_theme.frame_focused,
                        (camera.x_rel(xi_abs), camera.y_rel(yi_abs)),
                        (camera.x_rel(xf_abs), camera.y_rel(yf_abs)),
                    )
                    
    for box_xi, box_yi, box_xf, box_yf, box_buf, box_id, box_slave in zip(nodes.xi, nodes.yi, nodes.xf, nodes.yf, nodes.buffer, nodes.id, nodes.slave):
        for slv in box_slave:
            i = nodes.idmap[slv]
            box_xc_i, box_yc_i = (box_xf + box_xi) / 2, (box_yf + box_yi) / 2,
            box_xc_f, box_yc_f = (nodes.xf[i] + nodes.xi[i]) / 2, (nodes.yf[i] + nodes.yi[i]) / 2,
            pg.draw.line(
                screen, default_theme.thread,
                (camera.x_rel(box_xc_i), camera.y_rel(box_yc_i)),
                (camera.x_rel(box_xc_f), camera.y_rel(box_yc_f)),
            )

    for box_xi, box_yi, box_xf, box_yf, box_buf, box_id, box_slave in zip(nodes.xi, nodes.yi, nodes.xf, nodes.yf, nodes.buffer, nodes.id, nodes.slave):
        pg.draw.rect(screen, default_theme.frame_focused if user.state == State.EDITING and box_id == user.focused else default_theme.frame_unfocused, (
            camera.x_rel(box_xi),
            camera.y_rel(box_yi),
            camera.x_rel(box_xf) - camera.x_rel(box_xi),
            camera.y_rel(box_yf) - camera.y_rel(box_yi)
        ))
        text = wrap_text(box_buf, camera.x_rel(box_xf) - camera.x_rel(box_xi), camera.y_rel(box_yf) - camera.y_rel(box_yi), font_metrics[box_id])
        for dy, line in enumerate(text.split('\n')):
            screen.blit(font.render(line, True, default_theme.text), (
                camera.x_rel(box_xi),
                camera.y_rel(box_yi) + font.get_height() * dy
            ))

    pg.display.update()
