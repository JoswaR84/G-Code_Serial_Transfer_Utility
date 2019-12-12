#!/usr/bin/env python3
# Installed Modules & Software
# python -m pip install pyserial
# sudo apt install matchbox-keyboard

from comm_vars import *
from tkinter import *
from re import search

import subprocess
import serial
import json
import os

class MainView(Frame):
    def __init__(self, *args, **kwargs):
        Frame.__init__(self, *args, **kwargs)
        # Instantiate Other Class Pages
        self.upload_page = Upload(self)        
        self.password_page = Password(self)        
        self.config_page = Config(self)
        self.nocable_page = NoCable(self)

        # MainView GUI
        self.buttonframe = Frame(self)
        self.container = Frame(self)
        self.buttonframe.pack(side='top', fill='x', expand=False)
        self.container.pack(side='top', fill='both', expand=True)

        self.upload_page.place(in_=self.container, x=0, y=0, relwidth=1, relheight=1)
        self.password_page.place(in_=self.container, x=0, y=0, relwidth=1, relheight=1)
        self.config_page.place(in_=self.container, x=0, y=0, relwidth=1, relheight=1)
        self.nocable_page.place(in_=self.container, x=0, y=0, relwidth=1, relheight=1)

        self.keyboard_button = Button(self.buttonframe, text='Virtual Keyboard', command=self.open_keyboard, bg='lightblue')
        self.keyboard_button.pack(side='top', fill='x', expand=1)
        self.upload_button = Button(self.buttonframe, text='Upload', command=self.upload_page.check_lift, bg='lightblue')
        self.upload_button.pack(side='left', fill='x', expand=1)
        self.config_button = Button(self.buttonframe, text='Config', command=self.password_page.check_lift, bg='lightblue')
        self.config_button.pack(side='right', fill='x', expand=1)
        
        self.upload_page.lift()
        self.upload_page.search.focus()
        
    def open_keyboard(self):
        '''Opens Virtual Keyboard'''
        subprocess.Popen("matchbox-keyboard", shell=False)

    def status_polling(self):            
        '''Check cable status, USB status, and Update self.config_page.usb_files_list'''
        print('loop')
        main.upload_page.get_usb_files()        
        if not main.upload_page.search.get() and not main.upload_page.listbox.curselection():
            main.upload_page.set_reset_uploads()
        main.nocable_page.check_cable()        
        global pw_check
        if pw_check == pw_set:            
            pw_check = None
            main.password_page.password.delete(0, END)
        main.after(10000, self.status_polling)

class Page(Frame):
    def __init__(self, *args, **kwargs):
        Frame.__init__(self, *args, **kwargs)
         
    def check_lift(self):
        '''Lifts Frames'''
        if self.name == 'upload':                           
            self.lift()
            self.search.focus()
        elif pw_check == pw_set:
            main.config_page.lift()
        elif self.name == 'password':     
            self.lift()
            self.password.focus()

class NoCable(Page):
    def __init__(self, *args, **kwargs):
        Page.__init__(self, *args, **kwargs)
        self.name = 'nocable'
        
        # NoCable GUI
        Label(self, text='No Connection is Detected!').pack(pady=(100, 0))
        
    def check_cable(self):        
        if os.path.exists('/dev/ttyUSB0'):
            self.lower()
            main.keyboard_button.config(state='normal')
            main.upload_button.config(state='normal')
            main.config_button.config(state='normal')
        else:
            self.lift()
            main.keyboard_button.config(state='disabled')
            main.upload_button.config(state='disabled')
            main.config_button.config(state='disabled')
            
class Password(Page):
    def __init__(self, *args, **kwargs):
        Page.__init__(self, *args, **kwargs)
        self.name = 'password'

        # Password GUI
        Label(self, text='Enter Password').pack(fill='x', padx=10, pady=(60, 0))
        self.password = Entry(self, show="*")
        self.password.pack(fill='x', padx=10, pady=5)
        Button(self, text="Submit", command=self.check_password).pack(side= TOP, fill='x', padx=10)

    def check_password(self):
        '''Check Password and Return Config'''
        if self.password.get() == pw_set:
            global pw_check
            pw_check = self.password.get()
            main.config_page.lift()
        else:
            self.pw_notice = Label(main.password_page, text='Password Incorrect', fg='red')
            self.pw_notice.place(x=238, y=35)
            self.pw_notice.after(3000, self.clear_pw_notice)

    def clear_pw_notice(self):
        self.pw_notice.destroy()
        self.password.delete(0, END)

