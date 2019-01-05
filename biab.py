from Tkinter import *
from touchscreen import TouchScreen

import tkFont
import sys


class BiabApp(object):
    ts = None

    def __init__(self, master, **kwargs):
        enable_ts = kwargs.get('touchscreen', False)
        self.master=master
        pad=3
        self._geom='200x200+0+0'
        master.geometry("{0}x{1}+0+0".format(
            master.winfo_screenwidth()-pad, master.winfo_screenheight()-pad))
        master.overrideredirect(True) # keyboard events don't work after this
        helv36 = tkFont.Font(family='Helvetica', size=36, weight='bold')

        b = Button(master, text="Quit", command=self.quit, width=10, height=2)
        b['font'] = helv36
        b.grid(row=0, column=0)
        if enable_ts:
            print("Enabling TouchScreen Support")
            self.ts = TouchScreen(master)


    def toggle_geom(self,event):
        geom=self.master.winfo_geometry()
        print(geom,self._geom)
        self.master.geometry(self._geom)
        self._geom=geom


    def quit(self):
        print("Exiting application")
	if self.ts:
            self.ts.quit()
        self.master.quit()
        sys.exit(0)
