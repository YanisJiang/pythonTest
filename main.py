from math import radians

import pygame
from pygame.time import Clock

from render.color import Color
from render.render import Render
from space_2d.vec2 import Vec2
from space_3d.cube import Cube
from space_3d.vec3 import Vec3

pygame.init()

line_color = Color(255, 0, 0, 255)
screen = pygame.display.set_mode([500, 500])

origin = Vec2(250, 250)
focus = 200
depth = 100
camera = Vec3(0, 0, depth)

cube = Cube(Vec3(0, 0, 0), 50)
cube.set_rotation(Vec3(0, 0, 0))

cube_render = Render(cube, screen)

angle = radians(1)
rotation_increment = Vec3(radians(1), radians(1), radians(1))

d_color = Color(0, 0, 0)
clocks = Clock()
running = True


while running:
    screen.fill(d_color.to_list())

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    if not running:
        break

    cube.add_rotation(rotation_increment)

    cube_render.render(camera, origin, focus)

    pygame.display.flip()
    clocks.tick(60)


pygame.quit()
