# Win32 Soft Renderer Implementation Plan

> **协作约定：** 本仓库 AI **不直接改** `.py`；由用户按任务逐步改代码，AI 引导与指正。Steps 用 checkbox（`- [ ]`）跟踪。Task 内只写中文步骤与约定，**不贴实现代码**。

**目标：** 去掉 pygame，用 ctypes Win32 窗口 + 自研软光栅（三角形 + Z-Buffer + 扁平 Lambert）显示可自转的彩色立方体，并支持键鼠控制相机。

**架构：** 保留 `space_2d`/`space_3d`；新建 `render/` 管线与 `platform/win32/`；`main.py` 只做组装与循环。依赖单向：`main → platform → render → space_*`。

**技术栈：** Python 3、ctypes（user32/gdi32）、stdlib `array`/`math`/`time`；无 pygame。

## 全局约束

- 仅 Windows；不做跨平台抽象
- 工程内最终无 `import pygame`
- 光栅优先重心坐标 + Z-Buffer；扁平 Lambert + 少量环境光；固定方向光
- 第一版不做：完整 clip、纹理、Gouraud/Phong、多光源、阴影
- 客户区与帧缓冲 1:1（推荐 800×600）
- 业务代码由用户修改；本 plan 文档由 AI 维护
- Task 步骤用中文描述；实现代码在对话中按需给出，不写进 Task

## 拆分总览（顺序依赖）

| 块 | 内容 | 依赖 | 可独立验收 |
|---|---|---|---|
| A | `Framebuffer` + `Vec3.normalized` | 无 | 单测 |
| B | `Camera` + `shade` | A | 单测 |
| C | `raster` + `pipeline` | A+B、现有 Cube | 写 BMP/断言像素或离屏测 |
| D | Win32 `Window` present | A | 纯色窗口 |
| E | Win32 `Input` + `main` 接线、删 pygame、README | C+D | `python main.py` 全验收 |

---

## 文件结构

| 路径 | 职责 |
|---|---|
| `render/framebuffer.py` | RGB 字节缓冲 + float Z-Buffer；`clear` / `set_pixel` / `to_bgra_bytes` |
| `render/camera.py` | 位置、yaw/pitch；世界→相机；透视到屏幕 |
| `render/shade.py` | Lambert 扁平着色 |
| `render/raster.py` | 三角形重心填充 + depth test |
| `render/pipeline.py` | `draw_cube` 串起管线 |
| `render/color.py` | 可保留；管线内部可用 `(r,g,b)` int 0–255 |
| `platform/win32/window.py` | 窗口、消息泵、`present` |
| `platform/win32/input.py` | 键鼠状态 |
| `platform/win32/__init__.py` | 导出 |
| `space_3d/vec3.py` | 增加 `length` / `normalized` |
| `main.py` | 主循环 |
| `tests/` | 单测 |
| `README.md` | 运行说明 |
| 删除/停用 | `render/render.py` 旧画家路径（末尾任务删除） |

---

### 任务 1：Framebuffer + Vec3.normalized

**涉及文件**
- 新建：`render/framebuffer.py`
- 新建：`tests/test_framebuffer.py`
- 修改：`space_3d/vec3.py`（增加方法）
- 新建：`tests/test_vec3_normalize.py`

**对外约定**
- `Framebuffer(width, height)`：内部 BGRA 色缓冲 + float 深度缓冲
- `clear(rgb, depth=1.0)`：整屏填色并重置深度
- `set_pixel(x, y, z, rgb)`：越界忽略；存相机空间 z，越近越小；仅当 `z < zbuf` 时写入
- `to_bgra_bytes()`：顶向下、第 0 行为屏幕顶部，每像素 B,G,R,0
- `Vec3.length()` / `Vec3.normalized()`：零向量归一化返回零向量

**步骤**

- [ ] **步骤 1：** 写 `tests/test_framebuffer.py`：清屏后对同一像素写入远/近不同颜色，断言近的颜色胜出，且 `to_bgra_bytes` 通道顺序为 BGRA
- [ ] **步骤 2：** 跑该单测，确认因模块不存在而失败
- [ ] **步骤 3：** 实现 `render/framebuffer.py`（建议用 `array` 存色与深度）
- [ ] **步骤 4：** 再跑单测，确认通过
- [ ] **步骤 5：** 写 `tests/test_vec3_normalize.py`（例如 `(0,3,0)` 归一化后约为 `(0,1,0)`），并在 `Vec3` 上实现 `length` / `normalized`
- [ ] **步骤 6：** 自行提交（可选）：说明为 framebuffer 与 Vec3.normalized

**本任务验收：** 上述两个测试文件均通过。

---

### 任务 2：Camera + Lambert 着色

**涉及文件**
- 新建：`render/camera.py`、`render/shade.py`
- 新建：`tests/test_camera.py`、`tests/test_shade.py`

**对外约定**
- `Camera(position, yaw, pitch, focus, width, height)`
- `world_to_view(p)`：世界点 → 相机空间
- `project(view_p)`：返回 `(sx, sy, z_view)`；`view_p.z` 过近或在身后则返回 `None`
- `add_yaw_pitch`：pitch 钳制到约 ±π/2×0.99
- `move_local(forward, right, up)`：沿相机局部轴移动
- 相机约定：`yaw=0,pitch=0` 朝 **+Z**，世界 +Y 向上、+X 向右
- `shade_lambert(base_rgb, normal, light_dir, ambient=0.15)`：`light_dir` 为指向光源的方向；`ndotl = max(0, n·l)`；颜色按 `ambient + (1-ambient)*ndotl` 缩放并钳到 0–255

