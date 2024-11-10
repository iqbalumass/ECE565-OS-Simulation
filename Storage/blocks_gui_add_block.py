import json
import tkinter as tk
from tkinter import messagebox, ttk

reads=0
writes=0

# Load JSON data into memory
def load_data(filename='directory.json'):
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        messagebox.showerror("Error", "File 'directory.json' not found.")
        return []
    except json.JSONDecodeError:
        messagebox.showerror("Error", "Error decoding JSON data.")
        return []

# Save JSON data to file
def save_data(data, filename='directory.json'):
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)

# Load and display blocks based on in-memory data
def load_and_display_blocks():
    global json_data
    # Reset all blocks to 'free' (white background)
    for i in range(32):
        block_buttons[i].config(bg="white", text=str(i))
    
    # Process each entry and color occupied blocks
    for entry in json_data:
        start = entry["start"]
        length = entry["length"]
        occupied_blocks = list(range(start, start + length))
        for block in occupied_blocks:
            if 0 <= block < 32:  # Ensure block is within valid range
                block_buttons[block].config(bg="light blue", text=f"{block}\n(Occupied)")

# Update the JSON data based on user input
def update_file():
    # Create a new window for update options
    update_window = tk.Toplevel(root)
    update_window.title("Update File")
    
    # Dropdown for file selection
    file_label = tk.Label(update_window, text="Select File:")
    file_label.grid(row=0, column=0, padx=5, pady=5)
    file_dropdown = ttk.Combobox(update_window, values=[entry["file"] for entry in json_data])
    file_dropdown.grid(row=0, column=1, padx=5, pady=5)
    
    # Radio buttons for add/remove block
    action_var = tk.StringVar(value="add")
    add_radio = tk.Radiobutton(update_window, text="Add Block", variable=action_var, value="add")
    add_radio.grid(row=1, column=0, padx=5, pady=5)
    remove_radio = tk.Radiobutton(update_window, text="Remove Block", variable=action_var, value="remove")
    remove_radio.grid(row=1, column=1, padx=5, pady=5)
    
    # Radio buttons for position (beginning, middle, end)
    position_var = tk.StringVar(value="end")
    tk.Label(update_window, text="Position:").grid(row=2, column=0, padx=5, pady=5)
    pos_begin = tk.Radiobutton(update_window, text="Beginning", variable=position_var, value="beginning")
    pos_middle = tk.Radiobutton(update_window, text="Middle", variable=position_var, value="middle")
    pos_end = tk.Radiobutton(update_window, text="End", variable=position_var, value="end")
    pos_begin.grid(row=2, column=1, padx=5, pady=5)
    pos_middle.grid(row=2, column=2, padx=5, pady=5)
    pos_end.grid(row=2, column=3, padx=5, pady=5)
    
    # Update button
    def apply_update():
        file_name = file_dropdown.get()
        action = action_var.get()
        position = position_var.get()
        
        # Find the file entry in the data
        entry = next((item for item in json_data if item["file"] == file_name), None)
        if not entry:
            messagebox.showerror("Error", "File not found.")
            return
        
        start = entry["start"]
        length = entry["length"]
        
        if action == "add":
            if position == "beginning":
                start -= 1  # Move start to the left
                length += 1  # Increase length
            elif position == "middle":
                length += 1  # Just increase length
            elif position == "end":
                length += 1  # Increase length

        elif action == "remove":
            if position == "beginning" and length > 1:
                start += 1  # Move start to the right
                length -= 1  # Decrease length
            elif position == "middle" and length > 2:  # Ensure there's at least one left
                length -= 1  # Just decrease length
            elif position == "end" and length > 1:
                length -= 1  # Decrease length

        # Update entry with new start and length, ensuring valid ranges
        entry["start"] = max(0, start)  # Ensure start is non-negative
        entry["length"] = min(32 - entry["start"], length)  # Ensure length does not exceed limit

        # Just refresh the display for now, without saving to the file
        load_and_display_blocks()
    
    update_button = tk.Button(update_window, text="Apply Update", command=apply_update)
    update_button.grid(row=3, column=1, columnspan=2, pady=10)

    # Button to save changes to the file
    save_button = tk.Button(update_window, text="Save Changes to File", command=lambda: save_data(json_data))
    save_button.grid(row=4, column=1, columnspan=2, pady=10)

# Set up the main application window
root = tk.Tk()
root.title("Disk Block Occupancy Viewer")
root.geometry("800x400")

# Instructions label
label = tk.Label(root, text="Block Occupancy (Blue = Occupied, White = Free)")
label.pack(pady=10)

# Frame to hold the block buttons
frame = tk.Frame(root)
frame.pack(pady=10)

# Create buttons for each of the 32 blocks
block_buttons = []
for i in range(32):
    btn = tk.Button(frame, text=str(i), width=6, height=3, bg="white")
    btn.grid(row=i // 8, column=i % 8, padx=5, pady=5)  # Arrange in a 4x8 grid
    block_buttons.append(btn)

# Load Blocks button to initialize display
load_button = tk.Button(root, text="Load Blocks from directory.json", command=load_and_display_blocks)
load_button.pack(pady=5)

# Update File button to open update options
update_button = tk.Button(root, text="Update File", command=update_file)
update_button.pack(pady=5)

# Load initial data into memory
json_data = load_data()

# Run the application
root.mainloop()
