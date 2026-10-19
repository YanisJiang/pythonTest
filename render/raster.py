import numpy as np

from render.color import Color
from render.framebuffer import Framebuffer
from space_3d.vec3 import Vec3


def fill_triangle(framebuffer: Framebuffer, p1: Vec3, p2: Vec3, p3: Vec3, color: Color):
    min_x = max(0, min(framebuffer.width - 1, min(p1.x, p2.x, p3.x)))
    max_x = max(0, min(framebuffer.width - 1, max(p1.x, p2.x, p3.x)))
    min_y = max(0, min(framebuffer.height - 1, min(p1.y, p2.y, p3.y)))
    max_y = max(0, min(framebuffer.height - 1, max(p1.y, p2.y, p3.y)))

    area = (p2.x - p1.x) * (p3.y - p1.y) - (p2.y - p1.y) * (p3.x - p1.x)

    if area == 0:
        return

    width = framebuffer.width
    height = framebuffer.height

    color_buf = np.frombuffer(framebuffer.color, dtype=np.uint8).reshape(
        height, width, 4
    )
    depth_buf = np.frombuffer(framebuffer.depth, dtype=np.float32).reshape(
        height, width
    )
    x0 = int(min_x)
    x1 = int(max_x)
    y0 = int(min_y)
    y1 = int(max_y)
    ys = np.arange(y0, y1 + 1, dtype=np.float32)[:, None]
    xs = np.arange(x0, x1 + 1, dtype=np.float32)[None, :]
    a = (p2.x - p1.x) * (ys - p1.y) - (p2.y - p1.y) * (xs - p1.x)
    b = (p3.x - p2.x) * (ys - p2.y) - (p3.y - p2.y) * (xs - p2.x)
    c = (p1.x - p3.x) * (ys - p3.y) - (p1.y - p3.y) * (xs - p3.x)
    inside = ((a >= 0) & (b >= 0) & (c >= 0)) | ((a <= 0) & (b <= 0) & (c <= 0))
    z = (a * p3.z + b * p1.z + c * p2.z) / area
    depth_view = depth_buf[y0 : y1 + 1, x0 : x1 + 1]
    color_view = color_buf[y0 : y1 + 1, x0 : x1 + 1]
    mask = inside & (z < depth_view)
    depth_view[mask] = z[mask]
    color_view[mask] = (color.b, color.g, color.r, 0)
