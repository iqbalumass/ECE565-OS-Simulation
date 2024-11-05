import json
import tkinter as tk
from tkinter import messagebox

# Function to load JSON data from the file and display occupied blocks
def load_and_display_blocks():
    try:
        with open('directory.json', 'r') as file:
            json_data = json.load(file)
            
        # Clear the text widget before displaying new data
        output_text.delete(1.0, tk.END)
        
        # Process each entry and display occupied blocks
        for entry in json_data:
            file_name = entry["file"]
            start = entry["start"]
            length = entry["length"]
            
            occupied_blocks = list(range(start, start + length))
            output_text.insert(tk.END, f"File '{file_name}' occupies blocks: {occupied_blocks}\n")
    except FileNotFoundError:
        messagebox.showerror("Error", "File 'directory.json' not found.")
    except json.JSONDecodeError:
        messagebox.showerror("Error", "Error decoding JSON data.")

# Set up the main application window
root = tk.Tk()
root.title("Occupied Blocks Viewer")
root.geometry("400x300")

# Create a label
label = tk.Label(root, text="Click the button to load occupied blocks from directory.json")
label.pack(pady=10)

# Create a Text widget for displaying the output
output_text = tk.Text(root, wrap=tk.WORD, height=10, width=50)
output_text.pack(pady=10)

# Create a button to load and display blocks
load_button = tk.Button(root, text="Load Blocks", command=load_and_display_blocks)
load_button.pack(pady=5)

# Run the application
root.mainloop()
