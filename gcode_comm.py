from tkinter import *
from fnmatch import fnmatch

import serial
import json
import os

p3 = None
pw_check = None
pw_set = 'muchtanks'
ext_list = ('.GCD', '.NCC', '.NCD', '.NCI')
config_file_loc = '/home/pi/Desktop/commcraft/config.txt'
fanuc_file_location = ''

class MainView(Frame):
    def __init__(self, *args, **kwargs):
        Frame.__init__(self, *args, **kwargs)        
        p1 = Upload(self)
        p2 = Password(self)
        global p3 
        p3 = Config(self)        

        buttonframe = Frame(self)
        container = Frame(self)
        buttonframe.pack(side='top', fill='x', expand=False)
        container.pack(side='top', fill='both', expand=True)

        p1.place(in_=container, x=0, y=0, relwidth=1, relheight=1)
        p2.place(in_=container, x=0, y=0, relwidth=1, relheight=1)
        p3.place(in_=container, x=0, y=0, relwidth=1, relheight=1)

        Button(buttonframe, text='Upload', command=p1.check_lift, bg='lightblue').pack(side='left', fill='x', expand=1)
        Button(buttonframe, text='Config', command=p2.check_lift, bg='lightblue').pack(side='right', fill='x', expand=1)

        p1.show()

class Page(Frame):
    def __init__(self, *args, **kwargs):
        Frame.__init__(self, *args, **kwargs)

    def show(self):
        self.lift()
         
    def check_lift(self):
        if self.name == 'upload':                           
            self.lift()
        elif pw_check == pw_set:
            p3.lift()
        elif self.name == 'password':     
            self.lift()    

class Password(Page):
    def __init__(self, *args, **kwargs):
        Page.__init__(self, *args, **kwargs)
        self.name = 'password'
        
        def check_password():                    
            if self.password.get() == pw_set:
                global pw_check
                pw_check = self.password.get()
                p3.lift()  
                
        Label(self, text='Enter Password').pack(fill='x')
        self.password = Entry(self, show="*")
        self.password.pack(fill='x')        
        Button(self, text="Submit", command=check_password).pack(fill='x')

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
#            serial_conn = serial.Serial()
#            serial_conn.baudrate = p3.baud_var.get()
#            serial_conn.bytesize = p3.data_bits_var.get()            
#            if p3.parity_var.get() == 'none':
#                serial_conn.parity = 'N'
#            if p3.parity_var.get() == 'even':
#                serial_conn.parity = 'E'
#            if p3.parity_var.get() == 'odd':
#                serial_conn.parity = 'O'
#            if p3.parity_var.get() == 'mark':
#                serial_conn.parity = 'M'
#            if p3.parity_var.get() == 'space':
#                serial_conn.parity = 'S'
#            serial_conn.stopbits = int(p3.stop_bits_var.get())
#            serial_conn.xonxoff = p3.flow_control_var.get()
#            serial_conn.rtscts = p3.rtscts_var.get()
#            serial_conn.dsrdtr = p3.dsrdtr_var.get()
#            serial_conn.open()
            # Upload files to Serial Device
            if upload_files:                
                for file in upload_files_list:
#                    extract_filename = file.split('/')
#                    filename = extract_filename[-1]
#                    file.write(open(os.path.join(fanuc_file_location, filename).read))
                    read_file = open(file, 'r')
                    print(read_file.read())
                    
