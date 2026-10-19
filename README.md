# 矩阵和图形学

在 Windows 窗口里用软光栅显示一个彩色立方体：三角形填充、深度缓冲、扁平 Lambert 光照。立方体自行旋转，相机可用鼠标和键盘移动。

窗口程序不使用 pygame。依赖 Python 3 和 numpy。

## 运行

```text
py -3 -m pip install numpy
py -3 main.py
```

窗口客户区是 800×800。实际绘制在 400×400 的帧缓冲上，再放大到窗口。关闭窗口即退出。

## 操作

- 按住鼠标左键拖动：转动视角
- W / S：沿视线前进、后退
- A / D：向左、向右平移
- 空格 / Ctrl：向上、向下
- 立方体持续自转

## 测试

```text
py -3 -m pytest tests/test_framebuffer.py tests/test_raster.py tests/test_pipeline_smoke.py tests/test_camera.py tests/test_shade.py -q
```
