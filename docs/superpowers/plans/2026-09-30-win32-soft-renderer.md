# Win32 Soft Renderer Implementation Plan

> **For agentic workers:** 本仓库约定 AI **不直接改** `.py`；由用户按任务逐步改代码，AI 引导与指正。若日后协作边界变更，可用 `superpowers:executing-plans` 逐任务执行。Steps 用 checkbox（`- [ ]`）跟踪。

**Goal:** 去掉 pygame，用 ctypes Win32 窗口 + 自研软光栅（三角形 + Z-Buffer + 扁平 Lambert）显示可自转的彩色立方体，并支持键鼠控制相机。

**Architecture:** 保留 `space_2d`/`space_3d`；新建 `render/` 管线与 `platform/win32/`；`main.py` 只做组装与循环。依赖单向：`main → platform → render → space_*`。

**Tech Stack:** Python 3、ctypes（user32/gdi32）、stdlib `array`/`math`/`time`；无 pygame。

## Global Constraints

- 仅 Windows；不做跨平台抽象
- 工程内最终无 `import pygame`
- 光栅优先重心坐标 + Z-Buffer；扁平 Lambert + 少量环境光；固定方向光
- 第一版不做：完整 clip、纹理、Gouraud/Phong、多光源、阴影
- 客户区与帧缓冲 1:1（推荐 800×600）
- 业务代码由用户修改；本 plan 文档由 AI 维护

## 拆分总览（顺序依赖）

| 块 | 内容 | 依赖 | 可独立验收 |
|---|---|---|---|
| A | `Framebuffer` + `Vec3.normalized` | 无 | 单测 |
| B | `Camera` + `shade` | A | 单测 |
| C | `raster` + `pipeline` | A+B、现有 Cube | 写 BMP/断言像素或离屏测 |
| D | Win32 `Window` present | A | 纯色窗口 |
| E | Win32 `Input` + `main` 接线、删 pygame、README | C+D | `python main.py` 全验收 |

---

## File Structure

| Path | Responsibility |
|---|---|
| `render/framebuffer.py` | RGB byte 缓冲 + float Z-Buffer；`clear` / `set_pixel` / `bytes` |
| `render/camera.py` | 位置、yaw/pitch；世界→相机；透视到屏幕 |
| `render/shade.py` | Lambert 扁平：`shade_face(base_rgb, normal, light_dir) -> (r,g,b)` |
| `render/raster.py` | 三角形重心填充 + depth test |
| `render/pipeline.py` | `draw(fb, cube, camera, light_dir)` 串起管线 |
| `render/color.py` | 可保留；管线内部可用 `(r,g,b)` int 0–255 |
| `platform/win32/window.py` | 窗口、消息泵、`present(rgb_bytes)` |
| `platform/win32/input.py` | 键鼠状态（由 window 过程更新） |
| `platform/win32/__init__.py` | 导出 |
| `space_3d/vec3.py` | 增加 `length` / `normalized` |
| `main.py` | 主循环 |
| `tests/test_framebuffer.py` 等 | 单测 |
| `README.md` | 运行说明 |
| 删除/停用 | `render/render.py` 旧画家路径（Task 末尾删除） |

---

### Task 1: Framebuffer + Vec3.normalized

**Files:**
- Create: `render/framebuffer.py`
- Create: `tests/test_framebuffer.py`
- Modify: `space_3d/vec3.py`（末尾加方法）
- Create: `tests/test_vec3_normalize.py`

**Interfaces:**
- Consumes: 无
- Produces:
  - `Framebuffer(width: int, height: int)`
  - `Framebuffer.clear(rgb: tuple[int,int,int] = (0,0,0), depth: float = 1.0) -> None`
  - `Framebuffer.set_pixel(x: int, y: int, z: float, rgb: tuple[int,int,int]) -> None`（越界忽略；`z < zbuf` 才写入；约定相机空间越近 z 越小，清屏 depth=1.0，有效深度写入 0..1 映射或直接用相机 z 并统一比较方向——**本 plan 约定：存相机空间 z，越近越小，`set_pixel` 当 `z < zbuf[i]` 时更新**）
  - `Framebuffer.to_bgra_bytes() -> bytes`（Win32 顶向下 DIB 常用 BGR0；高度行序：第 0 行是屏幕顶部）
  - `Vec3.length() -> float`
  - `Vec3.normalized() -> Vec3`

