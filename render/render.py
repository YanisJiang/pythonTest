from space_2d.vec2 import Vec2
from space_3d.cube import Cube
from space_3d.vec3 import Vec3


def _get_normal(cube: Cube, face: [int, int, int, int]) -> Vec3:
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


def _get_face_center(cube: Cube, face: [int, int, int, int]) -> Vec3:
    # faces 里存的是下标，要用 cur_points 取出旋转后的点
    point1 = cube.cur_points[face[0]]
    point2 = cube.cur_points[face[1]]
    point3 = cube.cur_points[face[2]]
    point4 = cube.cur_points[face[3]]

    mean_point = (point1 + point2 + point3 + point4) * (1 / 4)
    return mean_point


def _projection_v3_to_v2(
    v3: Vec3, origin: Vec2, scale: Vec3, focus: float, depth: float
) -> [float, float]:
    sx = origin.x + focus * v3.x * scale.x / (v3.z * scale.z + depth)
    sy = origin.y + focus * v3.y * scale.y / (v3.z * scale.z + depth)
    return [sx, sy]
