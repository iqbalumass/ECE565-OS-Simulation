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

class MainApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Disk Block Management")
        self.root.geometry("1000x1000")

        self.blocks = [None] * 32  # Placeholder for BLOCK objects

        # Add a descriptive label at the top
        self.description_label = tk.Label(
            self.root,
            text="Here we will be showing performances of three Allocation Methods: Contiguous Allocation, Linked List Allocation and Indexed Allocation in terms of number of Disk Operations (Read/Write) needed to Add/Remove a Block to/from an existing file.\n Assume, there are 32 blocks in our disk.",
            font=("TkDefaultFont", 10),
            wraplength=800,  # Wrap text if it's too wide
            justify="center"  # Center the text
        )
        self.description_label.pack(pady=10)
        
        
        # Display the 32 blocks as labels
        self.blocks_frame = tk.Frame(self.root)
        self.blocks_frame.pack(pady=20)

        # Create a 4x8 grid for block entries
        self.block_labels = []
        for i in range(32):
            label = tk.Label(self.blocks_frame, text=f"Block {i}\nFile: None", borderwidth=1, relief="solid", width=10, height=4)
            label.grid(row=i // 8, column=i % 8, padx=5, pady=5)
            self.block_labels.append(label)
        
        # Load button
        self.load_button = tk.Button(self.root, text="Get started", command=self.load_entries)
        self.load_button.pack(pady=5)

        # Update button (disabled initially)
        self.update_button = tk.Button(self.root, text="Simulate Adding/Removing Block", state=tk.DISABLED, command=self.update_file)
        self.update_button.pack(pady=5)

        

    def load_entries(self):
            print('load')

    
            with open("linked/directory.json", "r") as f:
                self.directory_data = json.load(f)

            # Disable the Load button
            self.load_button.config(state=tk.DISABLED)

            # Hide the blocks by removing the frame
            self.blocks_frame.pack_forget()
            self.notebook = ttk.Notebook(self.root)
            f1 = ttk.Frame(self.notebook)   # first page, which would get widgets gridded into it
            f2 = ttk.Frame(self.notebook)   # second page
            f3= ttk.Frame(self.notebook)

            
            self.contiguous_gui = ContiguousAllocationBlockGUI(f1)
            self.linked_gui = LinkedAllocationBlockGUI(f2)
            self.indexed_gui = IndexedAllocationBlockGUI(f3)
            self.notebook.add(f1, text='Contiguous Allocation')
            self.notebook.add(f2, text='Linked Allocation')
            self.notebook.add(f3, text='Indexed Allocation')

            # Pack the Notebook so it appears in the layout
            self.notebook.pack(fill='both', expand=True, pady=10)
            # Enable the Update button after loading
            self.update_button.config(state=tk.NORMAL)
    def update_file(self):
        print('update file')
            # Create a new popup window
        update_window = Toplevel(self.root)
        update_window.title("Update File")
        update_window.geometry("500x250")  # Adjust window size

        # Dropdown menu for selecting a file (using ttk.Combobox)
        file_names = [entry["file"] for entry in self.directory_data]
        selected_file = StringVar(update_window)
        selected_file.set(file_names[0])  # Default selection

        tk.Label(update_window, text="Select File:").grid(row=0, column=0, pady=5, padx=10, sticky="w")
        file_dropdown = ttk.Combobox(update_window, textvariable=selected_file, values=file_names, state="readonly")
        file_dropdown.grid(row=0, column=1, pady=5, padx=10, sticky="w")

        # Radio buttons for Add/Remove block options
        action = StringVar(value="Add")
        tk.Label(update_window, text="Select Action:").grid(row=1, column=0, pady=5, padx=10, sticky="w")
        tk.Radiobutton(update_window, text="Add Block", variable=action, value="Add").grid(row=1, column=1, sticky="w")
        tk.Radiobutton(update_window, text="Remove Block", variable=action, value="Remove").grid(row=1, column=2, sticky="w")

        # Radio buttons for Position options
        position = StringVar(value="beginning")
        tk.Label(update_window, text="Select Position:").grid(row=2, column=0, pady=5, padx=10, sticky="w")
        tk.Radiobutton(update_window, text="Beginning", variable=position, value="beginning").grid(row=2, column=1, sticky="w")
        tk.Radiobutton(update_window, text="Middle", variable=position, value="middle").grid(row=2, column=2, sticky="w")
        tk.Radiobutton(update_window, text="End", variable=position, value="end").grid(row=2, column=3, sticky="w")

        # Update button to confirm and call add/remove functions
        def confirm_update():
            file_name = selected_file.get()
            pos = position.get()
            action_type = action.get()

            # Find the file entry in the data
            entry = next((item for item in self.directory_data if item["file"] == file_name), None)
            if not entry:
                messagebox.showerror("Error", "File not found.")
                return
            
            start = entry["start"]
            length = entry["length"]

            print(f'start is {start}')
            print(f'length is {length}')

            # Call add or remove function based on action_type
            if action_type == "Add":
                global reads, writes
                add(self, file_name, start, length, position=pos)  # Parameters are placeholders
            else:
                remove(self, file_name, start, length, position=pos)  # Parameters are placeholders

            update_window.destroy()  # Close the update window

        update_button = tk.Button(update_window, text="Update File", command=confirm_update)
        update_button.grid(row=3, column=0, columnspan=4, pady=10)  # Adjusted position

        def add(file_name, start, length, position):
            ##self.linked_gui.add(self,file_name, start, length, position)
            pass
            
        def remove(file_name, start, length, position):
            pass

    

# Run the main loop
def main():
    root = tk.Tk()
    app = MainApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
