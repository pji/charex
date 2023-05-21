"""
gui
~~~

A graphical user interface for :mod:`charex`.
"""
import tkinter as tk
from tkinter import ttk

from charex import charex as ch
from charex import charsets as cset
from charex import util


# Constants.
ALL = (tk.N, tk.E, tk.W, tk.S)
SIDES = (tk.W, tk.E)
ENDS = (tk.N, tk.S)


# Application classes.
class CharDecode:
    def __init__(self, root):
        root.title = 'charex'
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)

        book = ttk.Notebook(root, padding='1 1 1 1')
        book.grid(column=0, row=0, sticky=ALL)
        cd_frame = ttk.Frame(book, padding='3 3 12 12')
        ce_frame = ttk.Frame(book, padding='3 3 12 12')
        book.add(cd_frame, text='cd')
        book.add(ce_frame, text='ce')

        self.build_cd(cd_frame)
        self.build_ce(ce_frame)

    def build_cd(self, main):
        main.columnconfigure(0, weight=1)
        main.columnconfigure(1, weight=0)
        main.rowconfigure(1, weight=0)
        main.rowconfigure(2, weight=0)
        main.rowconfigure(3, weight=1)

        self.cd_address = tk.StringVar()
        address_entry = ttk.Entry(
            main,
            width=80,
            textvariable=self.cd_address,
            justify=tk.RIGHT
        )
        address_entry.grid(column=0, columnspan=2, row=1, sticky=SIDES)

        cd_button = ttk.Button(main, text='Decode', command=self.cd)
        cd_button.grid(column=0, row=2, columnspan=2, sticky=SIDES)

        self.cd_result = tk.Text(main, width=80, height=24, wrap='word')
        ys = ttk.Scrollbar(
            main,
            orient='vertical',
            command=self.cd_result.yview
        )
        self.cd_result['yscrollcommand'] = ys.set
        self.cd_result.grid(column=0, row=3, sticky=ALL)
        ys.grid(column=1, row=3, sticky=ENDS)

        for child in main.winfo_children():
            child.grid_configure(padx=5, pady=5)

        address_entry.focus()
        root.bind('<Return>', self.cd)

    def build_ce(self, main):
        main.columnconfigure(0, weight=1)
        main.columnconfigure(1, weight=0)
        main.rowconfigure(1, weight=0)
        main.rowconfigure(2, weight=0)
        main.rowconfigure(3, weight=1)

        self.ce_address = tk.StringVar()
        address_entry = ttk.Entry(
            main,
            width=80,
            textvariable=self.ce_address,
            justify=tk.RIGHT
        )
        address_entry.grid(column=0, columnspan=2, row=1, sticky=SIDES)

        ce_button = ttk.Button(main, text='Encode', command=self.ce)
        ce_button.grid(column=0, row=2, columnspan=2, sticky=SIDES)

        self.ce_result = tk.Text(main, width=80, height=24, wrap='word')
        ys = ttk.Scrollbar(
            main,
            orient='vertical',
            command=self.ce_result.yview
        )
        self.ce_result['yscrollcommand'] = ys.set
        self.ce_result.grid(column=0, row=3, sticky=ALL)
        ys.grid(column=1, row=3, sticky=ENDS)

        for child in main.winfo_children():
            child.grid_configure(padx=5, pady=5)

        address_entry.focus()
        root.bind('<Return>', self.ce)

    def cd(self, *args):
        try:
            codecs = cset.get_codecs()
            base = self.cd_address.get()
            results = cset.multidecode(base, (codec for codec in codecs))

            width = max(len(codec) for codec in codecs)
            out = ''
            for key in results:
                c = results[key]
                details = ''
                if len(c) < 1:
                    details = '*** no character ***'
                elif len(c) > 1:
                    details = '*** multiple characters ***'
                else:
                    char = ch.Character(c)
                    details = f'{char.code_point} {char.name}'
                c = util.neutralize_control_characters(c)
                out += f'{key:>{width}}: {c} {details}\n'
            self.cd_result.insert('end', out)

        except ValueError:
            ...

    def ce(self, *args):
        try:
            codecs = cset.get_codecs()
            base = self.ce_address.get()
            results = cset.multiencode(base, (codec for codec in codecs))

            width = max(len(codec) for codec in codecs)
            out = ''
            for key in results:
                if b := results[key]:
                    c = ' '.join(f'{n:>02x}'.upper() for n in b)
                    out += f'{key:>{width}}: {c}\n'
            self.ce_result.insert('end', out)

        except ValueError:
            ...


if __name__ == '__main__':
    root = tk.Tk()
    app = CharDecode(root)
    root.mainloop()
