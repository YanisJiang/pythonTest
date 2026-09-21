import math


class Vec3:
    def __init__(self, x: float, y: float, z: float):
        self.x = x
        self.y = y
        self.z = z

    x: float
    y: float
    z: float


class Matrix3:
    def __init__(self, v1: Vec3, v2: Vec3, v3: Vec3):
        self.v1 = v1
        self.v2 = v2
        self.v3 = v3

    v1: Vec3
    v2: Vec3
    v3: Vec3


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
    line_marks: []
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

        self.line_marks = [
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
        self.rotation.x = rotation.x
        self.rotation.y = rotation.y
        self.rotation.z = rotation.z

    def update_delta_matrix(self, rotation: Vec3):
        self.delta_x_matrix = Matrix3(
            Vec3(1, 0, 0),
            Vec3(0, math.cos(rotation.x), -math.sin(rotation.x)),
            Vec3(0, math.sin(rotation.x), math.cos(rotation.x)),
        )

        self.delta_y_matrix = Matrix3(
            Vec3(math.cos(rotation.y), 0, -math.sin(rotation.y)),
            Vec3(0, 1, 0),
            Vec3(math.sin(rotation.y), 0, math.cos(rotation.y)),
        )

        self.delta_z_matrix = Matrix3(
            Vec3(math.cos(rotation.z), -math.sin(rotation.z), 0),
            Vec3(math.sin(rotation.z), math.cos(rotation.z), 0),
            Vec3(0, 0, 1),
        )
