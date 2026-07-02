import sys
import ctypes

def set_custom_titlebar_color(widget):
    """Sets the custom titlebar color for a QWidget (Windows 11 only)."""
    if sys.platform == "win32":
        try:
            hwnd = int(widget.winId())
            DWMWA_CAPTION_COLOR = 35
            DWMWA_TEXT_COLOR = 36
            
            # Color #0c1230 in COLORREF format (0x00bbggrr)
            # R=12 (0c), G=18 (12), B=48 (30) -> 0x0030120c
            bg_color = 0x0030120c
            text_color = 0x00FFFFFF # White
            
            ctypes.windll.dwmapi.DwmSetWindowAttribute(
                hwnd, DWMWA_CAPTION_COLOR,
                ctypes.byref(ctypes.c_int(bg_color)), 4)
            
            ctypes.windll.dwmapi.DwmSetWindowAttribute(
                hwnd, DWMWA_TEXT_COLOR,
                ctypes.byref(ctypes.c_int(text_color)), 4)
        except Exception as e:
            print(f"Failed to set title bar color for {widget}:", e)
