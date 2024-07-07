import tkinter as tk
import tkinter.filedialog as fd
import tkinter.messagebox as tm
import os
from copy import deepcopy
from tkinter.ttk import Combobox, Scrollbar
from asg_library.intdata import get_parser
from asg_library.sternol.var_descriptions_parser import VarDescrParser
from myimages import snapshoter_image

APP_DIR = os.getcwd()


class Snapshoter(tk.Tk):
    BG_COLOR = '#CECDCD'

    ALL_GROUPS = {
        'Checks & CFW': [['C_', 'CFW_'], {}],
        'Individualizations': [['I_'], {}],
        'Manoeuvres': [['M_'], {}],
        'Local variables': [['L_', 'A_'], {}],
        'Orders & OFW': [['O_', 'OFW_'], {}],
        'Timers': [['T_'], {}],
        'Sequence indications': [['P_'], {}],
        'COS indications': [['S_'], {}],
        'Channels': [['Channels'], {}],
    }

    OBJS_PREFIXES = {
        'TS': 'SECTION',
        'PT': 'POINT',
        'SI': 'SIGNAL',
        'SH': 'SHSIGNAL',
        'RI': 'INDICATOR',
        'LB': 'LINEBLOCK',
        'ABTCE': 'ABTCE',
        'ABTC': 'ABTC_MSH',
        'FTC': 'FTC',
        'MU': 'MODULE',
        'SAUT': 'AB_R4',
    }

    def __init__(self):
        super().__init__()
        self.title('Snapshoter')
        self.geometry("1315x570+50+50")
        self.config(bg=self.BG_COLOR)
        self.resizable(True, True)
        self.maxsize(1315, 570)
        self.iconphoto(False, tk.PhotoImage(data=snapshoter_image))

        self.main_frame_top = tk.Frame()
        self.main_frame_bottom = tk.Frame()
        self.main_frame_top.pack(anchor='w')
        self.main_frame_bottom.pack(anchor='w')

        self.frame_log = tk.LabelFrame(self.main_frame_top, text='Лог',
                                       bg=self.BG_COLOR)
        self.frame_log.grid(row=0, column=0, sticky='NS')

        self.frame_options = tk.LabelFrame(self.main_frame_top,
                                           text='Опционально',
                                           bg=self.BG_COLOR)
        self.frame_options.grid(row=0, column=1, sticky='NS')

        self.frame_descriptions = tk.LabelFrame(self.main_frame_top,
                                                text='Описание переменных',
                                                bg=self.BG_COLOR)

        self.frame_variables = tk.Frame(self.main_frame_bottom,
                                        bg=self.BG_COLOR)
        self.frame_variables.pack(anchor='s')

        self.btn_select_log = tk.Button(self.frame_log, text='Выбрать лог',
                                        command=self.choose_log,
                                        width=10,
                                        height=2)
        self.lbl_file = tk.Label(self.frame_log, text='лог не выбран',
                                 state='disabled',
                                 height=2, activebackground=self.BG_COLOR)

        self.lbl_cycle = tk.Label(self.frame_log, text='Номер цикла:',
                                  height=2, background=self.BG_COLOR,
                                  font=('Arial', 10))

        self.cycle_input = Combobox(self.frame_log, width=15, justify=tk.RIGHT,
                                    font=('Arial', 10),
                                    state='disabled')
        self.cycle_input.bind('<<ComboboxSelected>>', self.obj_choose)

        self.lbl_obj = tk.Label(self.frame_log, text='Имя объекта:',
                                height=2, background=self.BG_COLOR,
                                font=('Arial', 10))

        self.obj_input = Combobox(self.frame_log, width=15, justify=tk.RIGHT,
                                  font=('Arial', 10), validate='key',
                                  state='disabled')

        self.btn_snapshot = tk.Button(self.frame_log, text='Snapshot!',
                                      font=('Arial', 10),
                                      command=self.snapshot, height=5)

        self.flag_cp = tk.BooleanVar()
        self.flag_cp.set(False)
        self.cbox_chpoint = tk.Checkbutton(self.frame_options,
                                           text='Учитывать лог нормализации',
                                           onvalue=True, offvalue=False,
                                           variable=self.flag_cp, height=2,
                                           background=self.BG_COLOR,
                                           activebackground=self.BG_COLOR)

        self.flag_ind = tk.BooleanVar()
        self.flag_ind.set(False)
        self.cbox_intdata = tk.Checkbutton(self.frame_options,
                                           text='Individualizations',
                                           onvalue=True, offvalue=False,
                                           variable=self.flag_ind,
                                           command=self.intdata_bt_activator,
                                           background=self.BG_COLOR,
                                           activebackground=self.BG_COLOR)

        self.btn_select_intdata = tk.Button(self.frame_options,
                                            text='IntData file',
                                            command=self.choose_intdata,
                                            width=10,
                                            height=2,
                                            state='disabled')

        self.flag_descr = tk.BooleanVar()
        self.flag_descr.set(False)
        self.cbox_vardescr = tk.Checkbutton(self.frame_options,
                                            text='Variable Descriptions',
                                            onvalue=True, offvalue=False,
                                            variable=self.flag_descr,
                                            command=self.vardescr_bt_activator,
                                            background=self.BG_COLOR,
                                            activebackground=self.BG_COLOR)

        self.btn_select_vardescr = tk.Button(self.frame_options,
                                             text='VarDescr. file',
                                             command=self.choose_vardescr,
                                             width=10,
                                             height=2,
                                             state='disabled')

        self.lbl_file.grid(row=0, column=0, padx=10, pady=10)
        self.btn_select_log.grid(row=0, column=1, padx=10, pady=10)
        self.lbl_cycle.grid(row=1, column=0, padx=10, pady=10)
        self.cycle_input.grid(row=1, column=1, padx=10, pady=10)
        self.lbl_obj.grid(row=2, column=0, padx=10, pady=10)
        self.obj_input.grid(row=2, column=1, padx=10, pady=10)
        self.btn_snapshot.grid(row=0, column=2, rowspan=3, padx=10, pady=10,
                               sticky='ns')

        self.cbox_chpoint.grid(row=0, column=0, padx=10, pady=10)
        self.cbox_intdata.grid(row=1, column=0, padx=10, pady=10, sticky='W')
        self.btn_select_intdata.grid(row=1, column=1, padx=10, pady=10,
                                     sticky='W')
        self.cbox_vardescr.grid(row=2, column=0, padx=10, pady=10, sticky='W')
        self.btn_select_vardescr.grid(row=2, column=1, padx=10, pady=10,
                                      sticky='W')

        self.log_path = None
        self.work_dir = None
        self.intdata_path = None
        self.vardescr_path = None
        self.log_cycles = None
        self.cycle = None
        self.obj = None
        self.parsed_data = None
        self.parsed_cp_data = None
        self.snap_data = None

        self.intdata_parser = get_parser()
        self.vardescr = VarDescrParser()

    def intdata_bt_activator(self):
        if self.btn_select_intdata['state'] == 'disabled':
            self.btn_select_intdata['state'] = 'active'
        else:
            self.btn_select_intdata['state'] = 'disabled'

    def vardescr_bt_activator(self):
        if self.btn_select_vardescr['state'] == 'disabled':
            self.btn_select_vardescr['state'] = 'active'
            self.frame_descriptions.grid(row=0, column=2, sticky='NS')
        else:
            self.btn_select_vardescr['state'] = 'disabled'
            for widget in self.frame_descriptions.winfo_children():
                widget.destroy()
            self.frame_descriptions.grid_forget()

    def obj_choose(self, event):
        self.obj_input['state'] = 'readonly'
        objects = []
        for cycle in self.parsed_data:
            for obj in self.parsed_data[cycle].keys():
                if obj not in objects:
                    objects.append(obj)
        objects.sort()
        self.obj_input['values'] = objects

    @staticmethod
    def log_parsing(log_path):
        with open(f'{log_path}', encoding='utf-8') as file:
            file_l = file.readlines()
        file_l = [line for line in file_l if line.startswith('! ILS')]
        log_dict = {}
        for line in file_l:
            cycle_num = line.split('#')[1].split('@')[0]
            if cycle_num not in log_dict:
                log_dict.update([(cycle_num, {})])
            if '=>' not in line:
                obj = line.split('#')[1].split()[1].split('.')[0]
                var = line.split('#')[1].split()[1].split('.')[1]
                value = line.split('#')[1].split()[3].split('(')[0]
            else:
                obj = line.split('#')[1].split()[3].split('.')[0]
                var = line.split('#')[1].split()[3].split('.')[1]
                value = line.split('#')[1].split()[4].split('(')[0]
            if obj not in log_dict[cycle_num]:
                log_dict[cycle_num].update([(obj, {var: value})])
            else:
                log_dict[cycle_num][obj].update([(var, value)])

        return log_dict

    def create_var_list_widgets(self):
        for i, var_group in enumerate(self.snap_data):
            tk.Label(self.frame_variables, text=f'{var_group}:', height=2,
                     background=self.BG_COLOR,
                     font=('Arial', 10)).grid(row=1, column=i, padx=10, pady=5,
                                              sticky='WE')
            lb = tk.Listbox(self.frame_variables, height=20, font=('Arial', 8))
            lb.bind('<<ListboxSelect>>', self.var_selected)
            lb.grid(row=2, column=i, padx=10, pady=0)
            for var in self.snap_data[var_group][1]:
                lb.insert(tk.END,
                          f'{var} = {self.snap_data[var_group][1][var]}')

    def var_selected(self, event):
        if self.vardescr_path and self.flag_descr.get():
            selected = event.widget.get(event.widget.curselection()[0])
            var = selected.split('=')[0].strip()
            value = selected.split('=')[1].strip()
            self.get_descriptions(var, value)

    def get_descriptions(self, var, value):
        obj_type = 'global'
        if '(' in var:
            var = var[:var.index('(')]
        else:
            for prefix in self.OBJS_PREFIXES:
                if self.obj.startswith(prefix):
                    obj_type = self.OBJS_PREFIXES[prefix]
        tk.Label(self.frame_descriptions, text=var, height=2,
                 background=self.BG_COLOR,
                 font=('Arial', 10)).grid(row=0, column=0, padx=10, pady=10,
                                          sticky='WE')
        long_descr = self.vardescr.get_long_descriptions(obj_type, var)
        value_descr = self.vardescr.get_value_descriptions(obj_type, var,
                                                           value)
        if not value_descr and 'PUMP' in value:
            value_descr = self.vardescr.get_value_descriptions(obj_type, var,
                                                               value.strip(
                                                                   'PUMP'))
        l_d = tk.Text(self.frame_descriptions, wrap='word', height=2,
                      background=self.BG_COLOR, width=83, relief='flat',
                      font=('Arial', 10))
        if long_descr:
            l_d.insert(1.0, long_descr)
        else:
            l_d.insert(1.0, 'Описание переменной не найдено')
        l_d.grid(row=1, column=0, padx=10, pady=10, sticky='W')
        ys_l_d = Scrollbar(self.frame_descriptions, orient='vertical',
                           command=l_d.yview)
        ys_l_d.grid(row=1, column=1, sticky='NS')
        l_d['yscrollcommand'] = ys_l_d.set
        v_d = tk.Text(self.frame_descriptions, wrap='word', height=2,
                      background=self.BG_COLOR, width=83, relief='flat',
                      font=('Arial', 10))
        if value_descr:
            v_d.insert(1.0, f'{value}: {value_descr}')
        else:
            v_d.insert(1.0,
                       f'{value}: Описание значения переменной не найдено')
        v_d.grid(row=2, column=0, padx=10, pady=10, sticky='W')
        ys_v_d = Scrollbar(self.frame_descriptions, orient='vertical',
                           command=v_d.yview)
        ys_v_d.grid(row=2, column=1, sticky='NS')
        v_d['yscrollcommand'] = ys_v_d.set

    def choose_log(self):
        filetypes = (('Лог', '*.log'),)
        self.log_path = fd.askopenfilename(title='Выберите лог',
                                           initialdir=APP_DIR,
                                           filetypes=filetypes)
        if self.log_path:
            self.lbl_file['text'] = f'{self.log_path.split("/")[-1]}'
            self.work_dir = '/'.join(self.log_path.split('/')[:-1])
            self.parsed_data = self.log_parsing(self.log_path)
            if self.parsed_data:
                self.lbl_file['state'] = 'active'
                self.cycle_input['state'] = 'readonly'
                self.log_cycles = [cycle for cycle in self.parsed_data]
                self.cycle_input['values'] = self.log_cycles
            else:
                self.lbl_file['text'] = 'лог не выбран'
                tm.showerror('Ошибка!', 'Неверный формат лога')

    def choose_intdata(self):
        filetypes = (('Interlocking_data', '*data'),)
        self.intdata_path = fd.askopenfilename(title='Выберите файл IntData',
                                               initialdir=self.work_dir,
                                               filetypes=filetypes)
        if self.intdata_path:
            self.intdata_parser.parse_data(intdata=self.intdata_path)

    def choose_vardescr(self):
        filetypes = (('variableDescriptions', 'variableDescriptions.txt'),)
        self.vardescr_path = fd.askopenfilename(
            title='Выберите файл variableDescriptions',
            initialdir=self.work_dir,
            filetypes=filetypes)
        if self.vardescr_path:
            self.vardescr.parse_data(vardescr_path=self.vardescr_path)

    def snapshot(self):
        self.snap_data = deepcopy(self.ALL_GROUPS)
        self.cycle = self.cycle_input.get()
        self.obj = self.obj_input.get()
        if self.cycle and self.obj:
            self.snap_log_data()
            if self.flag_cp.get():
                self.snap_cp_data()
            if self.flag_ind.get():
                self.get_ibits_values()
            else:
                self.snap_data.pop('Individualizations')
                for widget in self.frame_variables.winfo_children():
                    widget.destroy()
            self.sorting_variables()
            self.create_var_list_widgets()
        else:
            tm.showinfo('Внимание!', 'Нужно указать номер цикла и объект')

    def get_prev_cycles(self, parsed_data):
        prev_cycles = [c for c in parsed_data if c < self.cycle]
        prev_cycles.sort(reverse=True)
        return prev_cycles

    def get_variables_in_cycle(self, parsed_data, cycle):
        if cycle in parsed_data:
            if self.obj in parsed_data[cycle]:
                for variable in parsed_data[cycle][self.obj]:
                    value = parsed_data[cycle][self.obj][variable]
                    if value == '-1':
                        value = 'REST'
                    if variable.startswith('O_') and 'PUMP' not in value:
                        value = f'PUMP{value}'

                    if '(' in variable and (variable not in
                                            self.snap_data['Channels']
                                            [1].keys()):
                        self.snap_data['Channels'][1].update(
                            [(variable, value)])
                        continue
                    for group in self.snap_data:
                        for prefix in self.snap_data[group][0]:
                            if variable.startswith(prefix):
                                if variable not in (self.snap_data[group][1].
                                                    keys()):
                                    self.snap_data[group][1].update(
                                        [(variable, value)])
                                    break
        else:
            tm.showwarning('Цикл не найден',
                           'Указанного цикла нет в логе, сделан snapshot для '
                           'предыдущего найденного цикла')

    def sorting_variables(self):
        for group in self.snap_data:
            sorted_tuples = sorted(self.snap_data[group][1].items(),
                                   key=lambda item: item[0])
            self.snap_data[group][1] = {var: value for var, value in
                                        sorted_tuples}

    def snap_cp_data(self):
        try:
            cp_path = self.work_dir + '/scenario_0001.log'
            self.parsed_cp_data = self.log_parsing(cp_path)
            for cycle in self.get_prev_cycles(self.parsed_cp_data):
                self.get_variables_in_cycle(self.parsed_cp_data, cycle)
        except FileNotFoundError:
            tm.showwarning('Не найден файл',
                           'Не найден файл нормализации (scenario_0001.log).')
            self.flag_cp.set(False)

    def snap_log_data(self):
        self.get_variables_in_cycle(self.parsed_data, self.cycle)
        for cycle in self.get_prev_cycles(self.parsed_data):
            self.get_variables_in_cycle(self.parsed_data, cycle)

    def get_ibits_values(self):
        for ibit in self.intdata_parser.get_ibit_name_list(self.obj):
            self.snap_data['Individualizations'][1].update(
                [(ibit,
                  str(self.intdata_parser.get_ibit_value(self.obj, ibit)))])


if __name__ == '__main__':
    app = Snapshoter()
    app.mainloop()