class Upload(Page):
    def __init__(self, *args, **kwargs):
        Page.__init__(self, *args, **kwargs)
        self.name = 'upload'
        self.usb_files_list = []
        self.usb_files_path_list = []

        # Upload GUI
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.grid_columnconfigure(3, weight=1)

        # First Column
        Label(self, text='Select for Upload').grid(columnspan=3, row=0, padx=(10, 0), pady=(15, 0), sticky=S)
        self.search = Entry(self)
        self.search.grid(column=0, row=1, padx=(10, 0), sticky=W+E)
        ## Second Column for Button Only
        Button(self, text='Search', command=self.search_uploads).grid(column=1, row=1, sticky=W+E)
        ## Third Column for Button Only
        Button(self, text='Clear', command=self.set_reset_uploads).grid(column=2, row=1, sticky=W+E)
        # Back to First Column
        self.listbox = Listbox(self, selectmode=MULTIPLE, yscrollcommand=True)
        self.listbox.grid(columnspan=3, row=2, padx=(10, 0), sticky=W+E+S+N)
        Button(self, text='Upload Files', command=self.upload_files).grid(columnspan=3, row=3, padx=(10, 0), sticky=W+E+S)
        # Fourth Column
        Label(self, text='Uploaded Files').grid(column=3, row=0, padx=(15, 10), pady=(15, 0), sticky=S)
        self.upload_box = Listbox(self)
        self.upload_box.config(highlightthickness=0)
        self.upload_box.grid(column=3, row=1, rowspan=2, padx=(15, 10), sticky=W+E+S+N)
        self.clear_uploaded_buttton = Button(self, text='Clear Uploaded', command=self.clear_uploaded)
        self.clear_uploaded_buttton.grid(column=3, row=3, padx=(15, 10),sticky=W+E+S+N)

    def get_usb_files(self):
        '''Query G-Code Files on USB'''
        for dir_path, sub_dir, files in os.walk('/media/pi/'):
            for file in files:
                if file not in self.usb_files_list and file.endswith(ext_list):
                    self.usb_files_list.append(file)
                    self.usb_files_path_list.append(os.path.join(dir_path, file))

    def set_reset_uploads(self):
        '''Set/Reset Upload Listbox'''
        self.search.delete(0, END)
        self.listbox.delete(0, END)
        for file in self.usb_files_list:
            self.listbox.insert(END, file)

    def search_uploads(self):
        '''Search and Return Matching Files'''
        search_term = self.search.get()
        search_items = self.listbox.get(0, END)
        self.listbox.delete(0, END)
        for item in search_items:
            if search(search_term, item, re.IGNORECASE):
                self.listbox.insert(END, item)

    def upload_files(self):
        '''Upload selected files'''
        try:
            upload_files = self.listbox.selection_get()
            upload_files_list = upload_files.split('\n')
        except:
            upload_files = None
        # Connect to Serial Device
        serial_conn = serial.Serial()
        serial_conn.port = '/dev/ttyUSB0'
        serial_conn.baudrate = main.config_page.baud_var.get()
        serial_conn.bytesize = main.config_page.data_bits_var.get()
        if main.config_page.parity_var.get() == 'none':
            serial_conn.parity = 'N'
        if main.config_page.parity_var.get() == 'even':
            serial_conn.parity = 'E'
        if main.config_page.parity_var.get() == 'odd':
            serial_conn.parity = 'O'
        if main.config_page.parity_var.get() == 'mark':
            serial_conn.parity = 'M'
        if main.config_page.parity_var.get() == 'space':
            serial_conn.parity = 'S'
        serial_conn.stopbits = int(main.config_page.stop_bits_var.get())
        serial_conn.xonxoff = main.config_page.flow_control_var.get()
        serial_conn.rtscts = main.config_page.rtscts_var.get()
        serial_conn.dsrdtr = main.config_page.dsrdtr_var.get()
        serial_conn.open()
        # Upload files to Serial Device
        if upload_files:
            for file in upload_files_list:
                for path in self.usb_files_path_list:
                    if file in path and file not in self.upload_box.get(0, END):
                        self.upload_box.insert(END, file)
                        read_file = open(path, 'rb').read()   
                        serial_conn.write(read_file)
        # Close Serial Connection
        serial_conn.close()

    def clear_uploaded(self):
        self.upload_box.delete(0, END)

