from math import cos, radians, sin

from space_2d.vec2 import Vec2
from space_3d.vec3 import Vec3


class Camera:
    position: Vec3
    size: Vec2
    yaw: float
    pitch: float
    focus: float

    def __init__(
        self, position: Vec3, size: Vec2, yaw: float, pitch: float, focus: float
    ) -> None:
        self.position = position
        self.size = size
        self.yaw = yaw
        self.pitch = pitch
        self.focus = focus

    def world_to_view(self, world: Vec3) -> Vec3:
        delta = world - self.position
        (forward, up, right) = self.get_dir()
        return Vec3(delta.dot(right), delta.dot(up), delta.dot(forward))

    def get_dir(self) -> tuple[Vec3, Vec3, Vec3]:
        r_yaw = radians(self.yaw)
        r_pitch = radians(self.pitch)
        forward = Vec3(
            cos(r_pitch) * sin(r_yaw), -sin(r_pitch), cos(r_yaw) * cos(r_pitch)
        )
        up = Vec3(sin(r_yaw) * sin(r_pitch), cos(r_pitch), cos(r_yaw) * sin(r_pitch))
        right = Vec3(cos(r_yaw), 0, -sin(r_yaw))
        return (forward, up, right)

    def project(self, view: Vec3):
        if view.z < 0.001:
            return None
        return (
            self.size.x / 2 + self.focus * view.x / view.z,
            self.size.y / 2 - self.focus * view.y / view.z,
            view.z,
        )

    def move_local(self, forward, right, up):
        (self_forward, self_up, self_right) = self.get_dir()
        self.position += self_forward * forward + self_up * up + self_right * right
