import subprocess
import sys
from datetime import datetime as dt
from pathlib import Path
from tkinter import filedialog

import mss
import numpy as np
from mss.screenshot import ScreenShot


def gen_icon_path():
    try:
        __base_path = Path(sys._MEIPASS)
    except Exception:
        __base_path = Path().resolve()
    return __base_path / "favicon.ico"


def _ss(x: int, y: int, width: int, height: int) -> ScreenShot | None:
    try:
        bbox = {"top": y, "left": x, "width": width, "height": height}

        with mss.mss() as sct:
            ss = sct.grab(bbox)
        return ss
    except Exception:
        return None


def screenshot_to_ndarray(x: int, y: int, width: int, height: int) -> np.ndarray | None:
    if ss := _ss(x, y, width, height):
        return np.array(ss)


def screenshot_to_png(x, y, width, height) -> str | None:
    file_name = f"{dt.now().strftime("%Y_%m_%d_%H%M%S")}.png"
    try:
        if ss := _ss(x, y, width, height):
            file_path = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[("PNG files", "*.png")],
                initialfile=file_name,
            )
            if file_path:
                mss.tools.to_png(ss.rgb, ss.size, output=file_path)
            return file_path
    except Exception:
        return None


def open_browser(url: str, prog: str = "explorer"):
    if url.startswith("http"):
        cmd = f'{prog} "{url}"'
        subprocess.run(cmd)
