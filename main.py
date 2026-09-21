import math

import pygame
from pygame.time import Clock

from cus_math import add_rotation, projection_v3_to_v2, set_rotation
from space_2d import Vec2
from space_3d import Cube, Vec3

pygame.init()

line_color = pygame.Color(255, 0, 0)
screen = pygame.display.set_mode([500, 500])

origin = Vec2(250, 250)
focus = 200
depth = 100

cube = Cube(Vec3(0, 0, 0), 50)
set_rotation(cube, Vec3(0, math.radians(90), 0))
angle = math.radians(1)
rotation_increment = Vec3(angle, 0, 0)

d_color = pygame.Color(0, 0, 0)
clocks = Clock()
running = True

while running:
    screen.fill(d_color)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    if not running:
        break

    add_rotation(cube, rotation_increment)

    for i, j in cube.line_marks:
        start_pos = projection_v3_to_v2(
            cube.cur_points[i], origin, cube.scale, focus, depth
        )
        end_pos = projection_v3_to_v2(
            cube.cur_points[j], origin, cube.scale, focus, depth
        )
        pygame.draw.line(screen, line_color, start_pos, end_pos, 1)

    pygame.display.flip()
    clocks.tick(60)

pygame.quit()
