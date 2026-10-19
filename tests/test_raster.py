# 新建 tests/test_raster.py。建一个 20×20 的 Framebuffer，
# 先 clear。用三个点画一个盖住中心的三角形，三个点的深度都用 0.5，
# 颜色用 (255, 0, 0)。然后取出像素 (10, 10) 的颜色，断言红色通道是 255。
# Framebuffer 的 to_bgra_bytes 里，每个像素是 B,G,R,0，红色在第三个字节。


from render.color import Color
from render.raster import fill_triangle
from render.framebuffer import Framebuffer
from space_3d.vec3 import Vec3


def test_fill_triangle():
    framebuffer = Framebuffer(20, 20)
    framebuffer.clear()
    fill_triangle(
        framebuffer,
        Vec3(5, 7, 0.5),
        Vec3(15, 7, 0.5),
        Vec3(10, 15, 0.5),
        Color(255, 0, 0),
    )
    assert framebuffer.get_color(10, 10)[2] == 255
    