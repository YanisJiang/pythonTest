from math import cos, sin

from pygame import Color


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

    def __truediv__(self, scale):
        return Vec3(self.x / scale, self.y / scale, self.z / scale)

    def dot(self, other):
        return self.x * other.x + self.y * other.y + self.z * other.z

    def cross(self, other):
        return Vec3(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x,
        )


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


class Cube:
    # 位置
    position: Vec3
    # 旋转
    rotation: Vec3
    # 缩放
    scale: Vec3

    # 顶点偏移
    __offsets: []
    # 棱边
    lines: []
    # 面
    faces: []
    faces_color: []
    origin_points: []
    cur_points: []

    # 旋转矩阵
    rotate_matrix: Matrix3
    delta_x_matrix: Matrix3
    delta_y_matrix: Matrix3
    delta_z_matrix: Matrix3

    def __init__(self, center: Vec3, length: float):
        self.position = center
        self.rotation = Vec3(0, 0, 0)
        self.scale = Vec3(1, 1, 1)

        self.__offsets = [
            Vec3(-1, 1, 1),
            Vec3(-1, 1, -1),
            Vec3(1, 1, 1),
            Vec3(1, 1, -1),
            Vec3(-1, -1, 1),
            Vec3(-1, -1, -1),
            Vec3(1, -1, 1),
            Vec3(1, -1, -1),
        ]

        self.lines = [
            (0, 1),
            (1, 3),
            (3, 2),
            (2, 0),
            (0, 4),
            (1, 5),
            (3, 7),
            (2, 6),
            (4, 5),
            (5, 7),
            (7, 6),
            (6, 4),
        ]

        self.faces = [
            [0, 1, 3, 2],
            [4, 6, 7, 5],
            [0, 4, 5, 1],
            [2, 3, 7, 6],
            [0, 2, 6, 4],
            [1, 5, 7, 3],
        ]

        self.faces_color = [
            Color(255, 255, 255),
            Color(255, 255, 0),
            Color(0, 255, 0),
            Color(0, 0, 255),
            Color(255, 0, 0),
            Color(255, 165, 0),
        ]

        self.rotate_matrix = Matrix3(Vec3(1, 0, 0), Vec3(0, 1, 0), Vec3(0, 0, 1))
        self.delta_x_matrix = Matrix3(Vec3(1, 0, 0), Vec3(0, 1, 0), Vec3(0, 0, 1))
        self.delta_y_matrix = Matrix3(Vec3(1, 0, 0), Vec3(0, 1, 0), Vec3(0, 0, 1))
        self.delta_z_matrix = Matrix3(Vec3(1, 0, 0), Vec3(0, 1, 0), Vec3(0, 0, 1))

        self.__init_points__(length / 2)

    def __init_points__(self, half_length: float):
        self.origin_points = []
        self.cur_points = []
        for offset in self.__offsets:
            new_x = self.position.x + half_length * offset.x
            new_y = self.position.y + half_length * offset.y
            new_z = self.position.z + half_length * offset.z
            self.origin_points.append(Vec3(new_x, new_y, new_z))
            self.cur_points.append(Vec3(new_x, new_y, new_z))

    def add_rotation(self, rotation: Vec3):
        self.rotation.x += rotation.x
        self.rotation.y += rotation.y
        self.rotation.z += rotation.z
        self.update_delta_matrix(rotation)

    def set_rotation(self, rotation: Vec3):
        delta_rotation = Vec3(
            rotation.x - self.rotation.x,
            rotation.y - self.rotation.y,
            rotation.z - self.rotation.z,
        )
        self.add_rotation(delta_rotation)

    def update_delta_matrix(self, rotation: Vec3):
        self.delta_x_matrix = Matrix3(
            Vec3(1, 0, 0),
            Vec3(0, cos(rotation.x), -sin(rotation.x)),
            Vec3(0, sin(rotation.x), cos(rotation.x)),
        )

        self.delta_y_matrix = Matrix3(
            Vec3(cos(rotation.y), 0, -sin(rotation.y)),
            Vec3(0, 1, 0),
            Vec3(sin(rotation.y), 0, cos(rotation.y)),
        )

        self.delta_z_matrix = Matrix3(
            Vec3(cos(rotation.z), -sin(rotation.z), 0),
            Vec3(sin(rotation.z), cos(rotation.z), 0),
            Vec3(0, 0, 1),
        )
