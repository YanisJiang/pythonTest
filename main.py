import math

import pygame
from pygame.time import Clock

from cus_math import (
    add_rotation,
    get_face_center,
    get_normal,
    projection_v3_to_v2,
    set_rotation,
)
from space_2d import Vec2
from space_3d import Cube, Vec3

pygame.init()

line_color = pygame.Color(255, 0, 0)
screen = pygame.display.set_mode([500, 500])

origin = Vec2(250, 250)
focus = 200
depth = 100
camer = Vec3(0, 0, depth)

cube = Cube(Vec3(0, 0, 0), 50)
set_rotation(cube, Vec3(0, 0, 0))
angle = math.radians(1)
rotation_increment = Vec3(math.radians(1), math.radians(1), math.radians(1))

d_color = pygame.Color(0, 0, 0)
clocks = Clock()
running = True


def face_depth(item):
    face, _color = item
    return sum(cube.cur_points[i].z for i in face) / len(face)


while running:
    screen.fill(d_color)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    if not running:
        break

    add_rotation(cube, rotation_increment)

    faces = list(zip(cube.faces, cube.faces_color))
    faces = sorted(faces, key=face_depth, reverse=True)

    for face, color in faces:
        if get_normal(cube, face).dot(camer - get_face_center(cube, face)) > 0:
            continue
        else:
            points = []
            for i in face:
                points.append(
                    projection_v3_to_v2(
                        cube.cur_points[i], origin, cube.scale, focus, depth
                    )
                )
            pygame.draw.polygon(screen, color, points)

    pygame.display.flip()
    clocks.tick(60)


pygame.quit()
