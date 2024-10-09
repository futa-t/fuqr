import time
import tkinter
from typing import Any

import cv2
import mss
import numpy as np

_TRANSPARENTCOLOR = "hotpink2"


def screenshot_to_ndarray(x: int, y: int, width: int, height: int) -> np.ndarray | None:
    bbox = {"top": y, "left": x, "width": width, "height": height}

    try:
        with mss.mss() as sct:
            ss = sct.grab(bbox)
        return np.array(ss)
    except Exception:
        return None


class QrReader:
    def __init__(self, master: tkinter.Tk | tkinter.Toplevel = None):
        if master:
            self._root = tkinter.Toplevel(master)
        else:
            self._root = tkinter.Tk()

        self._root.title("fuqr")
        self._root.geometry("300x340")
        self._root.attributes("-topmost", True)
        self._root.wm_attributes("-transparentcolor", _TRANSPARENTCOLOR)
        self._root.wm_attributes("-toolwindow", True)
        self._root.option_add("*Button.cursor", "hand2")

        self.default_msg = "QRコードを枠内に納めてください"
        self.qr_value = None

        self.last_size = self._root.geometry()

        self.timer_move = None

        f = tkinter.Frame(self._root, padx=4, pady=4)
        f.pack(fill=tkinter.BOTH, expand=True)

        self._reader = tkinter.Frame(f, bg=_TRANSPARENTCOLOR)
        self._reader.pack(fill=tkinter.BOTH, expand=True)

        self.var_msg = tkinter.StringVar(value=self.default_msg)
        tkinter.Label(f, textvariable=self.var_msg).pack(fill=tkinter.X, pady=4)

        f_save = tkinter.Frame(f, height=24)
        f_save.propagate(False)
        f_save.pack(fill=tkinter.X, pady=2)

        tkinter.Button(f_save, text="オリジナルを保存").place(
            x=0, y=0, relheight=1, relwidth=0.49
        )
        tkinter.Button(f_save, text="エンコードしなおして保存").place(
            relx=0.51, rely=0, relheight=1, relwidth=0.49
        )

        f_cmd = tkinter.Frame(f, height=24)
        f_cmd.propagate(False)
        f_cmd.pack(fill=tkinter.X, pady=2)
        tkinter.Button(f_cmd, text="開く").place(x=0, y=0, relheight=1, relwidth=0.49)
        tkinter.Button(f_cmd, text="コピー").place(
            relx=0.51, rely=0, relheight=1, relwidth=0.49
        )

        self.loop()

        self._root.wait_window()

    def loop(self):
        self.capture()
        self._root.after(500, self.loop)

    def capture(self):
        self._root.update_idletasks()

        x = self._root.winfo_rootx()
        y = self._root.winfo_rooty()

        w = self._root.winfo_width()
        h = self._root.winfo_height()

        try:
            img = screenshot_to_ndarray(x, y, w, h)
            _, d, _, _ = cv2.QRCodeDetector().detectAndDecodeMulti(img)
            if d[0]:
                self.qr_value = d[0]
                self.var_msg.set(d[0])
        except Exception:
            self.var_msg.set(self.default_msg)
