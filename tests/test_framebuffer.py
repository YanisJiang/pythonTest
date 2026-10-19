from render.framebuffer import Framebuffer


def test_clear_and_set_pixel_depth():
    fb = Framebuffer(4, 2)
    fb.clear((10, 20, 30), 1.0)
    fb.set_pixel(1, 0, 0.5, (255, 0, 0))
    fb.set_pixel(1, 0, 0.8, (0, 255, 0))
    fb.set_pixel(1, 0, 0.2, (0, 0, 255))

    raw = fb.to_bgra_bytes()

    i = (0 * 4 + 1) * 4
    assert raw[i : i + 4] == bytes([255, 0, 0, 0])
