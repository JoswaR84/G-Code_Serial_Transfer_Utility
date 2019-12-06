from tkinter import *
from fnmatch import fnmatch

import serial
import os

p3 = None
pw_set = 'muchtanks'
pw_check = None

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
                
        Label(self, text='Enter Password').pack()
        self.password = Entry(self, show="*")
        self.password.pack()        
        Button(self, text="Submit", command=check_password).pack()

class Upload(Page):
    def __init__(self, *args, **kwargs):
        Page.__init__(self, *args, **kwargs)
        self.name = 'upload'                
        
        def upload_files():
            upload_files = self.listbox.selection_get()
            print(upload_files)
        
        extensions = ('.GCD', '.NCC', '.NCD', '.NCI')        
        self.usb_files_list = []
        for root_dir, dirs, files in os.walk('/media/pi/'):
            for file in files:
                if file.endswith(extensions):
                    self.usb_files_list.append(file)  
                
        Label(self, text="Select files to upload!").pack(fill='x', side='top')
        self.listbox = Listbox(self, selectmode=MULTIPLE, yscrollcommand=True)
        self.listbox.pack(fill='both', side='top')
        for file in self.usb_files_list:
            self.listbox.insert(END, file)
            
        Button(self, text='Upload File', command=upload_files).pack(fill='x', side='bottom')

class Config(Page):
    def __init__(self, *args, **kwargs):
        Page.__init__(self, *args, **kwargs)
        self.name = 'config'
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=10)
        
        self.comm_port_list = []
        for file in os.listdir(path='/dev'):
            if fnmatch(file, 'ttyUSB*'):
                self.comm_port_list.append(file)       
        Label(self, text='Comm Port').grid(row=1, sticky=W)
        self.COMM_PORT_OPTIONS = self.comm_port_list
        self.comm_port_var = StringVar(self)
        self.comm_port_var.set(self.COMM_PORT_OPTIONS[0])
        OptionMenu(self, self.comm_port_var, *self.COMM_PORT_OPTIONS).grid(column=1, row=1, sticky=W+E)        

        Label(self, text='Baud Rate').grid(row=2, sticky=W)
        self.BAUD_OPTIONS = ['1200', '2400', '4800', '9600', '19200']
        self.baud_var = StringVar(self)
        self.baud_var.set(self.BAUD_OPTIONS[3])
        OptionMenu(self, self.baud_var, *self.BAUD_OPTIONS).grid(column=1, row=2, sticky=W+E)        

        Label(self, text='Data Bits').grid(row=3, sticky=W)
        self.DATA_BITS_OPTIONS = ['5', '6', '7', '8']
        self.data_bits_var = StringVar(self)
        self.data_bits_var.set(self.DATA_BITS_OPTIONS[2])
        OptionMenu(self, self.data_bits_var, *self.DATA_BITS_OPTIONS).grid(column=1, row=3, sticky=W+E)        

        Label(self, text='Parity').grid(row=4, sticky=W)
        self.PARITY_OPTIONS = ['none', 'even', 'odd', 'mark', 'space']
        self.parity_var = StringVar(self)
        self.parity_var.set(self.PARITY_OPTIONS[1])
        OptionMenu(self, self.parity_var, *self.PARITY_OPTIONS).grid(column=1, row=4, sticky=W+E)        

        Label(self, text='Stop Bits').grid(row=5, sticky=W)
        self.STOP_BITS_OPTIONS = ['1', '1.5', '2']
        self.stop_bits_var = StringVar(self)
        self.stop_bits_var.set(self.STOP_BITS_OPTIONS[0])
        OptionMenu(self, self.stop_bits_var, *self.STOP_BITS_OPTIONS).grid(column=1, row=5, sticky=W+E)

        Label(self, text='Flow Control Enabled').grid(row=6, sticky=W)
        self.flow_control_var = StringVar(value='True')
        Checkbutton(self, variable=self.flow_control_var, onvalue='True', offvalue='False').grid(column=1, row=6, sticky=W)

        Label(self, text='RTSCTS Enabled').grid(row=7, sticky=W)
        self.rtscts_var = StringVar(value='True')
        Checkbutton(self, variable=self.rtscts_var, onvalue='True', offvalue='False').grid(column=1, row=7, sticky=W)

        Label(self, text='DSRDTR Enabled').grid(row=8, sticky=W)
        self.dsrdtr_var = StringVar(value='True')
        Checkbutton(self, variable=self.dsrdtr_var, onvalue='True', offvalue='False').grid(column=1, row=8, sticky=W)

if __name__ == '__main__':
    root = Tk()
    main = MainView(root)
    main.pack(fill='both', expand=True)
    root.title('CommCraft')
    root.geometry('300x250')
    root.mainloop()
