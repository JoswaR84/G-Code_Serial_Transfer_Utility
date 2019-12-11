#!/usr/bin/env python3
# Command to import pyserial
# python -m pip install pyserial
# sudo apt install matchbox-keyboard
from comm_vars import *

from tkinter import *
from re import search
from fnmatch import fnmatch

import subprocess
import serial
import json
import os

class MainView(Frame):
    def __init__(self, *args, **kwargs):
        Frame.__init__(self, *args, **kwargs)
        self.upload_page = Upload(self)        
        self.password_page = Password(self)        
        self.config_page = Config(self)
        self.nocable_page = NoCable(self)

        def open_keyboard():
            # Opens Virtual Keyboard
            subprocess.Popen("matchbox-keyboard", shell=False)

        # MainView GUI
        buttonframe = Frame(self)
        container = Frame(self)
        buttonframe.pack(side='top', fill='x', expand=False)
        container.pack(side='top', fill='both', expand=True)

        self.upload_page.place(in_=container, x=0, y=0, relwidth=1, relheight=1)
        self.password_page.place(in_=container, x=0, y=0, relwidth=1, relheight=1)
        self.config_page.place(in_=container, x=0, y=0, relwidth=1, relheight=1)
        self.nocable_page.place(in_=container, x=0, y=0, relwidth=1, relheight=1)

        Button(buttonframe, text='Virtual Keyboard', command=open_keyboard, bg='lightblue').pack(side='top', fill='x', expand=1)
        Button(buttonframe, text='Upload', command=self.upload_page.check_lift, bg='lightblue').pack(side='left', fill='x', expand=1)
        Button(buttonframe, text='Config', command=self.password_page.check_lift, bg='lightblue').pack(side='right', fill='x', expand=1)
        
        self.upload_page.lift()
        self.upload_page.search.focus()

class Page(Frame):
    def __init__(self, *args, **kwargs):
        Frame.__init__(self, *args, **kwargs)
         
    def check_lift(self):
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
        Label(self, text='No Connection is Detected!').pack(pady=(150, 0))

class Password(Page):
    def __init__(self, *args, **kwargs):
        Page.__init__(self, *args, **kwargs)
        self.name = 'password'
        
        def check_password():                    
            if self.password.get() == pw_set:
                global pw_check
                pw_check = self.password.get()
                main.config_page.lift()  

        # Password GUI
        Label(self, text='Enter Password').pack(fill='x', padx=10, pady=(75, 0))
        self.password = Entry(self, show="*")
        self.password.pack(fill='x', padx=10, pady=5)
        Button(self, text="Submit", command=check_password).pack(fill='x', padx=10)

class Upload(Page):
    def __init__(self, *args, **kwargs):
        Page.__init__(self, *args, **kwargs)
        self.name = 'upload'                
        
        def upload_files():
            try:
                upload_files = self.listbox.selection_get()
                upload_files_list = upload_files.split('\n')
            except:
                upload_files = None
            # Connect to Serial Device
            serial_conn = serial.Serial()
            serial_conn.port = os.path.join('/dev', self.config_page.comm_port_var.get())            
            serial_conn.baudrate = self.config_page.baud_var.get()
            serial_conn.bytesize = self.config_page.data_bits_var.get()            
            if self.config_page.parity_var.get() == 'none':
                serial_conn.parity = 'N'
            if self.config_page.parity_var.get() == 'even':
                serial_conn.parity = 'E'
            if self.config_page.parity_var.get() == 'odd':
                serial_conn.parity = 'O'
            if self.config_page.parity_var.get() == 'mark':
                serial_conn.parity = 'M'
            if self.config_page.parity_var.get() == 'space':
                serial_conn.parity = 'S'
            serial_conn.stopbits = int(self.config_page.stop_bits_var.get())
            serial_conn.xonxoff = self.config_page.flow_control_var.get()
            serial_conn.rtscts = self.config_page.rtscts_var.get()
            serial_conn.dsrdtr = self.config_page.dsrdtr_var.get()
            serial_conn.open()
           # Upload files to Serial Device
            if upload_files:                
                for file in upload_files_list:
                    # need to reappend usb path
                    file.write(open(os.path.join(fanuc_file_location, filename).read))
                    # need to remove from upload list and add to uploaded list
            serial_conn.close()
        
        def search_uploads():
            search_term = self.search.get()
            search_items = self.listbox.get(0, END)
            self.listbox.delete(0, END)
            for item in search_items:
                if search(search_term, item, re.IGNORECASE):
                    self.listbox.insert(END, item)
        
        def clear_search():
            self.search.delete(0, 'end')
            self.listbox.delete(0, END)
            for file in self.usb_files_list:
                self.listbox.insert(END, file)
        
        # Query G-Code Files on Lauch, MainView.status_polling checks if app is running
        extensions = ext_list
        self.usb_files_list = []
        for dir_path, sub_dir, files in os.walk('/media/pi/'):
            for file in files:
                if file.endswith(extensions):
                    self.usb_files_list.append(file)
                
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
        Button(self, text='Search', command=search_uploads).grid(column=1, row=1, sticky=W+E)
        ## Third Column for Button Only
        Button(self, text='Clear', command=clear_search).grid(column=2, row=1, sticky=W+E)
        # Back to First Column
        self.listbox = Listbox(self, selectmode=MULTIPLE, yscrollcommand=True)
        self.listbox.config(height=13)
        self.listbox.grid(columnspan=3, row=2, padx=(10, 0), sticky=W+E+S+N)
        for file in self.usb_files_list:
            self.listbox.insert(END, file)
        Button(self, text='Upload Files', command=upload_files).grid(columnspan=3, row=3, padx=(10, 0), sticky=W+E+S)
        # Fourth Column
        Label(self, text='Uploaded Files').grid(column=3, row=0, padx=(15, 10), pady=(15, 0), sticky=S)
        self.upload_box = Listbox(self)
        self.upload_box.config(highlightthickness=0, height=16)
        self.upload_box.grid(column=3, row=1, rowspan=3, padx=(15, 10), sticky=W+E+S+N)

