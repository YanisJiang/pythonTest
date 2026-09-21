import math
import pygame
import cus_math
from pygame.time import Clock

pygame.init()

line_color = pygame.Color(255, 0, 0)

screen = pygame.display.set_mode([500, 500])

running = True

origin = cus_math.Vec2(250, 250)

focus = 200
depth = 100

cube = cus_math.Cube(cus_math.Vec3(0, 0, 0), 50)

theta = 10

R_theta = cus_math.Matrix3(
    cus_math.Vec3(math.cos(theta), 0, math.sin(theta)),
    cus_math.Vec3(0, 1, 0),
    cus_math.Vec3(-math.sin(theta), 0, math.cos(theta)),
)

while running:
    theta += 0.05

    R_theta = cus_math.Matrix3(
        cus_math.Vec3(math.cos(theta), 0, math.sin(theta)),
        cus_math.Vec3(0, 1, 0),
        cus_math.Vec3(-math.sin(theta), 0, math.cos(theta)),
    )

    d_color = pygame.Color(0, 0, 0)
    screen.fill(d_color)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            running = False

    if not running:
        break

    for line in cube.lines:
        start_pos = cus_math.projection_v3_to_v2(
            cus_math.mul_matrix_to_v3(R_theta, line[0]), origin, focus, depth
        )
        end_pos = cus_math.projection_v3_to_v2(
            cus_math.mul_matrix_to_v3(R_theta, line[1]), origin, focus, depth
        )
        pygame.draw.aaline(screen, line_color, start_pos, end_pos)

    pygame.display.flip()

    Clock().tick(60)