- [ ] **Step 1: 写失败单测 `tests/test_framebuffer.py`**

```python
from render.framebuffer import Framebuffer


def test_clear_and_set_pixel_depth():
    fb = Framebuffer(4, 2)
    fb.clear((10, 20, 30), depth=1.0)
    fb.set_pixel(1, 0, 0.5, (255, 0, 0))
    fb.set_pixel(1, 0, 0.8, (0, 255, 0))  # farther, ignored
    fb.set_pixel(1, 0, 0.2, (0, 0, 255))  # nearer, wins
    raw = fb.to_bgra_bytes()
    # pixel (1,0): B,G,R,0
    i = (0 * 4 + 1) * 4
    assert raw[i : i + 4] == bytes([255, 0, 0, 0])
```

- [ ] **Step 2: 运行确认失败**

```bash
python -m pytest tests/test_framebuffer.py -v
```

Expected: FAIL（模块不存在或 import 失败）

- [ ] **Step 3: 实现 `render/framebuffer.py`**

```python
import array


class Framebuffer:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.color = array.array("B", [0] * (width * height * 4))  # BGRA
        self.zbuf = array.array("f", [1.0] * (width * height))

    def clear(self, rgb=(0, 0, 0), depth: float = 1.0) -> None:
        r, g, b = rgb
        for i in range(self.width * self.height):
            o = i * 4
            self.color[o] = b
            self.color[o + 1] = g
            self.color[o + 2] = r
            self.color[o + 3] = 0
            self.zbuf[i] = depth

    def set_pixel(self, x: int, y: int, z: float, rgb: tuple) -> None:
        if x < 0 or y < 0 or x >= self.width or y >= self.height:
            return
        i = y * self.width + x
        if z >= self.zbuf[i]:
            return
        self.zbuf[i] = z
        o = i * 4
        r, g, b = rgb
        self.color[o] = int(b)
        self.color[o + 1] = int(g)
        self.color[o + 2] = int(r)
        self.color[o + 3] = 0

    def to_bgra_bytes(self) -> bytes:
        return self.color.tobytes()
```

- [ ] **Step 4: 测通过**

```bash
python -m pytest tests/test_framebuffer.py -v
```

Expected: PASS

- [ ] **Step 5: Vec3 单测 + 实现**

`tests/test_vec3_normalize.py`:

```python
from space_3d.vec3 import Vec3


def test_normalized():
    v = Vec3(0, 3, 0).normalized()
    assert abs(v.x) < 1e-6 and abs(v.y - 1.0) < 1e-6 and abs(v.z) < 1e-6
```

在 `space_3d/vec3.py` 的 `Vec3` 内增加：

```python
def length(self) -> float:
    return (self.x * self.x + self.y * self.y + self.z * self.z) ** 0.5

def normalized(self) -> "Vec3":
    L = self.length()
    if L == 0:
        return Vec3(0, 0, 0)
    return self * (1.0 / L)
```

- [ ] **Step 6: Commit**

```bash
git add render/framebuffer.py space_3d/vec3.py tests/test_framebuffer.py tests/test_vec3_normalize.py
git commit -m "feat: add framebuffer and Vec3.normalized"
```

---

### Task 2: Camera + Lambert shade

**Files:**
- Create: `render/camera.py`
- Create: `render/shade.py`
- Create: `tests/test_camera.py`
- Create: `tests/test_shade.py`