**步骤**

- [ ] **步骤 1：** 写 `tests/test_shade.py`：正对光源时接近原色；背对时只剩环境光分量
- [ ] **步骤 2：** 实现 `render/shade.py` 并跑通着色测试
- [ ] **步骤 3：** 写 `tests/test_camera.py`：相机在原点、朝 +Z，点 `(0,0,100)` 投影应落在画布中心附近
- [ ] **步骤 4：** 实现 `render/camera.py`（`world_to_view`：先平移再按 yaw/pitch 旋转，使前方落到 +Z；屏幕 Y 需翻转）
- [ ] **步骤 5：** 若投影符号与单测不符，以单测为准微调前向公式或测试点，保持「中心点投到画布中心」
- [ ] **步骤 6：** 自行提交（可选）

**本任务验收：** 着色与相机单测均通过。

---

### 任务 3：Raster + Pipeline

**涉及文件**
- 新建：`render/raster.py`、`render/pipeline.py`
- 新建：`tests/test_raster.py`、`tests/test_pipeline_smoke.py`
- 删除（本任务末或任务 5）：`render/render.py`（旧 pygame 画家路径）

**对外约定**
- `fill_triangle(fb, p0, p1, p2, rgb)`：`p*` 为屏幕 x/y + 深度 z；重心坐标填充并走 `set_pixel` 深度测试
- `draw_cube(fb, cube, camera, light_dir)`：用法线做背面剔除 + Lambert，四边形拆两三角形再光栅

**步骤**

- [ ] **步骤 1：** 写 `tests/test_raster.py`：在小帧缓冲里画覆盖中心的三角形，断言中心像素红色通道正确
- [ ] **步骤 2：** 实现 `render/raster.py`（重心坐标；面积近零则跳过；若绕序导致全空则交换两顶点）
- [ ] **步骤 3：** 实现 `render/pipeline.py`：算面法线（朝外）、背面剔除、着色、投影四点后画两个三角形；任一顶点投影失败则跳过该面
- [ ] **步骤 4：** 写烟雾测：旋转立方体 + 合适相机位置，断言帧缓冲有非零像素；失败时先查全剔面/全投影失败
- [ ] **步骤 5：** 自行提交（可选）

**本任务验收：** 光栅与烟雾测通过。

---

### 任务 4：Win32 窗口 + present

**涉及文件**
- 新建：`platform/__init__.py`（可空）
- 新建：`platform/win32/__init__.py`、`window.py`、`input.py`（本任务可先空壳，任务 5 填全键鼠）

**对外约定**
- `InputState`：`keys`、`mouse_down`、`mouse_dx`/`mouse_dy`；`end_frame()` 清 dx/dy
- `Window(title, width, height, input_state)`：`pump` / `should_close` / `present(bgra)` / `destroy`

**步骤**

- [ ] **步骤 1：** 实现最小 `InputState`（字段与 `end_frame`）
- [ ] **步骤 2：** 实现 `Window`：注册窗口类、创建窗口、消息泵；`present` 用顶向下 32 位 DIB（`biHeight` 为负）把 BGRA 贴到客户区；`WndProc` 至少处理销毁/退出，键鼠可写入 `InputState`
- [ ] **步骤 3：** 手测：开窗口、清成深蓝、present 约数秒可关
- [ ] **步骤 4：** 自行提交（可选）

**本任务验收：** 能弹出纯色窗口并正常关闭。

---

### 任务 5：main 接线、输入、删 pygame、README

**涉及文件**
- 修改：`main.py`、必要时补齐 `window.py`/`input.py`
- 修改：`README.md`
- 删除：`render/render.py`（若仍存在且仅服务 pygame）
- 确认全仓库无 `import pygame`

**步骤**

- [ ] **步骤 1：** 重写 `main.py`：创建窗口与帧缓冲、立方体自转、`draw_cube`、固定方向光；鼠标左键拖曳转视角；WASD + 空格/Ctrl 移动；限约 60 FPS；键码与 `WndProc` 写入方式一致
- [ ] **步骤 2：** 更新 `README.md`：如何运行、键鼠操作说明
- [ ] **步骤 3：** 删除旧画家路径；全库搜索确认无 pygame
- [ ] **步骤 4：** 手工验收：彩色明暗立方体、相机可控、遮挡正确、无崩溃
- [ ] **步骤 5：** 自行提交（可选）

**本任务验收：** `python main.py` 满足上述四条。

---

## Spec 覆盖（自审）

| Spec 项 | 任务 |
|---|---|
| 丢 pygame / Win32 ctypes | 4–5 |
| 保留 Cube/数学 | 全程 |
| 三角形 + Z-Buffer | 1, 3 |
| 扁平 Lambert | 2, 3 |
| 自转 + 键鼠相机 | 5 |
| 目录布局 | 文件结构 |
| 验收三条 | 任务 5 步骤 4 |
| 不做 clip/纹理/… | 未列入任务 |

## 类型一致性

- `Framebuffer.to_bgra_bytes()` ↔ `Window.present(bgra)`
- `draw_cube(fb, cube, camera, light_dir)`
- 深度：越近 z 越小，`z < zbuf` 写入
- 相机默认朝 +Z；`main` 相机放在 `z=-250` 看向原点

---

## 执行方式

1. **逐任务引导（默认）：** 你按 任务 1 → 5 改代码；每完成一步告诉我，我对照指正并给下一步要点（需要时再给代码片段）。
2. 若以后放开「AI 可改代码」，再另议自动执行。
