import time

from host.win32.input import InputState
from host.win32.window import Window
from render import framebuffer
from render.camera import Camera
from render.pipeline import draw_cube
from space_2d.vec2 import Vec2
from space_3d.cube import Cube
from space_3d.vec3 import Vec3

input_state = InputState()

window_size = Vec2(800, 800)
rander_size = Vec2(400, 400)

window = Window("title", window_size.x, window_size.y, input_state)

framebuffer = framebuffer.Framebuffer(rander_size.x, rander_size.y)

cube = Cube(Vec3(0, 0, 0), 40)
camera = Camera(Vec3(0, 0, -250), rander_size, 0, 0, 200)
light = Vec3(0.5, 0.8, 0.2)

speed = 100

rotation_delta = Vec3(40, 40, 40)

previous = time.perf_counter()
while not window.should_close():
    now = time.perf_counter()
    dt = now - previous
    previous = time.perf_counter()

    window.pump()
    sensitivity = 0.2
    if input_state.mouse_left:
        camera.yaw += input_state.mouse_delta.x * sensitivity
        camera.pitch = max(
            min(camera.pitch + input_state.mouse_delta.y * sensitivity, 89), -89
        )
    if 87 in input_state.cur_key:
        camera.move_local(speed * dt, 0, 0)
    if 83 in input_state.cur_key:
        camera.move_local(-speed * dt, 0, 0)
    if 68 in input_state.cur_key:
        camera.move_local(0, speed * dt, 0)
    if 65 in input_state.cur_key:
        camera.move_local(0, -speed * dt, 0)
    if 32 in input_state.cur_key:
        camera.move_local(0, 0, speed * dt)
    if 17 in input_state.cur_key:
        camera.move_local(0, 0, -speed * dt)
    cube.add_rotation(rotation_delta * dt)
    framebuffer.clear()
    draw_cube(framebuffer, cube, camera, light)
    window.present(framebuffer.to_bgra_bytes(), framebuffer.width, framebuffer.height)
    input_state.end_frame()
    remain = 1 / 60 - (time.perf_counter() - now)
    if remain > 0:
        time.sleep(remain)
