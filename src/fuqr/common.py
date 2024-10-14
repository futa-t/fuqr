# ruff: noqa: F403
import tkinter

import pyperclip

from fuqr import const, util
from fuqr.generator import QrGenerator
from fuqr.reader import QrReaderFrame

__version__ = "0.2.0"

_ICON = util.gen_icon_path()


class FuQr:
    MSG_NOTFOUND = "QRコードを認識できません"
    MSG_FOUND = "QRコードを認識しました"

    def __init__(self, master: tkinter.Misc = None):
        if master:
            self._root = tkinter.Toplevel(master)
        else:
            self._root = tkinter.Tk()

        if _ICON.exists():
            self._root.iconbitmap(default=_ICON)

        self._root.title("fuqr")
        self._root.geometry("300x380")
        self._root.attributes("-topmost", True)
        self._root.wm_attributes("-transparentcolor", const.TRANSPARENTCOLOR)
        self._root.option_add("*Button.cursor", "hand2")
        self._root.option_add("*Font", ("Meiryo UI", 10))

        self.reader = QrReaderFrame(self._root)
        self.reader.pack(fill=tkinter.BOTH, expand=True)

        lbl_value = tkinter.Label(
            self._root, textvariable=self.reader.variable, anchor=tkinter.W
        )
        lbl_value.pack(fill=tkinter.X, pady=2)

        f_save = tkinter.Frame(self._root, height=24)
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

        f_cmd = tkinter.Frame(self._root, height=24)
        f_cmd.propagate(False)
        f_cmd.pack(fill=tkinter.X, pady=2)
        self.btn_open_browser = tkinter.Button(
            f_cmd, text="ブラウザで開く", command=self.open_browser
        )
        self.btn_open_browser.place(x=0, y=0, relheight=1, relwidth=0.49)
        tkinter.Button(f_cmd, text="コピー", command=self.copy_value).place(
            relx=0.51, rely=0, relheight=1, relwidth=0.49
        )

        self._status = f"fuqr v{__version__}"
        self._var_status = tkinter.StringVar(value=self._status)
        lbl_status = tkinter.Label(self._root, textvariable=self._var_status)
        lbl_status.pack(fill=tkinter.X, side=tkinter.BOTTOM)
        self._id_update = None
        self.update_status_loop()

    def run(self):
        match type(self._root):
            case tkinter.Tk:
                self._root.mainloop()
            case tkinter.Toplevel:
                self._root.wait_window()

    def open_detail(self, e: tkinter.Event):
        if self.reader.value is None:
            return

        t = tkinter.Toplevel(self._root, padx=6, pady=4)
        tkinter.Label(t, text=self.reader.value).pack(fill=tkinter.X)

        t.wait_window()

    def copy_value(self):
        if self.reader.value:
            pyperclip.copy(self.reader.value)
            self.update_status("コピーしました")
        else:
            self.update_status("コピーに失敗しました。結果がありません")
        self._root.after(2000, self.update_status_loop)

    def update_status(self, text, sec: int = 2):
        if self._id_update:
            self._root.after_cancel(self._id_update)
        self._var_status.set(text)

        self._root.after(sec * 1000, self.update_status_loop)

    def open_browser(self):
        match self.reader.value:
            case str(v) if v.startswith("http"):
                util.open_browser(v)
            case _:
                self.update_status("URL形式ではありません")

    def encode_save(self):
        if self.reader.value:
            gen = QrGenerator(self._root)
            gen.generate(self.reader.value)
            gen.run()

    def update_status_loop(self, *args):
        val = self.reader.value
        if val:
            self._var_status.set(self.MSG_FOUND)
        else:
            self._var_status.set(self.MSG_NOTFOUND)
        self._id_update = self._root.after(500, self.update_status_loop)

    def screenshot(self):
        try:
            if f := util.screenshot_to_png(self.reader.bbox):
                self._var_status = f
        except Exception:
            pass


if __name__ == "__main__":
    fq = FuQr()
    fq.run()
