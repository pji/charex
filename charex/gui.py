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
from charex.shell import make_description_row


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
        self.book = book
        book.grid(column=0, row=0, sticky=ALL)
        cd_frame = ttk.Frame(book, padding='3 3 12 12')
        ce_frame = ttk.Frame(book, padding='3 3 12 12')
        cl_frame = ttk.Frame(book, padding='3 3 12 12')
        book.add(cd_frame, text='cd')
        book.add(ce_frame, text='ce')
        book.add(cl_frame, text='cl')

        self.build_cd(cd_frame)
        self.build_ce(ce_frame)
        self.build_cl(cl_frame)
        root.bind('<Return>', self.execute)

    def execute(self, *args):
        cmds = {
            0: self.cd,
            1: self.ce,
            2: self.cl,
        }
        tab_id = self.book.select()
        tab = self.book.index(tab_id)
        cmd = cmds[tab]
        cmd()

    def config_simple_grid(self, frame):
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=0)
        frame.rowconfigure(1, weight=0)
        frame.rowconfigure(2, weight=0)
        frame.rowconfigure(3, weight=1)

    def make_button(
        self,
        frame,
        name,
        cmd,
        col=0,
        row=2,
        colspan=2,
        rowspan=1,
        sticky=SIDES
    ):
        button = ttk.Button(frame, text=name, command=cmd)
        button.grid(
            column=col,
            row=row,
            columnspan=colspan,
            rowspan=rowspan,
            sticky=sticky
        )
        return button

    def make_entry(
        self,
        frame,
        value,
        width=80,
        col=0,
        row=1,
        colspan=2,
        rowspan=1,
        sticky=SIDES,
        justify=tk.RIGHT
    ):
        entry = ttk.Entry(
            frame,
            width=width,
            textvariable=value,
            justify=tk.RIGHT
        )
        entry.grid(
            column=col,
            row=row,
            columnspan=colspan,
            rowspan=rowspan,
            sticky=sticky
        )
        return entry

    def make_results(self, frame):
        text = tk.Text(frame, width=80, height=24, wrap='word')
        ys = ttk.Scrollbar(
            frame,
            orient='vertical',
            command=text.yview
        )
        text['yscrollcommand'] = ys.set
        text.grid(column=0, row=3, sticky=ALL)
        ys.grid(column=1, row=3, sticky=ENDS)
        return text

    def pad_kids(self, frame):
        for child in frame.winfo_children():
            child.grid_configure(padx=2, pady=2)

    def build_cd(self, main):
        self.config_simple_grid(main)
        self.cd_address = tk.StringVar()
        address_entry = self.make_entry(main, self.cd_address)
        cd_button = self.make_button(main, 'Decode', self.cd)
        self.cd_result = self.make_results(main)
        self.pad_kids(main)
        address_entry.focus_set()

    def build_ce(self, main):
        self.config_simple_grid(main)
        self.ce_char = tk.StringVar()
        char_entry = self.make_entry(main, self.ce_char)
        cd_button = self.make_button(main, 'Encode', self.ce)
        self.ce_result = self.make_results(main)
        self.pad_kids(main)

    def build_cl(self, frame):
        self.config_simple_grid(frame)
        cd_button = self.make_button(frame, 'List Character Sets', self.cl)
        self.cl_result = self.make_results(frame)
        self.pad_kids(frame)

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
            out += '\n'
            self.cd_result.insert('0.0', out)

        except ValueError:
            ...

    def ce(self, *args):
        try:
            codecs = cset.get_codecs()
            base = self.ce_char.get()
            results = cset.multiencode(base, (codec for codec in codecs))

            width = max(len(codec) for codec in codecs)
            out = ''
            for key in results:
                if b := results[key]:
                    c = ' '.join(f'{n:>02x}'.upper() for n in b)
                    out += f'{key:>{width}}: {c}\n'
            out += '\n'
            self.ce_result.insert('0.0', out)

        except ValueError:
            ...

    def cl(self, *args):
        codecs = cset.get_codecs()

        out = ''
        width = max(len(codec) for codec in codecs)
        for codec in codecs:
            descr = cset.get_codec_description(codec)
            row = make_description_row(codec, width, descr)
            out += row + '\n\n'
        out += '\n\n'
        self.cl_result.insert('0.0', out)


if __name__ == '__main__':
    root = tk.Tk()
    app = CharDecode(root)
    root.mainloop()
