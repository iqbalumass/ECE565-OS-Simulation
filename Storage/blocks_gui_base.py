import json
import tkinter as tk
from tkinter import messagebox

def load_and_display_blocks():
    try:
        with open('directory.json', 'r') as file:
            json_data = json.load(file)
        
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
    
    except FileNotFoundError:
        messagebox.showerror("Error", "File 'directory.json' not found.")
    except json.JSONDecodeError:
        messagebox.showerror("Error", "Error decoding JSON data.")

# Set up the main application window
root = tk.Tk()
root.title("Block Occupancy Viewer")
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

# Button to load and display occupied blocks
load_button = tk.Button(root, text="Load Blocks", command=load_and_display_blocks)
load_button.pack(pady=10)

# Run the application
root.mainloop()
