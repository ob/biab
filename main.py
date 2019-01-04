from Tkinter import *
from touchscreen import TouchScreen
from biab import BiabApp

import argparse
import sys

def main(av):
    parser = argparse.ArgumentParser(description='BIAB')
    parser.add_argument('--touchscreen', action='store_true')
    args = parser.parse_args()

    root=Tk()
    app=BiabApp(root, touchscreen=args.touchscreen)
    root.mainloop()



if __name__ == '__main__':
    main(sys.argv)
