from array import array


class Framebuffer:
    width: int
    height: int
    color: []
    depth: []

    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height

        self.clear()

    def clear(self, rgb: (int, int, int) = (0, 0, 0), z: float = 1e9):
        n = self.width * self.height
        r, g, b = rgb
        self.color = array[int]("B", bytes([b, g, r, 0]) * n)
        self.depth = array[float]("f", [z]) * n

    def get_color(self, x: int, y: int):
        start = (y * self.width + x) * 4
        return [
            self.color[start],
            self.color[start + 1],
            self.color[start + 2],
            self.color[start + 3],
        ]

    def get_depth(self, x: int, y: int):
        return self.depth[y * self.width + x]

    def set_color(self, x: int, y: int, rgb: (int, int, int)):
        r, g, b = rgb
        alpha = 0
        start = (y * self.width + x) * 4
        self.color[start] = b
        self.color[start + 1] = g
        self.color[start + 2] = r
        self.color[start + 3] = alpha

    def set_depth(self, x: int, y: int, z: float):
        self.depth[y * self.width + x] = z

    def set_pixel(self, x: int, y: int, z: float, rgb: (int, int, int)):
        if x >= self.width or y >= self.height or x < 0 or y < 0:
            return
        cur_depth = self.get_depth(x, y)
        if z < cur_depth:
            self.set_color(x, y, rgb)
            self.set_depth(x, y, z)

    def to_bgra_bytes(self):
        return bytes(self.color)
