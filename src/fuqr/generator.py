import tkinter
from datetime import datetime as dt
from enum import Enum, auto
from tkinter import filedialog

import qrcode
from PIL import Image, ImageTk
from qrcode.exceptions import DataOverflowError
from qrcode.image.pil import PilImage

from fuqr.util import gen_icon_path


class QrImageResult(Enum):
    SUCCESS = auto()
    TOOLONG = auto()
    INVALID = auto()


class QrImage(tkinter.Label):
    def __init__(
        self, master, *, value: str = None, size: tuple[int, int] = None, **kwgs
    ):
        super().__init__(master, **kwgs)

        self._img: PilImage
        self._imgtk: ImageTk

        self._value = value
        self._size = size

        if value:
            self.generate(value)

    @property
    def value(self) -> str:
        return self._value

    @value.setter
    def value(self, value: str):
        if self._value != value:
            self._value = value
            self.generate(value)

    @property
    def size(self) -> tuple[int, int]:
        return self._size

    @size.setter
    def size(self, size: tuple[int, int]):
        match size:
            case [w, h]:
                self._size = (w, h)
                self.generate()
            case int(v):
                self._size = (v, v)
                self.generate()

    def generate(self, value: str = None) -> QrImageResult:
        if value == "":
            self["image"] = None
            return QrImageResult.INVALID

        self._value = value or self._value

        if self._value is None:
            return QrImageResult.INVALID

        try:
            im_qr = qrcode.make(self._value)
            self._img = im_qr
            if self._size:
                self._img = im_qr.resize(self._size, Image.LANCZOS)
            self._imgtk = ImageTk.PhotoImage(self._img)
            self["image"] = self._imgtk
            return QrImageResult.SUCCESS
        except ValueError:
            return QrImageResult.INVALID
        except DataOverflowError:
            return QrImageResult.TOOLONG
        except Exception:
            raise

    def save_to_png(self, filename: str):
        self._img.save(filename)

    def open_save_dialog(self):
        file_name = f"{dt.now().strftime("%Y_%m_%d_%H%M%S")}.png"
        if file_path := filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png")],
            initialfile=file_name,
        ):
            self.save_to_png(file_path)


class QrGenerator:
    def __init__(self, master: tkinter.Misc = None):
        if master:
            self._root = tkinter.Toplevel(master)
        else:
            self._root = tkinter.Tk()

        self._root.title("QR作成")
        self._root.minsize(300, 0)
        self._root.iconbitmap(gen_icon_path())
        self._root.option_add("*Button.Cursor", "hand2")

        f = tkinter.Frame(self._root, padx=4)
        f.pack(fill=tkinter.BOTH, expand=True)

        self.lbl_qr = QrImage(f, text="文字列を入力してください", size=(300, 300))
        self.lbl_qr.pack(side=tkinter.TOP)

        self.txt_value = tkinter.Text(
            f, relief=tkinter.FLAT, height=1, width=-1, font=("", 12)
        )

        self.txt_value.bind("<<Modified>>", self._get_value)
        self.txt_value.bind("<KeyRelease>", self.on_txt_keyrelease)
        self.txt_value.pack(fill=tkinter.X, pady=2, padx=2)

        self.txt_value.focus()

        self.btn_save = tkinter.Button(
            f,
            text="保存",
            width=5,
            state="disabled",
            command=self.lbl_qr.open_save_dialog,
        )
        self.btn_save.pack(pady=2)

        self._msg = tkinter.StringVar()
        lbl_status = tkinter.Label(f, textvariable=self._msg)
        lbl_status.pack(fill=tkinter.X, side=tkinter.BOTTOM)

    def on_txt_keyrelease(self, e: tkinter.Event):
        value = self.txt_value.get("1.0", "end-1c")
        self.txt_value["height"] = value.count("\n") + 1

    def _get_value(self, e):
        self._value = self.txt_value.get("1.0", "end-1c")
        self._generate_qrcode(self._value)
        self.txt_value.edit_modified(False)

    def _set_value(self, value):
        self.txt_value.delete("1.0", "end")
        self.txt_value.insert("1.0", value)

    def _generate_qrcode(self, value):
        try:
            match self.lbl_qr.generate(value):
                case QrImageResult.SUCCESS:
                    self._msg.set("作成に成功しました")
                    self.btn_save["state"] = "active"
                case QrImageResult.TOOLONG:
                    self._show_error("データが長すぎます")
                case QrImageResult.INVALID:
                    self._show_error("無効な入力です")
        except Exception as e:
            self._show_error(f"予期せぬエラーが発生しました: {str(e)}")

    def generate(self, value):
        self._set_value(value)
        self._generate_qrcode(value)

    def _show_error(self, message):
        self._msg.set(message)
        self.btn_save["state"] = "disabled"

    def run(self):
        match type(self._root):
            case tkinter.Tk:
                self._root.mainloop()
            case tkinter.Toplevel:
                self._root.wait_window()


def generate_once(value: str):
    t = tkinter.Tk()
    t.iconbitmap(gen_icon_path())
    t.title(value)
    qr = QrImage(t, value=value)
    qr.pack(fill=tkinter.BOTH, expand=True)
    tkinter.Button(t, text="保存", command=qr.open_save_dialog).pack(
        fill=tkinter.X, pady=4, padx=4
    )
    t.mainloop()


if __name__ == "__main__":
    qg = QrGenerator()
    qg.run()
