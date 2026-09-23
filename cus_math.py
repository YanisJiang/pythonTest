from space_2d import Vec2
from space_3d import Cube, Vec3


def projection_v3_to_v2(
    v3: Vec3, origin: Vec2, scale: Vec3, focus: float, depth: float
) -> [float, float]:
    sx = origin.x + focus * v3.x * scale.x / (v3.z * scale.z + depth)
    sy = origin.y + focus * v3.y * scale.y / (v3.z * scale.z + depth)
    return [sx, sy]


def add_rotation(cube: Cube, rotation: Vec3):
    cube.add_rotation(rotation)

    cube.cur_points = []
    cube.rotate_matrix = (
        cube.rotate_matrix
        * cube.delta_x_matrix
        * cube.delta_y_matrix
        * cube.delta_z_matrix
    )
    for origin_point in cube.origin_points:
        cur_point = cube.rotate_matrix * origin_point
        cube.cur_points.append(cur_point)


def set_rotation(cube: Cube, rotation: Vec3):
    delta_rotation = rotation - cube.rotation
    add_rotation(cube, delta_rotation)


def get_normal(cube: Cube, face: [int, int, int, int]) -> Vec3:
    # faces 里存的是下标，要用 cur_points 取出旋转后的点
    point1 = cube.cur_points[face[0]]
    point2 = cube.cur_points[face[1]]
    point3 = cube.cur_points[face[2]]

    normal = (point2 - point1).cross(point3 - point1)
    mean_point = (point1 + point2 + point3) * (1 / 3)

    # 法线应背离立方体中心（朝外）
    if (mean_point - cube.position).dot(normal) < 0:
        normal = normal * -1

    return normal
