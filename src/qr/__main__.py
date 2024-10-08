import tkinter

import fuqr

fuqr.QrReader()

r = tkinter.Tk()


def o():
    e = fuqr.QrReader()
    print(e.qr_value)


tkinter.Button(r, text="open", command=o).pack()
r.mainloop()
