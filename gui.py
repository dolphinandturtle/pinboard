class Camera:
    def __init__(self, x=0, y=0, z=1):
        self.x = x
        self.y = y
        self.z = z

    def move(self, dx, dy):
        self.x += dx
        self.y += dy

    def x_rel(self, x_abs):
        return x_abs - self.x

    def x_abs(self, x_rel):
        return self.x + x_rel

    def y_rel(self, y_abs):
        return y_abs - self.y

    def y_abs(self, y_rel):
        return self.y + y_rel


class Buttons:
    def __init__(self, id_max=0, idmap=None, id=None, xi=None, yi=None, xf=None, yf=None):
        self.id_max = id_max
        self.idmap = {} if idmap is None else idmap
        self.id = [] if id is None else id
        self.xi = [] if xi is None else xi
        self.yi = [] if yi is None else yi
        self.xf = [] if xf is None else xf
        self.yf = [] if yf is None else yf

    def probe(self):
        pass

class Texts:
    def __init__(self, id_max=0, idmap=None, id=None, xi=None, yi=None, xf=None, yf=None, buffer=None):
        self.id_max = id_max
        self.idmap = {} if idmap is None else idmap
        self.id = [] if id is None else id
        self.xi = [] if xi is None else xi
        self.yi = [] if yi is None else yi
        self.xf = [] if xf is None else xf
        self.yf = [] if yf is None else yf
        self.buffer = [] if buffer is None else buffer

    def draw(self):
        pass

    def update(self):
        pass

class Boxes:
    def __init__(self, id_max=0, idmap=None, id=None, xi=None, yi=None, xf=None, yf=None):
        self.id_max = id_max
        self.idmap = {} if idmap is None else idmap
        self.id = [] if id is None else id
        self.xi = [] if xi is None else xi
        self.yi = [] if yi is None else yi
        self.xf = [] if xf is None else xf
        self.yf = [] if yf is None else yf

    def draw(self):
        pass

    def update(self):
        pass
