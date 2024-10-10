import subprocess
import sys
import threading
import tkinter
from datetime import datetime as dt
from pathlib import Path
from tkinter import filedialog

import cv2
import mss
import mss.tools
import numpy as np
import qrcode
from mss.screenshot import ScreenShot
from PIL import ImageTk

__version__ = "0.1.2"

_TRANSPARENTCOLOR = "hotpink2"

try:
    __base_path = Path(sys._MEIPASS)
except Exception:
    __base_path = Path().resolve()
ICON = __base_path / "favicon.ico"


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


def analyze_from_ss(x, y, width, height) -> str | None:
    try:
        ss = screenshot_to_ndarray(x, y, width, height)
        r, _, _ = cv2.QRCodeDetector().detectAndDecode(ss)
        if r:
            return r
    except Exception:
        return None


def save_qrcode_window(value: str):
    im_qr = qrcode.make(value)

    t = tkinter.Toplevel(padx=8, pady=4)
    t.title(value)
    t.iconbitmap(ICON)
    imtk_qr = ImageTk.PhotoImage(im_qr)

    tkinter.Label(t, image=imtk_qr).pack(fill=tkinter.BOTH, expand=True)
    tkinter.Label(t, text=value).pack(fill=tkinter.X, pady=4)

    def save():
        file_name = f"{dt.now().strftime("%Y_%m_%d_%H%M%S")}_regen.png"
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png")],
            initialfile=file_name,
        )
        if file_path:
            im_qr.save(file_path)

    tkinter.Button(t, text="保存", command=save).pack(fill=tkinter.X, pady=4)
    t.wait_window()


class QrReader:
    def __init__(self, master: tkinter.Tk | tkinter.Toplevel = None):
        if master:
            self._root = tkinter.Toplevel(master)
        else:
            self._root = tkinter.Tk()

        if ICON.exists():
            self._root.iconbitmap(ICON)

        self._root.title("fuqr")
        self._root.geometry("300x340")
        self._root.attributes("-topmost", True)
        self._root.wm_attributes("-transparentcolor", _TRANSPARENTCOLOR)
        self._root.option_add("*Button.cursor", "hand2")

        self.default_msg = "QRコードを認識できません"
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
        tkinter.Button(
            f_save,
            text="エンコードしなおして保存",
            command=self.encode_save,
        ).place(relx=0.51, rely=0, relheight=1, relwidth=0.49)

        f_cmd = tkinter.Frame(f, height=24)
        f_cmd.propagate(False)
        f_cmd.pack(fill=tkinter.X, pady=2)
        self.btn_open_browser = tkinter.Button(
            f_cmd, text="ブラウザで開く", command=self.open_browser
        )
        self.btn_open_browser.place(x=0, y=0, relheight=1, relwidth=0.49)
        tkinter.Button(f_cmd, text="コピー", command=self.copy_value).place(
            relx=0.51, rely=0, relheight=1, relwidth=0.49
        )

        self.reader_info = None
        self._root.bind("<Configure>", self.on_move)

        self.loop()

        self.th_analyze = threading.Thread(target=self.th_loop, daemon=True)
        self.th_flg = threading.Event()
        self.th_lock = threading.Lock()
        self.th_analyze.start()

    def run(self):
        match type(self._root):
            case tkinter.Tk:
                self._root.mainloop()
            case tkinter.Toplevel:
                self._root.wait_window()
        self.th_flg.set()

    def copy_value(self):
        if self.qr_value:
            self._root.clipboard_clear()
            self._root.clipboard_append(self.qr_value)

    def open_browser(self):
        if self.qr_value.startswith("http"):
            subprocess.Popen(["explorer", self.qr_value])

    def encode_save(self):
        if self.qr_value:
            save_qrcode_window(self.qr_value)

    def on_move(self, e: tkinter.Event):
        self._root.update_idletasks()
        x = self._reader.winfo_rootx()
        y = self._reader.winfo_rooty()

        w = self._reader.winfo_width()
        h = self._reader.winfo_height()

        self.reader_info = (x, y, w, h)

    def th_loop(self):
        while not self.th_flg.wait(0.5):
            with self.th_lock:
                self.capture_analyze()
        self.th_flg.clear()

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


def main():
    QrReader()
