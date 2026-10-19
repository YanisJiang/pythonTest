from space_2d.vec2 import Vec2


class InputState:
    cur_key: set
    mouse_left: bool
    mouse_delta: Vec2

    def __init__(self) -> None:
        self.cur_key = set()
        self.mouse_left = False
        self.mouse_delta = Vec2(0, 0)

    def end_frame(self):
        self.mouse_delta.x = 0
        self.mouse_delta.y = 0
