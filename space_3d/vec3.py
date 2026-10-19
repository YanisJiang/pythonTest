from math import sqrt


class Vec3:
    x: float
    y: float
    z: float

    def __init__(self, x: float, y: float, z: float):
        self.x = x
        self.y = y
        self.z = z

    def __add__(self, other):
        return Vec3(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other):
        return Vec3(self.x - other.x, self.y - other.y, self.z - other.z)

    def __mul__(self, scale):
        return Vec3(self.x * scale, self.y * scale, self.z * scale)

    def __rmul__(self, scale):
        return Vec3(self.x * scale, self.y * scale, self.z * scale)

    def __truediv__(self, other):
        if isinstance(other, Vec3):
            return Vec3(self.x / other.x, self.y / other.y, self.z / other.z)
        if isinstance(other, (int, float)):
            return Vec3(self.x / other, self.y / other, self.z / other)
        else:
            return NotImplemented

    def __eq__(self, other, /) -> bool:
        return self.x == other.x and self.y == other.y and self.z == other.z

    def __str__(self) -> str:
        return f"(x: {self.x}, y:{self.y}, z: {self.z})"
    
    def __ne__(self, other, /) -> bool:
        return self.x != other.x or self.y != other.y or self.z != other.z

    def dot(self, other):
        return self.x * other.x + self.y * other.y + self.z * other.z

    def cross(self, other):
        return Vec3(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x,
        )

    def equals_zero(self):
        return self.length_sq() == 0

    def length_sq(self):
        return self.x * self.x + self.y * self.y + self.z * self.z

    def length(self):
        if self.equals_zero():
            return 0
        return sqrt(self.length_sq())

    def normalized(self):
        result = Vec3(0, 0, 0)
        if not self.equals_zero():
            inv_length = 1 / self.length()
            result.x = self.x * inv_length
            result.y = self.y * inv_length
            result.z = self.z * inv_length
        return result
