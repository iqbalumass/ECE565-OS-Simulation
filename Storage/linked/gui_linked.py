import tkinter as tk
from tkinter import StringVar, Toplevel, messagebox
import json
from tkinter import ttk

import sys
import os
from paths import *

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from block import BLOCK, BlockGUI


reads=0
writes=0
file_name=None
action_type=None
pos=None

class LinkedAllocationBLOCK(BLOCK):
    def __init__(self, file, next_block, block_id):
        self.file = file
        self.next_block = next_block
        self.block_id = block_id  # Unique Block ID (0 to 31)
        self.addresses = list(range(block_id * 4, block_id * 4 + 4))  # 4 addresses per block

class LinkedAllocationBlockGUI(BlockGUI):
    def __init__(self, root):
        self.root = root
        # self.root.title("Disk Block Management")
        # self.root.geometry("800x500")

        # Instructions label
        label = tk.Label(self.root, text="Block Occupancy (Blue = Occupied, White = Free)")
        label.pack(pady=10)

        # Reads and writes label
        self.read_write_label = tk.Label(self.root, text=f"Reads: {reads} | Writes: {writes}")
        self.read_write_label.pack(pady=5)

        # File, action, position label
        self.file_label = tk.Label(self.root, text=f"File: {file_name} | Action: {action_type} | Position : {pos}")
        self.file_label.pack(pady=5)

        self.blocks = [None] * 32  # Placeholder for BLOCK objects
        
        
        # Display the 32 blocks as labels
        blocks_frame = tk.Frame(self.root)
        blocks_frame.pack(pady=10)

        # Create a 4x8 grid for block entries
        self.block_labels = []
        for i in range(32):
            label = tk.Label(blocks_frame, text=f"Block {i}\nFile: None\nNext: None", borderwidth=1, relief="solid", width=10, height=4)
            label.grid(row=i // 8, column=i % 8, padx=5, pady=5)
            self.block_labels.append(label)
        
        # Load button
        # self.load_button = tk.Button(self.root, text="Load block entries from JSON", command=self.load_entries)
        # self.load_button.pack(pady=5)

        # Update button (disabled initially)
        # self.update_button = tk.Button(self.root, text="Update File", state=tk.DISABLED, command=self.update_file)
        # self.update_button.pack(pady=5)
        # # Automatically load entries when initializing the GUI
        self.load_entries()  

    def load_entries(self):
        try:
            with open(BLOCK_ENTRIES_PATH, "r") as file:
                data = json.load(file)

            with open(DIRECTORY_PATH, "r") as f:
                self.directory_data = json.load(f)

            # Set to track indexes where file is null
            self.null_file_indexes = set()
            
            # Initialize BLOCK objects from JSON data
            for i in range(32):
                block_data = data.get(str(i), {"file": None, "next_block": None})
                self.blocks[i] = LinkedAllocationBLOCK(block_data["file"], block_data["next_block"],i)
                self.update_block_label(i)

                

                # Set background color to light blue after loading
                if block_data["file"] is None:
                    self.null_file_indexes.add(i)
                else:
                    self.block_labels[i].config(bg="light blue")
            
            
            
            # Print indexes with null files
            # print("Blocks with null files:")
            # print(self.null_file_indexes)

            # Enable the Update button after loading
            #self.update_button.config(state=tk.NORMAL)
            # messagebox.showinfo("Linked Allocation GUI", "Block entries loaded from JSON.")
        
        except FileNotFoundError:
            messagebox.showerror("Error", "block_entries.json file not found.")
        except json.JSONDecodeError:
            messagebox.showerror("Error", "Invalid JSON format.")

    def update_block_label(self, index):
        block = self.blocks[index]
        self.block_labels[index].config(text=f"Block {index}\nFile: {block.file}\nNext: {block.next_block}")

    def update_read_write_label(self):
        """Update the reads and writes label."""
        self.read_write_label.config(text=f"Reads: {reads} | Writes: {writes}")

    # def update_file_label(self):
    #     self.file_label.config(text=f'File: {file_name} | Action: {action_type} | Position : {pos}')
    
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
            global file_name,action_type,pos
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
            global reads, writes
            current_block_index = start

            if position=="beginning":
                # Pick a free block from null_file_indexes
                new_block_index = self.null_file_indexes.pop()
                print(f'(From Linked Allocation): new_block_index is {new_block_index}')

                #Add the file and pointer to the new block    
                self.blocks[new_block_index].file = file_name
                self.blocks[new_block_index].next_block = start 

                start = new_block_index
                writes=writes+1

                print(f'(From Linked Allocation): Reads: {reads}, Writes {writes}')
                ###Changes to GUI
                messagebox.showinfo("Linked Allocation GUI", f"Adding New Block at Block {new_block_index} .")
                self.update_block_label(new_block_index)
                self.block_labels[new_block_index].config(bg="light blue")


            if position=="end":
                while self.blocks[current_block_index].next_block is not None:
                    reads=reads+1
                    #print(current_block_index)
                    current_block_index = self.blocks[current_block_index].next_block

                reads=reads+1
                print(f'(From Linked Allocation): current_block_index is {current_block_index}')
                print(f'(From Linked Allocation): reads is {reads}')


                # Pick the next free block from null_file_indexes
                new_block_index = self.null_file_indexes.pop()
                print(f'(From Linked Allocation): Adding block to Block{new_block_index}')

                # Assign file data to the new block
                self.blocks[new_block_index].file = file_name
                self.blocks[new_block_index].next_block = None  # Since it's the end of the list
                writes=writes+1
                # Update the previous block to point to the new block
                self.blocks[current_block_index].next_block = new_block_index
                writes=writes+1

                print(f'(From Linked Allocation): Reads: {reads}, Writes {writes}')
                # print(self.blocks[new_block_index].next_block)
                # print(self.blocks[current_block_index].next_block)

                ###Changes to GUI
                messagebox.showinfo("Linked Allocation GUI", f"Adding New Block at Block {new_block_index} .")
                self.update_block_label(new_block_index)
                self.update_block_label(current_block_index)
                self.block_labels[new_block_index].config(bg="light blue")
                

            if position=="middle":
                
                target=length//2

                #might not occur but still keeping this around
                if target==0:
                    add(file_name, start,length, position)
                    return

                # Traverse the list to the block just before the desired position
                current_block_index = start
                previous_block_index = None
                count = 0

                while current_block_index is not None and count < target:
                    print(f'(From Linked Allocation): current block is Block {current_block_index} points to block {self.blocks[current_block_index].next_block} ')
                    previous_block_index = current_block_index
                    current_block_index = self.blocks[current_block_index].next_block
                    count += 1
                    reads=reads+1

                if current_block_index is None and count < target:
                # Position is out of bounds (larger than the list length)
                    print("(From Linked Allocation): Position out of bounds.")

                # Pick a free block from null_file_indexes
                new_block_index = self.null_file_indexes.pop()
                print(f'(From Linked Allocation): new_block_index is {new_block_index}')

                # Assign file data to the new block
                self.blocks[new_block_index].file = file_name
                self.blocks[new_block_index].next_block = current_block_index  # The new block points to the current block at position
                
                writes=writes+1
                if previous_block_index is not None:
                    self.blocks[previous_block_index].next_block = new_block_index  # The previous block points to the new block
                    writes=writes+1
                print(f'(From Linked Allocation): Reads: {reads}, Writes {writes}')
                # print(self.blocks[new_block_index].next_block)
                # print(self.blocks[current_block_index].next_block)

                ###Changes to GUI
                messagebox.showinfo("Linked Allocation GUI", f"Adding New Block at Block {new_block_index} .")
                self.update_block_label(new_block_index)
                self.update_block_label(current_block_index)
                self.update_block_label(previous_block_index)
                self.block_labels[new_block_index].config(bg="light blue")

            self.update_read_write_label()
            #self.update_file_label()

        def remove(file_name, start, length, position):
            global reads,writes
            current_block_index = start
            previous_block_index=None

            if position=="beginning":
                if start is None:
                    # The list is empty, so nothing to remove
                    return None
                
                block_to_remove = start

                # Update the start pointer to the next block
                start = self.blocks[block_to_remove].next_block

                # Free the block file and next_block attributes
                self.blocks[block_to_remove].file = None
                self.blocks[block_to_remove].next_block = None

                # Return the removed block to the free list
                self.null_file_indexes.add(block_to_remove)

                print(f'(From Linked Allocation): Reads: {reads}, Writes {writes}')
                ###Changes to GUI
                messagebox.showinfo("Linked Allocation GUI", f"Removing Block at Block {block_to_remove} .")
                self.update_block_label(block_to_remove)
                self.update_block_label(start)
                self.block_labels[block_to_remove].config(bg="white")


            if position=="end":

                while self.blocks[current_block_index].next_block is not None:
                    reads=reads+1
                    #print(current_block_index)
                    previous_block_index=current_block_index
                    current_block_index = self.blocks[current_block_index].next_block

                # Now, current_block_index is the last block
                # previous_block_index is the second-to-last block

                if previous_block_index is not None:
                    # Update the second-to-last block's next_block to None
                    self.blocks[previous_block_index].next_block = None
                    writes=writes+1

                
                ## Free the last block
                self.blocks[current_block_index].file = None  # Clear the file data (optional)
                self.blocks[current_block_index].next_block = None

                # Return the last block to the free list
                self.null_file_indexes.add(current_block_index)
                print(f'(From Linked Allocation): current_block_index is {current_block_index}')
                print(f'(From Linked Allocation): reads is {reads}')

                print(f'(From Linked Allocation): Reads: {reads}, Writes {writes}')
                ###Changes to GUI
                messagebox.showinfo("Linked Allocation GUI", f"Removing Block at Block {current_block_index} .")
                self.update_block_label(previous_block_index)
                self.update_block_label(current_block_index)
                self.block_labels[current_block_index].config(bg="white")


            if position=="middle":
                target=length//2

                #might not occur but still keeping this around
                if target==0:
                    add(file_name, start,length, position)
                    return

                # Traverse the list to the block just before the desired position
                current_block_index = start
                previous_block_index = None
                count = 0

                while current_block_index is not None and count < target:
                    print(f'(From Linked Allocation): current block is Block {current_block_index} points to block {self.blocks[current_block_index].next_block} ')
                    previous_block_index = current_block_index
                    current_block_index = self.blocks[current_block_index].next_block
                    count += 1
                    reads=reads+1

                if current_block_index is None and count < target:
                # Position is out of bounds (larger than the list length)
                    print("(From Linked Allocation): Position out of bounds.")


                # Now current_block_index is the block to remove
                # previous_block_index is the block before it       
                
                # Update the previous block's next_block to skip the current block
                if previous_block_index is not None:
                    self.blocks[previous_block_index].next_block = self.blocks[current_block_index].next_block

                writes=writes+1

                #Free the current block
                self.blocks[current_block_index].file=None
                self.blocks[current_block_index].next_block=None
                self.null_file_indexes.add(current_block_index)
                
                
    
        

                print(f'(From Linked Allocation): Reads: {reads}, Writes {writes}')
                

                ###Changes to GUI
                messagebox.showinfo("Linked Allocation GUI", f"Removing Block at Block {current_block_index} .")
                self.update_block_label(current_block_index)
                self.update_block_label(previous_block_index)
                self.block_labels[current_block_index].config(bg="white")

            self.update_read_write_label()
            #self.update_file_label()

    '''
        This add() and remove() is for integration. Please do not consider it duplicate
    '''
    def add(self,file_name, start, length, position):
        global reads, writes
        current_block_index = start
        

        if position=="beginning":
            # Pick a free block from null_file_indexes
            new_block_index = self.null_file_indexes.pop()
            print(f'(From Linked Allocation): new_block_index is {new_block_index}')

            #Add the file and pointer to the new block    
            self.blocks[new_block_index].file = file_name
            self.blocks[new_block_index].next_block = start 

            start = new_block_index
            writes=writes+1

            print(f'(From Linked Allocation): Reads: {reads}, Writes {writes}')
            ###Changes to GUI
            messagebox.showinfo("Linked Allocation GUI", f"Adding New Block at Block {new_block_index} .")
            self.update_block_label(new_block_index)
            self.block_labels[new_block_index].config(bg="light blue")


        if position=="end":
            while self.blocks[current_block_index].next_block is not None:
                reads=reads+1
                #print(current_block_index)
                current_block_index = self.blocks[current_block_index].next_block

            reads=reads+1
            print(f'(From Linked Allocation): current_block_index is {current_block_index}')
            print(f'(From Linked Allocation): reads is {reads}')


            # Pick the next free block from null_file_indexes
            new_block_index = self.null_file_indexes.pop()
            print(f'(From Linked Allocation): Adding block to Block{new_block_index}')

            # Assign file data to the new block
            self.blocks[new_block_index].file = file_name
            self.blocks[new_block_index].next_block = None  # Since it's the end of the list
            writes=writes+1
            # Update the previous block to point to the new block
            self.blocks[current_block_index].next_block = new_block_index
            writes=writes+1

            print(f'(From Linked Allocation): Reads: {reads}, Writes {writes}')
            #print(self.blocks[new_block_index].next_block)
            #print(self.blocks[current_block_index].next_block)

            ###Changes to GUI
            messagebox.showinfo("Linked Allocation GUI", f"Adding New Block at Block {new_block_index} .")
            self.update_block_label(new_block_index)
            self.update_block_label(current_block_index)
            self.block_labels[new_block_index].config(bg="light blue")
            

        if position=="middle":
            
            target=length//2

            #might not occur but still keeping this around
            if target==0:
                self.add(file_name, start,length, position)
                return

            # Traverse the list to the block just before the desired position
            current_block_index = start
            previous_block_index = None
            count = 0

            while current_block_index is not None and count < target:
                print(f'(From Linked Allocation): current block is Block {current_block_index} points to block {self.blocks[current_block_index].next_block} ')
                previous_block_index = current_block_index
                current_block_index = self.blocks[current_block_index].next_block
                count += 1
                reads=reads+1

            if current_block_index is None and count < target:
            # Position is out of bounds (larger than the list length)
                print("(From Linked Allocation): Position out of bounds.")

            # Pick a free block from null_file_indexes
            new_block_index = self.null_file_indexes.pop()
            print(f'(From Linked Allocation): new_block_index is {new_block_index}')

            # Assign file data to the new block
            self.blocks[new_block_index].file = file_name
            self.blocks[new_block_index].next_block = current_block_index  # The new block points to the current block at position
            
            writes=writes+1
            if previous_block_index is not None:
                self.blocks[previous_block_index].next_block = new_block_index  # The previous block points to the new block
                writes=writes+1
            print(f'(From Linked Allocation): Reads: {reads}, Writes {writes}')
            #print(self.blocks[new_block_index].next_block)
            #print(self.blocks[current_block_index].next_block)

            ###Changes to GUI
            messagebox.showinfo("Linked Allocation GUI", f"Adding New Block at Block {new_block_index} .")
            self.update_block_label(new_block_index)
            self.update_block_label(current_block_index)
            self.update_block_label(previous_block_index)
            self.block_labels[new_block_index].config(bg="light blue")

        self.update_read_write_label()
        #self.update_file_label()

    def remove(self,file_name, start, length, position):
        global reads,writes
        current_block_index = start
        previous_block_index=None

        if position=="beginning":
            if start is None:
                # The list is empty, so nothing to remove
                return None
            
            block_to_remove = start

            # Update the start pointer to the next block
            start = self.blocks[block_to_remove].next_block

            # Free the block file and next_block attributes
            self.blocks[block_to_remove].file = None
            self.blocks[block_to_remove].next_block = None

            # Return the removed block to the free list
            self.null_file_indexes.add(block_to_remove)

            print(f'(From Linked Allocation): Reads: {reads}, Writes {writes}')
            ###Changes to GUI
            messagebox.showinfo("Linked Allocation GUI", f"Removing Block at Block {block_to_remove} .")
            self.update_block_label(block_to_remove)
            self.update_block_label(start)
            self.block_labels[block_to_remove].config(bg="white")


        if position=="end":

            while self.blocks[current_block_index].next_block is not None:
                reads=reads+1
                #print(current_block_index)
                previous_block_index=current_block_index
                current_block_index = self.blocks[current_block_index].next_block

            # Now, current_block_index is the last block
            # previous_block_index is the second-to-last block

            if previous_block_index is not None:
                # Update the second-to-last block's next_block to None
                self.blocks[previous_block_index].next_block = None
                writes=writes+1

            
            ## Free the last block
            self.blocks[current_block_index].file = None  # Clear the file data (optional)
            self.blocks[current_block_index].next_block = None

            # Return the last block to the free list
            self.null_file_indexes.add(current_block_index)
            print(f'(From Linked Allocation): current_block_index is {current_block_index}')
            print(f'(From Linked Allocation): reads is {reads}')

            print(f'(From Linked Allocation): Reads: {reads}, Writes {writes}')
            ###Changes to GUI
            messagebox.showinfo("Linked Allocation GUI", f"Removing Block at Block {current_block_index} .")
            self.update_block_label(previous_block_index)
            self.update_block_label(current_block_index)
            self.block_labels[current_block_index].config(bg="white")


        if position=="middle":
            target=length//2

            #might not occur but still keeping this around
            if target==0:
                self.add(file_name, start,length, position)
                return

            # Traverse the list to the block just before the desired position
            current_block_index = start
            previous_block_index = None
            count = 0

            while current_block_index is not None and count < target:
                print(f'(From Linked Allocation): current block is Block {current_block_index} points to block {self.blocks[current_block_index].next_block} ')
                previous_block_index = current_block_index
                current_block_index = self.blocks[current_block_index].next_block
                count += 1
                reads=reads+1

            if current_block_index is None and count < target:
            # Position is out of bounds (larger than the list length)
                print("(From Linked Allocation): Position out of bounds.")


            # Now current_block_index is the block to remove
            # previous_block_index is the block before it       
            
            # Update the previous block's next_block to skip the current block
            if previous_block_index is not None:
                self.blocks[previous_block_index].next_block = self.blocks[current_block_index].next_block

            writes=writes+1

            #Free the current block
            self.blocks[current_block_index].file=None
            self.blocks[current_block_index].next_block=None
            self.null_file_indexes.add(current_block_index)
            
            

    

            print(f'(From Linked Allocation): Reads: {reads}, Writes {writes}')
            

            ###Changes to GUI
            messagebox.showinfo("Linked Allocation GUI", f"Removing Block at Block {current_block_index} .")
            self.update_block_label(current_block_index)
            self.update_block_label(previous_block_index)
            self.block_labels[current_block_index].config(bg="white")

        self.update_read_write_label()
        #self.update_file_label()

    def read(self,vpn):
        # In Linked Allocation, we traverse the linked list of blocks
        current_block = self.blocks[vpn // 4]  # Start with the block corresponding to the VPN
        address_index = vpn % 4  # Modulo to find the address within the block
        print(f"(From Linked Allocation): Linked Allocation: Read VPN {vpn} -> Block {current_block.block_id}, Address {current_block.addresses[address_index]}")
        return current_block.addresses[address_index]
    
if __name__ == "__main__":
    root = tk.Tk()
    app = LinkedAllocationBlockGUI(root)
    ret_value= app.read(5)
    root.mainloop()


'''
Some Test CASES:
'''
#add('list',28,4,'beginning', reads, writes) #Ans: reads=0, writes=1
#add('list',28,4,'middle', reads, writes) #Ans: reads=2, writes=2
#add('list',28,4,'end', reads, writes) #Ans: reads=4 ,writes=2
#remove('list',28,4,'beginning', reads, writes) #Ans: reads=0,writes=0
#remove('list',28,4,'middle', reads, writes) #Ans:reads=2, writes=1
#remove('list',28,4,'end', reads, writes) #Ans: reads=3,writes=1

'''
Test case on count: Please check
'''
#add('count', 0, 2, 'beginning', reads, writes)# Ans: read=0, writes=1
#add('count', 0, 2, 'middle', reads, writes)   #Ans: read=1 , writes=2
#add('count', 0, 2, 'end', reads, writes) # Ans: read=2, writes=2
#remove('count', 0, 2, 'beginning', reads, writes)# Ans: reads=0,writes=0
#remove('count', 0, 2, 'middle', reads, writes)  #Ans: reads=1, writes=1
#remove('count', 0, 2, 'end', reads, writes) #Ans: reads=1 , writes=1



'''
Test case on f: Please check
'''
#add('f', 6, 2, 'beginning', reads, writes)# Ans: read=0, writes=1
#add('f', 6, 2, 'middle', reads, writes)   #Ans: read=1 , writes=2
#add('f', 6, 2, 'end', reads, writes) # Ans: read=2, writes=2
#remove('f', 6, 2, 'beginning', reads, writes)# Ans: reads=0,writes=0
#remove('f', 6, 2, 'middle', reads, writes)  #Ans: reads=1, writes=1
#remove('f', 6, 2, 'end', reads, writes) #Ans: reads=1 , writes=1