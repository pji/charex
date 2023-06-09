"""
gui
~~~

A graphical user interface for :mod:`charex`.
"""
import tkinter as tk
from tkinter import ttk

from charex import charex as ch
from charex import cmds
from charex import charsets as cset
from charex import denormal as dn
from charex import escape as esc
from charex import normal as nl
from charex import util
from charex import shell as sh


# Constants.
ALL = (tk.N, tk.E, tk.W, tk.S)
SIDES = (tk.W, tk.E)
ENDS = (tk.N, tk.S)


# Application classes.
class Application:
    """The GUI for :mod:`charex`."""
    # Initialization.
    def __init__(self, root):
        # Configure the main window.
        self.root = root
        root.title('charex')
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)

        # Create the tab navigation and tabs.
        book = ttk.Notebook(root, padding='1 1 1 1')
        self.book = book
        book.grid(column=0, row=0, sticky=ALL)
        self.tabs = {}
        self.wake_focus = {}
        names = [
            name.split('_')[-1]
            for name in dir(self)
            if name.startswith('init_')
        ]
        for i, name in enumerate(names):
            frame = ttk.Frame(book, padding='3 3 12 12')
            book.add(frame, text=name)
            init = getattr(self, f'init_{name}')
            num = i + 1
            if num == 1:
                num = ''
            init(frame, num)
            self.tabs[i] = getattr(self, name)

        # Bind event handlers.
        root.bind('<Return>', self.handle_return)
        root.bind('<<NotebookTabChanged>>', self.handle_notebook_tab_changed)

    def init_cd(self, frame, num=None):
        """Initialize the "cd" tab.

        :param frame: The frame for the "cd" notebook tab.
        :return: None.
        :rtype: NoneType
        """
        self.cd_address = tk.StringVar()
        self.cd_result = self.make_results(frame)

        self.config_simple_grid(frame)
        address_entry = self.make_entry(frame, self.cd_address)
        cd_button = self.make_button(frame, 'Decode', self.cd)
        self.pad_kids(frame)
        address_entry.focus_set()
        self.wake_focus[f'!frame{num}'] = address_entry

    def init_ce(self, frame, num=None):
        self.ce_char = tk.StringVar()
        self.ce_result = self.make_results(frame)

        self.config_simple_grid(frame)
        char_entry = self.make_entry(frame, self.ce_char)
        cd_button = self.make_button(frame, 'Encode', self.ce)
        self.pad_kids(frame)
        self.wake_focus[f'!frame{num}'] = char_entry

    def init_cl(self, frame, num=None):
        self.cl_result = self.make_results(frame)

        self.config_simple_grid(frame)
        cl_button = self.make_button(frame, 'List Character Sets', self.cl)
        self.pad_kids(frame)

    def init_ct(self, frame, num=None):
        self.ct_base = tk.StringVar()
        self.ct_form = tk.StringVar()
        self.ct_maxdepth = tk.StringVar()
        self.ct_maxdepth.set('0')
        self.ct_result = self.make_results(frame, row=5, colspan=4)

        self.config_five_params_grid(frame)

        char_entry = self.make_entry(
            frame,
            self.ct_base,
            colspan=5
        )

        form_label = ttk.Label(frame, text='Form:', justify=tk.RIGHT)
        form_label.grid(column=0, row=2, columnspan=1, sticky=SIDES)
        form_combo = ttk.Combobox(frame, textvariable=self.ct_form)
        form_combo['values'] = nl.get_forms()
        form_combo.state(['readonly'])
        form_combo.grid(column=1, row=2, columnspan=1, sticky=SIDES)

        maxdepth_label = ttk.Label(frame, text='Max Depth:', justify=tk.RIGHT)
        maxdepth_label.grid(column=2, row=2, columnspan=1, sticky=SIDES)
        maxdepth_entry = self.make_entry(
            frame,
            self.ct_maxdepth,
            width=40,
            col=3,
            row=2,
            colspan=2
        )

        cd_button = self.make_button(
            frame,
            'Count Denormalizations',
            self.ct,
            row=4,
            colspan=5
        )
        self.pad_kids(frame)
        self.wake_focus[f'!frame{num}'] = char_entry

    def init_dn(self, frame, num=None):
        self.dn_base = tk.StringVar()
        self.dn_form = tk.StringVar()
        self.dn_maxdepth = tk.StringVar()
        self.dn_maxdepth.set('0')
        self.dn_random = tk.BooleanVar(value=False)
        self.dn_seed = tk.StringVar()
        self.dn_result = self.make_results(frame, row=5, colspan=4)

        self.config_five_params_grid(frame)

        char_entry = self.make_entry(
            frame,
            self.dn_base,
            colspan=5
        )

        form_label = ttk.Label(frame, text='Form:', justify=tk.RIGHT)
        form_label.grid(column=0, row=2, columnspan=1, sticky=SIDES)
        form_combo = ttk.Combobox(frame, textvariable=self.dn_form)
        form_combo['values'] = nl.get_forms()
        form_combo.state(['readonly'])
        form_combo.grid(column=1, row=2, columnspan=1, sticky=SIDES)

        maxdepth_label = ttk.Label(frame, text='Max Depth:', justify=tk.RIGHT)
        maxdepth_label.grid(column=2, row=2, columnspan=1, sticky=SIDES)
        maxdepth_entry = self.make_entry(
            frame,
            self.dn_maxdepth,
            width=40,
            col=3,
            row=2,
            colspan=2
        )

        random_label = ttk.Label(frame, text='Random:', justify=tk.RIGHT)
        random_label.grid(column=0, row=3, columnspan=1, sticky=SIDES)
        random_check = ttk.Checkbutton(
            frame,
            variable=self.dn_random,
            onvalue='True',
            offvalue='False'
        )
        random_check.grid(column=1, row=3, columnspan=1, sticky=SIDES)

        seed_label = ttk.Label(frame, text='Seed:', justify=tk.RIGHT)
        seed_label.grid(column=2, row=3, columnspan=1, sticky=SIDES)
        seed_entry = self.make_entry(
            frame,
            self.dn_seed,
            width=40,
            col=3,
            row=3,
            colspan=2
        )

        cd_button = self.make_button(
            frame,
            'Denormalize',
            self.dn,
            row=4,
            colspan=5
        )
        self.pad_kids(frame)
        self.wake_focus[f'!frame{num}'] = char_entry

    def init_dt(self, frame, num=None):
        """Initialize the "dt" tab.

        :param frame: The frame for the "dt" notebook tab.
        :return: None.
        :rtype: NoneType
        """
        self.dt_char = tk.StringVar()
        self.dt_result = self.make_results(frame)

        self.config_simple_grid(frame)
        address_entry = self.make_entry(frame, self.dt_char)
        cd_button = self.make_button(frame, 'Character Details', self.dt)
        self.pad_kids(frame)
        self.wake_focus[f'!frame{num}'] = address_entry

    def init_el(self, frame, num=None):
        self.el_result = self.make_results(frame)

        self.config_simple_grid(frame)
        el_button = self.make_button(frame, 'List Escape Schemes', self.el)
        self.pad_kids(frame)

    def init_es(self, frame, num=None):
        self.es_base = tk.StringVar()
        self.es_scheme = tk.StringVar()
        self.es_result = self.make_results(frame, row=5, colspan=4)

        self.config_five_params_grid(frame)

        char_entry = self.make_entry(
            frame,
            self.es_base,
            colspan=5
        )

        scheme_label = ttk.Label(frame, text='Scheme:', justify=tk.RIGHT)
        scheme_label.grid(column=0, row=2, columnspan=1, sticky=SIDES)
        scheme_combo = ttk.Combobox(frame, textvariable=self.es_scheme)
        scheme_combo['values'] = esc.get_schemes()
        scheme_combo.state(['readonly'])
        scheme_combo.grid(column=1, row=2, columnspan=4, sticky=SIDES)

        es_button = self.make_button(
            frame,
            'Escape',
            self.es,
            row=4,
            colspan=5
        )
        self.pad_kids(frame)
        self.wake_focus[f'!frame{num}'] = char_entry

    def init_fl(self, frame, num=None):
        self.fl_result = self.make_results(frame)

        self.config_simple_grid(frame)
        fl_button = self.make_button(
            frame,
            'List Normalization Forms',
            self.fl
        )
        self.pad_kids(frame)

    def init_nl(self, frame, num=None):
        self.nl_base = tk.StringVar()
        self.nl_form = tk.StringVar()
        self.nl_result = self.make_results(frame, row=5, colspan=4)

        self.config_five_params_grid(frame)

        char_entry = self.make_entry(
            frame,
            self.nl_base,
            colspan=5
        )

        form_label = ttk.Label(frame, text='Form:', justify=tk.RIGHT)
        form_label.grid(column=0, row=2, columnspan=1, sticky=SIDES)
        form_combo = ttk.Combobox(frame, textvariable=self.nl_form)
        form_combo['values'] = nl.get_forms()
        form_combo.state(['readonly'])
        form_combo.grid(column=1, row=2, columnspan=4, sticky=SIDES)

        cd_button = self.make_button(
            frame,
            'Normalize',
            self.nl,
            row=4,
            colspan=5
        )
        self.pad_kids(frame)
        self.wake_focus[f'!frame{num}'] = char_entry

    def init_pf(self, frame, num=None):
        self.pf_prop = tk.StringVar()
        self.pf_value = tk.StringVar()
        self.pf_insensitive = tk.BooleanVar(value=False)
        self.pf_regex = tk.BooleanVar(value=False)
        self.pf_result = self.make_results(frame, row=5, colspan=4)

        self.config_five_params_grid(frame)

        form_label = ttk.Label(frame, text='Property:', justify=tk.RIGHT)
        form_label.grid(column=0, row=0, columnspan=1, sticky=SIDES)
        self.pfprop_combo = ttk.Combobox(frame, textvariable=self.pf_prop)
        self.pfprop_combo['values'] = ch.get_properties()
        self.pfprop_combo.state(['readonly'])
        self.pfprop_combo.bind('<<ComboboxSelected>>', self.handle_pf_pfprop)
        self.pfprop_combo.grid(column=1, row=0, columnspan=4, sticky=SIDES)

        val_label = ttk.Label(frame, text='Value:', justify=tk.RIGHT)
        val_label.grid(column=0, row=1, columnspan=1, sticky=SIDES)
        self.pfval_combo = ttk.Combobox(frame, textvariable=self.pf_value)
        self.pfval_combo.grid(column=1, row=1, columnspan=4, sticky=SIDES)

        insensitive_label = ttk.Label(
            frame, text='Ignore Case:', justify=tk.RIGHT
        )
        insensitive_label.grid(column=0, row=3, columnspan=1, sticky=SIDES)
        insensitive_check = ttk.Checkbutton(
            frame,
            variable=self.pf_insensitive,
            onvalue='True',
            offvalue='False'
        )
        insensitive_check.grid(column=1, row=3, columnspan=1, sticky=SIDES)

        regex_label = ttk.Label(frame, text='Regex:', justify=tk.RIGHT)
        regex_label.grid(column=2, row=3, columnspan=1, sticky=SIDES)
        regex_check = ttk.Checkbutton(
            frame,
            variable=self.pf_regex,
            onvalue='True',
            offvalue='False'
        )
        regex_check.grid(column=3, row=3, columnspan=1, sticky=SIDES)

        pf_button = self.make_button(
            frame,
            'Filter by the Property Value',
            self.pf,
            row=4,
            colspan=5
        )
        self.pad_kids(frame)

    def init_up(self, frame, num=None):
        self.up_result = self.make_results(frame)

        self.config_simple_grid(frame)
        up_button = self.make_button(
            frame,
            'List Unicode Properties',
            self.up
        )
        self.pad_kids(frame)

    def init_uv(self, frame, num=None):
        self.uv_prop = tk.StringVar()
        self.uv_result = self.make_results(frame)

        self.config_simple_grid(frame)

        form_combo = ttk.Combobox(frame, textvariable=self.uv_prop)
        form_combo['values'] = ch.get_properties()
        form_combo.state(['readonly'])
        form_combo.grid(column=0, row=0, columnspan=2, sticky=SIDES)

        uv_button = self.make_button(
            frame,
            'List Values of Unicode Property',
            self.uv
        )
        self.pad_kids(frame)

    # Core commands.
    def cd(self, *args):
        try:
            self.cd_result.delete('0.0', 'end')
            address = self.cd_address.get()
            for line in cmds.cd(address):
                self.cd_result.insert('end', line + '\n')

        except ValueError:
            ...

    def ce(self, *args):
        try:
            self.ce_result.delete('0.0', 'end')
            base = self.ce_char.get()
            for line in cmds.ce(base):
                self.ce_result.insert('end', line + '\n')

        except ValueError:
            ...

    def cl(self, *args):
        self.cl_result.delete('0.0', 'end')
        for line in cmds.cl(True):
            self.cl_result.insert('end', line + '\n\n')

    def ct(self, *args):
        self.ct_result.delete('0.0', 'end')
        base = self.ct_base.get()
        form = self.ct_form.get()
        maxdepth = int(self.ct_maxdepth.get())
        line = cmds.ct(base, form, maxdepth)
        self.ct_result.insert('end', line + '\n\n')

    def dn(self, *args):
        self.dn_result.delete('0.0', 'end')
        base = self.dn_base.get()
        form = self.dn_form.get()
        maxdepth = int(self.dn_maxdepth.get())
        random = self.dn_random.get()
        seed_ = self.dn_seed.get()

        if not random:
            for line in dn.gen_denormalize(base, form, maxdepth):
                self.dn_result.insert('end', line + '\n')

        else:
            for line in dn.gen_random_denormalize(
                base,
                form,
                maxdepth,
                seed_
            ):
                self.dn_result.insert('end', line + '\n')

    def dt(self, *args):
        try:
            self.dt_result.delete('0.0', 'end')
            base = self.dt_char.get()
            for line in cmds.dt(base):
                self.dt_result.insert('end', line + '\n')

        except ValueError:
            ...

    def el(self, *args):
        self.el_result.delete('0.0', 'end')
        for line in cmds.el(True):
            self.el_result.insert('end', line + '\n\n')

    def es(self, *args):
        self.es_result.delete('0.0', 'end')
        base = self.es_base.get()
        scheme = self.es_scheme.get()
        line = cmds.es(base, scheme, 'utf8')
        self.es_result.insert('end', line)

    def fl(self, *args):
        self.fl_result.delete('0.0', 'end')
        for line in cmds.fl(True):
            self.fl_result.insert('end', line + '\n\n')

    def nl(self, *args):
        self.nl_result.delete('0.0', 'end')
        base = self.nl_base.get()
        form = self.nl_form.get()

        result = cmds.nl(form, base, True)
        self.nl_result.insert('end', result)

    def pf(self, *args):
        self.pf_result.delete('0.0', 'end')
        prop = self.pf_prop.get()
        value = self.pf_value.get()
        insensitive = self.pf_insensitive.get()
        regex = self.pf_regex.get()

        for line in cmds.pf(prop, value, insensitive, regex):
            self.pf_result.insert('end', line + '\n')

    def up(self, *args):
        self.up_result.delete('0.0', 'end')
        for line in cmds.up(True):
            self.up_result.insert('end', line + '\n\n')

    def uv(self, *args):
        prop = self.uv_prop.get()

        self.uv_result.delete('0.0', 'end')
        for line in cmds.uv(prop, True):
            self.uv_result.insert('end', line + '\n\n')

    # Event handlers.
    def handle_notebook_tab_changed(self, event):
        focus = self.root.focus_get()
        name = str(focus)
        frame = name.split('.')[-2]
        if frame in self.wake_focus:
            entry = self.wake_focus[frame]
            entry.focus_set()

    def handle_return(self, *args):
        tab_id = self.book.select()
        tab = self.book.index(tab_id)
        cmd = self.tabs[tab]
        cmd()

    def handle_pf_pfprop(self, event):
        prop = self.pf_prop.get()
        self.pfval_combo['values'] = ch.get_property_values(prop)

    # Grid configuration.
    def config_simple_grid(self, frame):
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=0)
        frame.rowconfigure(1, weight=0)
        frame.rowconfigure(2, weight=0)
        frame.rowconfigure(3, weight=1)

    def config_five_params_grid(self, frame):
        frame.columnconfigure(0, weight=0)
        frame.columnconfigure(1, weight=1)
        frame.columnconfigure(2, weight=0)
        frame.columnconfigure(3, weight=1)
        frame.columnconfigure(4, weight=0)
        frame.rowconfigure(1, weight=0)
        frame.rowconfigure(2, weight=0)
        frame.rowconfigure(3, weight=0)
        frame.rowconfigure(4, weight=0)
        frame.rowconfigure(5, weight=1)

    # Generic widget creation.
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

    def make_results(
        self,
        frame,
        row=3,
        colspan=1
    ):
        text = tk.Text(frame, width=80, height=24, wrap='word')
        ys = ttk.Scrollbar(
            frame,
            orient='vertical',
            command=text.yview
        )
        text['yscrollcommand'] = ys.set
        text.grid(column=0, row=row, columnspan=colspan, sticky=ALL)
        ys.grid(column=colspan, row=row, sticky=ENDS)
        return text

    # Generic frame configuration.
    def pad_kids(self, frame):
        for child in frame.winfo_children():
            child.grid_configure(padx=2, pady=4)


def main():
    root = tk.Tk()
    app = Application(root)
    root.mainloop()


if __name__ == '__main__':
    main()
