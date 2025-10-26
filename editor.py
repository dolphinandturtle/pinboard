class Editor:
    def __init__(self):
        self.buffer = ""
        self.cur = 0

    def get_buffer(self):
        return buffer

    def get_cursor(self):
        return cur

    def set_buffer(self, buffer):
        self.buffer = buffer
        self.cur = len(buffer)

    def move_left(self):
        if self.cur > 0:
            self.cur -= 1

    def move_right(self):
        if self.cur < len(self.buffer):
            self.cur += 1

    def insert(self, new):
        return self.buffer[:self.cur] + new + self.buffer[self.cur:]

    def backspace(self):
        return self.buffer[:self.cur-1] + self.buffer[self.cur:]
