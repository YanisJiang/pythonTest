class Vec2:
    x: float
    y: float

    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def __add__(self, other):
        return Vec2(self.x + other.x, self.y + other.y)

    def _sub__(self, other):
        return Vec2(self.x - other.x, self.y - other.y)
