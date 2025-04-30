# -*- coding: utf-8 -*-
import os
if __name__ == "__main__":
    # if Windows, run interface_win.py
    if os.name == 'nt':
        from interface_win import *
    else:
        from interface_macos import *
