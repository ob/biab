from Tkinter import *

import os
import fcntl
import threading
import time
import select
import struct


class TouchScreen(object):
    calib_file = "/etc/pointercal"
    tp_dev = "/dev/hidraw0"


    def __init__(self, master, **kwargs):
        self.exiting = False
        self.master = master
        t = threading.Thread(target=self.poll)
        t.start()


    def quit(self):
        self.exiting = True


    def read_ts_calibration(self):
        # a1..a7 are touch panel calibration coefficients
        a1=1 #0
        a2=0 #1
        a3=0 #2
        a4=0 #3
        a5=1 #4
        a6=0 #5
        a7=1 #6
        # scx, scy are screen dimensions at moment of performing calibration
        scx=0
        scy=0
        # file is built from single line, values are space separated, there is 9 values
        try:
                with open(self.calib_file,'r') as ff:
                        a1,a2,a3,a4,a5,a6,a7,scx,scy = ff.readline().split()
        except:
                print("No tslib calibration file, using defaults.")

        print("A1..A7: ",a1,a2,a3,a4,a5,a6,a7)
        print("Screen dims: X=",scx," Y=", scy)
        return [int(a1),int(a2),int(a3),int(a4),int(a5),int(a6),int(a7)]


    # convert touch panel raw location point into real point using formula from tslib -> linear.c file
    def display_touch_point(self, c, pt):
        #samp->x = pt[0] ; samp->y = pt[1];
        #xtemp = samp->x; ytemp = samp->y;
        dx = ( c[2] + c[0]*pt[0] + c[1]*pt[1] ) / c[6]; # samp->x =     ( lin->a[2] + lin->a[0]*xtemp + lin->a[1]*ytemp ) / lin->a[6];
        dy = ( c[5] + c[3]*pt[0] + c[4]*pt[1] ) / c[6]; # samp->y =     ( lin->a[5] + lin->a[3]*xtemp + lin->a[4]*ytemp ) / lin->a[6];
        #if (info->dev->res_x && lin->cal_res_x) samp->x = samp->x * info->dev->res_x / lin->cal_res_x;
        #if (info->dev->res_y && lin->cal_res_y) samp->y = samp->y * info->dev->res_y / lin->cal_res_y;

        return (int(dx),int(dy))


    def poll(self):
        cal_data = self.read_ts_calibration()
        max_errs = 100
        tp_f = os.open(self.tp_dev, os.O_RDONLY | os.O_NONBLOCK)
        flags = fcntl.fcntl(tp_f, fcntl.F_GETFL, 0)
        fcntl.fcntl(tp_f, fcntl.F_SETFL, flags & ~os.O_NONBLOCK)
        widget = None

        while not self.exiting:
            r, w, e = select.select([tp_f], [], [], 0.5)

            if r == [tp_f]:
                try:
                    data = os.read(tp_f, 22)
                    (tag, btn, x, y) = struct.unpack_from('>c?HH', data)
                    print(" btn = ", btn, " x y = ", x, y)
                except Exception as e:
                    print("Failed to read 22 bytes from {}: {}".format(self.tp_dev, e))
                    max_errs -= 1
                    if max_errs > 0:
                        continue
                    else:
                        print("Disabling touch screen")
                        break
                if btn:
                    point = [x, y]
                    (dx, dy) = self.display_touch_point(cal_data, point)
                    self.master.event_generate('<Motion>', warp=True, x=dx, y=dy)
                    widget = self.master.winfo_containing(dx, dy)
                    widget.event_generate('<Button-1>', x=dx, y=dy)
                elif widget:
                    widget.event_generate('<ButtonRelease-1>')
                    widget = None

        os.close(tp_f)
