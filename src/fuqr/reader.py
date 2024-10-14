import tkinter

import cv2
import pyperclip

from fuqr.const import TRANSPARENTCOLOR
from fuqr.types import BBox
from fuqr.util import Thread, gen_icon_path, screenshot_to_ndarray

BORDERCOLOR = "gray94"
BORDERCOLOR_SUCCESS = "pale green"


class QrReaderFrame(tkinter.Frame):
    def __init__(self, master: tkinter.Misc, **kwgs):
        self._toplevel = master.winfo_toplevel()
        self._toplevel.wm_attributes("-transparentcolor", TRANSPARENTCOLOR)

        super().__init__(master, bg=BORDERCOLOR, padx=4, pady=4, **kwgs)

        self._reader = tkinter.Frame(self, bg=TRANSPARENTCOLOR)
        self._reader.pack(fill=tkinter.BOTH, expand=True)

        self.bbox = BBox()
        self.event_on_move = self._toplevel.bind("<Configure>", self.on_move, "+")

        self._once_flg = False

        self.value = None
        self.variable = tkinter.StringVar()
        self._timer_update_value = None

        self.th = Thread(target=self.th_loop, daemon=True)
        self.th.start()
        self.update_value()

    def th_loop(self):
        while not self.th.stop_event.wait(0.5):
            with self.th.lock:
                self.value = self.capture_and_decode()
        self.th.stop_event.clear()

    def capture_and_decode(self):
        try:
            ss = screenshot_to_ndarray(self.bbox)
            r, _, _ = cv2.QRCodeDetector().detectAndDecode(ss)
            if r:
                return r
        except Exception:
            return None

    def on_move(self, e: tkinter.Event):
        try:
            self._toplevel.update_idletasks()
            self.bbox.top = self.winfo_rooty()
            self.bbox.left = self.winfo_rootx()
            self.bbox.width = self.winfo_width()
            self.bbox.height = self.winfo_height()
        except Exception:
            return

    def update_value(self):
        if self.value:
            self.configure(bg=BORDERCOLOR_SUCCESS)
            if self.value != self.variable.get():
                self.variable.set(self.value)
        else:
            self.configure(bg=BORDERCOLOR)
        self.update()
        if not self.th.stop_event.is_set():
            self._timer_update_value = self.after(500, self.update_value)

    def read_once(self):
        self._once_flg = True
        self.update_value()
        self.wait_variable(self.variable)
        self.cleanup()

        return self.variable.get()

    def cleanup(self):
        if self._timer_update_value:
            self.after_cancel(self._timer_update_value)
            self._timer_update_value = None

        self.th.stop_event.set()
        self.th.join()

        try:
            self._toplevel.unbind("<Configure>", self.event_on_move)
        except Exception:
            pass

    def destroy(self):
        if self._once_flg:
            self.variable.set(None)
        self.cleanup()
        super().destroy()


class QrReader:
    def __init__(self, master: tkinter.Misc = None):
        if master:
            self._root = tkinter.Toplevel(master)
        else:
            self._root = tkinter.Tk()

        self._root.geometry("300x350")
        f = tkinter.Frame(self._root)
        f.pack(fill=tkinter.BOTH, expand=True, padx=4, pady=4)

        self.reader = QrReaderFrame(f, height=300, width=300)
        self.reader.propagate(False)
        self.reader.pack(fill=tkinter.BOTH, expand=True)

        self.reader.variable.trace_add("write", self.main)

        self.history = []

        self.qr_value = tkinter.StringVar()
        tkinter.Label(f, textvariable=self.qr_value, anchor=tkinter.W).pack(
            fill=tkinter.X
        )

        self.btn_txt_copy = tkinter.StringVar(value="コピー")
        tkinter.Button(
            f, textvariable=self.btn_txt_copy, command=self.copy, cursor="hand2"
        ).pack(fill=tkinter.X)

    def copy(self):
        if self.reader.value:
            pyperclip.copy(self.reader.value)
            self.btn_txt_copy.set("コピーしました")
            self._root.after(1000, lambda *args: self.btn_txt_copy.set("コピー"))

    def main(self, *args):
        if not self.reader.value:
            return

        v = self.reader.value
        if v in self.history:
            self.history.remove(v)
        self.history.append(v)
        self.qr_value.set(v)

    def run(self):
        match type(self._root):
            case tkinter.Tk:
                self._root.mainloop()
            case tkinter.Toplevel:
                self._root.wait_window()


def read_once() -> str:
    t = tkinter.Tk()
    t.iconbitmap(gen_icon_path())
    t.title("QRコード読み取り")
    f = tkinter.Frame(t, width=300, height=300)
    f.propagate(False)
    f.pack(fill=tkinter.BOTH, expand=True)
    qr = QrReaderFrame(f)
    qr.pack(fill=tkinter.BOTH, expand=True)
    tkinter.Label(t, text="枠内にQRコードを収めてください").pack(side=tkinter.BOTTOM)
    return qr.read_once()


if __name__ == "__main__":
    qr = QrReader()
    qr.run()
