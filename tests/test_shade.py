from render.shade import shade_lambert
from space_3d.vec3 import Vec3


def test_shade_lambert():
    assert shade_lambert(
        (200, 100, 0), Vec3(0, 0, 1), Vec3(0, 0, 1), ambient=0.0
    ) == (200, 100, 0)

    assert shade_lambert(
        (100, 100, 100), Vec3(0, 0, 1), Vec3(0, 0, -1), ambient=0.2
    ) == (20, 20, 20)


test_shade_lambert()