import tkinter as tk
from tkinter import StringVar, Toplevel, messagebox
import json
from tkinter import ttk


import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from block import BLOCK, BlockGUI

reads = 0
writes = 0
file_name=None
action_type=None
pos=None

class IndexedAllocationBLOCK(BLOCK):
    def __init__(self, file=None, next_block=None, data_blocks=None, is_index_block=False):
        self.file = file  # The file this block belongs to (None if empty)
        self.next_block = next_block  # Link to the next block (used in linked allocation)
        self.data_blocks = data_blocks or []  # Data blocks for indexed allocation (empty list by default)
        self.is_index_block = is_index_block  # Flag to indicate if it's an index block

class IndexedAllocationBlockGUI(BlockGUI):
    def __init__(self, root):
        self.root = root
        # self.root.title("Disk Block Management")
        # self.root.geometry("800x600")

        # Labels and instructions
        self.instruction_label = tk.Label(self.root, text="Disk Block Occupancy (Blue = Occupied, White = Free, Light Green=Index)")
        self.instruction_label.pack(pady=10)

    
        
        # Reads and writes
        self.read_write_label = tk.Label(self.root, text="Reads: 0 | Writes: 0")
        self.read_write_label.pack(pady=5)

        # File, action, position label
        self.file_label = tk.Label(self.root, text=f"File: {file_name} | Action: {action_type} | Position : {pos}")
        self.file_label.pack(pady=5)

        

        # Blocks display
        self.blocks_frame = tk.Frame(self.root)
        self.blocks_frame.pack(pady=10)

        # Block data (32 blocks)
        self.blocks = [None] * 32
        self.block_labels = []

        for i in range(32):
            label = tk.Label(self.blocks_frame, text=f"Block {i}", borderwidth=1, relief="solid", width=12, height=4)
            label.grid(row=i//8, column=i%8, padx=5, pady=5)
            self.block_labels.append(label)
            
            # Bind hover event to show tooltip
            label.bind("<Enter>", lambda event, index=i: self.show_tooltip(event, index))
            label.bind("<Leave>", self.hide_tooltip)

        # Load Button
        # self.load_button = tk.Button(self.root, text="Load Block Entries", command=self.load_entries)
        # self.load_button.pack(pady=5)
        
        # Update Button (temporarily disabled)
        # self.update_button = tk.Button(self.root, text="Update Block", state=tk.DISABLED,command=self.update_file)
        # self.update_button.pack(pady=5)

        # Automatically load entries when initializing the GUI
        self.load_entries()  

        # Tooltip label (initially hidden)
        self.tooltip = tk.Label(self.root, text="", background="light yellow", borderwidth=1, relief="solid", padx=5, pady=3)
        self.tooltip.place_forget()

    def load_entries(self):
        try:
            with open("indexed/block_entries.json", "r") as file:
                block_entries_data = json.load(file)

            with open("indexed/directory.json", "r") as f:
                self.directory_data = json.load(f)

            self.indexed_allocation = {}

            for file_info in self.directory_data:
                file_name = file_info["file"]
                index_block = file_info["start"]  # The index block
                length = file_info["length"]

                # Gather data blocks, starting from the block after index_block
                data_blocks = []
                next_block = block_entries_data[str(index_block)]["next_block"]  # First data block
                while len(data_blocks) < length and next_block is not None:
                    data_blocks.append(next_block)
                    next_block = block_entries_data[str(next_block)]["next_block"]

                # Store the index block and its data blocks
                self.indexed_allocation[file_name] = {
                    "index_block": index_block,
                    "data_blocks": data_blocks
                }

                # Assign the file to its blocks
                # Mark index block (distinguish it by passing is_index_block=True)
                self.blocks[index_block] = IndexedAllocationBLOCK(file=file_name, next_block=None, data_blocks=data_blocks, is_index_block=True)
                
                # Mark data blocks (starting from index block's next block)
                for block in data_blocks:
                    self.blocks[block] = IndexedAllocationBLOCK(file=file_name, next_block=None)

            # Now update the labels to reflect the new indexed allocation
            self.update_gui_blocks()

            # Enable the Update Button after loading entries
            # self.update_button.config(state=tk.NORMAL)

        except FileNotFoundError:
            messagebox.showerror("Error", "block_entries.json file not found.")
        except json.JSONDecodeError:
            messagebox.showerror("Error", "Invalid JSON format.")


    def update_file(self):
        

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
        def confirm_update(update_button):
            global file_name,pos,action_type
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

            # print(f'start is {start}')
            # print(f'length is {length}')

            # Call add or remove function based on action_type
            if action_type == "Add":
                global reads, writes
                add(file_name, start, length, position=pos)  # Parameters are placeholders
            else:
                remove(file_name, start, length, position=pos)  # Parameters are placeholders

            update_window.destroy()  # Close the update window
             # Disable the "Update File" button after the update
            update_button.config(state=tk.DISABLED)  # Disable the update button
        
        update_button = tk.Button(update_window, text="Update File", command=lambda: confirm_update(self.update_button))
        update_button.grid(row=3, column=0, columnspan=4, pady=10)  # Adjusted position

        def add(file_name, start, length, position):
            global writes
            # Fetch the current indexed allocation for the file
            file_allocation = self.indexed_allocation[file_name]
            index_block = file_allocation["index_block"]
            data_blocks = file_allocation["data_blocks"]
            
            # Determine where to add the new block
            if position == "beginning":
                new_block = self.find_free_block()
                data_blocks.insert(0, new_block)
            elif position == "middle":
                new_block = self.find_free_block()
                mid_index = len(data_blocks) // 2
                data_blocks.insert(mid_index, new_block)
            elif position == "end":
                new_block = self.find_free_block()
                data_blocks.append(new_block)

            # Update the indexed allocation with the new data blocks
            self.indexed_allocation[file_name]["data_blocks"] = data_blocks

            # Mark the new block as used
            self.blocks[new_block] = IndexedAllocationBLOCK(file=file_name, next_block=None)
            print(f'new block is {new_block}')
            messagebox.showinfo("Indexed Allocation GUI", f"Adding New Block at Block {new_block} .")

            # Update the GUI with the new block
            self.update_gui_blocks()

            # Increment the write counter
            writes += 1
            self.update_read_write_label()
            self.update_file_label()

    

        def remove(file_name, start, length, position):
            
            global writes

            # Fetch the current indexed allocation for the file
            file_allocation = self.indexed_allocation[file_name]
            index_block = file_allocation["index_block"]
            data_blocks = file_allocation["data_blocks"]

            # Determine which block to remove
            if position == "beginning":
                block_to_remove = data_blocks.pop(0)
            elif position == "middle":
                mid_index = len(data_blocks) // 2
                block_to_remove = data_blocks.pop(mid_index)
            elif position == "end":
                block_to_remove = data_blocks.pop()

            # Mark the block as free
            self.blocks[block_to_remove] = None
            messagebox.showinfo("Indexed Allocation GUI", f"Removing Block at Block {block_to_remove} .")

            # Update the indexed allocation
            self.indexed_allocation[file_name]["data_blocks"] = data_blocks

            # Update the GUI
            self.update_gui_blocks()
            
            
            self.update_read_write_label()
            self.update_file_label()

    '''
    These add() and remove() are for the integrated module. Please do not consider duplicate.
    '''

    def add(self,file_name, start, length, position):
            global writes
            # Fetch the current indexed allocation for the file
            file_allocation = self.indexed_allocation[file_name]
            index_block = file_allocation["index_block"]
            data_blocks = file_allocation["data_blocks"]
            
            # Determine where to add the new block
            if position == "beginning":
                new_block = self.find_free_block()
                data_blocks.insert(0, new_block)
            elif position == "middle":
                new_block = self.find_free_block()
                mid_index = len(data_blocks) // 2
                data_blocks.insert(mid_index, new_block)
            elif position == "end":
                new_block = self.find_free_block()
                data_blocks.append(new_block)

            # Update the indexed allocation with the new data blocks
            self.indexed_allocation[file_name]["data_blocks"] = data_blocks

            # Mark the new block as used
            self.blocks[new_block] = IndexedAllocationBLOCK(file=file_name, next_block=None)
            print(f'new block is {new_block}')
            messagebox.showinfo("Indexed Allocation GUI", f"Adding New Block at Block {new_block} .")

            # Update the GUI with the new block
            self.update_gui_blocks()

            # Increment the write counter
            writes += 1
            self.update_read_write_label()
            self.update_file_label()    

    def remove(self,file_name, start, length, position):
            
            global writes

            # Fetch the current indexed allocation for the file
            file_allocation = self.indexed_allocation[file_name]
            index_block = file_allocation["index_block"]
            data_blocks = file_allocation["data_blocks"]

            # Determine which block to remove
            if position == "beginning":
                block_to_remove = data_blocks.pop(0)
            elif position == "middle":
                mid_index = len(data_blocks) // 2
                block_to_remove = data_blocks.pop(mid_index)
            elif position == "end":
                block_to_remove = data_blocks.pop()

            # Mark the block as free
            self.blocks[block_to_remove] = None
            messagebox.showinfo("Indexed Allocation GUI", f"Removing Block at Block {block_to_remove} .")

            # Update the indexed allocation
            self.indexed_allocation[file_name]["data_blocks"] = data_blocks

            # Update the GUI
            self.update_gui_blocks()
            
            
            self.update_read_write_label()
            self.update_file_label()

    def find_free_block(self):
        for i in range(32):  # Assuming there are 32 blocks
            if not self.blocks[i]:
                return i
        raise Exception("No free block available")

    def update_block_label(self, index):
        block = self.blocks[index]
        label = self.block_labels[index]
        
        # Update label text with file and next block information
        if block:
            label.config(text=f"Block {index}\nFile: {block.file or 'None'}")
            
            if block.is_index_block:  # If the block is an index block, highlight it with a distinct color
                label.config(bg="light green")  # Highlight index blocks in light green
            elif block.file:  # If the block belongs to a file
                label.config(bg="light blue")  # Highlight other blocks in light blue
            else:
                label.config(bg="white")  # Reset background if the block is not in use
        else:
            label.config(text=f"Block {index}\nFile: None")
            label.config(bg="white")

    def update_gui_blocks(self):
        for i in range(32):  # Assuming there are 32 blocks
            self.update_block_label(i)

    def update_read_write_label(self):
        self.read_write_label.config(text=f"Reads: {reads} | Writes: {writes}")
    def update_file_label(self):
        self.file_label.config(text=f'File: {file_name} | Action: {action_type} | Position : {pos}')

    def show_tooltip(self, event, index):
        block = self.blocks[index]
    
        if block:  # If the block is not None, show detailed info
            file_info = f"File: {block.file or 'None'}"
            next_block_info = f"Next: {block.next_block or 'None'}"
            index_block_info = "Index Block" if block.is_index_block else "Data Block"
            
            # Start building the tooltip text
            tooltip_text = f"{file_info}\n{next_block_info}\n{index_block_info}"
            
            # If the block is an index block, show its data blocks as well
            if block.is_index_block and block.data_blocks:
                data_blocks_info = "\nData Blocks:"
                for i, data_block in enumerate(block.data_blocks):
                    data_blocks_info += f"\n  {data_block} (Block {data_block})"
                tooltip_text += data_blocks_info

        else:  # If the block is None, show default message
            tooltip_text = "Empty Block"

        self.tooltip.config(text=tooltip_text)
        
        # Position the tooltip near the label
        x, y, _, _ = event.widget.bbox("insert")
        #x=event.x_root
        #y=event.y_root
        
        self.tooltip.place(x=x + 90, y=y + 90)

        # Get the cursor's position relative to the widget
        
        
    def hide_tooltip(self, event=None):
        self.tooltip.place_forget()

def main():
    root = tk.Tk()
    app = IndexedAllocationBlockGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()

##Test case outputs : 
# any add operation causes: 1 write
# any remove will cause no reads or writes. 