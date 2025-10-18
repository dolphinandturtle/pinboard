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


class ButtonsRect:
    def __init__(self, id_max=0, idmap=None, id=None, xi=None, yi=None, xf=None, yf=None):
        self.id_max = id_max
        self.idmap = {} if idmap is None else idmap
        self.id = [] if id is None else id
        self.xi = [] if xi is None else xi
        self.yi = [] if yi is None else yi
        self.xf = [] if xf is None else xf
        self.yf = [] if yf is None else yf

    def probe(self, x, y) -> int:
        ids_intersect_x = [id for id, xi, xf in zip(self.id, self.xi, self.xf) if xi < x < xf]
        return [id for id in ids_intersect_x if self.yi[self.idmap[id]] < y < self.yf[self.idmap[id]]]


class ButtonsLine:
    def __init__(self, id_max=0, idmap=None, id=None, xi=None, yi=None, xf=None, yf=None):
        self.id_max = id_max
        self.idmap = {} if idmap is None else idmap
        self.id = [] if id is None else id
        self.xi = [] if xi is None else xi
        self.yi = [] if yi is None else yi
        self.xf = [] if xf is None else xf
        self.yf = [] if yf is None else yf

    def probe(self, x, y) -> int:
        WIDTH = 10
        ids_intersect_x = [id for id, xi, xf in zip(self.id, self.xi, self.xf) if xi < x < xf]
        m = (yf - yi) / (xf - xi)
        m * (x - xi) + yi - WIDTH < y < m * (x - xi) + yi + WIDTH
        out = []
        for id in ids_intersect_x:
            i = self.idmap[id]
            xi, xf = self.xi[i], self.xf[i]
            yi, yf = self.yi[i], self.yf[i]
            m = (yf - yi) / (xf - xi)
            ey = m * (x - xi) + yi
            if ey - WIDTH <= y <= ey + WIDTH:
                out.append(id)
        return out


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

    def draw(self, screen, font):
        pass

    def update(self):
        pass

    @staticmethod
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

class Sprites:
    def __init__(self, id_max=0, idmap=None, id=None, xi=None, yi=None, xf=None, yf=None, surf=None):
        self.id_max = id_max
        self.idmap = {} if idmap is None else idmap
        self.id = [] if id is None else id
        self.xi = [] if xi is None else xi
        self.yi = [] if yi is None else yi
        self.xf = [] if xf is None else xf
        self.yf = [] if yf is None else yf
        self.surf = [] if surf is None else surf

    def draw(self):
        pass

    def update(self):
        pass