**Interfaces:**
- Consumes: `Vec3`（`+ - * dot cross normalized`）
- Produces:
  - `Camera(position: Vec3, yaw: float, pitch: float, focus: float, width: int, height: int)`
  - `Camera.world_to_view(p: Vec3) -> Vec3`
  - `Camera.project(view_p: Vec3) -> tuple[float,float,float] | None`  
    返回 `(sx, sy, z_view)`；若 `view_p.z <= 1e-4` 返回 `None`（在相机后方/过近）
  - `Camera.add_yaw_pitch(dyaw: float, dpitch: float) -> None`（pitch 钳制到 ±π/2*0.99）
  - `Camera.move_local(forward: float, right: float, up: float) -> None`
  - `shade_lambert(base_rgb: tuple[int,int,int], normal: Vec3, light_dir: Vec3, ambient: float = 0.15) -> tuple[int,int,int]`  
    `light_dir` 为**指向光源**的单位向量（或入射光反方向，文档写死：指向光源）；`ndotl = max(0, normal.normalized().dot(light_dir.normalized()))`；`c = ambient + (1-ambient)*ndotl`

- [ ] **Step 1: 写 `tests/test_shade.py`**

```python
from render.shade import shade_lambert
from space_3d.vec3 import Vec3


def test_full_facing():
    c = shade_lambert((200, 100, 0), Vec3(0, 0, 1), Vec3(0, 0, 1), ambient=0.0)
    assert c == (200, 100, 0)


def test_back_facing_ambient_only():
    c = shade_lambert((100, 100, 100), Vec3(0, 0, 1), Vec3(0, 0, -1), ambient=0.2)
    assert c == (20, 20, 20)
```

- [ ] **Step 2: 实现 `render/shade.py` 并测过**

```python
from space_3d.vec3 import Vec3


def shade_lambert(base_rgb, normal: Vec3, light_dir: Vec3, ambient: float = 0.15):
    n = normal.normalized()
    l = light_dir.normalized()
    ndotl = max(0.0, n.dot(l))
    f = ambient + (1.0 - ambient) * ndotl
    r, g, b = base_rgb
    return (min(255, int(r * f)), min(255, int(g * f)), min(255, int(b * f)))
```

- [ ] **Step 3: 写 `tests/test_camera.py`**

```python
from math import radians
from render.camera import Camera
from space_3d.vec3 import Vec3


def test_project_center():
    cam = Camera(Vec3(0, 0, 0), yaw=0.0, pitch=0.0, focus=200.0, width=200, height=200)
    # 约定：相机看向 -Z 或 +Z？本实现：yaw/pitch=0 时看向 +Z 前方，点 (0,0,100) 投影到中心附近
    sx, sy, z = cam.project(cam.world_to_view(Vec3(0, 0, 100)))
    assert abs(sx - 100) < 1e-3 and abs(sy - 100) < 1e-3
```

- [ ] **Step 4: 实现 `render/camera.py`**

约定（写进文件头注释）：
- yaw=0,pitch=0：相机朝 **+Z**，世界 +Y 向上，+X 向右
- `world_to_view`：先平移到相机原点，再按 yaw（绕 Y）、pitch（绕 X）旋转，使「前方」落到 +Z

