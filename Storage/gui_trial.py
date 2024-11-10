import tkinter as tk
from tkinter import messagebox, Toplevel, StringVar, Radiobutton, ttk
import json

total_blocks = 32
disk_blocks = [None] * total_blocks
reads=0
writes=0

# Function to update the reads and writes labels
def update_read_write_labels():
    read_write_label.config(text=f"Reads: {reads} | Writes: {writes}")
    root.update()

def load_blocks():
    try:
        # Load the JSON data from directory.json
        with open("directory.json", "r") as file:
            global directory_data
            directory_data = json.load(file)

        # Update blocks based on directory.json data
        for entry in directory_data:
            file_name = entry["file"]
            start = entry["start"]
            length = entry["length"]

            # Mark blocks as occupied by the file
            for i in range(start, start + length):
                if 0 <= i < len(blocks):  # Ensure index is within range
                    blocks[i].config(text=f"{i}\n{file_name}", bg="lightblue")
                    disk_blocks[i]=file_name

        update_file_button.config(state=tk.NORMAL)  # Enable the Update File button

    except FileNotFoundError:
        messagebox.showerror("Error", "directory.json file not found.")
    except json.JSONDecodeError:
        messagebox.showerror("Error", "Error parsing directory.json.")

def update_file():
    # Create a new popup window
    update_window = Toplevel(root)
    update_window.title("Update File")
    update_window.geometry("500x250")  # Adjust window size

    # Dropdown menu for selecting a file (using ttk.Combobox)
    file_names = [entry["file"] for entry in directory_data]
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
        entry = next((item for item in directory_data if item["file"] == file_name), None)
        if not entry:
            messagebox.showerror("Error", "File not found.")
            return
        
        start = entry["start"]
        length = entry["length"]

        print(f'start is{start}')
        print(f'length is {length}')

        # Call add or remove function based on action_type
        if action_type == "Add":
            global reads, writes
            add(file_name, start, length, position=pos)  # Parameters are placeholders
        else:
            remove(file_name, start, length, position=pos)  # Parameters are placeholders

        update_window.destroy()  # Close the update window

    update_button = tk.Button(update_window, text="Update File", command=confirm_update)
    update_button.grid(row=3, column=0, columnspan=4, pady=10)  # Adjusted position

