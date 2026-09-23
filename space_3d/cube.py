from math import cos, sin

from space_3d.matrix_3d import Matrix3
from space_3d.vec3 import Vec3


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
            [255, 255, 255],
            [255, 255, 0],
            [0, 255, 0],
            [0, 0, 255],
            [255, 0, 0],
            [255, 165, 0],
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

    def add_rotation(self, rotation: Vec3):
        self.rotation += rotation
        self.update_delta_matrix(rotation)

        self.cur_points = []
        self.rotate_matrix = (
            self.rotate_matrix
            * self.delta_x_matrix
            * self.delta_y_matrix
            * self.delta_z_matrix
        )
        for origin_point in self.origin_points:
            cur_point = self.rotate_matrix * origin_point
            self.cur_points.append(cur_point)

    def set_rotation(self, rotation: Vec3):
        delta_rotation = rotation - self.rotation
        self.add_rotation(delta_rotation)