```python
from math import cos, sin, pi
from space_3d.vec3 import Vec3


class Camera:
    def __init__(self, position: Vec3, yaw: float, pitch: float, focus: float, width: int, height: int):
        self.position = position
        self.yaw = yaw
        self.pitch = pitch
        self.focus = focus
        self.width = width
        self.height = height

    def _forward_right_up(self):
        cy, sy = cos(self.yaw), sin(self.yaw)
        cp, sp = cos(self.pitch), sin(self.pitch)
        forward = Vec3(sy * cp, -sp, cy * cp).normalized()
        world_up = Vec3(0, 1, 0)
        right = forward.cross(world_up)
        if right.length() < 1e-6:
            right = Vec3(1, 0, 0)
        else:
            right = right.normalized()
        up = right.cross(forward).normalized()
        return forward, right, up

    def world_to_view(self, p: Vec3) -> Vec3:
        forward, right, up = self._forward_right_up()
        d = p - self.position
        return Vec3(d.dot(right), d.dot(up), d.dot(forward))

    def project(self, view_p: Vec3):
        if view_p.z <= 1e-4:
            return None
        sx = self.width * 0.5 + self.focus * view_p.x / view_p.z
        sy = self.height * 0.5 - self.focus * view_p.y / view_p.z  # Y 向上 → 屏幕向下为正需翻转
        return (sx, sy, view_p.z)

    def add_yaw_pitch(self, dyaw: float, dpitch: float) -> None:
        self.yaw += dyaw
        limit = pi * 0.5 * 0.99
        self.pitch = max(-limit, min(limit, self.pitch + dpitch))

    def move_local(self, forward_m: float, right_m: float, up_m: float) -> None:
        forward, right, up = self._forward_right_up()
        self.position = self.position + forward * forward_m + right * right_m + up * up_m
```

若 Step 3 单测因约定差符号失败：以单测为准微调 `forward` 公式或测试点，保持「中心点投影在画布中心」不变。

- [ ] **Step 5: Commit**

```bash
git add render/camera.py render/shade.py tests/test_camera.py tests/test_shade.py
git commit -m "feat: add camera and lambert shading"
```

---

### Task 3: Raster + Pipeline

**Files:**
- Create: `render/raster.py`
- Create: `render/pipeline.py`
- Create: `tests/test_raster.py`
- Create: `tests/test_pipeline_smoke.py`
- Delete（本任务末或 Task 5）：`render/render.py`（旧 pygame 画家算法）

**Interfaces:**
- Consumes: `Framebuffer.set_pixel`；`Camera.world_to_view`/`project`；`shade_lambert`；`Cube`（`cur_points`/`faces`/`faces_color`/`position`）
- Produces:
  - `fill_triangle(fb, p0, p1, p2, rgb)`  
    `p* = (x: float, y: float, z: float)` 屏幕 x/y + 用于 depth 的 z
  - `draw_cube(fb: Framebuffer, cube: Cube, camera: Camera, light_dir: Vec3) -> None`

- [ ] **Step 1: `tests/test_raster.py`**

```python
from render.framebuffer import Framebuffer
from render.raster import fill_triangle


def test_triangle_covers_center():
    fb = Framebuffer(20, 20)
    fb.clear((0, 0, 0), 1.0)
    fill_triangle(fb, (2, 2, 0.5), (17, 2, 0.5), (10, 17, 0.5), (255, 0, 0))
    # center-ish pixel should be red-ish
    i = (10 * 20 + 10) * 4
    raw = fb.to_bgra_bytes()
    assert raw[i + 2] == 255  # R in BGRA
```

- [ ] **Step 2: 实现 `render/raster.py`（重心坐标）**

```python
def _edge(ax, ay, bx, by, px, py):
    return (px - ax) * (by - ay) - (py - ay) * (bx - ax)


def fill_triangle(fb, p0, p1, p2, rgb):
    (x0, y0, z0), (x1, y1, z1), (x2, y2, z2) = p0, p1, p2
    area = _edge(x0, y0, x1, y1, x2, y2)
    if abs(area) < 1e-6:
        return
    min_x = max(0, int(min(x0, x1, x2)))
    max_x = min(fb.width - 1, int(max(x0, x1, x2)))
    min_y = max(0, int(min(y0, y1, y2)))
    max_y = min(fb.height - 1, int(max(y0, y1, y2)))
    for y in range(min_y, max_y + 1):
        for x in range(min_x, max_x + 1):
            w0 = _edge(x1, y1, x2, y2, x, y)
            w1 = _edge(x2, y2, x0, y0, x, y)
            w2 = _edge(x0, y0, x1, y1, x, y)
            if area < 0:
                w0, w1, w2, area_s = -w0, -w1, -w2, -area
            else:
                area_s = area
            if w0 < 0 or w1 < 0 or w2 < 0:
                continue
            a, b, c = w0 / area_s, w1 / area_s, w2 / area_s
            z = a * z0 + b * z1 + c * z2
            fb.set_pixel(x, y, z, rgb)
```

