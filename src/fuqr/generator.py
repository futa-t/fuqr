import tkinter

import qrcode
from PIL import Image, ImageTk
from qrcode.exceptions import DataOverflowError

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

        self.txt_value = tkinter.Text(
            self._root, relief=tkinter.FLAT, height=1, width=-1, font=("", 12)
        )

        self.txt_value.bind("<<Modified>>", self._get_value)
        self.txt_value.bind("<KeyRelease>", self.on_txt_keyrelease)
        self.txt_value.pack(fill=tkinter.X)

        self.txt_value.focus()

        self._msg = tkinter.StringVar()
        lbl_status = tkinter.Label(self._root, textvariable=self._msg)
        lbl_status.pack(fill=tkinter.X, side=tkinter.BOTTOM)

    def on_txt_keyrelease(self, e: tkinter.Event):
        value = self.txt_value.get("1.0", "end-1c")
        self.txt_value["height"] = value.count("\n") + 1

    def _get_value(self, e):
        self._value = self.txt_value.get("1.0", "end-1c")
        self.generate_qrcode(self._value)
        self.txt_value.edit_modified(False)

    def generate_qrcode(self, value):
        try:
            if value == "":
                self.lbl_qr["image"] = ""  # Clear the current image
                raise ValueError
            im_qr = qrcode.make(value)
            self._im_qr = ImageTk.PhotoImage(im_qr.resize(self._size_qr, Image.LANCZOS))
            self.lbl_qr["image"] = self._im_qr
            self._msg.set("作成成功")
        except DataOverflowError:
            self._show_error("データが長すぎます。短い文字列を入力してください。")
        except ValueError:
            self._show_error("無効な入力です。")
        except Exception as e:
            self._show_error(f"予期せぬエラーが発生しました: {str(e)}")

    def _show_error(self, message):
        self._msg.set(message)

    def run(self):
        match type(self._root):
            case tkinter.Tk:
                self._root.mainloop()
            case tkinter.Toplevel:
                self._root.wait_window()


if __name__ == "__main__":
    qg = QrGenerator()
    qg.run()
