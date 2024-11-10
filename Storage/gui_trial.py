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
            remove(file_name, start, length, position=pos, reads=0, writes=0)  # Parameters are placeholders

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
    print(f"Read:{reads} and Writes:{writes}")
    update_gui_blocks()
    update_read_write_labels()  # Update the reads and writes display

    #pass  # Implement logic here later

def remove(file_name, start, length, position):
    global disk_blocks, reads, writes
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