单测通过为准；若绕序导致全空，交换三角形两顶点。

- [ ] **Step 3: 实现 `render/pipeline.py`**

```python
from render.framebuffer import Framebuffer
from render.camera import Camera
from render.raster import fill_triangle
from render.shade import shade_lambert
from space_3d.cube import Cube
from space_3d.vec3 import Vec3


def _face_normal(cube: Cube, face):
    p1 = cube.cur_points[face[0]]
    p2 = cube.cur_points[face[1]]
    p3 = cube.cur_points[face[2]]
    n = (p2 - p1).cross(p3 - p1)
    mean = (p1 + p2 + p3) * (1 / 3)
    if (mean - cube.position).dot(n) < 0:
        n = n * -1
    return n


def _face_center(cube: Cube, face):
    pts = [cube.cur_points[i] for i in face]
    s = pts[0]
    for p in pts[1:]:
        s = s + p
    return s * (1 / len(pts))


def draw_cube(fb: Framebuffer, cube: Cube, camera: Camera, light_dir: Vec3) -> None:
    for face, base in zip(cube.faces, cube.faces_color):
        n = _face_normal(cube, face)
        center = _face_center(cube, face)
        # 背面剔除：法线与 (center -> camera.position) 
        if n.dot(camera.position - center) <= 0:
            continue
        rgb = shade_lambert(tuple(base[:3]), n, light_dir)
        # 四边形 → 两三角形 (0,1,2) (0,2,3)
        idxs = [face[0], face[1], face[2], face[0], face[2], face[3]]
        tri = []
        ok = True
        screen = []
        for i in face:
            vp = camera.world_to_view(cube.cur_points[i])
            pr = camera.project(vp)
            if pr is None:
                ok = False
                break
            screen.append(pr)
        if not ok:
            continue
        fill_triangle(fb, screen[0], screen[1], screen[2], rgb)
        fill_triangle(fb, screen[0], screen[2], screen[3], rgb)
```

- [ ] **Step 4: 烟雾测 `tests/test_pipeline_smoke.py`**

```python
from math import radians
from render.framebuffer import Framebuffer
from render.camera import Camera
from render.pipeline import draw_cube
from space_3d.cube import Cube
from space_3d.vec3 import Vec3


def test_draw_writes_nonzero_pixels():
    fb = Framebuffer(200, 200)
    fb.clear((0, 0, 0), 1.0)
    cube = Cube(Vec3(0, 0, 0), 40)
    cube.set_rotation(Vec3(radians(20), radians(30), 0))
    cam = Camera(Vec3(0, 0, -120), yaw=0.0, pitch=0.0, focus=200.0, width=200, height=200)
    # 若相机朝 +Z、立方体在原点，相机应在 z 负方向看向原点：position (0,0,-120)，forward 应指向 +Z
    draw_cube(fb, cube, cam, Vec3(0.4, 0.7, 0.2))
    assert any(b != 0 for b in fb.to_bgra_bytes())
```

若烟雾测失败：先打印是否背面全剔、投影是否全 None，调整相机位置/朝向约定，使立方体进入视野。

- [ ] **Step 5: Commit**

```bash
git add render/raster.py render/pipeline.py tests/test_raster.py tests/test_pipeline_smoke.py
git commit -m "feat: add triangle rasterizer and cube pipeline"
```

---

### Task 4: Win32 Window + present

**Files:**
- Create: `platform/__init__.py`（可空）
- Create: `platform/win32/__init__.py`
- Create: `platform/win32/window.py`
- Create: `platform/win32/input.py`（本任务可先放空壳，Task 5 填全）

