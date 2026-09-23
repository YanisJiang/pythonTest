class Color:
    r: float
    g: float
    b: float
    a: float

    def __init__(self, r: float, g: float, b: float, a: float = 255):
        self.r = r
        self.g = g
        self.b = b
        self.a = a

    @classmethod
    def from_list(cls, color: [float, float, float, float]):
        return cls(color[0], color[1], color[2], color[3])

    def __iter__(self):
        yield self.r
        yield self.g
        yield self.b
        yield self.a

    def to_list(self):
        return [self.r, self.g, self.b, self.a]