# Placeholder add and remove functions
def add(file_name, start, length, position):
    global disk_blocks, reads, writes
    highlight_index = None  # Default: no block highlighted
    
    # Check for adding at the "beginning"
    if position == "beginning":
        
        if start - 1 > 0 and disk_blocks[start - 1] is None:
            print('Add block to beginning without shifting')
            disk_blocks[start - 1] = file_name
            highlight_index = start - 1  # Highlight this block
            writes=writes+1
            print(writes)
        elif start-1>=0 and disk_blocks[start - 1]is not None:
            print('Add block to beginning with shifting')
            if start + length < total_blocks and disk_blocks[start + length] is None:
                for i in range(total_blocks - 1, start, -1):
                    disk_blocks[i] = disk_blocks[i - 1] if i > start else None
                    reads=reads+1
                    writes=writes+1
                highlight_index = start  # Highlight the added block at start
            writes=writes+1
        elif start-1<0:
            print('Add block to beginning with shifting')
            if start + length < total_blocks and disk_blocks[start + length] is None:
                for i in range(start+length, start, -1):
                    disk_blocks[i] = disk_blocks[i - 1] if i > start else None
                    reads=reads+1
                    writes=writes+1
                highlight_index = start  # Highlight the added block at start
            writes=writes+1

        else:
            print('No space')
    
    
    
    
    
    # Check for adding at the "middle"
    elif position == "middle":
        print("there will always be shifting if there is space-middle case")
        print('\\\\\original length of odd and even case for middle needs to be handled\\\\\\ ')
        
        if start == 0:
            target = start + (length // 2)
        elif start!=0 and start+length==32:
            target = start + (length // 2) - 1
        else:
            target=start + (length // 2) 

        ### case count: if length is 2, 2//2=1. if length is 3, 3//2=1  && case f: if if length=2, 2//2=1. if  length=3, 3//2=1 &&& case list= length=4//2=2
        print(target) ### case count: if start=0, target becomes 0+1=1    && case f: if start=6, target becomes 6+1=7 && case list, if start=28, target id 28+2=30
        print(f'We have to move block item from target block {target}')
        print(f'Making it a list as we can shift eitheri left or right')
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
            if disk_blocks[start + length]==None:
                print(f'Block {start + length} is unallocated')
                print('shift right')
                if length%2==0:
                    print(f'moving {num_of_blocks_to_move[0]} blocks')
                    print(f"Target is start+(length//2)")
                    for i in range(start+length,target,-1):
                        print(f'moving block {i-1} to block {i}')
                        disk_blocks[i]=disk_blocks[i-1]
                        disk_blocks[i-1]=None
                        reads=reads+1
                        writes=writes+1
                    print('Allocation space made, now insert at target') 
                    print(f'disk block {target} has {disk_blocks[target]}')  
                    disk_blocks[target]=file_name
                    writes=writes+1
                    print(f'disk block {target} has {disk_blocks[target]}')
                else:
                    print(f'moving {num_of_blocks_to_move[1]} blocks')
                    print(f"Target is start+(length//2)")
                    for i in range(start+length,target,-1):
                        print(f'moving block {i-1} to block {i}')
                        disk_blocks[i]=disk_blocks[i-1]
                        disk_blocks[i-1]=None
                        reads=reads+1
                        writes=writes+1
                    print('Allocation space made, now insert at target')   
                    print(f'disk block {target} has {disk_blocks[target]}')
                    disk_blocks[target]=file_name
                    print(f'disk block {target} has {disk_blocks[target]}')

        elif start+length==32:
            '''
            we try and see if Case 2 applies
            ''' 
            if disk_blocks[start-1]==None:
                print(f'Block {start-1} is unallocated')
                print('shift left')
                if length%2==0:
                    print(f'moving {num_of_blocks_to_move[0]} blocks')
                    print(f"Target is start+(length//2)")
                    for i in range(start-1,target,1):
                        print(f'moving block {i+1} to block {i}')
                        disk_blocks[i]=disk_blocks[i+1]
                        disk_blocks[i+1]=None
                        reads=reads+1
                        writes=writes+1
                    print('Allocation space made, now insert at target') 
                    print(f'disk block {target} has {disk_blocks[target]}')  
                    disk_blocks[target]=file_name
                    writes=writes+1
                    print(f'disk block {target} has {disk_blocks[target]}')

                else:
                    print(f'moving {num_of_blocks_to_move[1]} blocks')
                    print(f"Target is start+(length//2)")
                    for i in range(start-1,target,1):
                        print(f'moving block {i+1} to block {i}')
                        disk_blocks[i]=disk_blocks[i+1]
                        disk_blocks[i+1]=None
                        reads=reads+1
                        writes=writes+1
                    print('Allocation space made, now insert at target') 
                    print(f'disk block {target} has {disk_blocks[target]}')  
                    disk_blocks[target]=file_name
                    print(f'disk block {target} has {disk_blocks[target]}')
        else:
            '''
            start>0 and start+length<32, prefer to apply Case 1 than Case 2
            '''
            if disk_blocks[start + length]==None:
                print(f'Block {start + length} is unallocated')
                print('shift right')
                print(f'target is {target}')
                if length%2==0:
                    print(f'moving {num_of_blocks_to_move[0]} blocks')
                    print(f"Target is start+(length//2)")
                    for i in range(start+length,target,-1):
                        print(f'moving block {i-1} to block {i}')
                        disk_blocks[i]=disk_blocks[i-1]
                        disk_blocks[i-1]=None
                        reads=reads+1
                        writes=writes+1
                    print('Allocation space made, now insert at target') 
                    print(f'disk block {target} has {disk_blocks[target]}')  
                    disk_blocks[target]=file_name
                    writes=writes+1
                    print(f'disk block {target} has {disk_blocks[target]}')

                else:
                    print(f'moving {num_of_blocks_to_move[1]} blocks')
                    print(f"Target is start+(length//2)")
                    for i in range(start+length,target,-1):
                        print(f'moving block {i-1} to block {i}')
                        disk_blocks[i]=disk_blocks[i-1]
                        disk_blocks[i-1]=None
                        reads=reads+1
                        writes=writes+1
                    print('Allocation space made, now insert at target')   
                    print(f'disk block {target} has {disk_blocks[target]}')
                    disk_blocks[target]=file_name
                    print(f'disk block {target} has {disk_blocks[target]}')

            
            elif disk_blocks[start - 1]==None:
                print(f'Block {start-1} is unallocated')
                print('shift left')

                if length%2==0:
                    print(f'moving {num_of_blocks_to_move[0]} blocks')
                    print(f"Target is start+(length//2)")
                    for i in range(start-1,target,1):
                        print(f'moving block {i+1} to block {i}')
                        disk_blocks[i]=disk_blocks[i+1]
                        disk_blocks[i+1]=None
                        reads=reads+1
                        writes=writes+1
                    print('Allocation space made, now insert at target') 
                    print(f'disk block {target} has {disk_blocks[target]}')  
                    disk_blocks[target]=file_name
                    print(f'disk block {target} has {disk_blocks[target]}')
                else:
                    print(f'moving {num_of_blocks_to_move[1]} blocks')
                    print(f"Target is start+(length//2)")
                    for i in range(start-1,target,1):
                        print(f'moving block {i+1} to block {i}')
                        disk_blocks[i]=disk_blocks[i+1]
                        disk_blocks[i+1]=None
                        reads=reads+1
                        writes=writes+1
                    print('Allocation space made, now insert at target') 
                    print(f'disk block {target} has {disk_blocks[target]}')  
                    disk_blocks[target]=file_name
                    print(f'disk block {target} has {disk_blocks[target]}')

            else:
                print('NO SPACE')

        print(f"Read:{reads} and Writes:{writes}")

    
    

     # Check for adding at the "end"
    
    
    
    
    elif position == "end":
        
        if start + length < total_blocks and disk_blocks[start + length] is None :
            print('Add block to ending need no shifting')
            disk_blocks[start + length] = file_name
            highlight_index = start + length  # Highlight the added block
            writes=writes+1
        elif start - 1 > 0 and disk_blocks[start - 1] is None:
            print('Add block to ending needs shifting')
            for i in range(start+length - 1, start - 1, -1):
                print(f'move block {i} to {i-1}')
                disk_blocks[i] = disk_blocks[i - 1] if i > start else None
                reads=reads+1
                writes=writes+1
            disk_blocks[start-1] = file_name
            writes=writes+1
            highlight_index = start+length  # Highlight the added block at end position
        else:
            print('NO SPACE')
    
    
    print(f"Read:{reads} and Writes:{writes}")
    update_gui_blocks()
    update_read_write_labels()  # Update the reads and writes display

    #pass  # Implement logic here later

def remove(file_name, start, length, position):
    global disk_blocks, reads, writes
    


    if position=='beginning':
        print(f'remove block at {start}')
        disk_blocks[start]=None
        highlight_index=start
        for i in range(start, start+length-1,1):
            print(f'move block {i+1} to {i}')
            disk_blocks[i]=disk_blocks[i+1]
            disk_blocks[i+1]=None
            reads=reads+1
            writes=writes+1
        disk_blocks[start + length-1]=None
        print(f'block {start+length} is now {disk_blocks[start + length-1]}')
    elif position=='middle':
        print(f'remove block at {start+(length//2)}') 
        '''
        After removing we gotta move the blocks.   '''
        target=start+(length//2)
        disk_blocks[target]=None
        for i in range(target, start+length-1,1):
            print(f'move block {i+1} to {i}')
            disk_blocks[i]=disk_blocks[i+1]
            disk_blocks[i+1]=None
            reads=reads+1
            writes=writes+1
        disk_blocks[start + length-1]=None
        print(f'block {start+length-1} is now {disk_blocks[start + length-1]}')
        #writes=writes+1
        highlight_index=target
    else: #position=end
        print(f'remove block at {start+length-1}')
        disk_blocks[start + length-1]=None
        highlight_index=start+length-1
    length=length-1

    
    print(f"Read:{reads} and Writes:{writes}")
    update_gui_blocks()
    update_read_write_labels() 
    pass  # Implement logic here later

# Function to update GUI blocks after changes
def update_gui_blocks():
    for i, block in enumerate(disk_blocks):
        if block is None:
            blocks[i].config(text=str(i), bg="white")  # Free block
        else:
            blocks[i].config(text=f"{i}\n{block}", bg="lightblue")  # Occupied block

# Initialize the main window
root = tk.Tk()
root.title("Disk Block Manager")
root.geometry("800x400")  # Adjust size as needed

# Instructions label
label = tk.Label(root, text="Block Occupancy (Blue = Occupied, White = Free)")
label.pack(pady=10)

# Reads and writes label
read_write_label = tk.Label(root, text=f"Reads: {reads} | Writes: {writes}")
read_write_label.pack(pady=5)

# Display the 32 blocks as labels
blocks_frame = tk.Frame(root)
blocks_frame.pack(pady=10)

blocks = []
for i in range(32):
    block_label = tk.Label(blocks_frame, text=str(i), relief="solid", width=6, height=3, bg="white")
    block_label.grid(row=i // 8, column=i % 8, padx=5, pady=5)
    blocks.append(block_label)

# Load blocks button
load_button = tk.Button(root, text="Load blocks from directory.json", command=load_blocks)
load_button.pack(pady=5)

# Update File button (initially disabled)
update_file_button = tk.Button(root, text="Update File", state=tk.DISABLED, command=update_file)
update_file_button.pack(pady=5)

# Run the main loop
root.mainloop()
