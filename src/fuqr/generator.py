import tkinter

import qrcode
from PIL import Image, ImageTk

from fuqr import util


class QrGenerator:
    def __init__(self, master: tkinter.Misc = None):
        if master:
            self._root = tkinter.Toplevel(master)
        else:
            self._root = tkinter.Tk()

        self._root.title("QR作成")
        self._root.minsize(300, 0)
        self._root.iconbitmap(util.gen_icon_path())

        self.lbl_qr = tkinter.Label(self._root, text="文字列を入力してください")
        self.lbl_qr.pack(side=tkinter.TOP)
        self._size_qr = (300, 300)
        self._value = tkinter.StringVar(value=value)
        tkinter.Entry(self._root, textvariable=self._value).pack(fill=tkinter.X)
        self._value.trace_add("write", self.regen)
        if value:
            self.generate_qrcode(value)

    def regen(self, *args):
        self.generate_qrcode(self._value.get())

    def generate_qrcode(self, value):
        im_qr = qrcode.make(value)

        self._im_qr = ImageTk.PhotoImage(im_qr.resize(self._size_qr, Image.LANCZOS))
        self.lbl_qr["image"] = self._im_qr

    def run(self):
        match type(self._root):
            case tkinter.Tk:
                self._root.mainloop()
            case tkinter.Toplevel:
                self._root.wait_window()


if __name__ == "__main__":
    qg = QrGenerator()
    qg.run()
