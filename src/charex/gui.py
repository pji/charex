"""
gui
~~~

A graphical user interface for :mod:`charex`.
"""
import tkinter as tk
from tkinter import ttk

from charex import charex as ch
from charex import charsets as cset
from charex import cmds
from charex import denormal as dn
from charex import escape as esc
from charex import normal as nl
from charex import shell as sh
from charex import util


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

        # Create the tab navigation.
        book = ttk.Notebook(root, padding='1 1 1 1')
        self.book = book
        book.grid(column=0, row=0, sticky=ALL)

        # Create and initialize each tab.
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

        :param frame: The frame for the tab.
        :param num: The number of the frame.
        :return: None.
        :rtype: NoneType
        """
        # The data for the interactive fields in the tab.
        self.cd_address = tk.StringVar()
        self.cd_result = self.make_results(frame)

        # Tab layout.
        widgets = [
            [True, 'entry', '', 2, self.cd_address],
            [False, 'button', 'decode', 2, self.cd],
        ]
        wake_widget = self.build_2x3_grid(frame, widgets)
        self.pad_kids(frame)
        self.wake_focus[f'!frame{num}'] = wake_widget

    def init_ce(self, frame, num=None):
        """Initialize the "ce" tab.

        :param frame: The frame for the tab.
        :param num: The number of the frame.
        :return: None.
        :rtype: NoneType
        """
        # The data for the interactive fields in the tab.
        self.ce_char = tk.StringVar()
        self.ce_result = self.make_results(frame)

        # Tab layout.
        widgets = [
            [True, 'entry', '', 2, self.ce_char],
            [False, 'button', 'encode', 2, self.ce],
        ]
        wake_widget = self.build_2x3_grid(frame, widgets)
        self.pad_kids(frame)
        self.wake_focus[f'!frame{num}'] = wake_widget

    def init_cl(self, frame, num=None):
        """Initialize the "cl" tab.

        :param frame: The frame for the tab.
        :param num: The number of the frame.
        :return: None.
        :rtype: NoneType
        """
        # The data for the interactive fields in the tab.
        self.cl_result = self.make_results(frame)

        # Tab layout.
        widgets = [
            [False, 'button', 'list character sets', 2, self.cl],
        ]
        _ = self.build_2x3_grid(frame, widgets)
        self.pad_kids(frame)

    def init_ct(self, frame, num=None):
        """Initialize the "ct" tab.

        :param frame: The frame for the tab.
        :param num: The number of the frame.
        :return: None.
        :rtype: NoneType
        """
        # The data for the interactive fields in the tab.
        self.ct_base = tk.StringVar()
        self.ct_form = tk.StringVar()
        self.ct_maxdepth = tk.StringVar()
        self.ct_maxdepth.set('0')
        self.ct_result = self.make_results(frame, row=5, colspan=4)

        # Tab layout.
        widgets = [
            [True, 'entry', '', 5, self.ct_base],
            [False, 'combo', 'form', 2, self.ct_form, nl.get_forms()],
            [False, 'entry', 'max depth', 3, self.ct_maxdepth],
            [False, 'button', 'count denomalizations', 5, self.ct],
        ]
        wake_widget = self.build_5x6_grid(frame, widgets)
        self.pad_kids(frame)
        self.wake_focus[f'!frame{num}'] = wake_widget

    def init_dn(self, frame, num=None):
        """Initialize the "dn" tab.

        :param frame: The frame for the tab.
        :param num: The number of the frame.
        :return: None.
        :rtype: NoneType
        """
        # The data for the interactive fields in the tab.
        self.dn_base = tk.StringVar()
        self.dn_form = tk.StringVar()
        self.dn_maxdepth = tk.StringVar()
        self.dn_maxdepth.set('0')
        self.dn_random = tk.BooleanVar(value=False)
        self.dn_seed = tk.StringVar()
        self.dn_result = self.make_results(frame, row=5, colspan=4)

        # Tab layout.
        widgets = [
            [True, 'entry', '', 5, self.dn_base],
            [False, 'combo', 'form', 2, self.dn_form, nl.get_forms()],
            [False, 'entry', 'max depth', 3, self.dn_maxdepth],
            [False, 'check', 'random', 2, self.dn_random],
            [False, 'entry', 'seed', 3, self.dn_seed],
            [False, 'button', 'count denomalizations', 5, self.ct],
        ]
        wake_widget = self.build_5x6_grid(frame, widgets)
        self.pad_kids(frame)
        self.wake_focus[f'!frame{num}'] = wake_widget

    def init_dt(self, frame, num=None):
        """Initialize the "dt" tab.

        :param frame: The frame for the "dt" notebook tab.
        :return: None.
        :rtype: NoneType
        """
        # The data for the interactive fields in the tab.
        self.dt_char = tk.StringVar()
        self.dt_result = self.make_results(frame)

        # Tab layout.
        widgets = [
            [True, 'entry', '', 2, self.dt_char],
            [False, 'button', 'character details', 2, self.dt],
        ]
        wake_widget = self.build_2x3_grid(frame, widgets)
        self.pad_kids(frame)
        self.wake_focus[f'!frame{num}'] = wake_widget

    def init_el(self, frame, num=None):
        """Initialize the "el" tab.

        :param frame: The frame for the tab.
        :param num: The number of the frame.
        :return: None.
        :rtype: NoneType
        """
        # The data for the interactive fields in the tab.
        self.el_result = self.make_results(frame)

        # Tab layout.
        widgets = [
            [False, 'button', 'list escape schemes', 2, self.el],
        ]
        wake_widget = self.build_2x3_grid(frame, widgets)
        self.pad_kids(frame)

    def init_es(self, frame, num=None):
        """Initialize the "es" tab.

        :param frame: The frame for the tab.
        :param num: The number of the frame.
        :return: None.
        :rtype: NoneType
        """
        # The data for the interactive fields in the tab.
        self.es_base = tk.StringVar()
        self.es_scheme = tk.StringVar()
        self.es_result = self.make_results(frame, row=5, colspan=4)

        # Tab layout.
        widgets = [
            [True, 'entry', '', 5, self.es_base],
            [False, 'combo', 'scheme', 5, self.es_scheme, esc.get_schemes()],
            [False, 'button', 'count denomalizations', 5, self.es],
        ]
        wake_widget = self.build_5x6_grid(frame, widgets)
        self.pad_kids(frame)
        self.wake_focus[f'!frame{num}'] = wake_widget

    def init_fl(self, frame, num=None):
        """Initialize the "fl" tab.

        :param frame: The frame for the tab.
        :param num: The number of the frame.
        :return: None.
        :rtype: NoneType
        """
        # The data for the interactive fields in the tab.
        self.fl_result = self.make_results(frame)

        # Tab layout.
        widgets = [
            [False, 'button', 'list normalization forms', 2, self.fl],
        ]
        wake_widget = self.build_2x3_grid(frame, widgets)
        self.pad_kids(frame)

    def init_nl(self, frame, num=None):
        """Initialize the "nl" tab.

        :param frame: The frame for the tab.
        :param num: The number of the frame.
        :return: None.
        :rtype: NoneType
        """
        # The data for the interactive fields in the tab.
        self.nl_base = tk.StringVar()
        self.nl_form = tk.StringVar()
        self.nl_result = self.make_results(frame, row=5, colspan=4)

        # Tab layout.
        widgets = [
            [True, 'entry', '', 5, self.nl_base],
            [False, 'combo', 'form', 5, self.nl_form, nl.get_forms()],
            [False, 'button', 'normalize', 5, self.nl],
        ]
        wake_widget = self.build_5x6_grid(frame, widgets)
        self.pad_kids(frame)
        self.wake_focus[f'!frame{num}'] = wake_widget

    def init_ns(self, frame, num=None):
        """Initialize the "ns" tab.

        :param frame: The frame for the tab.
        :param num: The number of the frame.
        :return: None.
        :rtype: NoneType
        """
        # The data for the interactive fields in the tab.
        self.ns_result = self.make_results(frame)

        # Tab layout.
        widgets = [
            [False, 'button', 'list named sequences', 2, self.ns],
        ]
        wake_widget = self.build_2x3_grid(frame, widgets)
        self.pad_kids(frame)

    def init_pf(self, frame, num=None):
        """Initialize the "pf" tab.

        :param frame: The frame for the tab.
        :param num: The number of the frame.
        :return: None.
        :rtype: NoneType
        """
        # The data for the interactive fields in the tab.
        self.pf_prop = tk.StringVar()
        self.pf_value = tk.StringVar()
        self.pf_insensitive = tk.BooleanVar(value=False)
        self.pf_regex = tk.BooleanVar(value=False)
        self.pf_result = self.make_results(frame, row=5, colspan=4)

        # Tab layout.
        # This is a little more complex because the property selected
        # changes the contents of the value combobox.
        self.build_5x6_grid(frame, [])
        self.pfprop_combo = self.add_combo(
            frame, 0, 1, 'property', 5, self.pf_prop, ch.get_properties()
        )
        self.pfprop_combo.bind('<<ComboboxSelected>>', self.handle_pf_pfprop)
        self.pfval_combo = self.add_combo(
            frame, 0, 2, 'value', 5, self.pf_value, []
        )
        self.add_check(frame, 0, 3, 'ignore case', 2, self.pf_insensitive)
        self.add_check(frame, 2, 3, 'regex', 2, self.pf_regex)
        self.add_button(frame, 0, 4, 'filter by property value', 5, self.pf)
        self.pad_kids(frame)
        self.wake_focus[f'!frame{num}'] = self.pfprop_combo

    def init_sv(self, frame, num=None):
        """Initialize the "sv" tab.

        :param frame: The frame for the tab.
        :param num: The number of the frame.
        :return: None.
        :rtype: NoneType
        """
        # The data for the interactive fields in the tab.
        self.sv_result = self.make_results(frame)

        # Tab layout.
        widgets = [
            [True, 'button', 'list standardized variants', 2, self.sv],
        ]
        wake_widget = self.build_2x3_grid(frame, widgets)
        self.pad_kids(frame)

    def init_up(self, frame, num=None):
        """Initialize the "up" tab.

        :param frame: The frame for the tab.
        :param num: The number of the frame.
        :return: None.
        :rtype: NoneType
        """
        # The data for the interactive fields in the tab.
        self.up_result = self.make_results(frame)

        # Tab layout.
        widgets = [
            [False, 'button', 'list unicode properties', 2, self.up],
        ]
        wake_widget = self.build_2x3_grid(frame, widgets)
        self.pad_kids(frame)

    def init_uv(self, frame, num=None):
        """Initialize the "up" tab.

        :param frame: The frame for the tab.
        :param num: The number of the frame.
        :return: None.
        :rtype: NoneType
        """
        # The data for the interactive fields in the tab.
        self.uv_prop = tk.StringVar()
        self.uv_result = self.make_results(frame)

        # Tab layout.
        widgets = [
            [True, 'combo', '', 2, self.uv_prop, ch.get_properties()],
            [False, 'button', 'list values of unicode property', 2, self.uv],
        ]
        wake_widget = self.build_2x3_grid(frame, widgets)
        self.pad_kids(frame)
        self.wake_focus[f'!frame{num}'] = wake_widget

    # Layout methods.
    def add_button(self, frame, col, row, name, span, cmd):
        """Add a button widget to the frame.

        :param frame: The frame to add the button to.
        :param col: The leftmost column containing the button.
        :param row: The row containing the button.
        :param name: The label of the button.
        :param span: The number of columns the button spans.
        :param cmd: The method to run when the button is pressed.
        :return: The button as a :class:`tkinter.ttk.Button`.
        :rtype: tkinter.ttk.Button
        """
        name = name.title()
        button = ttk.Button(frame, text=name, command=cmd)
        button.grid(
            column=col,
            row=row,
            columnspan=span,
            sticky=SIDES
        )
        return button

    def add_check(self, frame, col, row, name, span, value):
        """Add a checkbox widget to the frame.

        :param frame: The frame to add the button to.
        :param col: The leftmost column containing the button.
        :param row: The row containing the button.
        :param name: The label of the button.
        :param span: The number of columns the button spans.
        :param value: The attribute to store the value of the checkbox.
        :return: The button as a :class:`tkinter.ttk.Checkbutton`.
        :rtype: tkinter.ttk.Checkbutton
        """
        name = name.title()
        label = ttk.Label(frame, text=f'{name}:', justify=tk.RIGHT)
        label.grid(column=col, row=row, columnspan=1, sticky=tk.E)
        check = ttk.Checkbutton(
            frame,
            variable=value,
            onvalue='True',
            offvalue='False'
        )
        check.grid(
            column=col + 1, row=row, columnspan=span, sticky=SIDES
        )
        return check

    def add_combo(self, frame, col, row, name, span, value, options):
        """Add a combobox widget to the frame.

        :param frame: The frame to add the button to.
        :param col: The leftmost column containing the button.
        :param row: The row containing the button.
        :param name: The label of the button. If this is an empty
            string, no label will be added.
        :param span: The number of columns the button spans.
        :param value: The attribute to store the value of the combobox.
        :param options: The list of options for the combobox.
        :return: The button as a :class:`tkinter.ttk.Combobox`.
        :rtype: tkinter.ttk.Combobox
        """
        if name:
            name = name.title()
            label = ttk.Label(frame, text=f'{name}:', justify=tk.RIGHT)
            label.grid(column=col, row=row, columnspan=1, sticky=tk.E)
            col += 1
            span -= 1
        combo = ttk.Combobox(frame, textvariable=value)
        combo['values'] = options
        combo.state(['readonly'])
        combo.grid(column=col, row=row, columnspan=span, sticky=SIDES)
        return combo

    def add_entry(self, frame, col, row, name, span, value):
        """Add a text field widget to the frame.

        :param frame: The frame to add the button to.
        :param col: The leftmost column containing the button.
        :param row: The row containing the button.
        :param name: The label of the button. If this is an empty
            string, no label will be added.
        :param span: The number of columns the button spans.
        :param value: The attribute to store the value of the field.
        :return: The button as a :class:`tkinter.ttk.Entry`.
        :rtype: tkinter.ttk.Entry
        """
        if name:
            name = name.title()
            label = ttk.Label(frame, text=f'{name}:', justify=tk.RIGHT)
            label.grid(column=col, row=row, columnspan=1, sticky=tk.E)
            col += 1
            span -= 1
        entry = ttk.Entry(
            frame,
            textvariable=value,
            justify=tk.RIGHT
        )
        entry.grid(
            column=col,
            row=row,
            columnspan=span,
            sticky=SIDES
        )
        return entry

    def build_2x3_grid(self, frame, widgets):
        """Populate the tab with a 2x3 grid of widgets.

        Note: The scrollbar of the results requires its own column,
        so this is effectively a 1x3 grid for the placement of
        widgets. You just need to remember that each widget actually
        needs a span of two.

        :param frame: The frame to build the grid on.
        :param widgets: The parameters for the widgets to add to
            the grid.
        :return: The widget that should be highlighted when the tab
            is selected or `None`.
        :rtype: Any
        """
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=0)
        frame.rowconfigure(1, weight=0)
        frame.rowconfigure(2, weight=0)
        frame.rowconfigure(3, weight=1)
        cols, rows = 2, 4
        return self.build_widgets(frame, cols, rows, widgets)

    def build_5x6_grid(self, frame, widgets):
        """Populate the tab with a 5x6 grid of widgets.

        Note: The scrollbar of the results requires its own column,
        so this is effectively a 4x6 grid for the placement of
        widgets. You just need to remember that each widget actually
        needs a wider span to account for the last column.

        :param frame: The frame to build the grid on.
        :param widgets: The parameters for the widgets to add to
            the grid.
        :return: The widget that should be highlighted when the tab
            is selected or `None`.
        :rtype: Any
        """
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
        cols, rows = 5, 6
        return self.build_widgets(frame, cols, rows, widgets)

    def build_widgets(self, frame, cols, rows, widgets):
        """Populate the frame with widgets."""
        col, row = 0, 1
        wake_widget = None
        for widget in widgets:
            wake, kind, name, span, *params = widget
            fn = getattr(self, f'add_{kind}')
            obj = fn(frame, col, row, name, span, *params)
            if wake:
                wake_widget = obj
            col += span
            if col >= cols:
                col = 0
                row += 1
        return wake_widget

    def make_results(self, frame, row=3, colspan=1):
        """Make the results field for a tab."""
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

    def pad_kids(self, frame):
        """Even out the padding between the widgets on a tab."""
        for child in frame.winfo_children():
            child.grid_configure(padx=2, pady=4)

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

    def ns(self, *args):
        self.ns_result.delete('0.0', 'end')
        for line in cmds.ns(False):
            self.ns_result.insert('end', line + '\n')

    def pf(self, *args):
        self.pf_result.delete('0.0', 'end')
        prop = self.pf_prop.get()
        value = self.pf_value.get()
        insensitive = self.pf_insensitive.get()
        regex = self.pf_regex.get()

        for line in cmds.pf(prop, value, insensitive, regex):
            self.pf_result.insert('end', line + '\n')

    def sv(self, *args):
        self.sv_result.delete('0.0', 'end')
        for line in cmds.sv(False):
            self.sv_result.insert('end', line + '\n')

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
        """Set the input focus when switching between tabs."""
        focus = self.root.focus_get()
        name = str(focus)
        frame = name.split('.')[-2]
        if frame in self.wake_focus:
            entry = self.wake_focus[frame]
            entry.focus_set()

    def handle_return(self, *args):
        """Execute the command when hitting return."""
        tab_id = self.book.select()
        tab = self.book.index(tab_id)
        cmd = self.tabs[tab]
        cmd()

    def handle_pf_pfprop(self, event):
        """Populate the property values list when selecting a property
        in the "pf" tab.
        """
        prop = self.pf_prop.get()
        self.pfval_combo['values'] = ch.get_property_values(prop)


def main():
    root = tk.Tk()
    app = Application(root)
    root.mainloop()
