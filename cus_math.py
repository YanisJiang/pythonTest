class Vec3:
    def __init__(self, x: float, y: float, z: float):
        self.x = x
        self.y = y
        self.z = z

    x: float
    y: float
    z: float


class Vec2:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    x: float
    y: float


class Matrix3:
    def __init__(self, v1: Vec3, v2: Vec3, v3: Vec3):
        self.v1 = v1
        self.v2 = v2
        self.v3 = v3

    v1: Vec3
    v2: Vec3
    v3: Vec3


class Cube:
    def __init__(self, center: Vec3, length: float):
        self.__center = center
        self.__length = length
        self.__half_length = length / 2
        self.points = []
        self.lines = []
        self.__init_points__()
        self.__init_lines__()

    def __init_points__(self):
        for offset in self.__offsets:
            new_x = self.__center.x + self.__half_length * offset.x
            new_y = self.__center.y + self.__half_length * offset.y
            new_z = self.__center.z + self.__half_length * offset.z
            self.points.append(Vec3(new_x, new_y, new_z))

    def __init_lines__(self):
        for line in self.__lines_mark:
            self.lines.append([self.points[line[0]], self.points[line[1]]])

    __center: Vec3
    __length: float
    __half_lengthh: float
    __offsets = [
        Vec3(-1, 1, 1),
        Vec3(-1, 1, -1),
        Vec3(1, 1, 1),
        Vec3(1, 1, -1),
        Vec3(-1, -1, 1),
        Vec3(-1, -1, -1),
        Vec3(1, -1, 1),
        Vec3(1, -1, -1),
    ]

    __lines_mark = [
        [0, 1],
        [1, 3],
        [3, 2],
        [2, 0],
        [0, 4],
        [1, 5],
        [3, 7],
        [2, 6],
        [4, 5],
        [5, 7],
        [7, 6],
        [6, 4],
    ]

    points: []
    lines: []


def projection_v3_to_v2(
    v3: Vec3, origin: Vec2, focus: float, depth: float
) -> [float, float]:
    sx = origin.x + focus * v3.x / (v3.z + depth)
    sy = origin.y + focus * v3.y / (v3.z + depth)
    return [sx, sy]


def mul_matrix_to_v3(matrix3: Matrix3, v3: Vec3) -> Vec3:
    new_x = matrix3.v1.x * v3.x + matrix3.v2.x * v3.y + matrix3.v3.x * v3.z
    new_y = matrix3.v1.y * v3.x + matrix3.v2.y * v3.y + matrix3.v3.y * v3.z
    new_z = matrix3.v1.z * v3.x + matrix3.v2.z * v3.y + matrix3.v3.z * v3.z
    return Vec3(new_x, new_y, new_z)
