# 新建 tests/test_pipeline_smoke.py。
# 建一个 200×200 的帧缓冲并 clear。
# 立方体中心在原点，边长 40，转一个不是 0 的角度。
# 相机放在 (0, 0, -120)，yaw 和 pitch 都是 0，focus 是 200，画布也是 200×200。
# 你的相机把角度当成度数，这里就传度数。
# 再准备一个方向光，比如 (0.4, 0.7, 0.2)。
# 调用 draw_cube 之后，断言帧缓冲的字节里至少有一个不是 0。

from render.camera import Camera
from render.framebuffer import Framebuffer
from render.pipeline import draw_cube
from space_2d.vec2 import Vec2
from space_3d.cube import Cube
from space_3d.vec3 import Vec3


def test_draw_cube():
    framebuffer = Framebuffer(200, 200)
    cube = Cube(Vec3(0, 0, 0), 40)
    cube.set_rotation(Vec3(70, 60, 50))
    camera = Camera(Vec3(0, 0, -120), Vec2(200, 200), 0, 0, 200)
    light = Vec3(0.4, 0.7, 0.2)
    draw_cube(framebuffer, cube, camera, light)
    assert any(b != 0 for b in framebuffer.to_bgra_bytes())
