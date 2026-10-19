from space_3d.vec3 import Vec3


def shade_lambert(base_rgb, normal: Vec3, light_dir: Vec3, ambient=0.15):

    # 把 normal 和 light_dir 都做归一化。
    n_normal = normal.normalized()
    n_light_dir = light_dir.normalized()
    # 计算 ndotl = max(0, n·l)，再算亮度系数 f = ambient + (1 - ambient) * ndotl。
    ndotl = max(0, n_normal.dot(n_light_dir))

    f = ambient + (1 - ambient) * ndotl
    # 把 base_rgb 的每个分量乘以 f，转成整数并钳到 0–255，返回 (r, g, b)。
    return (
        max(0, min(255, int(base_rgb[0] * f))),
        max(0, min(255, int(base_rgb[1] * f))),
        max(0, min(255, int(base_rgb[2] * f))),
    )
