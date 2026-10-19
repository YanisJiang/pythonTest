from space_3d.vec3 import Vec3


def test_vec3_normalized():
    v3 = Vec3(0, 3, 0)
    assert v3.normalized() == Vec3(0, 1, 0)
