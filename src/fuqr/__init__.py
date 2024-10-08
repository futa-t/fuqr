import tkinter

_TRANSPARENTCOLOR = "hotpink2"


class QrReader:
    def __init__(self, master=None):
        if master:
            self.root = tkinter.Toplevel(master)
        else:
            self.root = tkinter.Tk()

        self.root.title("fuqr")
        self.root.geometry("300x340")
        self.root.attributes("-topmost", True)
        self.root.wm_attributes("-transparentcolor", _TRANSPARENTCOLOR)
        self.root.wm_attributes("-toolwindow", True)
        self.root.option_add("*Button.cursor", "hand2")
        self.default_msg = "QRコードを枠内に納めてください"
        self.qr_value = None

        f = tkinter.Frame(self.root, padx=4, pady=4)
        f.pack(fill=tkinter.BOTH, expand=True)

        self._reader = tkinter.Frame(f, bg=_TRANSPARENTCOLOR)
        self._reader.pack(fill=tkinter.BOTH, expand=True)

        self.var_msg = tkinter.StringVar(value=self.default_msg)
        self._lbl_msg = tkinter.Label(f, textvariable=self.var_msg)
        self._lbl_msg.pack(fill=tkinter.X, pady=4)

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

        self.root.wait_window()
