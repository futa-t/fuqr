import threading
import tkinter
from datetime import datetime as dt

import cv2
import mss
import mss.tools
import numpy as np
from mss.screenshot import ScreenShot

_TRANSPARENTCOLOR = "hotpink2"


def _ss(x, y, width, height) -> ScreenShot | None:
    try:
        bbox = {"top": y, "left": x, "width": width, "height": height}

        with mss.mss() as sct:
            ss = sct.grab(bbox)
        return ss
    except Exception:
        return None


def screenshot_to_ndarray(x, y, width, height) -> np.ndarray | None:
    if ss := _ss(x, y, width, height):
        return np.array(ss)


def screenshot_to_png(x, y, width, height) -> str | None:
    file_name = f"{dt.now().strftime("%Y_%m_%d_%H%M%S")}.png"
    try:
        if ss := _ss(x, y, width, height):
            mss.tools.to_png(ss.rgb, ss.size, output=file_name)
            return file_name
    except Exception:
        return None


def analyze_from_ss(x, y, width, height) -> str | None:
    try:
        ss = screenshot_to_ndarray(x, y, width, height)
        r, _, _ = cv2.QRCodeDetector().detectAndDecode(ss)
        if r:
            return r
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
        self.msg = None

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

        tkinter.Button(
            f_save, text="スクリーンショットを保存", command=self.screenshot
        ).place(x=0, y=0, relheight=1, relwidth=0.49)
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

        self.reader_info = None
        self._root.bind("<Configure>", self.on_move)

        self.loop()

        self.th_analyze = threading.Thread(target=self.th_loop, daemon=True)
        self.th_flg = threading.Event()
        self.th_analyze.start()

        self._root.wait_window()

    def on_move(self, e: tkinter.Event):
        self._root.update_idletasks()
        x = self._reader.winfo_rootx()
        y = self._reader.winfo_rooty()

        w = self._reader.winfo_width()
        h = self._reader.winfo_height()

        self.reader_info = (x, y, w, h)

    def th_loop(self):
        while not self.th_flg.wait(0.5):
            self.capture_analyze()

    def loop(self):
        if self.qr_value:
            self.var_msg.set(self.qr_value)
        elif self.msg:
            self.var_msg.set(self.msg)
        self._root.after(500, self.loop)

    def capture_analyze(self):
        try:
            if qr_value := analyze_from_ss(*self.reader_info):
                self.qr_value = self.msg = qr_value
            else:
                self.qr_value = None
                self.msg = self.default_msg
        except Exception:
            self.qr_value = None
            self.msg = self.default_msg

    def screenshot(self):
        try:
            if f := screenshot_to_png(*self.reader_info):
                self.msg = f
        except Exception:
            pass
