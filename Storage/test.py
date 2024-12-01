import tkinter as tk
from tkinter import ttk
from tkinter import StringVar, Toplevel, messagebox
import json
import sys
import os


sys.path.append(os.path.abspath(os.path.dirname(__file__)))
# Import your specific GUI classes
from  indexed.gui_indexed import IndexedAllocationBlockGUI
from contiguous.gui_contiguous import ContiguousAllocationBlockGUI
from linked.gui_linked import LinkedAllocationBlockGUI
#import block



# Run the main loop
def test_frame_request_to_storage():
    root = tk.Tk()
    #app = MainApp(root)
    '''
    Feel free to use any. It is the same address, anyway
    '''
    app=IndexedAllocationBlockGUI(root)
    return_frame=app.read(5)
    app=ContiguousAllocationBlockGUI(root)
    return_frame=app.read(5)
    app=LinkedAllocationBlockGUI(root)
    return_frame=app.read(5)
    print(return_frame)


    #root.mainloop()

test_frame_request_to_storage()