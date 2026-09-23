class Vec2:
    x: float
    y: float

    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def __add__(self, other):
        return Vec2(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vec2(self.x - other.x, self.y - other.y)

    def __mul__(self, scale: float):
        return Vec2(self.x * scale, self.y * scale)

    def __rmul__(self, scale: float):
        return Vec2(self.x * scale, self.y * scale)

    def __truediv__(self, other):
        if isinstance(other, Vec2):
            return Vec2(self.x / other.x, self.y / other.y)
        elif isinstance(other, float):
            return Vec2(self.x / other, self.y / other)
        else:
            return NotImplemented

    def dot(self, other):
        return self.x * other.x + self.y * other.y

    def cross(self, other):
        return self.x * other.y - self.y * other.x