class Config(Page):
    def __init__(self, *args, **kwargs):
        Page.__init__(self, *args, **kwargs)
        self.name = 'config'
        
        def save_config():
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
        
        self.comm_port_list = []
        for file in os.listdir(path='/dev'):
            if fnmatch(file, 'ttyUSB*'):
                self.comm_port_list.append(file)       
        Label(self, text='Comm Port').grid(row=1, padx=(10, 0), pady=(15, 0), sticky=W)
        self.COMM_PORT_OPTIONS = self.comm_port_list
        self.comm_port_var = StringVar(self)        
        if self.comm_port_list:
            self.comm_port_var.set(self.COMM_PORT_OPTIONS[0])
            OptionMenu(self, self.comm_port_var, *self.COMM_PORT_OPTIONS).grid(column=1, row=1, padx=(0, 10), pady=(15, 0), sticky=W+E)
        else:
            OptionMenu(self, '', []).grid(column=1, row=1, sticky=W+E)

        Label(self, text='Baud Rate').grid(row=2, padx=(10, 0), sticky=W)
        self.BAUD_OPTIONS = [1200, 2400, 4800, 9600, 19200]
        self.baud_var = IntVar(self)
        config_baud = config_vars.get('baud')
        baud_indx = self.BAUD_OPTIONS.index(config_baud)
        self.baud_var.set(self.BAUD_OPTIONS[baud_indx])
        OptionMenu(self, self.baud_var, *self.BAUD_OPTIONS).grid(column=1, row=2, padx=(0, 10), sticky=W+E)        

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

        Label(self, text='Flow Control Enabled').grid(row=6, padx=(10, 0), pady=(10, 0), sticky=W)
        config_flow = config_vars.get('flow')
        self.flow_control_var = StringVar(value=config_flow)
        Checkbutton(self, variable=self.flow_control_var, onvalue=True, offvalue=False).grid(column=1, row=6, sticky=W)

        Label(self, text='RTSCTS Enabled').grid(row=7, padx=(10, 0), pady=(10, 0), sticky=W)
        config_rts = config_vars.get('rts')
        self.rtscts_var = StringVar(value=config_rts)
        Checkbutton(self, variable=self.rtscts_var, onvalue=True, offvalue=False).grid(column=1, row=7, sticky=W)

        Label(self, text='DSRDTR Enabled').grid(row=8, padx=(10, 0), pady=(10, 10), sticky=W)
        config_dsr = config_vars.get('dsr')
        self.dsrdtr_var = StringVar(value=config_dsr)
        Checkbutton(self, variable=self.dsrdtr_var, onvalue=True, offvalue=False).grid(column=1, row=8, sticky=W)
        
        Button(self, text='Save Config', command=save_config).grid(columnspan=2, row=9, padx=(10, 10),  sticky=S+W+E)

def password_polling():            
    # Deletes stored password after 10 minutes, relocking config
    pass

def status_polling():            
    # Check cable status, USB status, and Update self.config_page.usb_files_list
    print('I am here')
    print(main.config_page.comm_port_list)
    if not main.config_page.comm_port_list:
        print('i am in')
        main.self.nocable_page.lift()
    root.after(10000, status_polling)

# Main Event Loop
if __name__ == '__main__':
    root = Tk()
    main = MainView(root)
    main.pack(fill='both', expand=True)
    root.title('CommCraft')    
    root.geometry('600x355')
    root.after(10000, status_polling)
    root.mainloop()
