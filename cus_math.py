from space_2d import Vec2
from space_3d import Cube, Matrix3, Vec3


def projection_v3_to_v2(
    v3: Vec3, origin: Vec2, scale: Vec3, focus: float, depth: float
) -> [float, float]:
    sx = origin.x + focus * v3.x * scale.x / (v3.z * scale.z + depth)
    sy = origin.y + focus * v3.y * scale.y / (v3.z * scale.z + depth)
    return [sx, sy]


def mul_matrix3_to_v3(matrix3: Matrix3, v3: Vec3) -> Vec3:
    new_x = matrix3.v1.x * v3.x + matrix3.v2.x * v3.y + matrix3.v3.x * v3.z
    new_y = matrix3.v1.y * v3.x + matrix3.v2.y * v3.y + matrix3.v3.y * v3.z
    new_z = matrix3.v1.z * v3.x + matrix3.v2.z * v3.y + matrix3.v3.z * v3.z
    return Vec3(new_x, new_y, new_z)


def mul_matrix3_to_matrix3(matrix3_0: Matrix3, matrix3_1: Matrix3) -> Matrix3:
    return Matrix3(
        mul_matrix3_to_v3(matrix3_0, matrix3_1.v1),
        mul_matrix3_to_v3(matrix3_0, matrix3_1.v2),
        mul_matrix3_to_v3(matrix3_0, matrix3_1.v3),
    )


def add_rotation(cube: Cube, rotation: Vec3):
    cube.add_rotation(rotation)

    cube.cur_points = []
    cube.rotate_matrix = mul_matrix3_to_matrix3(cube.rotate_matrix, cube.delta_x_matrix)
    cube.rotate_matrix = mul_matrix3_to_matrix3(cube.rotate_matrix, cube.delta_y_matrix)
    cube.rotate_matrix = mul_matrix3_to_matrix3(cube.rotate_matrix, cube.delta_z_matrix)
    for origin_point in cube.origin_points:
        cur_point = mul_matrix3_to_v3(cube.rotate_matrix, origin_point)
        cube.cur_points.append(cur_point)


def set_rotation(cube: Cube, rotation: Vec3):
    delta_rotation = Vec3(
        rotation.x - cube.rotation.x,
        rotation.y - cube.rotation.y,
        rotation.z - cube.rotation.z,
    )

    add_rotation(cube, delta_rotation)
