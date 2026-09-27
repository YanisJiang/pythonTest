# Win32 软光栅渲染器设计

日期：2026-09-27  
状态：已口头对齐，待实现规划  

## 目标

丢弃 pygame，从零手搓软光栅渲染器，在 Windows 窗口中显示带 Lambert 光照的彩色立方体；支持立方体自转与键鼠控制相机。

## 协作边界（本仓库约定）

- **业务代码**（`.py` 等）：AI 不直接修改；由 AI 给出步骤与片段，用户自行改；改错由 AI 指正。
- **docs / rules**：AI 可在 Plan 确认后修改（本 spec 属此类）。

## 方案选择

保留 `space_2d` / `space_3d` 数学与 `Cube` 几何；整层替换渲染与窗口，不采用「连几何重写」或「单文件糊在一起」方案。

## 架构

单向依赖：

```
main（场景 / 主循环）
  → platform.win32（窗口、输入、present）
  → render（帧缓冲、Z-Buffer、光栅、Lambert、相机）
  → space_3d / space_2d（Cube、Vec、Matrix）
```

| 层 | 职责 | 不负责 |
|---|---|---|
| `space_*` | 数学、立方体顶点/面/旋转 | 像素、窗口 |
| `render` | 世界 mesh + 相机 + 光源 → RGB 帧缓冲 | Win32 API、Cube 定义 |
| `platform.win32` | 窗口、消息泵、键鼠、`StretchDIBits` present | Cube、光栅算法 |
| `main` | 组装与每帧调度 | 底层光栅细节 |

删除：pygame 依赖；现有绑定 pygame 的渲染路径。颜色用简单 RGB 三元组或小类型，不绑第三方库。

## 渲染管线（每帧）

1. **模型变换**：现有累积旋转矩阵 → 世界空间顶点（`cur_points`）。
2. **视图**：相机位置 + yaw/pitch；世界 → 相机空间（简单欧拉/look-at，无场景图）。
3. **投影**：透视到屏幕空间（明确 focus/fov、near、宽高；整理现有 focus/depth 思路）。
4. **图元装配**：每四边形拆 2 三角形；算面法线。
5. **背面剔除**：法线与「面心→相机」点积，背对则丢。
6. **Lambert（扁平）**：每三角形一色：`base * max(0, n·L)` + 少量环境光；固定方向光。
7. **光栅 + Z-Buffer**：优先重心坐标填充（实现简单、易带 depth）；写色前 depth test；清背景色与 far depth。
8. **输出**：`width×height` RGB 缓冲交给 Win32 present。

**第一版不做**：完整 clip 平面、纹理、Gouraud/Phong 插值、多光源、阴影。

## Win32 与输入

- `ctypes` 调 `user32` / `gdi32`：窗口类、`CreateWindowEx`、消息循环。
- 客户区固定分辨率（如 800×600），与帧缓冲 1:1。
- 每帧将 RGB 做成顶向下 DIB，`StretchDIBits`（或等价）贴到客户区。
- 主循环：`PeekMessage` → 更新输入 → 更新立方体/相机 → render → present → 可选限帧 sleep。
- **输入（第一版）**
  - 鼠标左键拖曳：相机 yaw/pitch
  - WASD：水平移动；空格 / Ctrl：升降
  - 立方体每帧自动旋转（暂停键非必须）
- 仅 Windows；不做跨平台抽象。
- 对外：`Window`（创建 / pump / present / should_close）、`InputState`（键、鼠标增量）。

## 建议目录

```
main.py
space_2d/          # 保留
space_3d/          # 保留
space_4d/          # 本阶段不动
render/
  framebuffer.py   # RGB + Z-Buffer
  camera.py
  raster.py        # 三角形 + depth
  shade.py         # Lambert 扁平
  pipeline.py      # draw(cube, camera, light)
platform/
  win32/
    window.py
    input.py
```

## 迁移要点

- 去掉 pygame；重写 `main` 组装方式。
- 旧 `render/render.py` 画家算法路径淘汰，由新管线替代。
- README：无 pygame、仅 Windows、运行方式。

## 验收

1. `python main.py` 弹出 Win32 窗口，可见带明暗的彩色立方体。
2. 拖鼠标转视角，WASD 移动；遮挡关系正确（Z-Buffer）。
3. 工程内无 `import pygame`。

## 成功标准（摘要）

无 pygame；三角形光栅 + Z-Buffer；扁平 Lambert；立方体自转 + 键鼠相机。
