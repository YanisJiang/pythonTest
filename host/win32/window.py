import ctypes
from ctypes import c_int, wintypes

from space_2d.vec2 import Vec2

from .input import InputState

windows = {}

user32 = ctypes.WinDLL("user32")

WINPROC = ctypes.WINFUNCTYPE(
    ctypes.c_longlong, wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM
)

user32.DefWindowProcW.argtypes = [
    wintypes.HWND,
    wintypes.UINT,
    wintypes.WPARAM,
    wintypes.LPARAM,
]
user32.DefWindowProcW.restype = ctypes.c_longlong


def windows_proc(hwnd, msg, wparam, lparam):
    window = windows.get(int(hwnd))
    if window:
        if msg == 256:
            window.input_state.cur_key.add(wparam)
        if msg == 257:
            window.input_state.cur_key.discard(wparam)
        if msg == 513:
            window.input_state.mouse_left = True
        if msg == 514:
            window.input_state.mouse_left = False
        if msg == 512:
            x = ctypes.c_short(lparam & 0xFFFF).value
            y = ctypes.c_short((lparam >> 16) & 0xFFFF).value
            if window.mouse_position is None:
                window.mouse_position = Vec2(x, y)
            window.input_state.mouse_delta.x += x - window.mouse_position.x
            window.input_state.mouse_delta.y += y - window.mouse_position.y
            window.mouse_position.x = x
            window.mouse_position.y = y

    if msg == 2:
        user32.PostQuitMessage(0)
        return 0
    return user32.DefWindowProcW(hwnd, msg, wparam, lparam)


class WNDCLASSW(ctypes.Structure):
    _fields_ = [
        ("style", wintypes.UINT),
        ("lpfnWndProc", WINPROC),
        ("cbClsExtra", c_int),
        ("cbWndExtra", c_int),
        ("hInstance", wintypes.HINSTANCE),
        ("hIcon", wintypes.HICON),
        ("hCursor", wintypes.HCURSOR),
        ("hbrBackground", wintypes.HBRUSH),
        ("lpszMenuName", wintypes.LPCWSTR),
        ("lpszClassName", wintypes.LPCWSTR),
    ]


class MSG(ctypes.Structure):
    _fields_ = [
        ("hwnd", wintypes.HWND),
        ("message", wintypes.UINT),
        ("wParam", wintypes.WPARAM),
        ("lParam", wintypes.LPARAM),
        ("time", wintypes.DWORD),
        ("pt", wintypes.POINT),
    ]


class BITMAPINFOHEADER(ctypes.Structure):
    _fields_ = [
        ("biSize", wintypes.DWORD),
        ("biWidth", wintypes.LONG),
        ("biHeight", wintypes.LONG),
        ("biPlanes", wintypes.WORD),
        ("biBitCount", wintypes.WORD),
        ("biCompression", wintypes.DWORD),
        ("biSizeImage", wintypes.DWORD),
        ("biXPelsPerMeter", wintypes.LONG),
        ("biYPelsPerMeter", wintypes.LONG),
        ("biClrUsed", wintypes.DWORD),
        ("biClrImportant", wintypes.DWORD),
    ]


class Window:
    title: str
    width: int
    height: int
    input_state: InputState
    mouse_position: Vec2
    proc: WINPROC
    module_handle: wintypes.HINSTANCE
    window_class: WNDCLASSW
    close: bool
    hwnd: wintypes.HWND

    def __init__(self, title, width, height, input_state):
        self.title = title
        self.width = width
        self.height = height
        self.input_state = input_state
        self.mouse_position = None
        self.close = False
        self.proc = WINPROC(windows_proc)
        self.module_handle = wintypes.HINSTANCE(
            ctypes.WinDLL("kernel32").GetModuleHandleW(None)
        )
        self.window_class = WNDCLASSW(
            0, self.proc, 0, 0, self.module_handle, None, None, None, None, "asset"
        )
        user32.RegisterClassW(ctypes.byref(self.window_class))

        user32.CreateWindowExW.restype = wintypes.HWND
        self.hwnd = user32.CreateWindowExW(
            0,
            "asset",
            self.title,
            0x00CF0000,
            0x80000000,
            0x80000000,
            self.width,
            self.height,
            None,
            None,
            self.module_handle,
            None,
        )

        windows[int(self.hwnd)] = self

        user32.ShowWindow(self.hwnd, 1)

    def pump(self):
        msg = MSG()
        while user32.PeekMessageW(ctypes.byref(msg), None, 0, 0, 1) != 0:
            if msg.message == 18:
                self.close = True
            user32.TranslateMessage(ctypes.byref(msg))
            user32.DispatchMessageW(ctypes.byref(msg))

    def should_close(self):
        return self.close

    def present(self, bgra, src_w, src_h):
        gdi32 = ctypes.WinDLL("gdi32")
        bitmap_info_header = BITMAPINFOHEADER(
            ctypes.sizeof(BITMAPINFOHEADER),
            src_w,
            -src_h,
            1,
            32,
            0,
            0,
            0,
            0,
            0,
            0,
        )
        user32.GetDC.restype = wintypes.HDC
        hdc = user32.GetDC(self.hwnd)
        gdi32.StretchDIBits.argtypes = [
            wintypes.HDC,
            c_int,
            c_int,
            c_int,
            c_int,
            c_int,
            c_int,
            c_int,
            c_int,
            ctypes.c_void_p,
            ctypes.POINTER(BITMAPINFOHEADER),
            wintypes.UINT,
            wintypes.DWORD,
        ]
        gdi32.SetStretchBltMode.argtypes = [wintypes.HDC, c_int]
        gdi32.SetStretchBltMode.restype = c_int
        gdi32.SetStretchBltMode(hdc, 4)
        gdi32.StretchDIBits(
            hdc,
            0,
            0,
            self.width,
            self.height,
            0,
            0,
            src_w,
            src_h,
            bgra,
            ctypes.byref(bitmap_info_header),
            0,
            0x00CC0020,
        )
        user32.ReleaseDC.argtypes = [wintypes.HDC, wintypes.HDC]
        user32.ReleaseDC.restype = c_int
        user32.ReleaseDC(self.hwnd, hdc)