#            serial_conn.close()
        
        extensions = ext_list      
        self.usb_files_list = []
        for dir_path, sub_dir, files in os.walk('/media/pi/'):
            for file in files:
                if file.endswith(extensions):
                    self.usb_files_list.append(os.path.join(dir_path, file))
                
        Label(self, text="Select files to upload!").pack(fill='x', side='top')
        self.listbox = Listbox(self, selectmode=MULTIPLE, yscrollcommand=True)
        self.listbox.pack(fill='both', side='top')
        for file in self.usb_files_list:
            self.listbox.insert(END, file)
            
        Button(self, text='Upload File', command=upload_files).pack(fill='x')

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
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=10)
        
        self.comm_port_list = []
        for file in os.listdir(path='/dev'):
            if fnmatch(file, 'ttyUSB*'):
                self.comm_port_list.append(file)       
        Label(self, text='Comm Port').grid(row=1, sticky=W)
        self.COMM_PORT_OPTIONS = self.comm_port_list
        self.comm_port_var = StringVar(self)        
        if self.comm_port_list:
            self.comm_port_var.set(self.COMM_PORT_OPTIONS[0])
            OptionMenu(self, self.comm_port_var, *self.COMM_PORT_OPTIONS).grid(column=1, row=1, sticky=W+E)
        else:
            OptionMenu(self, '', []).grid(column=1, row=1, sticky=W+E)

        Label(self, text='Baud Rate').grid(row=2, sticky=W)
        self.BAUD_OPTIONS = [1200, 2400, 4800, 9600, 19200]
        self.baud_var = IntVar(self)
        config_baud = config_vars.get('baud')
        baud_indx = self.BAUD_OPTIONS.index(config_baud)
        self.baud_var.set(self.BAUD_OPTIONS[baud_indx])
        OptionMenu(self, self.baud_var, *self.BAUD_OPTIONS).grid(column=1, row=2, sticky=W+E)        

        Label(self, text='Data Bits').grid(row=3, sticky=W)
        self.DATA_BITS_OPTIONS = [5, 6, 7, 8]
        self.data_bits_var = IntVar(self)
        config_bits = config_vars.get('bits')
        bits_indx = self.DATA_BITS_OPTIONS.index(config_bits)
        self.data_bits_var.set(self.DATA_BITS_OPTIONS[bits_indx])
        OptionMenu(self, self.data_bits_var, *self.DATA_BITS_OPTIONS).grid(column=1, row=3, sticky=W+E)        

        Label(self, text='Parity').grid(row=4, sticky=W)
        self.PARITY_OPTIONS = ['none', 'even', 'odd', 'mark', 'space']
        self.parity_var = StringVar(self)
        config_parity = config_vars.get('parity')
        parity_indx = self.PARITY_OPTIONS.index(config_parity)
        self.parity_var.set(self.PARITY_OPTIONS[parity_indx])
        OptionMenu(self, self.parity_var, *self.PARITY_OPTIONS).grid(column=1, row=4, sticky=W+E)        

        Label(self, text='Stop Bits').grid(row=5, sticky=W)
        self.STOP_BITS_OPTIONS = ['1', '1.5', '2']
        self.stop_bits_var = StringVar(self)
        config_stop_bit = config_vars.get('stop_bit')
        stop_bit_indx = self.STOP_BITS_OPTIONS.index(config_stop_bit)
        self.stop_bits_var.set(self.STOP_BITS_OPTIONS[stop_bit_indx])
        OptionMenu(self, self.stop_bits_var, *self.STOP_BITS_OPTIONS).grid(column=1, row=5, sticky=W+E)

        Label(self, text='Flow Control Enabled').grid(row=6, sticky=W)
        config_flow = config_vars.get('flow')
        self.flow_control_var = StringVar(value=config_flow)
        Checkbutton(self, variable=self.flow_control_var, onvalue=True, offvalue=False).grid(column=1, row=6, sticky=W)

        Label(self, text='RTSCTS Enabled').grid(row=7, sticky=W)
        config_rts = config_vars.get('rts')
        self.rtscts_var = StringVar(value=config_rts)
        Checkbutton(self, variable=self.rtscts_var, onvalue=True, offvalue=False).grid(column=1, row=7, sticky=W)

        Label(self, text='DSRDTR Enabled').grid(row=8, sticky=W)
        config_dsr = config_vars.get('dsr')
        self.dsrdtr_var = StringVar(value=config_dsr)
        Checkbutton(self, variable=self.dsrdtr_var, onvalue=True, offvalue=False).grid(column=1, row=8, sticky=W)
        
        Button(self, text='Save Config', command=save_config).grid(columnspan=2, row=9, sticky=S+W+E)

if __name__ == '__main__':
    root = Tk()
    main = MainView(root)
    main.pack(fill='both', expand=True)
    root.title('CommCraft')
    root.geometry('325x270')
    root.mainloop()
