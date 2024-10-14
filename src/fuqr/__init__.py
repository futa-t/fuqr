# ruff: noqa: F403
import threading
import tkinter

import cv2
import pyperclip

from fuqr import const, util
from fuqr.generator import QrGenerator, generate_once
from fuqr.reader import QrReader, read_once
from fuqr.types import BBox

__version__ = "0.1.3"

_ICON = util.gen_icon_path()


class QrReader:
    def __init__(self, master: tkinter.Misc = None):
        if master:
            self._root = tkinter.Toplevel(master)
        else:
            self._root = tkinter.Tk()

        if _ICON.exists():
            self._root.iconbitmap(_ICON)

        self._root.title("fuqr")
        self._root.geometry("300x340")
        self._root.attributes("-topmost", True)
        self._root.wm_attributes("-transparentcolor", const.TRANSPARENTCOLOR)
        self._root.option_add("*Button.cursor", "hand2")

        self.default_msg = "QRコードを認識できません"
        self.qr_value = None
        self.msg = None

        self.last_size = self._root.geometry()

        self.timer_move = None

        f = tkinter.Frame(self._root, padx=4, pady=4)
        f.pack(fill=tkinter.BOTH, expand=True)

        self._reader = tkinter.Frame(f, bg=const.TRANSPARENTCOLOR)
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

        self.reader_info = BBox(0, 0, 0, 0)
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
            pyperclip.copy(self.qr_value)

    def open_browser(self):
        util.open_browser(self.qr_value)

    def encode_save(self):
        if self.qr_value:
            gen = QrGenerator(self._root)
            gen.generate(self.qr_value)
            gen.run()

    def on_move(self, e: tkinter.Event):
        self._root.update_idletasks()
        self.reader_info.left = self._reader.winfo_rootx()
        self.reader_info.top = self._reader.winfo_rooty()

        self.reader_info.width = self._reader.winfo_width()
        self.reader_info.height = self._reader.winfo_height()

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

    def analyze_from_ss(self, bbox: BBox) -> str | None:
        try:
            ss = util.screenshot_to_ndarray(bbox)
            r, _, _ = cv2.QRCodeDetector().detectAndDecode(ss)
            if r:
                return r
        except Exception:
            return None

    def capture_analyze(self):
        try:
            if qr_value := self.analyze_from_ss(self.reader_info):
                self.qr_value = self.msg = qr_value
            else:
                self.qr_value = None
                self.msg = self.default_msg
        except Exception:
            self.qr_value = None
            self.msg = self.default_msg

    def screenshot(self):
        try:
            if f := util.screenshot_to_png(self.reader_info):
                self.msg = f
        except Exception:
            pass
