from render.camera import Camera
from render.color import Color
from render.framebuffer import Framebuffer
from render.raster import fill_triangle
from render.shade import shade_lambert
from space_3d.cube import Cube
from space_3d.vec3 import Vec3


def draw_cube(framebuffer: Framebuffer, cube: Cube, camera: Camera, light: Vec3):

    normals = []

    for index, [a, b, c, d] in enumerate[list[int]](cube.faces):
        normal = (cube.cur_points[b] - cube.cur_points[a]).cross(
            cube.cur_points[c] - cube.cur_points[a]
        )
        face_center = (cube.cur_points[a] + cube.cur_points[b] + cube.cur_points[c]) / 3
        if normal.dot(face_center - cube.position) < 0:
            normal = normal * -1
        if (camera.position - face_center).dot(normal) > 0:
            project_a = camera.project(camera.world_to_view(cube.cur_points[a]))
            project_b = camera.project(camera.world_to_view(cube.cur_points[b]))
            project_c = camera.project(camera.world_to_view(cube.cur_points[c]))
            project_d = camera.project(camera.world_to_view(cube.cur_points[d]))
            if (
                project_a is None
                or project_b is None
                or project_c is None
                or project_d is None
            ):
                continue
            view_a = Vec3(project_a[0], project_a[1], project_a[2])
            view_b = Vec3(project_b[0], project_b[1], project_b[2])
            view_c = Vec3(project_c[0], project_c[1], project_c[2])
            view_d = Vec3(project_d[0], project_d[1], project_d[2])
            color = shade_lambert(
                [
                    cube.faces_color[index][0],
                    cube.faces_color[index][1],
                    cube.faces_color[index][2],
                ],
                normal,
                light,
            )
            fill_triangle(
                framebuffer,
                view_a,
                view_b,
                view_c,
                Color(color[0],color[1],color[2]),
            )
            fill_triangle(
                framebuffer,
                view_a,
                view_c,
                view_d,
                Color(color[0],color[1],color[2]),
            )
            normals.append(normal)
