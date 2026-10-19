from render.camera import Camera
from space_2d.vec2 import Vec2
from space_3d.vec3 import Vec3


def test_project_center():
    origin = Vec3(0, 0, 0)
    size = Vec2(200, 200)
    pos = Vec3(0, 0, 100)
    camera = Camera(origin, size, yaw=0, pitch=0, focus=200)
    view = camera.world_to_view(pos)
    (x, y, deepth) = camera.project(view)
    assert abs(x - size.x / 2) < 0.001 and abs(y - size.y / 2) < 0.001