**Interfaces:**
- Consumes: `Framebuffer.to_bgra_bytes()`、`width`/`height`
- Produces:
  - `class InputState:` 字段 `keys: set`、`mouse_down: bool`、`mouse_dx: float`、`mouse_dy: float`；方法 `end_frame()` 清 dx/dy
  - `class Window:`
    - `__init__(self, title: str, width: int, height: int, input_state: InputState)`
    - `pump(self) -> None`
    - `should_close(self) -> bool`
    - `present(self, bgra: bytes) -> None`
    - `destroy(self) -> None`

- [ ] **Step 1: 实现最小 `platform/win32/input.py`**

```python
class InputState:
    def __init__(self):
        self.keys = set()
        self.mouse_down = False
        self.mouse_dx = 0.0
        self.mouse_dy = 0.0

    def end_frame(self):
        self.mouse_dx = 0.0
        self.mouse_dy = 0.0
```

- [ ] **Step 2: 实现 `platform/win32/window.py`**

要点（完整 ctypes 骨架须可运行；下列为结构清单，实现时按此写全）：

1. `ctypes.WinDLL("user32")` / `gdi32`
2. `WNDCLASSW`、`RegisterClassW`、`CreateWindowExW`、客户区 `AdjustWindowRect`
3. `WndProc`：处理 `WM_DESTROY`→`PostQuitMessage`；`WM_PAINT` 可空画；键鼠消息写入 `InputState`（`WM_KEYDOWN/UP`、`WM_LBUTTONDOWN/UP`、`WM_MOUSEMOVE`）
4. `pump`：`PeekMessageW` + `TranslateMessage` + `DispatchMessageW` 直到队列空；遇到 quit 设 `_closing=True`
5. `present(bgra)`：构造 `BITMAPINFO`（`biHeight = -height` 顶向下，`biBitCount=32`，`BI_RGB`），`GetDC` + `StretchDIBits`（或 `SetDIBitsToDevice`）+ `ReleaseDC`

验收手测脚本（可临时 `python -c` 或 `scratch_present.py`，测完可删）：

```python
from platform.win32.input import InputState
from platform.win32.window import Window
from render.framebuffer import Framebuffer
import time

inp = InputState()
w = Window("fb test", 800, 600, inp)
fb = Framebuffer(800, 600)
fb.clear((30, 30, 80))
t0 = time.time()
while not w.should_close() and time.time() - t0 < 3:
    w.pump()
    w.present(fb.to_bgra_bytes())
w.destroy()
```

Expected: 弹出深蓝窗口约 3 秒可关。

- [ ] **Step 3: Commit**

```bash
git add platform/
git commit -m "feat: add Win32 window present via StretchDIBits"
```

---

### Task 5: main 接线、输入、删 pygame、README

**Files:**
- Modify: `main.py`（整文件替换逻辑）
- Modify: `platform/win32/window.py` / `input.py`（补齐键鼠若 Task 4 未完）
- Modify: `README.md`
- Delete: `render/render.py`（若仍存在且仅服务 pygame）
- 确认全仓库无 `import pygame`

**Interfaces:**
- Consumes: Task 1–4 全部对外 API
- Produces: 可运行应用

- [ ] **Step 1: 重写 `main.py`**

