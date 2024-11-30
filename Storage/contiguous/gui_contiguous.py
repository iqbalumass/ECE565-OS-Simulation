import tkinter as tk
from tkinter import StringVar, Toplevel, messagebox
import json
from tkinter import ttk

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from block import BLOCK, BlockGUI

reads=0
writes=0
file_name=None
action_type=None
pos=None

class ContiguousAllocationBLOCK(BLOCK):
    def __init__(self, file):
        self.file = file

class ContiguousAllocationBlockGUI(BlockGUI):
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
            label = tk.Label(blocks_frame, text=f"Block {i}\nFile: None", borderwidth=1, relief="solid", width=10, height=4)
            label.grid(row=i // 8, column=i % 8, padx=5, pady=5)
            self.block_labels.append(label)
        
        # # Load button
        # self.load_button = tk.Button(self.root, text="Load block entries from JSON", command=self.load_entries)
        # self.load_button.pack(pady=5)
        

        # Update button (disabled initially)
        # self.update_button = tk.Button(self.root, text="Update File", state=tk.DISABLED, command=self.update_file)
        # self.update_button.pack(pady=5)

        # Automatically load entries when initializing the GUI
        self.load_entries()  

    def load_entries(self):
        try:
            
            with open("contiguous/block_entries.json", "r") as file:
                data = json.load(file)

            with open("contiguous/directory.json", "r") as f:
                self.directory_data = json.load(f)

            # Set to track indexes where file is null
            self.null_file_indexes = set()
            
            # Initialize BLOCK objects from JSON data
            for i in range(32):
                block_data = data.get(str(i), {"file": None})
                self.blocks[i] = ContiguousAllocationBLOCK(block_data["file"])
                self.update_block_label(i)

                

                # Set background color to light blue after loading
                if block_data["file"] is None:
                    self.null_file_indexes.add(i)
                else:
                    self.block_labels[i].config(bg="light blue")
            
            
            
            # Print indexes with null files
            print("Blocks with null files:")
            print(self.null_file_indexes)

            # Enable the Update button after loading
            # self.update_button.config(state=tk.NORMAL)
            # messagebox.showinfo("Contiguous Allocation GUI", "Block entries loaded from JSON.")

            
        
        except FileNotFoundError:
            messagebox.showerror("Error", "block_entries.json file not found.")
        except json.JSONDecodeError:
            messagebox.showerror("Error", "Invalid JSON format.")

    def update_block_label(self, index_or_indices):
    
        # Check if the argument is a list
        if isinstance(index_or_indices, list):
            # Loop through each index in the list and update the corresponding label
            for index in index_or_indices:
                block = self.blocks[index]
                self.block_labels[index].config(text=f"Block {index}\nFile: {block.file if block else 'None'}")
        else:
            # Handle the single index case
            index = index_or_indices
            block = self.blocks[index]
            self.block_labels[index].config(text=f"Block {index}\nFile: {block.file if block else 'None'}")
            

    def update_read_write_label(self):
        """Update the reads and writes label."""
        self.read_write_label.config(text=f"Reads: {reads} | Writes: {writes}")
    
    def update_file_label(self):
        self.file_label.config(text=f'File: {file_name} | Action: {action_type} | Position : {pos}')
        
        
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

            print(f'start is {start}')
            print(f'length is {length}')

            # Call add or remove function based on action_type
            if action_type == "Add":
                add(file_name, start, length, position=pos)  # Parameters are placeholders
            else:
                remove(file_name, start, length, position=pos)  # Parameters are placeholders

            update_window.destroy()  # Close the update window
            # Disable the "Update File" button after the update
            update_button.config(state=tk.DISABLED)  # Disable the update button

        
        def add(file_name, start, length, position):
            global reads,writes
            updated_indices = []  # Track indices that are updated
            target=None
            # Check for adding at the "beginning"
            if position == "beginning":
                
                if start-1<0:
                    print('invalid')
                    target=start
                else: 
                    target=start-1
                    print(f'target is {target}')
                
                if self.blocks[target].file is not None:
                    print(f"Block {target} is already occupied. Checking for space to shift...")
                    #Ensure there is space to shift blocks
                    if target + length < len(self.blocks) and self.blocks[target + length].file is None:
                        # Shift blocks to the right to make space

                        '''
                        Please Be Careful with the range. We will keep a variable 'start_index' as the starting point for the loop
                        if start is 0, start_index=start+length
                        if start >0, start_index=start+length-1

                        '''
                        start_index=None
                        if start==0:
                            start_index=start+length
                            
                        else:
                            start_index=start+length-1
                            print(f'start_index is {start_index}')

                        for i in range(start_index , target, -1):
                            self.blocks[i].file = self.blocks[i - 1].file if i > target else None
                            print(f"Shifted block {i-1} to block {i}")
                            self.block_labels[i].config(bg="light blue")
                            updated_indices.append(i)
                            reads=reads+1
                            writes=writes+1
            
                        # Insert the new block at the position
                        self.blocks[target].file = file_name
                        self.block_labels[target].config(bg="light blue")
                        writes=writes+1
                        print(f"Block added for file '{file_name}' at position {target}")
                        messagebox.showinfo("Contiguous Allocation GUI", f"Block added for file '{file_name}' at position {target}")
                        
                else:
                    # If the target position is empty, simply insert the block
                    self.blocks[target].file = file_name
                    self.block_labels[target].config(bg="light blue")
                    updated_indices.append(target)
                    writes=writes+1
                    print(f"Block added for file '{file_name}' at position {target}")
                    messagebox.showinfo("Contiguous Allocation GUI", f"Block added for file '{file_name}' at position {target}")
                        
                
            
            
            if position=="end":
                if start+length==len(self.blocks): #in list, 28+4=32 and self.blocks[32] is out of range
                    print('invalid')
                    target=start+length-1
                else: 
                    target=start+length
                
                if self.blocks[target].file is not None:
                    print(f"Block {target} is already occupied. Checking for space to shift...")
                    #Ensure there is space to shift blocks
                    if start-1>0 and self.blocks[start-1].file is None:
                        # Shift blocks to the left to make space

                        '''
                        Please Be Careful with the range. We will keep a variable 'start_index' as the starting point for the loop
                        For position="end", stop_index matters
                        if start is 0, start_index=start+length
                        if start >0, start_index=start+length-1

                        '''
                        start_index=start-1
                        stop_index=None
                        if start+length==len(self.blocks):
                            stop_index=start+length-1
                            
                        else:
                            stop_index=start+length
                        print(f'stop_index is {stop_index}')

                        for i in range(start_index , stop_index, 1):
                            self.blocks[i].file = self.blocks[i + 1].file if i < target else None
                            print(f"Shifted block {i+1} to block {i}")
                            self.block_labels[i].config(bg="light blue")
                            updated_indices.append(i)
                            reads=reads+1
                            writes=writes+1
            
                        # Insert the new block at the position
                        self.blocks[target].file = file_name
                        self.block_labels[target].config(bg="light blue")
                        writes=writes+1
                        updated_indices.append(target)
                        print(f"Block added for file '{file_name}' at position {target}")
                        messagebox.showinfo("Contiguous Allocation GUI", f"Block added for file '{file_name}' at position {target}")

                        
                else:
                    # If the target position is empty, simply insert the block
                    self.blocks[target].file = file_name
                    self.block_labels[target].config(bg="light blue")
                    updated_indices.append(target)
                    writes=writes+1
                    print(f"Block added for file '{file_name}' at position {target}")
                    messagebox.showinfo("Contiguous Allocation GUI", f"Block added for file '{file_name}' at position {target}")
                    

            
            if position=="middle":
                print("there will always be shifting if there is space-middle case")
                print('###original length of odd and even case for middle needs to be handled###')

                if start == 0:
                    target = start + (length // 2) #case count where start=0 and length=2
                elif start!=0 and start+length==32:
                    target = start + (length // 2) - 1 #case list where start 28, length=4 and start+length is out of range
                else:
                    target=start + (length // 2) #other cases

                print(f'target is {target}')
                print(f'We have to move block item from target block {target}')
                print(f'Making it a list as we can shift either left or right')
                num_of_blocks_to_move=[length//2, (length//2)+1] #if file length is even, we move length//2 blocks, else we move length//2+1 blocks


                '''
                Case 1: There is space to the right. i.e. disk_block[start+length] is None.. for count, disk_block[0+2]=2, for f,disk_block[6+2]=8, for list, disk_block[28+4]=32
                Case 2: There is space to the left, i.e., disk_block[start-1] is None.. for count, disk_block[0-1]=-1 for disk_block[6-1]=5 and for list, disk_blocl[28-1]=27
                Case 3: No space at all        
                '''
            
                if start==0:
                    '''
                    we try and see if Case 1 applies
                    '''
                    if self.blocks[start + length].file==None:
                        print(f'Block {start + length} is unallocated')
                        print('shift right')
                        if length%2==0:
                            print(f'Moving {num_of_blocks_to_move[0]} block(s)')
                            print(f"Target is {start+(length//2)}")
                            for i in range(start+length,target,-1):
                                print(f'moving block {i-1} to block {i}')
                                self.blocks[i].file=self.blocks[i-1].file
                                self.block_labels[i].config(bg="light blue")
                                updated_indices.append(i)
                                self.blocks[i-1]=None
                                reads=reads+1
                                writes=writes+1
                        else:
                            print(f'Moving {num_of_blocks_to_move[1]} block(s)')
                            print(f"Target is {start+(length//2)}")
                            for i in range(start+length,target,-1):
                                print(f'moving block {i-1} to block {i}')
                                self.blocks[i].file=self.blocks[i-1].file
                                self.block_labels[i].config(bg="light blue")
                                updated_indices.append(i)
                                self.blocks[i-1]=None
                                reads=reads+1
                                writes=writes+1
                            
                        print('Allocation space made, now insert at target')  
                        self.blocks[target]=ContiguousAllocationBLOCK(file_name)
                        #self.blocks[target].file=file_name
                        print(target)
                        updated_indices.append(target)
                        writes=writes+1
                        print(f'disk block {target} has {self.blocks[target].file}')
                        messagebox.showinfo("Contiguous Allocation GUI", f"Block added for file '{file_name}' at position {target}")




                elif start+length==32:
                    '''
                    We try and see if case 2 applies
                    '''
                    if self.blocks[start-1].file==None:
                        print(f'Block {start-1} is unallocated')
                        print('shift left')
                        if length%2==0:
                            print(f'Moving {num_of_blocks_to_move[0]} block(s)')
                            print(f"Target is {start+(length//2)}")
                            for i in range(start-1,target,1):
                                print(f'moving block {i+1} to block {i}')
                                self.blocks[i]=self.blocks[i+1]
                                self.block_labels[i].config(bg="light blue")
                                updated_indices.append(i)
                                self.blocks[i+1]=None
                                reads=reads+1
                                writes=writes+1
                        else:
                            print(f'Moving {num_of_blocks_to_move[1]} block(s)')
                            print(f"Target is {start+(length//2)}")
                            for i in range(start+length,target,1):
                                print(f'moving block {i+1} to block {i}')
                                self.blocks[i].file=self.blocks[i+1].file
                                self.block_labels[i].config(bg="light blue")
                                updated_indices.append(i)
                                self.blocks[i+1]=None
                                reads=reads+1
                                writes=writes+1
                            
                        print('Allocation space made, now insert at target')  
                        self.blocks[target]=ContiguousAllocationBLOCK(file_name)
                        #self.blocks[target].file=file_name
                        print(target)
                        updated_indices.append(target)
                        writes=writes+1
                        print(f'disk block {target} has {self.blocks[target].file}')
                        messagebox.showinfo("Contiguous Allocation GUI", f"Block added for file '{file_name}' at position {target}")

            
            
                else:
                    '''
                    start>0 and start+length<32, prefer to apply Case 1 than Case 2
                    '''
                    if self.blocks[start + length].file==None:
                        print(f'Block {start + length} is unallocated')
                        print('shift right')
                        print(f'target is {target}')

                        if length%2==0:
                            print(f'Moving {num_of_blocks_to_move[0]} block(s)')
                            print(f"Target is {start+(length//2)}")
                            for i in range(start+length,target,-1):
                                print(f'moving block {i-1} to block {i}')
                                self.blocks[i].file=self.blocks[i-1].file
                                self.block_labels[i].config(bg="light blue")
                                updated_indices.append(i)
                                self.blocks[i-1]=None
                                reads=reads+1
                                writes=writes+1
                        else:
                            print(f'Moving {num_of_blocks_to_move[1]} block(s)')
                            print(f"Target is {start+(length//2)}")
                            for i in range(start+length,target,-1):
                                print(f'moving block {i+1} to block {i}')
                                self.blocks[i].file=self.blocks[i-1].file
                                self.block_labels[i].config(bg="light blue")
                                updated_indices.append(i)
                                self.blocks[i-1]=None
                                reads=reads+1
                                writes=writes+1
                            
                        print('Allocation space made, now insert at target')  
                        self.blocks[target]=ContiguousAllocationBLOCK(file_name)
                        #self.blocks[target].file=file_name
                        print(target)
                        updated_indices.append(target)
                        writes=writes+1
                        print(f'disk block {target} has {self.blocks[target].file}')
                        messagebox.showinfo("Contiguous Allocation GUI", f"Block added for file '{file_name}' at position {target}")

            

                    elif self.blocks[start - 1].file==None:
                        print(f'Block {start-1} is unallocated')
                        print('shift left')

                        if length%2==0:
                            print(f'Moving {num_of_blocks_to_move[0]} block(s)')
                            print(f"Target is {start+(length//2)}")
                            for i in range(start-1,target,1):
                                print(f'moving block {i+1} to block {i}')
                                self.blocks[i].file=self.blocks[i+1].file
                                self.block_labels[i].config(bg="light blue")
                                updated_indices.append(i)
                                self.blocks[i+1]=None
                                reads=reads+1
                                writes=writes+1
                        else:
                            print(f'Moving {num_of_blocks_to_move[1]} block(s)')
                            print(f"Target is {start+(length//2)}")
                            for i in range(start+length,target,1):
                                print(f'moving block {i+1} to block {i}')
                                self.blocks[i].file=self.blocks[i+1].file
                                self.block_labels[i].config(bg="light blue")
                                updated_indices.append(i)
                                self.blocks[i+1]=None
                                reads=reads+1
                                writes=writes+1
                            
                        print('Allocation space made, now insert at target')  
                        self.blocks[target]=ContiguousAllocationBLOCK(file_name)
                        #self.blocks[target].file=file_name
                        print(target)
                        updated_indices.append(target)
                        writes=writes+1
                        print(f'disk block {target} has {self.blocks[target].file}')
                        messagebox.showinfo("Contiguous Allocation GUI", f"Block added for file '{file_name}' at position {target}")

                    else:
                        print('no space')
                        messagebox.showinfo()

            print(f"Read:{reads} and Writes:{writes}")
            self.update_block_label(updated_indices)
            self.update_read_write_label()  # Update the reads and writes display
            self.update_file_label()

            #pass  # Implement logic here later

        def remove(file_name, start, length, position):
            global reads,writes
            updated_indices=[] # Track indices that are updated

            if position=="beginning":
                print(f'remove block at {start}')
                self.blocks[start]=None
                for i in range(start, start+length-1,1):
                    print(f'move block {i+1} to {i}')
                    self.blocks[i]=self.blocks[i+1]
                    self.blocks[i+1]=None
                    updated_indices.append(i)
                    reads=reads+1
                    writes=writes+1
        
                self.blocks[start + length-1]=None
                messagebox.showinfo("Contiguous Allocation GUI", f"Removing block for file '{file_name}' at position {start}")
                self.block_labels[start+length-1].config(bg="white")
                updated_indices.append(start+length-1)

                print(f'block {start+length} is now {self.blocks[start + length-1]}')


            if position=="end":
                print(f'remove block at {start+length-1}')
                messagebox.showinfo("Contiguous Allocation GUI", f"Removing block for file '{file_name}' at position {start+length-1}")
                self.blocks[start + length-1]=None
                highlight_index=start+length-1
                self.block_labels[start+length-1].config(bg="white")
                updated_indices.append(start+length-1)
            

            if position=="middle":
                print(f'remove block at {start+(length//2)}')
                '''
                After removing we gotta move the blocks.   
                '''
                target=start+(length//2)
                self.blocks[target]=None
                for i in range(target, start+length-1,1):
                    print(f'move block {i+1} to {i}')
                    self.blocks[i]=self.blocks[i+1]
                    self.blocks[i+1]=None
                    updated_indices.append(i)
                    reads=reads+1
                    writes=writes+1
            self.blocks[start + length-1]=None
            messagebox.showinfo("Contiguous Allocation GUI", f"Removing block for file '{file_name}' at position {target}")
            self.block_labels[start+length-1].config(bg="white")
            updated_indices.append(start+length-1)
            print(f'block {start+length-1} is now {self.blocks[start + length-1]}')
            length=length-1
            print(f"Read:{reads} and Writes:{writes}")
            self.update_block_label(updated_indices)
            self.update_read_write_label()  # Update the reads and writes display
            self.update_file_label()
        
        update_button = tk.Button(update_window, text="Update File", command=lambda: confirm_update(self.update_button))
        update_button.grid(row=3, column=0, columnspan=4, pady=10)  # Adjusted position


    ''' 
    These add() and remove() are for the integrated module. Please do not consider duplicate

    '''
    def add(self, file_name, start, length, position):
            global reads,writes
            updated_indices = []  # Track indices that are updated
            target=None
            # Check for adding at the "beginning"
            if position == "beginning":
                
                if start-1<0:
                    print('invalid')
                    target=start
                else: 
                    target=start-1
                    print(f'target is {target}')
                
                if self.blocks[target].file is not None:
                    print(f"Block {target} is already occupied. Checking for space to shift...")
                    #Ensure there is space to shift blocks
                    if target + length < len(self.blocks) and self.blocks[target + length].file is None:
                        # Shift blocks to the right to make space

                        '''
                        Please Be Careful with the range. We will keep a variable 'start_index' as the starting point for the loop
                        if start is 0, start_index=start+length
                        if start >0, start_index=start+length-1

                        '''
                        start_index=None
                        if start==0:
                            start_index=start+length
                            
                        else:
                            start_index=start+length-1
                            print(f'start_index is {start_index}')

                        for i in range(start_index , target, -1):
                            self.blocks[i].file = self.blocks[i - 1].file if i > target else None
                            print(f"Shifted block {i-1} to block {i}")
                            self.block_labels[i].config(bg="light blue")
                            updated_indices.append(i)
                            reads=reads+1
                            writes=writes+1
            
                        # Insert the new block at the position
                        self.blocks[target].file = file_name
                        self.block_labels[target].config(bg="light blue")
                        writes=writes+1
                        print(f"Block added for file '{file_name}' at position {target}")
                        messagebox.showinfo("Contiguous Allocation GUI", f"Block added for file '{file_name}' at position {target}")
                        
                else:
                    # If the target position is empty, simply insert the block
                    self.blocks[target].file = file_name
                    self.block_labels[target].config(bg="light blue")
                    updated_indices.append(target)
                    writes=writes+1
                    print(f"Block added for file '{file_name}' at position {target}")
                    messagebox.showinfo("Contiguous Allocation GUI", f"Block added for file '{file_name}' at position {target}")
                        
                
            
            
            if position=="end":
                if start+length==len(self.blocks): #in list, 28+4=32 and self.blocks[32] is out of range
                    print('invalid')
                    target=start+length-1
                else: 
                    target=start+length
                
                if self.blocks[target].file is not None:
                    print(f"Block {target} is already occupied. Checking for space to shift...")
                    #Ensure there is space to shift blocks
                    if start-1>0 and self.blocks[start-1].file is None:
                        # Shift blocks to the left to make space

                        '''
                        Please Be Careful with the range. We will keep a variable 'start_index' as the starting point for the loop
                        For position="end", stop_index matters
                        if start is 0, start_index=start+length
                        if start >0, start_index=start+length-1

                        '''
                        start_index=start-1
                        stop_index=None
                        if start+length==len(self.blocks):
                            stop_index=start+length-1
                            
                        else:
                            stop_index=start+length
                        print(f'stop_index is {stop_index}')

                        for i in range(start_index , stop_index, 1):
                            self.blocks[i].file = self.blocks[i + 1].file if i < target else None
                            print(f"Shifted block {i+1} to block {i}")
                            self.block_labels[i].config(bg="light blue")
                            updated_indices.append(i)
                            reads=reads+1
                            writes=writes+1
            
                        # Insert the new block at the position
                        self.blocks[target].file = file_name
                        self.block_labels[target].config(bg="light blue")
                        writes=writes+1
                        updated_indices.append(target)
                        print(f"Block added for file '{file_name}' at position {target}")
                        messagebox.showinfo("Contiguous Allocation GUI", f"Block added for file '{file_name}' at position {target}")

                        
                else:
                    # If the target position is empty, simply insert the block
                    self.blocks[target].file = file_name
                    self.block_labels[target].config(bg="light blue")
                    updated_indices.append(target)
                    writes=writes+1
                    print(f"Block added for file '{file_name}' at position {target}")
                    messagebox.showinfo("Contiguous Allocation GUI", f"Block added for file '{file_name}' at position {target}")
                    

            
            if position=="middle":
                print("there will always be shifting if there is space-middle case")
                print('###original length of odd and even case for middle needs to be handled###')

                if start == 0:
                    target = start + (length // 2) #case count where start=0 and length=2
                elif start!=0 and start+length==32:
                    target = start + (length // 2) - 1 #case list where start 28, length=4 and start+length is out of range
                else:
                    target=start + (length // 2) #other cases

                print(f'target is {target}')
                print(f'We have to move block item from target block {target}')
                print(f'Making it a list as we can shift either left or right')
                num_of_blocks_to_move=[length//2, (length//2)+1] #if file length is even, we move length//2 blocks, else we move length//2+1 blocks


                '''
                Case 1: There is space to the right. i.e. disk_block[start+length] is None.. for count, disk_block[0+2]=2, for f,disk_block[6+2]=8, for list, disk_block[28+4]=32
                Case 2: There is space to the left, i.e., disk_block[start-1] is None.. for count, disk_block[0-1]=-1 for disk_block[6-1]=5 and for list, disk_blocl[28-1]=27
                Case 3: No space at all        
                '''
            
                if start==0:
                    '''
                    we try and see if Case 1 applies
                    '''
                    if self.blocks[start + length].file==None:
                        print(f'Block {start + length} is unallocated')
                        print('shift right')
                        if length%2==0:
                            print(f'Moving {num_of_blocks_to_move[0]} block(s)')
                            print(f"Target is {start+(length//2)}")
                            for i in range(start+length,target,-1):
                                print(f'moving block {i-1} to block {i}')
                                self.blocks[i].file=self.blocks[i-1].file
                                self.block_labels[i].config(bg="light blue")
                                updated_indices.append(i)
                                self.blocks[i-1]=None
                                reads=reads+1
                                writes=writes+1
                        else:
                            print(f'Moving {num_of_blocks_to_move[1]} block(s)')
                            print(f"Target is {start+(length//2)}")
                            for i in range(start+length,target,-1):
                                print(f'moving block {i-1} to block {i}')
                                self.blocks[i].file=self.blocks[i-1].file
                                self.block_labels[i].config(bg="light blue")
                                updated_indices.append(i)
                                self.blocks[i-1]=None
                                reads=reads+1
                                writes=writes+1
                            
                        print('Allocation space made, now insert at target')  
                        self.blocks[target]=ContiguousAllocationBLOCK(file_name)
                        #self.blocks[target].file=file_name
                        print(target)
                        updated_indices.append(target)
                        writes=writes+1
                        print(f'disk block {target} has {self.blocks[target].file}')
                        messagebox.showinfo("Contiguous Allocation GUI", f"Block added for file '{file_name}' at position {target}")




                elif start+length==32:
                    '''
                    We try and see if case 2 applies
                    '''
                    if self.blocks[start-1].file==None:
                        print(f'Block {start-1} is unallocated')
                        print('shift left')
                        if length%2==0:
                            print(f'Moving {num_of_blocks_to_move[0]} block(s)')
                            print(f"Target is {start+(length//2)}")
                            for i in range(start-1,target,1):
                                print(f'moving block {i+1} to block {i}')
                                self.blocks[i]=self.blocks[i+1]
                                self.block_labels[i].config(bg="light blue")
                                updated_indices.append(i)
                                self.blocks[i+1]=None
                                reads=reads+1
                                writes=writes+1
                        else:
                            print(f'Moving {num_of_blocks_to_move[1]} block(s)')
                            print(f"Target is {start+(length//2)}")
                            for i in range(start+length,target,1):
                                print(f'moving block {i+1} to block {i}')
                                self.blocks[i].file=self.blocks[i+1].file
                                self.block_labels[i].config(bg="light blue")
                                updated_indices.append(i)
                                self.blocks[i+1]=None
                                reads=reads+1
                                writes=writes+1
                            
                        print('Allocation space made, now insert at target')  
                        self.blocks[target]=ContiguousAllocationBLOCK(file_name)
                        #self.blocks[target].file=file_name
                        print(target)
                        updated_indices.append(target)
                        writes=writes+1
                        print(f'disk block {target} has {self.blocks[target].file}')
                        messagebox.showinfo("Contiguous Allocation GUI", f"Block added for file '{file_name}' at position {target}")

            
            
                else:
                    '''
                    start>0 and start+length<32, prefer to apply Case 1 than Case 2
                    '''
                    if self.blocks[start + length].file==None:
                        print(f'Block {start + length} is unallocated')
                        print('shift right')
                        print(f'target is {target}')

                        if length%2==0:
                            print(f'Moving {num_of_blocks_to_move[0]} block(s)')
                            print(f"Target is {start+(length//2)}")
                            for i in range(start+length,target,-1):
                                print(f'moving block {i-1} to block {i}')
                                self.blocks[i].file=self.blocks[i-1].file
                                self.block_labels[i].config(bg="light blue")
                                updated_indices.append(i)
                                self.blocks[i-1]=None
                                reads=reads+1
                                writes=writes+1
                        else:
                            print(f'Moving {num_of_blocks_to_move[1]} block(s)')
                            print(f"Target is {start+(length//2)}")
                            for i in range(start+length,target,-1):
                                print(f'moving block {i+1} to block {i}')
                                self.blocks[i].file=self.blocks[i-1].file
                                self.block_labels[i].config(bg="light blue")
                                updated_indices.append(i)
                                self.blocks[i-1]=None
                                reads=reads+1
                                writes=writes+1
                            
                        print('Allocation space made, now insert at target')  
                        self.blocks[target]=ContiguousAllocationBLOCK(file_name)
                        #self.blocks[target].file=file_name
                        print(target)
                        updated_indices.append(target)
                        writes=writes+1
                        print(f'disk block {target} has {self.blocks[target].file}')
                        messagebox.showinfo("Contiguous Allocation GUI", f"Block added for file '{file_name}' at position {target}")

            

                    elif self.blocks[start - 1].file==None:
                        print(f'Block {start-1} is unallocated')
                        print('shift left')

                        if length%2==0:
                            print(f'Moving {num_of_blocks_to_move[0]} block(s)')
                            print(f"Target is {start+(length//2)}")
                            for i in range(start-1,target,1):
                                print(f'moving block {i+1} to block {i}')
                                self.blocks[i].file=self.blocks[i+1].file
                                self.block_labels[i].config(bg="light blue")
                                updated_indices.append(i)
                                self.blocks[i+1]=None
                                reads=reads+1
                                writes=writes+1
                        else:
                            print(f'Moving {num_of_blocks_to_move[1]} block(s)')
                            print(f"Target is {start+(length//2)}")
                            for i in range(start+length,target,1):
                                print(f'moving block {i+1} to block {i}')
                                self.blocks[i].file=self.blocks[i+1].file
                                self.block_labels[i].config(bg="light blue")
                                updated_indices.append(i)
                                self.blocks[i+1]=None
                                reads=reads+1
                                writes=writes+1
                            
                        print('Allocation space made, now insert at target')  
                        self.blocks[target]=ContiguousAllocationBLOCK(file_name)
                        #self.blocks[target].file=file_name
                        print(target)
                        updated_indices.append(target)
                        writes=writes+1
                        print(f'disk block {target} has {self.blocks[target].file}')
                        messagebox.showinfo("Contiguous Allocation GUI", f"Block added for file '{file_name}' at position {target}")

                    else:
                        print('no space')
                        messagebox.showinfo()

            print(f"Read:{reads} and Writes:{writes}")
            self.update_block_label(updated_indices)
            self.update_read_write_label()  # Update the reads and writes display
            self.update_file_label()

            #pass  # Implement logic here later



    def remove(self,file_name, start, length, position):
        global reads,writes
        updated_indices=[] # Track indices that are updated
        target=None

        if position=="beginning":
            print(f'remove block at {start}')
            self.blocks[start]=None
            for i in range(start, start+length-1,1):
                print(f'move block {i+1} to {i}')
                self.blocks[i]=self.blocks[i+1]
                self.blocks[i+1]=None
                updated_indices.append(i)
                reads=reads+1
                writes=writes+1
    
            self.blocks[start + length-1]=None
            messagebox.showinfo("Contiguous Allocation GUI", f"Removing block for file '{file_name}' at position {start}")
            self.block_labels[start+length-1].config(bg="white")
            updated_indices.append(start+length-1)

            print(f'block {start+length} is now {self.blocks[start + length-1]}')


        if position=="end":
            print(f'remove block at {start+length-1}')
            messagebox.showinfo("Contiguous Allocation GUI", f"Removing block for file '{file_name}' at position {start+length-1}")
            self.blocks[start + length-1]=None
            highlight_index=start+length-1
            self.block_labels[start+length-1].config(bg="white")
            updated_indices.append(start+length-1)
        

        if position=="middle":
            print(f'remove block at {start+(length//2)}')
            '''
            After removing we gotta move the blocks.   
            '''
            target=start+(length//2)
            self.blocks[target]=None
            messagebox.showinfo("Contiguous Allocation GUI", f"Removing block for file '{file_name}' at position {target}")
            for i in range(target, start+length-1,1):
                print(f'move block {i+1} to {i}')
                self.blocks[i]=self.blocks[i+1]
                self.blocks[i+1]=None
                updated_indices.append(i)
                reads=reads+1
                writes=writes+1
        self.blocks[start + length-1]=None
        self.block_labels[start+length-1].config(bg="white")
        updated_indices.append(start+length-1)
        print(f'block {start+length-1} is now {self.blocks[start + length-1]}')
        length=length-1
        print(f"Read:{reads} and Writes:{writes}")
        self.update_block_label(updated_indices)
        self.update_read_write_label()  # Update the reads and writes display
        self.update_file_label()
if __name__ == "__main__":
    root = tk.Tk()
    app = ContiguousAllocationBlockGUI(root)
    root.mainloop()
        

'''
Test cases on list: Please check
'''
#add('list',28,4,'beginning', reads, writes) #Ans: reads=0, writes=1
#add('list',28,4,'middle', reads, writes) #Ans: reads=2, writes=3
#add('list',28,4,'end', reads, writes) #Ans: reads=4 ,writes=5
#remove('list',28,4,'beginning', reads, writes) #Ans: reads=3,writes=3
#remove('list',28,4,'middle', reads, writes) #Ans:reads=2, writes=2 or reads=1, writes=1
#remove('list',28,4,'end', reads, writes) #Ans: reads=0,writes=0


'''
Test case on count: Please check

'''
#add('count', 0, 2, 'beginning', reads, writes)# Ans: read=2, writes=3
#add('count', 0, 2, 'middle', reads, writes)   #Ans: read= 1, writes=2
#add('count', 0, 2, 'end', reads, writes) # Ans: read=0, writes=1
#remove('count', 0, 2, 'beginning', reads, writes)# Ans: reads=1,writes=1
#remove('count', 0, 2, 'middle', reads, writes)  #Ans: reads=1, writes=1 or read=0, write 0 if 1 is removed 
#remove('count', 0, 2, 'end', reads, writes) #Ans: reads=0 , writes=0



'''
Test case on f: Please check
'''
#add('f', 6, 2, 'beginning', reads, writes)# Ans: read=0, writes=1
#add('f', 6, 2, 'middle', reads, writes)   #Ans: read= 1, writes=2
#add('f', 6, 2, 'end', reads, writes) # Ans: read=0, writes=1
#remove('f', 6, 2, 'beginning', reads, writes)# Ans: reads=1,writes=1
#remove('f', 6, 2, 'middle', reads, writes)  #Ans: reads=1, writes=1
#remove('f', 6, 2, 'end', reads, writes) #Ans: reads=0 , writes=0