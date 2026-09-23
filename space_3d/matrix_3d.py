from space_3d.vec3 import Vec3


class Matrix3:
    v1: Vec3
    v2: Vec3
    v3: Vec3

    def __init__(self, v1: Vec3, v2: Vec3, v3: Vec3):
        self.v1 = v1
        self.v2 = v2
        self.v3 = v3

    def __mul__(self, other):
        if isinstance(other, Vec3):
            new_x = self.v1.x * other.x + self.v2.x * other.y + self.v3.x * other.z
            new_y = self.v1.y * other.x + self.v2.y * other.y + self.v3.y * other.z
            new_z = self.v1.z * other.x + self.v2.z * other.y + self.v3.z * other.z
            return Vec3(new_x, new_y, new_z)
        if isinstance(other, Matrix3):
            return Matrix3(self * other.v1, self * other.v2, self * other.v3)
        return NotImplemented