class Config(Page):
    def __init__(self, *args, **kwargs):
        Page.__init__(self, *args, **kwargs)
        self.name = 'config'
        self.comm_port_list = []

        # Load Vars from config.txt
        try:
            config_file = open(config_file_loc, 'r')
            config_vars_str = config_file.readline()
            config_vars = json.loads(config_vars_str)
        except:
            config_vars = {'baud': 9600, 'bits': 7, 'parity': 'even',
                           'stop_bit': '1', 'flow': True, 'rts': True, 'dsr': True}

        # Config GUI
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=10)

        Label(self, text='Baud Rate').grid(row=2, padx=(10, 0), pady=(15, 0), sticky=W)
        self.BAUD_OPTIONS = [1200, 2400, 4800, 9600, 19200]
        self.baud_var = IntVar(self)
        config_baud = config_vars.get('baud')
        baud_indx = self.BAUD_OPTIONS.index(config_baud)
        self.baud_var.set(self.BAUD_OPTIONS[baud_indx])
        OptionMenu(self, self.baud_var, *self.BAUD_OPTIONS).grid(column=1, row=2, padx=(0, 10), pady=(15, 0), sticky=W+E)

        Label(self, text='Data Bits').grid(row=3, padx=(10, 0), sticky=W)
        self.DATA_BITS_OPTIONS = [5, 6, 7, 8]
        self.data_bits_var = IntVar(self)
        config_bits = config_vars.get('bits')
        bits_indx = self.DATA_BITS_OPTIONS.index(config_bits)
        self.data_bits_var.set(self.DATA_BITS_OPTIONS[bits_indx])
        OptionMenu(self, self.data_bits_var, *self.DATA_BITS_OPTIONS).grid(column=1, row=3, padx=(0, 10), sticky=W+E)

        Label(self, text='Parity').grid(row=4, padx=(10, 0), sticky=W)
        self.PARITY_OPTIONS = ['none', 'even', 'odd', 'mark', 'space']
        self.parity_var = StringVar(self)
        config_parity = config_vars.get('parity')
        parity_indx = self.PARITY_OPTIONS.index(config_parity)
        self.parity_var.set(self.PARITY_OPTIONS[parity_indx])
        OptionMenu(self, self.parity_var, *self.PARITY_OPTIONS).grid(column=1, row=4, padx=(0, 10), sticky=W+E)

        Label(self, text='Stop Bits').grid(row=5, padx=(10, 0), sticky=W)
        self.STOP_BITS_OPTIONS = ['1', '1.5', '2']
        self.stop_bits_var = StringVar(self)
        config_stop_bit = config_vars.get('stop_bit')
        stop_bit_indx = self.STOP_BITS_OPTIONS.index(config_stop_bit)
        self.stop_bits_var.set(self.STOP_BITS_OPTIONS[stop_bit_indx])
        OptionMenu(self, self.stop_bits_var, *self.STOP_BITS_OPTIONS).grid(column=1, row=5, padx=(0, 10), sticky=W+E)

        Label(self, text='Flow Control Enabled').grid(row=6, padx=(10, 0), pady=(5, 0), sticky=W)
        config_flow = config_vars.get('flow')
        self.flow_control_var = StringVar(value=config_flow)
        Checkbutton(self, variable=self.flow_control_var, onvalue=True, offvalue=False).grid(column=1, row=6, sticky=W)

        Label(self, text='RTSCTS Enabled').grid(row=7, padx=(10, 0), pady=(5, 0), sticky=W)
        config_rts = config_vars.get('rts')
        self.rtscts_var = StringVar(value=config_rts)
        Checkbutton(self, variable=self.rtscts_var, onvalue=True, offvalue=False).grid(column=1, row=7, sticky=W)

        Label(self, text='DSRDTR Enabled').grid(row=8, padx=(10, 0), pady=(5, 10), sticky=W)
        config_dsr = config_vars.get('dsr')
        self.dsrdtr_var = StringVar(value=config_dsr)
        Checkbutton(self, variable=self.dsrdtr_var, onvalue=True, offvalue=False).grid(column=1, row=8, sticky=W)

        Button(self, text='Save Config', command=self.save_config).grid(columnspan=2, row=9, padx=(10, 10),  sticky=S+W+E)
        
    def save_config(self):
        '''Save Config to File, Loads on Launch'''
        baud = self.baud_var.get()
        bits = self.data_bits_var.get()
        parity = self.parity_var.get()
        stop_bit = self.stop_bits_var.get()
        flow = self.flow_control_var.get()
        rts = self.rtscts_var.get()
        dsr = self.dsrdtr_var.get()
        var_dict = {'baud': baud, 'bits': bits, 'parity': parity,
                    'stop_bit': stop_bit, 'flow': flow, 'rts': rts, 'dsr': dsr}
        var_dict_str = json.dumps(var_dict)
        config_file = open(config_file_loc, 'w')
        config_file.write(var_dict_str)
        config_file.close()

# Main Event Loop
if __name__ == '__main__':
    root = Tk()
    main = MainView(root)
    main.pack(fill='both', expand=True)
    main.after(0, main.status_polling)
    root.title('CommCraft')
    root.geometry('600x320')
    root.mainloop()