```python
from math import radians
import time

from platform.win32.input import InputState
from platform.win32.window import Window
from render.framebuffer import Framebuffer
from render.camera import Camera
from render.pipeline import draw_cube
from space_3d.cube import Cube
from space_3d.vec3 import Vec3

WIDTH, HEIGHT = 800, 600
FOCUS = 400.0

def main():
    inp = InputState()
    win = Window("soft renderer", WIDTH, HEIGHT, inp)
    fb = Framebuffer(WIDTH, HEIGHT)
    cube = Cube(Vec3(0, 0, 0), 80)
    cube.set_rotation(Vec3(0, 0, 0))
    cam = Camera(Vec3(0, 0, -250), yaw=0.0, pitch=0.0, focus=FOCUS, width=WIDTH, height=HEIGHT)
    light = Vec3(0.5, 0.8, 0.2)
    rot = Vec3(radians(0.6), radians(0.9), radians(0.4))
    move_speed = 120.0
    look_sens = 0.005
    prev = time.perf_counter()

    while not win.should_close():
        win.pump()
        now = time.perf_counter()
        dt = now - prev
        prev = now

        # 鼠标看
        if inp.mouse_down:
            cam.add_yaw_pitch(inp.mouse_dx * look_sens, inp.mouse_dy * look_sens)
        # WASD + 空格/Ctrl
        f = r = u = 0.0
        if ord("W") in inp.keys or ord("w") in inp.keys:
            f += move_speed * dt
        if ord("S") in inp.keys or ord("s") in inp.keys:
            f -= move_speed * dt
        if ord("D") in inp.keys or ord("d") in inp.keys:
            r += move_speed * dt
        if ord("A") in inp.keys or ord("a") in inp.keys:
            r -= move_speed * dt
        if 0x20 in inp.keys:  # VK_SPACE
            u += move_speed * dt
        if 0x11 in inp.keys:  # VK_CONTROL
            u -= move_speed * dt
        cam.move_local(f, r, u)
        inp.end_frame()

        cube.add_rotation(rot)
        fb.clear((20, 20, 20), 1.0)
        draw_cube(fb, cube, cam, light)
        win.present(fb.to_bgra_bytes())
        time.sleep(max(0.0, 1 / 60 - (time.perf_counter() - now)))

    win.destroy()

if __name__ == "__main__":
    main()
```

键码以 `window.py` 实际写入 `inp.keys` 的值为准（`wParam` 虚拟键码）；若用字符集，与 `WndProc` 保持一致。

- [ ] **Step 2: 更新 `README.md`**

```markdown
# pythonTest — 矩阵与软光栅

Windows 下用手写软光栅 + Win32 窗口显示旋转立方体（无 pygame）。

## 运行

```bash
python main.py
```

## 操作

- 鼠标左键拖曳：转视角
- WASD：移动；空格 / Ctrl：升降
```

- [ ] **Step 3: 删除旧路径并全库检查**

```bash
# 删除 render/render.py（若存在）
rg "pygame" -g "*.py"
```

Expected: 无匹配。

- [ ] **Step 4: 手工验收（对照 spec）**

1. `python main.py` → 彩色明暗立方体  
2. 拖鼠标、WASD → 相机动  
3. 旋转时遮挡正确  
4. 无 pygame

- [ ] **Step 5: Commit**

```bash
git add main.py README.md platform/ render/
git add -u render/render.py
git commit -m "feat: wire Win32 soft renderer main loop; remove pygame"
```

---

## Spec coverage（自审）

| Spec 项 | Task |
|---|---|
| 丢 pygame / Win32 ctypes | 4–5 |
| 保留 Cube/数学 | 全程 |
| 三角形 + Z-Buffer | 1, 3 |
| 扁平 Lambert | 2, 3 |
| 自转 + 键鼠相机 | 5 |
| 目录布局 | 全文 File Structure |
| 验收三条 | Task 5 Step 4 |
| 不做 clip/纹理/… | 未列入任务 |

## 类型一致性

- `Framebuffer.to_bgra_bytes()` ↔ `Window.present(bgra)`
- `draw_cube(fb, cube, camera, light_dir)`
- depth：越近 z 越小，`z < zbuf` 写入
- 相机默认朝 +Z；`main` 相机放在 `z=-250` 看向原点

---

## 执行方式（本仓库）

Plan 已保存后：**不要**默认用 subagent 直接改 `.py`。

推荐：

1. **逐任务引导（默认）**：你按 Task 1 → 5 改代码；每完成一个 Step / Task 告诉我，我对照指正与下一钩子。  
2. 若你之后放开「AI 可改代码」，再选 Inline / Subagent 自动执行。
